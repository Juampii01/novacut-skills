#!/usr/bin/env python3
# NovaCut Skills · nc-subtitulos · subtitulos.py
"""Subtítulos animados palabra por palabra, quemados en el video con ffmpeg (libass). También deja el .srt.

- La palabra que estás diciendo se resalta (color de acento y un pequeño "pop").
- Las palabras clave quedan en otro color todo el bloque (las que marcó el plan y, si no hay, los números).
- Máximo 2 líneas por bloque, cortes en pausas y en fin de frase.
- Zona segura: en 9:16 el texto queda arriba del 30 % inferior (ahí van los botones, la descripción y el audio de
  las redes) y con más margen a la derecha (botones de me gusta/comentar). En 16:9, cerca del borde inferior.
- Fuente incluida: Montserrat (licencia SIL OFL 1.1, archivo fuentes/OFL-Montserrat.txt). Si falta, usa una fuente
  del sistema y lo avisa.

Entrada: el JSON de palabras YA RE-MAPEADO al video cortado (el <salida>.palabras.json que deja nc-cortar/render.py).
Si el video no se cortó, sirve directo el palabras.json de transcribir.py.

Uso:
  python3 subtitulos.py video.mp4 video.palabras.json                      # -> video_subtitulado.mp4 + .srt
  python3 subtitulos.py video.mp4 palabras.json --estilo impacto --color-activo "#00E5FF"
  python3 subtitulos.py video.mp4 palabras.json --solo-srt                  # solo el .srt (y el .ass)
Dependencias: ffmpeg con libass (filtro "ass"). Solo biblioteca estándar de Python.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FUENTES = AQUI / "fuentes"

ESTILOS = {
    # tamaño en px para 1080 de ancho (9:16) o 1920 (16:9); palabras máximas por bloque; ancho medio de letra (em)
    "limpio": {"fuente": "Montserrat ExtraBold", "archivo": "Montserrat-ExtraBold.ttf", "v": 78, "h": 66, "palabras": 7, "mayus": False, "borde": 5, "sombra": 2, "em": 0.62},
    "impacto": {"fuente": "Montserrat Black", "archivo": "Montserrat-Black.ttf", "v": 104, "h": 84, "palabras": 3, "mayus": True, "borde": 6, "sombra": 3, "em": 0.72},
}
RESPALDO = "Arial"  # si no está la fuente incluida (libass busca una parecida en el sistema)
PAUSA_CORTE = 0.45
PUENTE = 0.35
NUMEROS = {
    "cero", "uno", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "quince", "veinte",
    "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa", "cien", "ciento", "doscientos", "quinientos", "mil",
    "millon", "millón", "millones", "mitad", "doble", "triple", "primero", "primera", "segundo", "segunda", "tercero", "tercera",
}
VACIAS = {"una", "uno"}  # "una" casi nunca es un número que valga resaltar


def error(msg: str, codigo: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def color_ass(hex_color: str) -> str:
    h = hex_color.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        error(f"Color inválido: {hex_color} (usá #RRGGBB, por ejemplo #FFD84D)")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def t_ass(s: float) -> str:
    cs = max(0, int(round(s * 100)))
    h, r = divmod(cs, 360000)
    m, r = divmod(r, 6000)
    sec, cs = divmod(r, 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def t_srt(s: float) -> str:
    ms = max(0, int(round(s * 1000)))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def limpiar_texto(t: str) -> str:
    """Saca la puntuación de los bordes que no aporta en pantalla (comas, puntos); deja ¿? ¡!."""
    t = re.sub(r'^[\s"\'“”«»(\[]+|[\s"\'“”«»)\].,;:…]+$', "", t).strip()
    return t.replace("\\", "").replace("{", "(").replace("}", ")")


def norm(t: str) -> str:
    import unicodedata  # noqa: PLC0415

    t = unicodedata.normalize("NFD", t.lower())
    return re.sub(r"[^\w%$]+", "", "".join(c for c in t if unicodedata.category(c) != "Mn"))


def es_numero(texto: str) -> bool:
    n = norm(texto)
    return bool(re.search(r"\d", n)) or "%" in texto or "$" in texto or (n in {norm(x) for x in NUMEROS} and n not in VACIAS)


def cargar(path: Path, claves_extra: set[int], auto: bool) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"No pude leer las palabras ({path}): {exc}")
    lista = data.get("palabras") if isinstance(data, dict) else data
    if not isinstance(lista, list) or not lista:
        error("El JSON no tiene una lista 'palabras'.")
    out = []
    hay_claves = any(w.get("clave") for w in lista) or bool(claves_extra)
    for i, w in enumerate(lista):
        crudo = str(w.get("texto", w.get("text", "")))
        texto = limpiar_texto(crudo)
        if not texto:
            continue
        orig = w.get("id_original", w.get("id", i))
        clave = bool(w.get("clave")) or orig in claves_extra or (auto and not hay_claves and es_numero(texto))
        fin_frase = bool(w.get("fin_frase")) or bool(re.search(r"[.?!…][\"'”»)]*$", crudo.strip()))
        out.append({"texto": texto, "inicio": float(w.get("inicio", w.get("start", 0))), "fin": float(w.get("fin", w.get("end", 0))), "clave": clave, "fin_frase": fin_frase})
    return out


def lineas_de(palabras: list[str], max_chars: int) -> list[list[int]] | None:
    """Reparte las palabras en líneas de hasta max_chars (greedy). None si hacen falta más de 2."""
    lineas: list[list[int]] = [[]]
    largo = 0
    for i, p in enumerate(palabras):
        extra = len(p) + (1 if lineas[-1] else 0)
        if lineas[-1] and largo + extra > max_chars:
            lineas.append([])
            largo = 0
            extra = len(p)
        lineas[-1].append(i)
        largo += extra
    if len(lineas) > 2:
        return None
    # Balancear: si la segunda línea quedó muy corta, pasar palabras de la primera.
    if len(lineas) == 2:
        while len(lineas[0]) > 1:
            l1 = sum(len(palabras[i]) for i in lineas[0][:-1]) + len(lineas[0]) - 2
            l2 = sum(len(palabras[i]) for i in [lineas[0][-1], *lineas[1]]) + len(lineas[1])
            if l2 <= max_chars and l2 <= l1 + 2:
                lineas[1].insert(0, lineas[0].pop())
            else:
                break
    return lineas


def bloques(palabras: list[dict], max_palabras: int, max_chars: int, mayus: bool) -> list[dict]:
    out: list[dict] = []
    actual: list[dict] = []

    def cerrar():
        nonlocal actual
        if actual:
            out.append({"inicio": actual[0]["inicio"], "fin": actual[-1]["fin"], "palabras": actual})
        actual = []

    for i, w in enumerate(palabras):
        prev = palabras[i - 1] if i else None
        texto = [x["texto"] for x in actual] + [w["texto"]]
        if mayus:
            texto = [t.upper() for t in texto]
        corte = bool(actual) and (
            len(actual) >= max_palabras
            or lineas_de(texto, max_chars) is None
            or (prev is not None and prev["fin_frase"])
            or (prev is not None and w["inicio"] - prev["fin"] > PAUSA_CORTE)
        )
        if corte:
            cerrar()
        actual.append(w)
    cerrar()
    for a, b in zip(out, out[1:]):
        hueco = b["inicio"] - a["fin"]
        if 0 < hueco < PUENTE:
            a["fin"] = b["inicio"]
    return out


def armar_ass(bls: list[dict], ancho: int, alto: int, estilo: dict, fuente: str, activo: str, clave: str, max_chars: int) -> str:
    vertical = alto > ancho
    escala = ancho / (1080 if vertical else 1920)
    tam = round((estilo["v"] if vertical else estilo["h"]) * escala)
    if vertical:
        margen_v, margen_l, margen_r = round(alto * 0.30), round(ancho * 0.08), round(ancho * 0.14)
    else:
        margen_v, margen_l, margen_r = round(alto * 0.10), round(ancho * 0.08), round(ancho * 0.08)
    blanco = "&H00FFFFFF"
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {ancho}
PlayResY: {alto}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: NovaCut,{fuente},{tam},{blanco},{activo},&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,{round(estilo['borde'] * escala)},{round(estilo['sombra'] * escala)},2,{margen_l},{margen_r},{margen_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    eventos = []
    for b in bls:
        ws = b["palabras"]
        textos = [w["texto"].upper() if estilo["mayus"] else w["texto"] for w in ws]
        lineas = lineas_de(textos, max_chars) or [list(range(len(ws)))]
        for i, w in enumerate(ws):
            ini = b["inicio"] if i == 0 else w["inicio"]
            fin = ws[i + 1]["inicio"] if i + 1 < len(ws) else b["fin"]
            if fin - ini < 0.01:
                continue
            partes_lineas = []
            for linea in lineas:
                partes = []
                for j in linea:
                    t = textos[j]
                    if j == i:
                        # Palabra activa: color de acento y un "pop" corto (entra al 118 % y baja al 106 %).
                        partes.append(f"{{\\c{activo}\\fscx118\\fscy118\\t(0,110,\\fscx106\\fscy106)}}{t}{{\\c{blanco}\\fscx100\\fscy100}}")
                    elif ws[j]["clave"]:
                        partes.append(f"{{\\c{clave}}}{t}{{\\c{blanco}}}")
                    else:
                        partes.append(t)
                partes_lineas.append(" ".join(partes))
            entrada = "{\\fad(70,0)}" if i == 0 else ""
            cuerpo = "\\N".join(partes_lineas)
            eventos.append(f"Dialogue: 0,{t_ass(ini)},{t_ass(fin)},NovaCut,,0,0,0,,{entrada}{cuerpo}")
    return cab + "\n".join(eventos) + "\n"


def armar_srt(bls: list[dict], max_chars: int) -> str:
    out = []
    for k, b in enumerate(bls, 1):
        textos = [w["texto"] for w in b["palabras"]]
        lineas = lineas_de(textos, max_chars) or [list(range(len(textos)))]
        texto = "\n".join(" ".join(textos[j] for j in l) for l in lineas)
        out.append(f"{k}\n{t_srt(b['inicio'])} --> {t_srt(b['fin'])}\n{texto}\n")
    return "\n".join(out)


def medidas(video: Path) -> tuple[int, int]:
    res = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation", "-of", "json", str(video)], capture_output=True, text=True)
    try:
        s = json.loads(res.stdout)["streams"][0]
    except (ValueError, KeyError, IndexError):
        error(f"No pude leer el video {video.name}.")
    w, h = int(s["width"]), int(s["height"])
    rot = next((int(float(x["rotation"])) for x in s.get("side_data_list", []) or [] if "rotation" in x), 0)
    return (h, w) if abs(rot) % 180 == 90 else (w, h)


def tiene_libass() -> bool:
    res = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return bool(re.search(r"^\s*\S+\s+ass\s", res.stdout, re.M))


def main() -> None:
    ap = argparse.ArgumentParser(description="Genera subtítulos ASS animados palabra por palabra y los quema en el video (además deja el .srt).")
    ap.add_argument("video")
    ap.add_argument("palabras", help="JSON de palabras con tiempos del video (el .palabras.json de render.py)")
    ap.add_argument("--salida", help="MP4 de salida (default: <video>_subtitulado.mp4)")
    ap.add_argument("--estilo", choices=list(ESTILOS), default="limpio", help="limpio (frases de 2 líneas) o impacto (1-3 palabras grandes en mayúsculas)")
    ap.add_argument("--color-activo", default="#FFD84D", help="color de la palabra que se está diciendo (default amarillo #FFD84D)")
    ap.add_argument("--color-clave", default="#3DDC84", help="color de las palabras clave (default verde #3DDC84)")
    ap.add_argument("--claves", default="", help="IDs ORIGINALES de palabras clave separados por coma (además de las del plan)")
    ap.add_argument("--sin-claves-auto", action="store_true", help="no resaltar números automáticamente cuando no hay claves marcadas")
    ap.add_argument("--solo-srt", action="store_true", help="no quemar nada: solo escribir el .srt y el .ass")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="medium")
    args = ap.parse_args()

    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            error(f"No encuentro {prog}. Instalá ffmpeg: ver nc-editar/instalar_dependencias.md")
    video = Path(args.video).expanduser().resolve()
    if not video.is_file():
        error(f"No existe el video: {video}")
    salida = Path(args.salida).expanduser().resolve() if args.salida else video.with_name(f"{video.stem}_subtitulado.mp4")
    if salida == video:
        error("La salida no puede ser el video de entrada: nunca lo sobrescribo.")
    try:
        claves = {int(x) for x in args.claves.split(",") if x.strip()}
    except ValueError:
        error("--claves tiene que ser una lista de números separados por coma (IDs de palabra).")

    palabras = cargar(Path(args.palabras).expanduser(), claves, not args.sin_claves_auto)
    if not palabras:
        error("No hay palabras para subtitular.")
    ancho, alto = medidas(video)
    estilo = ESTILOS[args.estilo]
    escala = ancho / (1080 if alto > ancho else 1920)
    tam = (estilo["v"] if alto > ancho else estilo["h"]) * escala
    util = ancho * (1 - 0.08 - (0.14 if alto > ancho else 0.08))
    max_chars = max(8, int(util / (tam * estilo["em"])))
    bls = bloques(palabras, estilo["palabras"], max_chars, estilo["mayus"])

    fuente_ok = (FUENTES / estilo["archivo"]).is_file()
    fuente = estilo["fuente"] if fuente_ok else RESPALDO
    if not fuente_ok:
        print(f"Aviso: no encuentro {FUENTES / estilo['archivo']}; uso una fuente del sistema ({RESPALDO} o la más parecida).", file=sys.stderr)
    ass = armar_ass(bls, ancho, alto, estilo, fuente, color_ass(args.color_activo), color_ass(args.color_clave), max_chars)
    srt = armar_srt(bls, max_chars)
    srt_path = salida.with_suffix(".srt")
    ass_path = salida.with_suffix(".ass")
    srt_path.write_text(srt, encoding="utf-8")
    ass_path.write_text(ass, encoding="utf-8")
    print(f"{len(bls)} bloques de subtítulos · estilo {args.estilo} · {ancho}x{alto} · hasta {max_chars} letras por línea")
    print(f"SRT: {srt_path}")
    if args.solo_srt:
        print(f"ASS: {ass_path}")
        return
    if not tiene_libass():
        error("Tu ffmpeg no tiene libass (filtro 'ass'), que hace falta para quemar los subtítulos.\n"
              "Mac: brew reinstall ffmpeg · Windows: instalá el build 'full' de Gyan (winget install Gyan.FFmpeg).\n"
              f"Igual te dejé el .srt para subirlo aparte: {srt_path}")

    with tempfile.TemporaryDirectory(prefix="novacut-") as tmp:
        t = Path(tmp)
        # ffmpeg corre dentro de la carpeta temporal y usa rutas relativas en el filtro: así no hay problemas con
        # los ":" y "\" de las rutas de Windows dentro de la sintaxis de filtros.
        (t / "subs.ass").write_text(ass, encoding="utf-8")
        if fuente_ok:
            shutil.copytree(FUENTES, t / "fuentes")
        filtro = "ass=subs.ass" + (":fontsdir=fuentes" if fuente_ok else "")
        parcial = salida.with_name(salida.stem + ".parcial" + salida.suffix)
        cmd = [
            "ffmpeg", "-hide_banner", "-nostdin", "-y", "-v", "verbose", "-i", str(video),
            "-map", "0:v:0", "-map", "0:a?", "-vf", f"{filtro},format=yuv420p",
            "-c:v", "libx264", "-profile:v", "high", "-preset", args.preset, "-crf", str(args.crf), "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
            "-c:a", "copy", "-movflags", "+faststart", str(parcial),
        ]
        print("Quemando los subtítulos...", file=sys.stderr)
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=tmp)
        if res.returncode != 0:
            lineas = [x for x in res.stderr.splitlines() if "error" in x.lower() or "Error" in x]
            error("ffmpeg no pudo quemar los subtítulos.\n" + "\n".join(lineas[-15:] or res.stderr.splitlines()[-15:]))
        os.replace(parcial, salida)
        elegidas = sorted({m.group(1).strip() for m in re.finditer(r"fontselect:.*?->\s*(.+?)(?:,|$)", res.stderr)})
    if elegidas:
        nombres = ", ".join(Path(x).name for x in elegidas)
        print(f"Fuente usada: {nombres}")
        if fuente_ok and not any("Montserrat" in x for x in elegidas):
            print("Aviso: libass no usó Montserrat; los subtítulos salieron con otra fuente.", file=sys.stderr)
    print(f"Listo: {salida}")


if __name__ == "__main__":
    main()
