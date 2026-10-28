#!/usr/bin/env python3
"""Arma la entrega del pack NovaCut Skills en dist/.

Genera:
  dist/NovaCut-Skills.zip          el pack completo (para Claude Code)
  dist/claude-ai/<skill>.zip       un zip por skill (para subir en claude.ai)

Uso:
  python3 scripts/armar_entrega.py
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIST = RAIZ / "dist"
SKILLS = RAIZ / "skills"

# Lo que viaja en el pack completo. "interno/" y "scripts/" quedan afuera.
INCLUIR = ["skills", "templates", "licencias",
           "README.md", "INSTALAR.md", "CREDITOS.md", "LICENCIA.md"]
IGNORAR = {"__pycache__", ".DS_Store"}

# Patrones que nunca deberían viajar en un producto.
SOSPECHOSOS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)smart\s*scale|sahakyan"),
]


def archivos(base: Path):
    for p in sorted(base.rglob("*")):
        if p.is_file() and not (set(p.parts) & IGNORAR) and p.suffix != ".pyc":
            yield p


def revisar_secretos() -> list:
    problemas = []
    for nombre in INCLUIR:
        ruta = RAIZ / nombre
        if not ruta.exists():
            continue
        lista = [ruta] if ruta.is_file() else list(archivos(ruta))
        for f in lista:
            try:
                texto = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for patron in SOSPECHOSOS:
                if patron.search(texto):
                    problemas.append(f"{f.relative_to(RAIZ)}: coincide con {patron.pattern}")
    return problemas


def revisar_skills() -> list:
    problemas = []
    for carpeta in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        md = carpeta / "SKILL.md"
        if not md.exists():
            problemas.append(f"{carpeta.name}: falta SKILL.md")
            continue
        m = re.search(r"^name:\s*(\S+)", md.read_text(encoding="utf-8"), re.M)
        if not m or m.group(1) != carpeta.name:
            problemas.append(f"{carpeta.name}: el 'name' del frontmatter no coincide con la carpeta")
    return problemas


def main() -> int:
    problemas = revisar_skills() + revisar_secretos()
    if problemas:
        print("NO SE ARMÓ LA ENTREGA. Revisá esto primero:")
        for p in problemas:
            print("  -", p)
        return 1

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "claude-ai").mkdir(parents=True)

    pack = DIST / "NovaCut-Skills.zip"
    with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre in INCLUIR:
            ruta = RAIZ / nombre
            if ruta.is_file():
                z.write(ruta, f"NovaCut-Skills/{nombre}")
            elif ruta.is_dir():
                for f in archivos(ruta):
                    z.write(f, f"NovaCut-Skills/{f.relative_to(RAIZ)}")

    total = 0
    for carpeta in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        destino = DIST / "claude-ai" / f"{carpeta.name}.zip"
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
            for f in archivos(carpeta):
                z.write(f, f"{carpeta.name}/{f.relative_to(carpeta)}")
            # La licencia viaja también en cada zip suelto.
            for lic in archivos(RAIZ / "licencias"):
                z.write(lic, f"{carpeta.name}/licencias/{lic.name}")
        total += 1

    print(f"Listo: {pack.relative_to(RAIZ)} y {total} zips en dist/claude-ai/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
