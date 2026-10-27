#!/usr/bin/env python3
# NovaCut Skills · nc-editar · verificar.py
"""Revisa que estén las dependencias del editor de video y dice cómo instalar lo que falte.

Uso: python3 verificar.py      (en Windows: py verificar.py)
Sale con código 0 si está todo para editar, 1 si falta algo indispensable.
Solo biblioteca estándar de Python.
"""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
import sys

SISTEMA = platform.system()  # "Darwin" (Mac), "Windows", "Linux"
if SISTEMA == "Windows":
    PIP = "py -m pip"
elif SISTEMA == "Darwin":
    # El Python de Homebrew no deja instalar paquetes sueltos: NovaCut usa su propio entorno.
    PIP = "python3.12 -m venv ~/.claude/novacut/venv && ~/.claude/novacut/venv/bin/python -m pip"
else:
    PIP = "python3 -m pip"


def ok(msg: str) -> None:
    print(f"  [OK]    {msg}")


def falta(msg: str, como: str) -> None:
    print(f"  [FALTA] {msg}\n          Cómo: {como}")


def aviso(msg: str) -> None:
    print(f"  [AVISO] {msg}")


def instalar_ffmpeg() -> str:
    if SISTEMA == "Darwin":
        return "brew install ffmpeg   (si no tenés Homebrew: https://brew.sh)"
    if SISTEMA == "Windows":
        return "winget install --id Gyan.FFmpeg -e   y después cerrá y abrí de nuevo la terminal"
    return "sudo apt install ffmpeg   (o el gestor de paquetes de tu sistema)"


def main() -> int:
    print(f"Sistema: {SISTEMA} {platform.machine()} · Python {platform.python_version()}")
    indispensable = True

    if sys.version_info < (3, 10):
        falta(f"Python 3.10 o más nuevo (tenés {platform.python_version()})", "Mac: brew install python · Windows: winget install Python.Python.3.12")
        indispensable = False
    else:
        ok(f"Python {platform.python_version()}")

    ff = shutil.which("ffmpeg")
    fp = shutil.which("ffprobe")
    if not ff or not fp:
        falta("ffmpeg / ffprobe", instalar_ffmpeg())
        indispensable = False
    else:
        res = subprocess.run(["ffmpeg", "-hide_banner", "-version"], capture_output=True, text=True)
        version = (res.stdout.splitlines() or ["?"])[0]
        m = re.search(r"version\s+n?(\d+)\.(\d+)", version)
        ok(version[:80])
        if m and (int(m.group(1)), int(m.group(2))) < (5, 1):
            aviso("tu ffmpeg es anterior a 5.1: funciona, pero conviene actualizarlo.")
        filtros = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        tiene = lambda n: bool(re.search(rf"^\s*\S+\s+{n}\s", filtros, re.M))  # noqa: E731
        for nombre, para, necesario in (
            ("ass", "quemar subtítulos (libass)", True),
            ("loudnorm", "normalizar el volumen", True),
            ("afftdn", "reducción de ruido", True),
            ("sidechaincompress", "bajar la música cuando hablás", False),
            ("zscale", "convertir video HDR del iPhone (si no está, los HDR pueden salir lavados)", False),
        ):
            if tiene(nombre):
                ok(f"filtro {nombre} ({para})")
            elif necesario:
                falta(f"filtro {nombre} ({para})", "instalá un ffmpeg completo: " + instalar_ffmpeg())
                indispensable = False
            else:
                aviso(f"falta el filtro {nombre} ({para})")
        if "libx264" not in subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout:
            falta("codificador libx264 (H.264)", "instalá un ffmpeg completo: " + instalar_ffmpeg())
            indispensable = False

    try:
        import faster_whisper  # noqa: F401, PLC0415

        ok(f"faster-whisper {getattr(faster_whisper, '__version__', '')}".strip())
    except ImportError:
        falta("faster-whisper (transcripción local)", f"{PIP} install faster-whisper")
        indispensable = False
    try:
        import numpy  # noqa: F401, PLC0415

        ok("numpy")
    except ImportError:
        aviso(f"falta numpy (viene con faster-whisper): {PIP} install numpy")

    print()
    if indispensable:
        print("Todo listo para editar.")
        print("La primera transcripción descarga el modelo de voz (una sola vez, ~480 MB el 'small').")
        return 0
    print("Falta algo indispensable. Instalalo con los comandos de arriba y volvé a correr este chequeo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
