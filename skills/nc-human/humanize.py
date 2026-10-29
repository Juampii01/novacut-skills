#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
humanize.py - le saca a un borrador la huella de máquina.

Tres pasadas, en este orden:

  1. INVISIBLES   borra o normaliza los caracteres que un teclado humano no
                  produce: espacios de ancho cero, unidores, guiones blandos,
                  BOM, caracteres de etiqueta Unicode, espacios duros y finos.
                  Sobreviven al copiar y pegar y son la marca más mecánica de
                  un texto generado.
  2. TIPOGRAFÍA   raya -> coma, semirraya -> guion, comillas curvas -> rectas,
                  puntos suspensivos de un carácter -> tres puntos, viñeta ->
                  guion. Los ¿ y ¡ NO se tocan: son castellano, no huella.
  3. LÉXICO       reemplaza el lexicón de slop.json por palabras simples,
                  respetando mayúsculas y sin tocar los links. Primero busca
                  la forma exacta (con sus tildes) y después la forma sin
                  tildes, para agarrar también "increible" o "sumergete".

Las señales de estructura ("no es solo X, es Y", tríadas, paredes de hashtags)
se REPORTAN, nunca se reescriben solas: cambiar la forma de una oración
necesita criterio, y eso es trabajo del modelo, no de una regex.

Uso
  python3 humanize.py borrador.txt
  python3 humanize.py borrador.txt --report
  pbpaste | python3 humanize.py - --report
  python3 humanize.py borrador.txt --json
  python3 humanize.py borrador.txt -o limpio.txt
