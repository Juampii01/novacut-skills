#!/usr/bin/env python3
# NovaCut Skills · nc-cortar · render.py
"""Aplica un plan de cortes v2 a un video: saca lo marcado y acorta las pausas largas, sin desfasar audio y video.

El plan nunca tiene segundos: dice qué PALABRAS se sacan (por ID), y los tiempos salen de la transcripción.

  {
    "version": 2,
    "format": "9:16",                      # opcional: "9:16" o "16:9" (default: según el video)
    "removals": [
      {"from_word": 3, "to_word": 3, "reason": "filler", "confidence": 0.9, "nota": "eh"},
      {"from_word": 10, "to_word": 18, "reason": "retake", "confidence": 0.85}
    ],
    "hook": {"from_word": 40, "to_word": 52},  # opcional: ese tramo pasa al principio del video
    "pausa_max": 0.5,                        # opcional: pausas más largas que esto se recortan (0.2 a 1.2)
    "captions": {"emphasis_words": [12, 44]}, # opcional: palabras clave para los subtítulos
    "summary": "..."
  }

Cómo corta (lo que hace que no se note):
- Todo se ajusta a la rejilla de cuadros (30 por segundo por defecto) y el MISMO corte se aplica al audio y al video:
  cada tramo son N cuadros y exactamente N × 1600 muestras de audio (48 kHz / 30). No hay desfase acumulado.
- Fundido de audio de 10 ms en cada borde: sin clics.
- Deja 80 ms de aire antes y 140 ms después de cada tramo (sin meter pedazos de lo cortado).
- Video de cuadros variables (VFR, típico del celular) o 29,97: se normaliza a cuadros fijos antes de cortar.
- HDR del iPhone: se pasa a SDR BT.709 (si tu ffmpeg tiene zscale), así no sale lavado.

Salida: MP4 H.264 + AAC, y al lado <salida>.palabras.json con los tiempos re-mapeados al video cortado (para
nc-subtitulos). Nunca sobrescribe el original.

Uso:
  python3 render.py video.mp4 palabras.json plan.json --simular      # valida y muestra qué se corta, sin renderizar
  python3 render.py video.mp4 palabras.json plan.json                # renderiza
  python3 render.py video.mp4 palabras.json plan.json --formato 9:16 --salida corte.mp4
Dependencias: ffmpeg/ffprobe. Solo biblioteca estándar de Python.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path

SR = 48000
FADE = 0.010
PAD_IN = 0.08
PAD_OUT = 0.14
PAUSA_MAX = 0.5
MIN_CUADROS = 3
TAMANOS = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
MOTIVOS = {"retake", "false_start", "filler", "silence", "off_topic", "other"}
NOMBRE_MOTIVO = {"retake": "retoma", "false_start": "arranque en falso", "filler": "muletilla", "silence": "silencio", "off_topic": "fuera de tema", "other": "otro"}
HDR = {"smpte2084", "arib-std-b67"}


class ErrorPlan(Exception):
    pass


def error(msg: str, codigo: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def correr(cmd: list[str], que: str) -> str:
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        error(f"ffmpeg falló en: {que}.\n{res.stderr[-1500:]}")
    return res.stderr


def fraccion(v: str | None) -> float:
    if not v or v in ("0/0", "N/A"):
        return 0.0
    if "/" in v:
        a, b = v.split("/", 1)
        return float(a) / float(b) if float(b) else 0.0
    return float(v)


# ─── Entrada ──────────────────────────────────────────────────────────────


def probar(video: Path) -> dict:
    res = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video)], capture_output=True, text=True)
    if res.returncode != 0:
        error(f"No pude leer {video.name}. ¿Es un video válido?\n{res.stderr[-400:]}")
    probe = json.loads(res.stdout)
    streams = probe.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video" and not (s.get("disposition") or {}).get("attached_pic")), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if v is None:
        error("El archivo no tiene video.")
    if a is None:
        error("El video no tiene audio: esta skill corta a partir de lo que decís.")
    rot = 0
    for side in v.get("side_data_list", []) or []:
        if "rotation" in side:
            rot = int(round(float(side["rotation"])))
    if not rot and (v.get("tags") or {}).get("rotate"):
        rot = -int(v["tags"]["rotate"])
    rot = ((rot + 180) % 360) - 180
    w, h = int(v.get("width") or 0), int(v.get("height") or 0)
    if abs(rot) == 90:
        w, h = h, w
    r_fps, avg = fraccion(v.get("r_frame_rate")), fraccion(v.get("avg_frame_rate"))
    trc = (v.get("color_transfer") or "").lower()
    prim = (v.get("color_primaries") or "").lower()
    dur_v = float(v.get("duration") or 0) or float(probe.get("format", {}).get("duration") or 0)
    return {
        "ancho": w,
        "alto": h,
        "fps": round(avg or r_fps, 3),
        "vfr": bool(r_fps and avg and abs(r_fps - avg) / r_fps > 0.01),
        "hdr": trc in HDR or (prim == "bt2020" and trc not in ("bt709", "")),
        "duracion": float(probe.get("format", {}).get("duration") or dur_v),
        "duracion_video": dur_v,
        "inicio_video": float(v.get("start_time") or 0),
        "inicio_audio": float(a.get("start_time") or 0),
    }


def cargar_palabras(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"No pude leer las palabras ({path}): {exc}")
    palabras = data.get("palabras") if isinstance(data, dict) else data
    if not isinstance(palabras, list) or not palabras:
        error("El JSON de palabras no tiene una lista 'palabras'.")
    out = []
    for i, w in enumerate(palabras):
        item = {"id": int(w.get("id", i)), "texto": str(w.get("texto", w.get("text", ""))), "inicio": float(w.get("inicio", w.get("start", 0))), "fin": float(w.get("fin", w.get("end", 0)))}
        if item["id"] != i:
            error("Los IDs de palabra tienen que ser 0, 1, 2... en orden. Volvé a correr transcribir.py.")
        if item["fin"] < item["inicio"]:
            item["fin"] = item["inicio"]
        out.append(item)
    return out


# ─── Plan ────────────────────────────────────────────────────────────────


def validar_plan(plan: dict, n: int) -> tuple[list[dict], list[str]]:
    """Devuelve los cortes ordenados y avisos. Lanza ErrorPlan si el plan no se puede aplicar."""
    avisos: list[str] = []
    if not isinstance(plan, dict):
        raise ErrorPlan("el plan tiene que ser un objeto JSON.")
    if plan.get("version") != 2:
        raise ErrorPlan('el plan tiene que tener "version": 2.')
    fmt = plan.get("format")
    if fmt is not None and fmt not in TAMANOS:
        raise ErrorPlan('"format" tiene que ser "9:16" o "16:9".')
    removals = plan.get("removals", [])
    if not isinstance(removals, list):
        raise ErrorPlan('"removals" tiene que ser una lista.')
    limpios = []
    for k, r in enumerate(removals):
        if not isinstance(r, dict) or "from_word" not in r or "to_word" not in r:
            raise ErrorPlan(f"el corte #{k + 1} necesita from_word y to_word (IDs de palabra, nunca segundos).")
        a, b = r["from_word"], r["to_word"]
        if not (isinstance(a, int) and isinstance(b, int)) or isinstance(a, bool) or isinstance(b, bool):
            raise ErrorPlan(f"el corte #{k + 1} tiene IDs que no son números enteros ({a!r}, {b!r}). Los cortes se indican con IDs de palabra, no con segundos.")
        if not (0 <= a < n and 0 <= b < n):
            raise ErrorPlan(f"el corte #{k + 1} usa IDs que no existen ({a}-{b}); la transcripción tiene palabras 0 a {n - 1}.")
        if a > b:
            raise ErrorPlan(f"el corte #{k + 1} tiene from_word ({a}) mayor que to_word ({b}).")
        reason = r.get("reason", "other")
        if reason not in MOTIVOS:
            avisos.append(f"corte #{k + 1}: motivo desconocido «{reason}» (se corta igual).")
        limpios.append({**r, "from_word": a, "to_word": b, "reason": reason})
    limpios.sort(key=lambda r: (r["from_word"], r["to_word"]))
    for x, y in zip(limpios, limpios[1:]):
        if y["from_word"] <= x["to_word"]:
            raise ErrorPlan(f"dos cortes se superponen: {x['from_word']}-{x['to_word']} y {y['from_word']}-{y['to_word']}. Unilos en uno solo o separalos.")
    hook = plan.get("hook")
    if hook is not None:
        if not isinstance(hook, dict) or not all(isinstance(hook.get(k), int) for k in ("from_word", "to_word")):
            raise ErrorPlan('"hook" tiene que ser {"from_word": id, "to_word": id}.')
        if not (0 <= hook["from_word"] <= hook["to_word"] < n):
            raise ErrorPlan(f"el gancho usa IDs inválidos ({hook['from_word']}-{hook['to_word']}).")
    pm = plan.get("pausa_max")
    if pm is not None and not isinstance(pm, (int, float)):
        raise ErrorPlan('"pausa_max" tiene que ser un número de segundos (0.2 a 1.2).')
    emph = (plan.get("captions") or {}).get("emphasis_words", [])
    if not isinstance(emph, list) or any(not isinstance(i, int) or not 0 <= i < n for i in emph):
        raise ErrorPlan('"captions.emphasis_words" tiene que ser una lista de IDs de palabra existentes.')
    quitadas = sum(r["to_word"] - r["from_word"] + 1 for r in limpios)
    if quitadas >= n:
        raise ErrorPlan("el plan corta todas las palabras: no quedaría video.")
    if quitadas > 0.6 * n:
        avisos.append(f"el plan saca {quitadas} de {n} palabras ({quitadas * 100 // n} %). ¿Seguro?")
    return limpios, avisos


def timeline(palabras: list[dict], cortes: list[dict], plan: dict, fps: int, duracion: float) -> dict:
    """Del plan a los tramos (en cuadros) que quedan, en orden, y las palabras con tiempos del video cortado."""
    n = len(palabras)
    quitadas = set()
    for r in cortes:
        quitadas.update(range(r["from_word"], r["to_word"] + 1))
    pausa_max = max(0.2, min(1.2, float(plan.get("pausa_max") or PAUSA_MAX)))
    hook = plan.get("hook")
    en_hook = (lambda i: hook["from_word"] <= i <= hook["to_word"]) if hook else (lambda i: False)
    primera = next((w["id"] for w in palabras if w["id"] not in quitadas), None)
    hook_al_inicio = bool(hook and primera is not None and hook["from_word"] <= primera)

    def tramos(queda) -> list[dict]:
        runs, actual = [], None

        def cerrar():
            nonlocal actual
            if actual is None:
                return
            f, l = palabras[actual[0]], palabras[actual[1]]
            prev = palabras[actual[0] - 1] if actual[0] > 0 else None
            nxt = palabras[actual[1] + 1] if actual[1] + 1 < n else None
            # El aire se recorta a la mitad del hueco con la palabra vecina, para no meter un pedazo de lo cortado.
            ini = max(0.0, f["inicio"] - min(PAD_IN, max(0.0, f["inicio"] - prev["fin"]) / 2 if prev else PAD_IN))
            fin = min(duracion, l["fin"] + min(PAD_OUT, max(0.0, nxt["inicio"] - l["fin"]) / 2 if nxt else PAD_OUT))
            runs.append({"primera": actual[0], "ultima": actual[1], "ini": ini, "fin": fin})
            actual = None

        for w in palabras:
            if not queda(w["id"]):
                cerrar()
                continue
            pausa_larga = actual is not None and w["inicio"] - palabras[actual[1]]["fin"] > pausa_max
            if actual is not None and (w["id"] != actual[1] + 1 or pausa_larga):
                cerrar()
            if actual is None:
                actual = [w["id"], w["id"]]
            else:
                actual[1] = w["id"]
        cerrar()
        return runs

    max_cuadro = int(math.floor(duracion * fps + 1e-6))

    def a_clips(runs: list[dict], rol: str) -> list[dict]:
        clips: list[dict] = []
        for r in runs:
            a = max(0, int(round(r["ini"] * fps)))
            b = min(max_cuadro, int(round(r["fin"] * fps)))
            if b - a < MIN_CUADROS:
                b = min(max_cuadro, a + MIN_CUADROS)
            prev = clips[-1] if clips else None
            # Dos tramos que se tocan después de ajustar a cuadros se unen (no hace falta un corte).
            if prev and a <= prev["b"] and r["primera"] > prev["ultima"]:
                prev["b"] = max(prev["b"], b)
                prev["ultima"] = r["ultima"]
                continue
            if prev and a < prev["b"]:
                a = prev["b"]
            if b <= a:
                continue
            clips.append({"a": a, "b": b, "rol": rol, "primera": r["primera"], "ultima": r["ultima"]})
        return clips

    hook_runs = tramos(lambda i: en_hook(i) and i not in quitadas) if hook and not hook_al_inicio else []
    cuerpo = tramos(lambda i: i not in quitadas and (hook_al_inicio or not en_hook(i)))
    clips = a_clips(hook_runs, "gancho") + a_clips(cuerpo, "cuerpo")

    emph = set((plan.get("captions") or {}).get("emphasis_words", []))
    nuevas, offset = [], 0.0
    for c in clips:
        c0, cdur = c["a"] / fps, (c["b"] - c["a"]) / fps
        for i in range(c["primera"], c["ultima"] + 1):
            if i in quitadas or (c["rol"] == "cuerpo" and not hook_al_inicio and en_hook(i)):
                continue
            w = palabras[i]
            ini = offset + max(0.0, w["inicio"] - c0)
            fin = offset + min(cdur, max(w["fin"] - c0, w["inicio"] - c0 + 0.05))
            nuevas.append({"id_original": i, "texto": w["texto"], "inicio": round(ini, 3), "fin": round(max(fin, ini + 0.05), 3), "clave": i in emph, "fin_frase": bool(re.search(r"[.?!…][\"'”»)]*$", w["texto"].strip()))})
        offset += cdur
    for k, w in enumerate(nuevas):
        w["id"] = k
    total = sum(c["b"] - c["a"] for c in clips)
    return {"clips": clips, "cuadros": total, "duracion": total / fps, "palabras": nuevas, "quitadas": quitadas, "pausa_max": pausa_max}


# ─── Audio: los mismos cortes, muestra a muestra ─────────────────────────


def extraer_audio(video: Path, info: dict, destino: Path) -> None:
    """WAV 48 kHz mono alineado con el cuadro 0 del video."""
    offset = info["inicio_audio"] - info["inicio_video"]
    f = []
    if offset > 0.001:
        f.append(f"adelay={int(round(offset * 1000))}:all=1")
    elif offset < -0.001:
        f.append(f"atrim=start={-offset:.4f}")
    f += ["asetpts=PTS-STARTPTS", f"aresample={SR}:async=1:first_pts=0"]
    correr(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error", "-i", str(video), "-map", "0:a:0", "-af", ",".join(f), "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(destino)], "extraer el audio")


def cortar_audio(wav: Path, clips: list[dict], fps: int, destino: Path) -> int:
    """Cada tramo son exactamente (cuadros × muestras por cuadro) muestras, con fundido de 10 ms en cada borde."""
    spf = SR // fps
    with wave.open(str(wav), "rb") as f:
        crudo = f.readframes(f.getnframes())
    total_src = len(crudo) // 2
    fade = max(1, int(round(FADE * SR)))
    rampa = [k / fade for k in range(fade)]
    total = 0
    with wave.open(str(destino), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SR)
        for c in clips:
            sa, sb = c["a"] * spf, c["b"] * spf
            pieza = array("h")
            hasta = min(sb, total_src)
            if sa < hasta:
                pieza.frombytes(crudo[2 * sa : 2 * hasta])
            if len(pieza) < sb - sa:
                pieza.extend([0] * (sb - sa - len(pieza)))
            if sys.byteorder == "big":
                pieza.byteswap()
            if len(pieza) >= 2 * fade:
                for k in range(fade):
                    pieza[k] = int(pieza[k] * rampa[k])
                    pieza[-1 - k] = int(pieza[-1 - k] * rampa[k])
            if sys.byteorder == "big":
                pieza.byteswap()
            out.writeframes(pieza.tobytes())
            total += len(pieza)
    return total


# ─── Video ───────────────────────────────────────────────────────────────


def tiene_filtro(nombre: str) -> bool:
    res = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return bool(re.search(rf"^\s*\S+\s+{re.escape(nombre)}\s", res.stdout, re.M))


def encuadre(src_w: int, src_h: int, fmt: str, offset_x: float) -> str:
    """Filtros para llevar el video al tamaño de salida (sin etiquetas de entrada/salida)."""
    out_w, out_h = TAMANOS[fmt]
    destino, origen = out_w / out_h, src_w / src_h
    if origen > destino * 1.02:
        # Más ancho que la salida (16:9 -> 9:16): recorte fijo, centrado o corrido con --encuadre-x.
        crop_w = min(src_w, int(round(src_h * destino / 2)) * 2)
        libre = src_w - crop_w
        x = max(0, min(libre, int(round(libre / 2 * (1 + max(-1.0, min(1.0, offset_x)))))))
        return f"crop={crop_w}:{src_h}:{x}:0,scale={out_w}:{out_h}:flags=lanczos,setsar=1"
    if origen < destino / 1.02 and fmt == "16:9":
        # Vertical a horizontal: el video al centro sobre una copia desenfocada de sí mismo.
        return (
            f"split[fa][fb];[fa]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,crop={out_w}:{out_h},boxblur=24:2,eq=brightness=-0.08[fondo];"
            f"[fb]scale=-2:{out_h}:flags=lanczos[frente];[fondo][frente]overlay=(W-w)/2:0,setsar=1"
        )
    return f"scale={out_w}:{out_h}:force_original_aspect_ratio=increase:flags=lanczos,crop={out_w}:{out_h},setsar=1"


def grafo_video(info: dict, clips: list[dict], fps: int, fmt: str, offset_x: float, hdr_ok: bool) -> str:
    cadena = ["setpts=PTS-STARTPTS"]
    if info["hdr"] and hdr_ok:
        cadena += ["zscale=t=linear:npl=100", "format=gbrpf32le", "zscale=p=bt709", "tonemap=tonemap=hable:desat=0", "zscale=t=bt709:m=bt709:r=tv"]
    cadena.append(f"fps={fps}")
    expr = "+".join(f"between(n,{c['a']},{c['b'] - 1})" for c in clips)
    cadena += [f"select='{expr}'", f"setpts=N/({fps}*TB)"]
    return f"[0:v]{','.join(cadena)},{encuadre(info['ancho'], info['alto'], fmt, offset_x)},format=yuv420p[v]"


def codificar(video: Path, wav_cortado: Path, grafo: str, cuadros: int, fps: int, salida: Path, crf: int, preset: str, tmpdir: Path) -> None:
    base = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error", "-stats", "-i", str(video), "-i", str(wav_cortado)]
    resto = [
        "-map", "[v]", "-map", "1:a:0",
        "-frames:v", str(cuadros), "-r", str(fps), "-fps_mode", "cfr",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", preset, "-crf", str(crf), "-g", str(fps * 2),
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart",
        str(salida),
    ]
    if len(grafo) < 20000:
        intentos = [base + ["-filter_complex", grafo] + resto]
    else:
        # Muchos cortes: el filtro va en un archivo (en Windows la línea de comandos tiene un límite de largo).
        script = tmpdir / "filtro.txt"
        script.write_text(grafo, encoding="utf-8")
        intentos = [base + ["-/filter_complex", str(script)] + resto, base + ["-filter_complex_script", str(script)] + resto]
    ultimo = ""
    for cmd in intentos:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode == 0:
            return
        ultimo = res.stderr
        if "fps_mode" in ultimo and "Unrecognized option" in ultimo:
            # ffmpeg anterior a 5.1: la opción se llamaba -vsync.
            cmd2 = [("-vsync" if x == "-fps_mode" else x) for x in cmd]
            res = subprocess.run(cmd2, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res.returncode == 0:
                return
            ultimo = res.stderr
    error(f"ffmpeg falló al renderizar el video cortado.\n{ultimo[-1500:]}")


def duraciones(path: Path) -> tuple[float, float, int, int]:
    res = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-count_frames", str(path)], capture_output=True, text=True)
    data = json.loads(res.stdout or "{}")
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    return float(v.get("duration") or 0), float(a.get("duration") or 0), int(v.get("nb_read_frames") or 0), int(v.get("width") or 0) * 10000 + int(v.get("height") or 0)


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def resumen(palabras: list[dict], cortes: list[dict], tl: dict, info: dict, fmt: str, avisos: list[str], plan: dict) -> str:
    lineas = [f"Video original: {mmss(info['duracion'])} ({info['duracion']:.2f} s) · {info['ancho']}x{info['alto']} · {info['fps']} fps{' VFR' if info['vfr'] else ''}{' HDR' if info['hdr'] else ''}"]
    lineas.append(f"Video editado:  {mmss(tl['duracion'])} ({tl['duracion']:.2f} s) · formato {fmt} · {len(tl['clips'])} tramos")
    ahorro = info["duracion"] - tl["duracion"]
    lineas.append(f"Se quitan {ahorro:.1f} s ({ahorro / max(info['duracion'], 0.001) * 100:.0f} %): {len(cortes)} cortes del plan + pausas de más de {tl['pausa_max']:.2f} s")
    if plan.get("hook"):
        h = plan["hook"]
        lineas.append(f"Gancho al principio: palabras {h['from_word']}-{h['to_word']}: «{' '.join(w['texto'] for w in palabras[h['from_word']:h['to_word'] + 1])}»")
    if cortes:
        lineas.append("Cortes:")
        for k, r in enumerate(cortes, 1):
            txt = " ".join(w["texto"] for w in palabras[r["from_word"] : r["to_word"] + 1])
            if len(txt) > 90:
                txt = txt[:87] + "..."
            t0 = palabras[r["from_word"]]["inicio"]
            lineas.append(f"  {k:>2}. [{mmss(t0)}] {NOMBRE_MOTIVO.get(r['reason'], r['reason'])}: «{txt}»")
    for a in avisos:
        lineas.append(f"Aviso: {a}")
    return "\n".join(lineas)


def main() -> None:
    ap = argparse.ArgumentParser(description="Aplica un plan de cortes v2 (por IDs de palabra) a un video, con cortes alineados a cuadros en audio y video.")
    ap.add_argument("video")
    ap.add_argument("palabras", help="JSON de transcribir.py")
    ap.add_argument("plan", help="plan v2 (JSON)")
    ap.add_argument("--salida", help="MP4 de salida (default: <video>_novacut/cortado.mp4)")
    ap.add_argument("--formato", choices=["auto", "9:16", "16:9"], help="default: el del plan o, si no dice, según el video")
    ap.add_argument("--fps", type=int, default=30, choices=[24, 25, 30, 60], help="cuadros por segundo de salida (default 30)")
    ap.add_argument("--encuadre-x", type=float, default=0.0, help="al recortar 16:9 a 9:16: -1 izquierda, 0 centro, 1 derecha")
    ap.add_argument("--crf", type=int, default=17, help="calidad x264 (menor = mejor; default 17)")
    ap.add_argument("--preset", default="medium", help="velocidad x264 (veryfast, fast, medium, slow; default medium)")
    ap.add_argument("--simular", action="store_true", help="solo validar el plan y mostrar qué se corta, sin renderizar")
    args = ap.parse_args()

    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            error(f"No encuentro {prog}. Instalá ffmpeg: ver nc-editar/instalar_dependencias.md")
    video = Path(args.video).expanduser().resolve()
    if not video.is_file():
        error(f"No existe el video: {video}")
    palabras = cargar_palabras(Path(args.palabras).expanduser())
    try:
        plan = json.loads(Path(args.plan).expanduser().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"No pude leer el plan: {exc}")
    try:
        cortes, avisos = validar_plan(plan, len(palabras))
    except ErrorPlan as exc:
        error(f"El plan no es válido: {exc}", 2)

    info = probar(video)
    fmt = args.formato if args.formato and args.formato != "auto" else plan.get("format")
    if fmt not in TAMANOS:
        fmt = "9:16" if info["alto"] > info["ancho"] else "16:9"
    if palabras[-1]["fin"] > info["duracion"] + 0.5:
        error(f"Las palabras llegan hasta {palabras[-1]['fin']:.1f} s pero el video dura {info['duracion']:.1f} s. ¿Son de otro video?")
    tl = timeline(palabras, cortes, plan, args.fps, min(info["duracion"], info["duracion_video"] or info["duracion"]))
    if not tl["clips"]:
        error("Después de aplicar el plan no queda nada del video.", 2)
    print(resumen(palabras, cortes, tl, info, fmt, avisos, plan))
    if args.simular:
        print("\n(Simulación: no se renderizó nada.)")
        return

    salida = Path(args.salida).expanduser().resolve() if args.salida else video.parent / f"{video.stem}_novacut" / "cortado.mp4"
    if salida == video:
        error("La salida no puede ser el video original: nunca lo sobrescribo. Elegí otro nombre con --salida.")
    salida.parent.mkdir(parents=True, exist_ok=True)
    hdr_ok = True
    if info["hdr"] and not tiene_filtro("zscale"):
        hdr_ok = False
        print("Aviso: el video es HDR y tu ffmpeg no tiene zscale; los colores pueden salir lavados.", file=sys.stderr)

    with tempfile.TemporaryDirectory(prefix="novacut-") as tmp:
        tmpdir = Path(tmp)
        wav = tmpdir / "audio.wav"
        wav_cortado = tmpdir / "audio_cortado.wav"
        extraer_audio(video, info, wav)
        muestras = cortar_audio(wav, tl["clips"], args.fps, wav_cortado)
        grafo = grafo_video(info, tl["clips"], args.fps, fmt, args.encuadre_x, hdr_ok)
        print(f"\nRenderizando {len(tl['clips'])} tramos ({tl['duracion']:.1f} s)...", file=sys.stderr)
        parcial = salida.with_name(salida.stem + ".parcial" + salida.suffix)
        codificar(video, wav_cortado, grafo, tl["cuadros"], args.fps, parcial, args.crf, args.preset, tmpdir)
        os.replace(parcial, salida)

    dv, da, cuadros, _ = duraciones(salida)
    esperado = tl["duracion"]
    ok_dur = abs(dv - esperado) <= 1.5 / args.fps
    ok_sync = abs(da - dv) <= 0.05
    palabras_json = salida.with_name(salida.stem + ".palabras.json")
    palabras_json.write_text(
        json.dumps(
            {"version": 1, "video": str(salida), "duracion": round(esperado, 3), "fps": args.fps, "formato": fmt, "origen": str(video), "palabras": tl["palabras"],
             "tramos": [{"desde_cuadro": c["a"], "hasta_cuadro": c["b"], "rol": c["rol"]} for c in tl["clips"]]},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\nListo: {salida}")
    print(f"  Duración video {dv:.3f} s · audio {da:.3f} s · esperado {esperado:.3f} s · {cuadros} cuadros (esperados {tl['cuadros']}) · audio {muestras / SR:.3f} s")
    print(f"  Control: duración {'OK' if ok_dur else 'REVISAR'} · sincronía audio/video {'OK' if ok_sync else 'REVISAR'} (diferencia {abs(da - dv) * 1000:.0f} ms)")
    print(f"  Palabras re-mapeadas para subtítulos: {palabras_json}")
    if not (ok_dur and ok_sync):
        sys.exit(5)


if __name__ == "__main__":
    main()
