#!/usr/bin/env python3
# NovaCut Skills · nc-cortar · transcribir.py
"""Transcribe un video hablado palabra por palabra, en tu computadora (sin API, sin claves).

Usa faster-whisper con tiempos por palabra y después ajusta el inicio y el final de cada palabra a la
energía real del audio (Whisper suele inventar el final de la palabra; un corte justo ahí se come sílabas).

Salida: un JSON con cada palabra numerada:
  {"version": 1, "video": "...", "duracion": 41.2, "idioma": "es", "modelo": "small",
   "palabras": [{"id": 0, "texto": "Hola,", "inicio": 0.52, "fin": 0.81, "conf": 0.98}, ...]}

Uso:
  python3 transcribir.py mi_video.mp4
  python3 transcribir.py mi_video.mp4 --modelo medium --idioma es --salida palabras.json

La primera vez se descarga el modelo (una sola vez; "small" pesa alrededor de 480 MB). Después funciona sin internet.
Dependencias: ffmpeg y `pip install faster-whisper` (trae numpy).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

MODELOS = ("tiny", "base", "small", "medium", "large-v3", "large-v3-turbo", "turbo")
# Un "prompt" con muletillas hace que Whisper las escriba en vez de "limpiarlas" (las necesitamos para cortarlas).
PROMPTS = {
    "es": "Eh, este... o sea, mmm, ¿viste? Bueno, eh, lo que te quiero decir es que...",
    "en": "Um, uh, so... like, you know, I mean, uh...",
}

# Ajuste de bordes a la energía (ventanas de 10 ms).
VENTANA = 0.01
ADELANTAR_INICIO = 0.12
ATRASAR_INICIO = 0.10
ESTIRAR_FIN = 0.18
RECORTAR_FIN = 0.12
PALABRA_MIN = 0.04


def error(msg: str, codigo: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def ffprobe(path: Path) -> dict:
    if not shutil.which("ffprobe"):
        error("No encuentro ffprobe (viene con ffmpeg). Instalá ffmpeg: ver nc-editar/instalar_dependencias.md")
    res = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)], capture_output=True, text=True)
    if res.returncode != 0:
        error(f"No pude leer el archivo {path.name}. ¿Es un video válido?\n{res.stderr[-400:]}")
    return json.loads(res.stdout)


def extraer_audio_16k(video: Path, destino: Path) -> float:
    """WAV 16 kHz mono alineado con el primer cuadro del video (si el audio arranca corrido, se compensa)."""
    info = ffprobe(video)
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video" and not (s.get("disposition") or {}).get("attached_pic")), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if a is None:
        error("El video no tiene audio. Esta skill trabaja con lo que decís: usá un video con sonido.")
    filtros = []
    if v is not None:
        offset = float(a.get("start_time") or 0) - float(v.get("start_time") or 0)
        if offset > 0.001:
            filtros.append(f"adelay={int(round(offset * 1000))}:all=1")
        elif offset < -0.001:
            filtros.append(f"atrim=start={-offset:.4f}")
    filtros += ["asetpts=PTS-STARTPTS", "aresample=16000:async=1:first_pts=0"]
    res = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error", "-i", str(video), "-map", "0:a:0", "-af", ",".join(filtros), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(destino)],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        error(f"ffmpeg no pudo extraer el audio:\n{res.stderr[-400:]}")
    return float(info.get("format", {}).get("duration") or 0)


def cargar_modelo(nombre: str, carpeta: str | None):
    try:
        from faster_whisper import WhisperModel  # noqa: PLC0415
    except ImportError:
        error(
            "Falta faster-whisper. Instalalo con:\n"
            "  Mac:     python3 -m pip install faster-whisper\n"
            "  Windows: py -m pip install faster-whisper"
        )
    hilos = max(1, os.cpu_count() or 1)
    origen = carpeta or nombre
    # Primero sin red (si ya está descargado); si no está, se descarga una sola vez.
    try:
        return WhisperModel(origen, device="cpu", compute_type="int8", cpu_threads=hilos, local_files_only=True)
    except Exception:  # noqa: BLE001
        pass
    if carpeta:
        error(f"No pude abrir el modelo de la carpeta {carpeta}. Revisá que sea un modelo de faster-whisper (CTranslate2).")
    print(f"Descargando el modelo '{nombre}' (solo la primera vez; puede tardar varios minutos)...", file=sys.stderr)
    try:
        return WhisperModel(nombre, device="cpu", compute_type="int8", cpu_threads=hilos)
    except Exception as exc:  # noqa: BLE001
        error(
            f"No pude descargar el modelo de transcripción '{nombre}'.\n"
            f"Detalle: {exc.__class__.__name__}: {str(exc)[:200]}\n"
            "Qué revisar:\n"
            "  1. Que tengas internet esta primera vez (se baja de huggingface.co; después ya no hace falta).\n"
            "  2. Que no haya un firewall o VPN bloqueando huggingface.co.\n"
            "  3. Que tengas espacio en disco (small ~480 MB, medium ~1,5 GB).\n"
            "  4. Si ya lo tenés descargado en una carpeta, usá --carpeta-modelo RUTA.",
            3,
        )


def transcribir(wav16: Path, modelo, idioma: str | None) -> tuple[list[dict], str]:
    lang = None if idioma in (None, "auto") else idioma
    segmentos, info = modelo.transcribe(
        str(wav16),
        language=lang,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 400},
        condition_on_previous_text=False,
        initial_prompt=PROMPTS.get(lang or "es"),
        beam_size=5,
    )
    palabras = []
    total = float(getattr(info, "duration", 0) or 0)
    for seg in segmentos:
        for w in getattr(seg, "words", None) or []:
            texto = str(getattr(w, "word", "")).strip()
            if not texto:
                continue
            item = {"texto": texto, "inicio": round(float(w.start), 3), "fin": round(float(w.end), 3)}
            prob = getattr(w, "probability", None)
            if prob is not None:
                item["conf"] = round(float(prob), 3)
            palabras.append(item)
        if total:
            print(f"  ...{min(100, int(seg.end / total * 100))}%", file=sys.stderr, end="\r")
    print("", file=sys.stderr)
    return palabras, getattr(info, "language", lang or "?")


def limpiar(palabras: list[dict]) -> list[dict]:
    """Ordena, descarta vacías o con tiempos imposibles."""
    ok = sorted((w for w in palabras if w["texto"].strip() and w["fin"] >= w["inicio"] >= 0), key=lambda w: (w["inicio"], w["fin"]))
    out: list[dict] = []
    for w in ok:
        if out and w["inicio"] < out[-1]["inicio"]:
            continue
        out.append(w)
    return out


# ─── Ajuste de bordes a la energía del audio ─────────────────────────────


def energia(wav16: Path):
    """Energía en dB por ventana de 10 ms y el umbral de voz de este audio (relativo al ruido de la sala)."""
    import numpy as np  # noqa: PLC0415 (viene con faster-whisper)

    with wave.open(str(wav16), "rb") as f:
        rate, canales = f.getframerate(), f.getnchannels()
        crudo = f.readframes(f.getnframes())
    x = np.frombuffer(crudo, dtype="<i2").astype(np.float32) / 32768.0
    if canales > 1:
        x = x.reshape(-1, canales).mean(axis=1)
    hop = max(1, int(rate * VENTANA))
    n = len(x) // hop
    if n == 0:
        return np.full(1, -100.0), -40.0
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    piso, fuerte = float(np.percentile(db, 10)), float(np.percentile(db, 90))
    umbral = max(piso + 6.0, min(fuerte - 20.0, piso + 12.0), -55.0)
    return db, umbral


def ajustar_bordes(palabras: list[dict], db, umbral: float, duracion: float) -> list[dict]:
    """Mueve inicio y fin de cada palabra hasta donde la voz empieza/termina de verdad, sin pisar a las vecinas."""
    n = len(db)
    sonando = db > umbral

    def idx(t: float) -> int:
        return max(0, min(n - 1, int(round(t / VENTANA))))

    out: list[dict] = []
    for i, w in enumerate(palabras):
        ini = float(w["inicio"])
        fin = max(float(w["fin"]), ini + PALABRA_MIN)
        fin_previo = out[-1]["fin"] if out else 0.0
        ini_siguiente = float(palabras[i + 1]["inicio"]) if i + 1 < len(palabras) else duracion

        k = idx(ini)
        if sonando[k]:
            lo = idx(max(fin_previo, ini - ADELANTAR_INICIO))
            while k > lo and sonando[k - 1]:
                k -= 1
        else:
            hi = idx(min(fin - PALABRA_MIN, ini + ATRASAR_INICIO))
            while k < hi and not sonando[k]:
                k += 1
        nuevo_ini = k * VENTANA

        k = idx(fin) - 1
        if 0 <= k < n and sonando[k]:
            hi = idx(min(ini_siguiente, fin + ESTIRAR_FIN))
            while k + 1 < hi and sonando[k + 1]:
                k += 1
        else:
            lo = idx(max(nuevo_ini + PALABRA_MIN, fin - RECORTAR_FIN))
            while k > lo and not sonando[k]:
                k -= 1
        nuevo_fin = (k + 1) * VENTANA

        nuevo_ini = max(fin_previo, min(nuevo_ini, ini + ATRASAR_INICIO))
        nuevo_fin = min(max(nuevo_fin, nuevo_ini + PALABRA_MIN), max(ini_siguiente, nuevo_ini + PALABRA_MIN), duracion or 1e9)
        if nuevo_fin - nuevo_ini < PALABRA_MIN:
            nuevo_ini, nuevo_fin = ini, fin
        out.append({**w, "inicio": round(nuevo_ini, 3), "fin": round(nuevo_fin, 3)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Transcribe un video palabra por palabra con faster-whisper (local, sin API) y guarda un JSON con IDs de palabra.",
    )
    ap.add_argument("video", help="video o audio de entrada (mp4, mov, m4a, wav...)")
    ap.add_argument("--modelo", default="small", help=f"modelo de whisper: {', '.join(MODELOS)} (default: small)")
    ap.add_argument("--idioma", default="es", help="código de idioma (es, en, pt...) o 'auto' (default: es)")
    ap.add_argument("--salida", help="ruta del JSON (default: <video>_novacut/palabras.json)")
    ap.add_argument("--carpeta-modelo", help="carpeta con un modelo de faster-whisper ya descargado (sin internet)")
    ap.add_argument("--sin-ajuste", action="store_true", help="no ajustar los bordes de las palabras a la energía del audio")
    args = ap.parse_args()

    video = Path(args.video).expanduser().resolve()
    if not video.is_file():
        error(f"No existe el archivo: {video}")
    if not shutil.which("ffmpeg"):
        error("No encuentro ffmpeg. Instalalo: ver nc-editar/instalar_dependencias.md")
    salida = Path(args.salida).expanduser() if args.salida else video.parent / f"{video.stem}_novacut" / "palabras.json"
    salida.parent.mkdir(parents=True, exist_ok=True)

    modelo = cargar_modelo(args.modelo, args.carpeta_modelo)
    with tempfile.TemporaryDirectory(prefix="novacut-") as tmp:
        wav16 = Path(tmp) / "audio16k.wav"
        duracion = extraer_audio_16k(video, wav16)
        print(f"Transcribiendo {video.name} ({duracion:.0f} s) con '{args.modelo}'...", file=sys.stderr)
        palabras, idioma = transcribir(wav16, modelo, args.idioma)
        palabras = limpiar(palabras)
        if not palabras:
            error("No encontré voz en el video. ¿Tiene audio hablado? ¿Está muy bajo?", 4)
        if not args.sin_ajuste:
            try:
                db, umbral = energia(wav16)
                palabras = ajustar_bordes(palabras, db, umbral, duracion)
            except ImportError:
                print("Aviso: sin numpy no ajusto los bordes de las palabras (instalá faster-whisper, que lo trae).", file=sys.stderr)

    for i, w in enumerate(palabras):
        w["id"] = i
    data = {
        "version": 1,
        "video": str(video),
        "duracion": round(duracion, 3),
        "idioma": idioma,
        "modelo": args.modelo,
        "palabras": [{"id": w["id"], "texto": w["texto"], "inicio": w["inicio"], "fin": w["fin"], **({"conf": w["conf"]} if "conf" in w else {})} for w in palabras],
    }
    salida.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Listo: {len(palabras)} palabras -> {salida}")


if __name__ == "__main__":
    main()