"""

import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")

URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")

ACCENTS = {"a": "aá", "e": "eé", "i": "iíï", "o": "oó", "u": "uúü",
           "á": "aá", "é": "eé", "í": "ií", "ó": "oó", "ú": "uú", "ü": "uü"}
# No pegado a una letra, ni a un # o @ (para no tocar #explorar ni @usuario).
LEFT = r"(?<![\w#@])"
RIGHT = r"(?!\w)"


def load_lexicon(path=LEX):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build_pattern(find, fuzzy=False):
    """Arma la regex de una entrada del lexicón.

    fuzzy=False: tal cual está escrita (sin distinguir mayúsculas).
    fuzzy=True:  además, cualquier vocal matchea con o sin tilde.
    Los espacios aceptan cualquier espacio en blanco.
    """
    out = []
    for ch in find:
        low = ch.lower()
        if ch.isspace():
            out.append(r"\s+")
        elif fuzzy and low in ACCENTS:
            out.append("[" + ACCENTS[low] + "]")
        else:
            out.append(re.escape(ch))
    body = "".join(out)
    left = LEFT if (find[:1].isalnum()) else ""
    right = RIGHT if (find[-1:].isalnum()) else ""
    return re.compile(left + body + right, re.IGNORECASE)


def lexicon_entries(lex):
    return sorted(lex["phrases"] + lex["words"], key=lambda e: len(e["find"]), reverse=True)


def _cp(spec):
    """'U+200B' -> 0x200b;  'U+E0000-U+E007F' -> (inicio, fin)."""
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect_urls(text):
    """Cambia los links por marcadores para que ninguna pasada escriba adentro."""
    found = []

    def stash(m):
        found.append(m.group(0))
        return f"\x00URL{len(found) - 1}\x00"

    return URL_RE.sub(stash, text), found


def restore_urls(text, found):
    for i, url in enumerate(found):
        text = text.replace(f"\x00URL{i}\x00", url)
    return text


def pass_invisible(text, lex):
    """Borra o pasa a espacio común los caracteres invisibles. Devuelve (texto, hallazgos)."""
    hits = []
    for entry in lex["invisible"]:
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({"name": entry["cp"] + " " + entry["name"], "count": n,
                         "action": "borrar" if entry["action"] == "delete" else "espacio"})
            text = re.sub(pattern, "" if entry["action"] == "delete" else " ", text)
    # Cualquier carácter de formato (Cf) que quede es invisible por definición.
    stray = [c for c in text if unicodedata.category(c) == "Cf"]
    if stray:
        hits.append({"name": "otros caracteres de formato invisibles", "count": len(stray),
                     "action": "borrar"})
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return text, hits


def pass_typographic(text, lex):
    hits = []
    for entry in lex["typographic"]:
        ch = entry["from"]
        n = text.count(ch)
        if not n:
            continue
        hits.append({"name": f"{ch} {entry['name']}", "count": n, "to": entry["to"].strip() or "(espacio)"})
        if ch == "—":
            # " palabra — palabra " y "palabra—palabra" quedan en coma + espacio.
            # Una raya al principio de línea (diálogo) pasa a guion.
            text = re.sub(r"(?m)^([ \t]*)—\s*", r"\1- ", text)
            text = re.sub(r"\s*—\s*", ", ", text)
        elif ch == "–":
            text = re.sub(r"\s*–\s*(?=\d)", "-", text)      # 5–10  -> 5-10
            text = re.sub(r"\s+–\s+", ", ", text)            # usada como raya
            text = text.replace("–", "-")
        else:
            text = text.replace(ch, entry["to"])
    # Una coma agregada antes de otra puntuación queda mal.
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*\n", "\n", text)
    return text, hits


def _match_case(src, repl):
    if not repl:
        return repl
    letters = [c for c in src if c.isalpha()]
    if len(letters) > 1 and all(c.isupper() for c in letters):
        return repl.upper()
    first = next((c for c in src if c.isalpha()), "")
    if first.isupper():
        return repl[0].upper() + repl[1:]
    return repl


def _cleanup(text):
    # Al borrar una cláusula entera queda puntuación huérfana ("sistema. ." o
    # una línea que ahora arranca con coma), y eso se lee peor que el slop.
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"¡\s*!|¿\s*\?", "", text)                  # ¡! o ¿? vacíos
    text = re.sub(r"([¡¿])\s*[,;:]\s*", r"\1", text)          # "¡, hola" -> "¡hola"
    text = re.sub(r"([¡¿])\s+", r"\1", text)
    text = re.sub(r"(?m)^[ \t]*(?:[,.;:]+[ \t]*)+", "", text)
    text = re.sub(r"(?m)^[ \t](?=\S)", "", text)       # un espacio que dejó un borrado.
                                                      # Las sangrías más hondas son a propósito.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)      # una raya pasó a coma y
                                                      # después se borró lo que seguía
    text = re.sub(r"([.!?])\s*,\s*", r"\1 ", text)     # ". , y entonces" -> ". y entonces"
    text = re.sub(r":\s*([.!?])", r"\1", text)
    text = text.replace("...", "\x00ELL\x00")          # protege los puntos suspensivos reales
    text = re.sub(r"\.\s*\.+", ".", text)
    text = re.sub(r"([!?])\s*\.", r"\1", text)
    text = text.replace("\x00ELL\x00", "...")
    # Una conjunción que quedó sola cuando se borró lo que unía: "Y." o "y?".
    text = re.sub(r"(^|[.!?]\s+)(?:y|e|o|u|pero|aunque)\s*([.!?])", r"\1", text,
                  flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"\s+(?:y|e|o|pero)\s*([.!?])", r"\1", text)
    text = re.sub(r"(?m)^[ \t](?=\S)", "", text)
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Una raya que pasó a coma seguida de un conector deja dos oraciones
    # pegadas ("es importante, además, es prueba"). Se pasa a punto.
    text = re.sub(r",\s*(además|así que|igual|también|al final|o sea|entonces)\s*,\s*",
                  lambda m: ". " + m.group(1)[0].upper() + m.group(1)[1:] + ", ", text)
    return text


def pass_lexical(text, lex):
    """Reemplaza palabras y frases del lexicón. Las más largas primero, así ganan las frases.

    Dos vueltas: primero la forma exacta (así "optimizá" va a "mejorá" y
    "optimiza" a "mejora"), después la forma sin tildes para los que escriben
    sin tildes.
    """
    hits = {}
    entries = lexicon_entries(lex)
    for fuzzy in (False, True):
        for entry in entries:
            pattern = build_pattern(entry["find"], fuzzy=fuzzy)
            found = pattern.findall(text)
            if not found:
                continue
            h = hits.setdefault(entry["find"], {"find": entry["find"],
                                                "replace": entry["replace"] or "(borrado)",
                                                "count": 0, "family": entry["family"]})
            h["count"] += len(found)
            text = pattern.sub(lambda m: _match_case(m.group(0), entry["replace"]), text)
    return _cleanup(text), list(hits.values())


def scan_structures(text, lex):
    flags = []
    for s in lex["structures"]:
        try:
            pattern = re.compile(s["regex"], re.MULTILINE)
        except re.error:
            continue
        found = pattern.findall(text)
        if found:
            flags.append({"name": s["name"], "count": len(found), "fix": s["fix"]})
    # La uniformidad en el largo de las oraciones también es estructura.
    lens = [len(s.split()) for s in SENT_RE.findall(text) if len(s.split()) > 2]
    if len(lens) >= 4:
        mean = sum(lens) / len(lens)
        var = sum((n - mean) ** 2 for n in lens) / len(lens)
        cv = (var ** 0.5) / mean if mean else 0
        if cv < 0.35:
            flags.append({
                "name": f"Oraciones todas del mismo largo (variación {cv:.2f})",
                "count": len(lens),
                "fix": "Partí una oración a la mitad. Dejá que otra se estire. Las máquinas escriben parejo.",
            })
    return flags


LETTER = "A-Za-zÁÉÍÓÚÑÜáéíóúñü"


def restore_capitals(original, text):
    """Borrar una apertura deja la palabra siguiente en minúscula.

    Solo se corrige para quien escribe con mayúscula al principio de las
    oraciones: escribir todo en minúscula a propósito es un estilo, no una
    huella, y pisarlo sería justo lo que este script existe para evitar.
    """
    starts = re.findall(r"(?:^|[.!?]\s+|\n)\s*[¿¡\"]*([" + LETTER + r"])", original)
    if not starts or sum(1 for c in starts if c.isupper()) * 2 < len(starts):
        return text

    text = re.sub(r"(^|(?<=[.!?] )|(?<=[.!?]\n)|(?<=\n))(\s*[¿¡\"]*)([a-záéíóúñü])",
                  lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)
    return text


def humanize(text, lex):
    raw_for_case = text
    text, urls = protect_urls(text)
    text, inv = pass_invisible(text, lex)
    text, typo = pass_typographic(text, lex)
    text, lexi = pass_lexical(text, lex)
    text = restore_capitals(raw_for_case, text)
    text = restore_urls(text, urls)
    return text.strip() + "\n", {
        "invisible": inv,
        "typographic": typo,
        "lexical": lexi,
        "structures": scan_structures(text, lex),
    }


def render_report(report, out=sys.stderr):
    def head(title):
        print(f"\n{title}\n" + "-" * len(title), file=out)

    total = sum(h["count"] for h in report["invisible"]) \
        + sum(h["count"] for h in report["typographic"]) \
        + sum(h["count"] for h in report["lexical"])

    head("REPORTE DE HUMANIZACIÓN")
    print(f"{total} marcas de máquina sacadas, "
          f"{len(report['structures'])} señales de estructura para reescribir a mano", file=out)

    if report["invisible"]:
        head("1. CARACTERES INVISIBLES")
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['action']}", file=out)
    if report["typographic"]:
        head("2. TIPOGRAFÍA")
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['to']}", file=out)
    if report["lexical"]:
        head("3. LEXICÓN DE SLOP")
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  {h['find']}  -> {h['replace']}   [{h['family']}]", file=out)
    if report["structures"]:
        head("4. SEÑALES DE ESTRUCTURA  (no se arreglan solas: reescribilas vos)")
        for h in report["structures"]:
            print(f"  {h['count']:>3}x  {h['name']}\n        {h['fix']}", file=out)
    if not any(report.values()):
        head("LIMPIO")
        print("  No hay nada que sacar.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Le saca a un borrador la huella de máquina.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("-o", "--out", help="escribir el texto limpio acá en vez de stdout")
    ap.add_argument("--report", action="store_true", help="mostrar qué cambió (por stderr)")
    ap.add_argument("--json", action="store_true", help="devolver {text, report} en JSON")
    ap.add_argument("--lexicon", default=LEX, help="ruta a slop.json")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    lex = load_lexicon(args.lexicon)
    clean, report = humanize(raw, lex)

    if args.json:
        print(json.dumps({"text": clean, "report": report}, indent=2, ensure_ascii=False))
        return
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(clean)
        print(f"escrito: {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(clean)
    if args.report:
        render_report(report)


if __name__ == "__main__":
    main()
