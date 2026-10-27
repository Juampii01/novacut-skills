#!/usr/bin/env python3
# NovaCut Skills · nc-audio · audio.py
"""Deja la voz de un video lista para redes: limpieza, volumen parejo a -14 LUFS y música de fondo opcional.

Cadena de voz (filtros de ffmpeg, sin IA ni servicios):
  pasa altos 80 Hz (rumor, golpes en la mesa) -> reducción de ruido (afftdn) -> +2 dB de presencia en 4 kHz
  -> de-esser -> compresor suave 3:1
Volumen: loudnorm en DOS pasadas (primero mide, después aplica en modo lineal = solo ganancia, sin "bombeo")
  a -14 LUFS integrados con techo de -1 dBTP. Antes se lleva la voz cerca del objetivo y un limitador deja lugar
  para que la segunda pasada pueda ser lineal.
Música (opcional): se mide, se lleva a ~22 dB por debajo de la voz, se repite si es corta, con fundidos de
  entrada y salida, y baja sola cuando hablás (ducking con sidechaincompress).
El retraso que agrega la reducción de ruido (~25 ms) se mide y se compensa: la voz no se corre del video.
El video no se recodifica (se copia tal cual). Nunca sobrescribe el original.

Uso:
  python3 audio.py cortado.mp4                                 # -> cortado_audio.mp4
  python3 audio.py cortado.mp4 --musica pista.mp3 --musica-db -22
  python3 audio.py cortado.mp4 --limpieza suave --salida final.mp4
  python3 audio.py video.mp4 --medir                            # solo mide LUFS y pico
Dependencias: ffmpeg. numpy (opcional, viene con faster-whisper) para medir el retraso exacto de los filtros.
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

SR = 48000
CADENAS = {
    "normal": [
        "highpass=f=80",
        "afftdn=nr=10:nf=-30:tn=1",
        "equalizer=f=4000:t=o:w=1:g=2",
        "deesser=i=0.4:m=0.5:f=0.5",
        "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=1",
    ],
    "suave": [
        "highpass=f=70",
        "afftdn=nr=6:nf=-35:tn=1",
        "acompressor=threshold=-22dB:ratio=2:attack=10:release=150:makeup=1",
    ],
    "fuerte": [
        "highpass=f=90",
        "afftdn=nr=18:nf=-28:tn=1",
        "equalizer=f=250:t=q:w=1:g=-3",
        "equalizer=f=3500:t=q:w=0.9:g=3",
        "deesser=i=0.5:m=0.5:f=0.5",
        "acompressor=threshold=-22dB:ratio=4:attack=6:release=100:makeup=1",
    ],
    "ninguna": [],
}
# Retraso conocido de afftdn (muestras a 48 kHz) si no se puede medir (sin numpy).
RETRASO_AFFTDN = 1200
# Ducking calibrado para una voz a -14 LUFS (≈ -17 dBFS RMS al hablar): la música baja unos 10-12 dB mientras
# hablás y vuelve en las pausas largas (ataque 20 ms, salida 450 ms: no "bombea" entre palabras).
# Ojo: el umbral de sidechaincompress no equivale al nivel RMS de la voz; estos valores se midieron, no se calcularon.
DUCKING = "sidechaincompress=threshold=0.005:ratio=8:attack=20:release=450:knee=4"
# La música en las pausas queda este tanto más arriba que mientras hablás.
DUCK_DB = 10.0


def error(msg: str, codigo: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def ffmpeg(args: list[str], que: str) -> str:
    res = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        error(f"ffmpeg falló en: {que}.\n{res.stderr[-1500:]}")
    return res.stderr


def json_loudnorm(stderr: str) -> dict:
    m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr, re.S)
    if not m:
        error("No pude medir el volumen (loudnorm no devolvió datos).")
    return json.loads(m[-1])


def medir(src: Path, cadena: list[str], objetivo: float, pico: float) -> dict:
    err = ffmpeg(["-i", str(src), "-map", "0:a:0", "-af", ",".join([*cadena, f"loudnorm=I={objetivo}:TP={pico}:LRA=18:print_format=json"]), "-f", "null", "-"], "medición de volumen")
    return json_loudnorm(err)


def ebur128(path: Path) -> tuple[float, float]:
    """Sonoridad integrada (LUFS) y pico verdadero (dBTP) medidos con el filtro ebur128."""
    err = ffmpeg(["-i", str(path), "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"], "medición final")
    resumen = err[err.rfind("Summary:") :] if "Summary:" in err else err
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", resumen)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", resumen)
    return (float(i.group(1)) if i else float("nan"), float(p.group(1)) if p and p.group(1) != "-inf" else float("-inf"))


def duracion(path: Path) -> float:
    res = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def tiene_video(path: Path) -> bool:
    res = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return "video" in res.stdout


def retraso(cadena: list[str], tmp: Path) -> int:
    """Muestras de retraso que agrega la cadena: ráfagas de ruido, correlación entre entrada y salida (hasta 100 ms)."""
    if not cadena:
        return 0
    try:
        import numpy as np  # noqa: PLC0415
    except ImportError:
        return RETRASO_AFFTDN if any(f.startswith("afftdn") for f in cadena) else 0
    rng = np.random.default_rng(1)
    n = int(2.5 * SR)
    x = np.zeros(n, dtype=np.float32)
    for k in range(5):
        a = int((0.2 + k * 0.45) * SR)
        x[a : a + int(0.25 * SR)] = rng.standard_normal(int(0.25 * SR)).astype(np.float32) * 0.1
    entrada, salida = tmp / "sonda.f32", tmp / "sonda_out.f32"
    entrada.write_bytes(x.astype("<f4").tobytes())
    ffmpeg(["-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(entrada), "-af", ",".join(cadena), "-f", "f32le", "-ar", str(SR), "-ac", "1", str(salida)], "medición de retraso")
    y = np.frombuffer(salida.read_bytes(), dtype="<f4")
    m = min(len(y), n)
    corr = np.fft.irfft(np.fft.rfft(y[:m], 2 * m) * np.conj(np.fft.rfft(x[:m], 2 * m)))
    lag = int(np.argmax(np.abs(corr[: int(0.1 * SR) + 1])))
    return lag if lag > 1 else 0


def compensada(cadena: list[str], lag: int) -> list[str]:
    if not lag:
        return cadena
    return [*cadena, f"atrim=start_sample={lag}", "asetpts=PTS-STARTPTS", f"apad=pad_len={lag}"]


def procesar_voz(src: Path, wav_out: Path, cadena: list[str], objetivo: float, pico: float) -> dict:
    """Limpieza + loudnorm en dos pasadas (la segunda en modo lineal). Devuelve los datos de cada pasada."""
    previa = medir(src, cadena, objetivo, pico)
    medido = float(previa["input_i"])
    if medido < -60:
        error("El audio está prácticamente en silencio. Revisá que el micrófono haya grabado.", 4)
    # Ganancia para quedar cerca del objetivo y un limitador a -2,5 dBFS: así la pasada lineal tiene lugar
    # para no pasar el techo y no cae en el modo dinámico (que "bombea").
    ganancia = max(-20.0, min(30.0, objetivo - medido))
    # Primera pasada: medir. Si con ese limitador la ganancia final pasaría el techo (loudnorm caería en modo
    # dinámico), se prueba con un limitador más bajo (voces con muchos picos: risas, golpes, consonantes fuertes).
    for limite in (0.75, 0.6, 0.5, 0.4):
        base = [*cadena, f"volume={ganancia:.2f}dB", f"alimiter=limit={limite}:attack=5:release=60:level=disabled:latency=1"]
        pasada1 = medir(src, base, objetivo, pico)
        if float(pasada1["input_tp"]) + (objetivo - float(pasada1["input_i"])) <= pico - 0.1:
            break
    ln = (
        f"loudnorm=I={objetivo}:TP={pico}:LRA=18:measured_I={pasada1['input_i']}:measured_TP={pasada1['input_tp']}"
        f":measured_LRA={pasada1['input_lra']}:measured_thresh={pasada1['input_thresh']}:offset={pasada1['target_offset']}:linear=true:print_format=json"
    )
    err = ffmpeg(["-i", str(src), "-map", "0:a:0", "-af", ",".join([*base, ln, f"aresample={SR}"]), "-ac", "2", "-c:a", "pcm_s16le", str(wav_out)], "normalización (segunda pasada)")
    pasada2 = json_loudnorm(err)
    return {"medido_original": medido, "ganancia_previa": round(ganancia, 2), "pasada1": pasada1, "pasada2": pasada2}


def mezclar_musica(voz: Path, musica: Path, wav_out: Path, dur: float, objetivo: float, musica_db: float, fade_in: float, fade_out: float) -> dict:
    m = medir(musica, [], -23.0, -1.0)
    mi = float(m["input_i"])
    if mi < -60:
        error("La música está en silencio. Elegí otra pista.", 4)
    # musica_db es el nivel mientras hablás; en las pausas la música sube DUCK_DB.
    gan = max(-40.0, min(20.0, objetivo + musica_db + DUCK_DB - mi))
    fade_in, fade_out = min(fade_in, dur / 3), min(fade_out, dur / 3)
    grafo = (
        f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo,asplit=2[voz][llave];"
        f"[1:a]aformat=sample_rates={SR}:channel_layouts=stereo,atrim=0:{dur:.6f},asetpts=PTS-STARTPTS,volume={gan:.2f}dB,"
        f"afade=t=in:d={fade_in:.2f},afade=t=out:st={max(0.0, dur - fade_out):.3f}:d={fade_out:.2f}[mus];"
        f"[mus][llave]{DUCKING}[bajada];"
        f"[voz][bajada]amix=inputs=2:duration=first:normalize=0:dropout_transition=0,"
        # Limitador a -1 dBFS: la voz sola no lo toca; solo actúa si la música suma por encima.
        "alimiter=limit=0.891:attack=5:release=60:level=disabled:latency=1[a]"
    )
    ffmpeg(["-i", str(voz), "-stream_loop", "-1", "-i", str(musica), "-filter_complex", grafo, "-map", "[a]", "-t", f"{dur:.6f}", "-c:a", "pcm_s16le", str(wav_out)], "mezcla con la música")
    return {"musica_lufs": mi, "ganancia_musica": round(gan, 2), "musica_db": musica_db}


def main() -> None:
    ap = argparse.ArgumentParser(description="Limpieza de voz, loudnorm en dos pasadas a -14 LUFS / -1 dBTP y música opcional con ducking.")
    ap.add_argument("entrada", help="video (o audio) de entrada")
    ap.add_argument("--salida", help="archivo de salida (default: <entrada>_audio.<ext>)")
    ap.add_argument("--limpieza", choices=list(CADENAS), default="normal", help="intensidad de la limpieza de voz (default: normal)")
    ap.add_argument("--objetivo", type=float, default=-14.0, help="sonoridad integrada en LUFS (default -14, lo que usan Instagram/YouTube/TikTok)")
    ap.add_argument("--pico", type=float, default=-1.0, help="techo de pico verdadero en dBTP (default -1)")
    ap.add_argument("--musica", help="pista de música de fondo (mp3, m4a, wav). Usá solo música con derechos para redes.")
    ap.add_argument("--musica-db", type=float, default=-22.0, help="volumen de la música mientras hablás, respecto de la voz, en dB (default -22; en las pausas sube ~10 dB)")
    ap.add_argument("--fundido", type=float, nargs=2, default=(0.8, 1.5), metavar=("ENTRADA", "SALIDA"), help="fundidos de la música en segundos")
    ap.add_argument("--medir", action="store_true", help="solo medir LUFS y pico, sin procesar")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        error("No encuentro ffmpeg. Instalalo: ver nc-editar/instalar_dependencias.md")
    src = Path(args.entrada).expanduser().resolve()
    if not src.is_file():
        error(f"No existe el archivo: {src}")
    if args.medir:
        i, p = ebur128(src)
        print(f"{src.name}: {i:.1f} LUFS integrados · pico verdadero {p:.1f} dBTP")
        return
    musica = Path(args.musica).expanduser().resolve() if args.musica else None
    if musica and not musica.is_file():
        error(f"No existe la música: {musica}")
    video = tiene_video(src)
    salida = Path(args.salida).expanduser().resolve() if args.salida else src.with_name(f"{src.stem}_audio{src.suffix if video else '.m4a'}")
    if salida == src:
        error("La salida no puede ser el archivo de entrada: nunca lo sobrescribo. Elegí otro nombre con --salida.")
    dur = duracion(src)

    with tempfile.TemporaryDirectory(prefix="novacut-") as tmp:
        t = Path(tmp)
        cadena = CADENAS[args.limpieza]
        lag = retraso(cadena, t)
        # Voz en mono para limpiarla y en estéreo (canales iguales) para medir: así loudnorm mide lo mismo que
        # se entrega y que mide cualquier medidor (ebur128, las apps).
        cadena = ["aformat=channel_layouts=mono", *compensada(cadena, lag), "pan=stereo|c0=c0|c1=c0"]
        voz = t / "voz.wav"
        print(f"Limpiando la voz ({args.limpieza}) y normalizando a {args.objetivo:.0f} LUFS en dos pasadas...", file=sys.stderr)
        info = procesar_voz(src, voz, cadena, args.objetivo, args.pico)
        mezcla = voz
        info_m = None
        if musica:
            print("Mezclando la música con ducking...", file=sys.stderr)
            mezcla = t / "mezcla.wav"
            info_m = mezclar_musica(voz, musica, mezcla, dur, args.objetivo, args.musica_db, *args.fundido)
        parcial = salida.with_name(salida.stem + ".parcial" + salida.suffix)
        if video:
            ffmpeg(["-i", str(src), "-i", str(mezcla), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-t", f"{dur:.6f}", "-movflags", "+faststart", str(parcial)], "armado del archivo final")
        else:
            ffmpeg(["-i", str(mezcla), "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", str(parcial)], "armado del archivo final")
        os.replace(parcial, salida)

    lufs, pk = ebur128(salida)
    p2 = info["pasada2"]
    print(f"Listo: {salida}")
    print(f"  Antes: {info['medido_original']:.1f} LUFS · después: {lufs:.1f} LUFS (objetivo {args.objetivo:.0f}) · pico {pk:.1f} dBTP (techo {args.pico:.0f})")
    print(f"  Segunda pasada de loudnorm: modo {p2.get('normalization_type', '?')} · retraso de filtros compensado: {lag / SR * 1000:.0f} ms")
    if info_m:
        print(f"  Música: {info_m['musica_lufs']:.1f} LUFS originales, ~{-args.musica_db:.0f} dB bajo la voz mientras hablás (~{-args.musica_db - DUCK_DB:.0f} dB en las pausas, ducking).")
    if abs(lufs - args.objetivo) > 1.0 or pk > args.pico + 0.5:
        print("  Aviso: el resultado quedó lejos del objetivo; revisá el audio de entrada.", file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    main()
