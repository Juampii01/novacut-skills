#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
humanize.py - le saca la huella de máquina a un borrador en español.

Tres pasadas, en este orden:

  1. INVISIBLES   borra o normaliza los caracteres que un teclado humano no
                  produce: espacios de ancho cero, unidores, guiones blandos,
                  BOM, caracteres de etiqueta Unicode, espacios duros y
                  angostos. Sobreviven al copiar y pegar y son la marca más
                  mecánica de un texto generado.
  2. TIPOGRAFÍA   raya larga -> coma, raya media -> guion, comillas curvas ->
                  rectas, puntos suspensivos de un carácter -> tres puntos,
                  viñeta -> guion.
  3. LÉXICO       reemplaza el lexicón de slop de slop.json ("en el mundo
                  actual", "potenciar", "sin lugar a dudas", "cabe destacar
                  que"...) por palabras normales, respetando mayúsculas y sin
                  tocar los links.

Las señales de estructura ("no es solo X, es Y", tríadas, "¿El resultado?",
muros de hashtags) se SEÑALAN, nunca se reescriben solas: cambiar la forma de
una frase necesita criterio, y eso es trabajo del modelo, no de una regex.

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

# Dos caracteres invisibles hacen un trabajo legítimo dentro de los emojis. El
# unidor de ancho cero entre dos pictogramas es lo que hace que 👨‍💻 sea un solo
# dibujo y no 👨💻, y las banderas de Inglaterra, Escocia y Gales se escriben con
# caracteres de etiqueta. Esos se conservan. Un unidor o una etiqueta en
# cualquier otro lugar se borra igual.
_PICTO = "\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿"
EMOJI_ZWJ_RE = re.compile(f"(?<=[{_PICTO}️\U0001F3FB-\U0001F3FF])‍(?=[{_PICTO}])")
FLAG_TAG_RE = re.compile(
    "\U0001F3F4\U000E0067\U000E0062"
    "(?:\U000E0065\U000E006E\U000E0067|\U000E0073\U000E0063\U000E0074|\U000E0077\U000E006C\U000E0073)"
    "\U000E007F")


def load_lexicon(path=LEX):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def term_pattern(find):
    """Una entrada del lexicón como regex. Bordes de palabra que funcionan
    también con tildes, ñ, ¿ y ¡ (\\b solo no alcanza: falla antes de un ¿)."""
    body = re.escape(find).replace(r"\ ", r"\s+")
    left = r"(?<!\w)" if find[:1].isalnum() else ""
    right = r"(?!\w)" if find[-1:].isalnum() else ""
    return re.compile(left + body + right, re.IGNORECASE)


def _cp(spec):
    """'U+200B' -> 0x200b;  'U+E0000-U+E007F' -> (inicio, fin)."""
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect_urls(text):
    """Cambia los links por marcadores para que ninguna pasada los toque."""
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
    """Borra o normaliza a espacio los caracteres invisibles. Devuelve (texto, hallazgos)."""
    hits = []
    flags = []

    def stash_flag(m):
        flags.append(m.group(0))
        return f"\x02{len(flags) - 1}\x03"

    text = FLAG_TAG_RE.sub(stash_flag, text)
    text = EMOJI_ZWJ_RE.sub("\x01", text)
    for entry in lex["invisible"]:
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({"name": entry["cp"] + " " + entry["name"], "count": n,
                         "action": entry["action"]})
            text = re.sub(pattern, "" if entry["action"] == "borrar" else " ", text)
    # Cualquier otro carácter de formato (categoría Cf) es invisible por definición.
    stray = [c for c in text if unicodedata.category(c) == "Cf"]
    if stray:
        hits.append({"name": "otros caracteres de formato invisibles", "count": len(stray),
                     "action": "borrar"})
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    text = text.replace("\x01", "‍")
    for i, flag in enumerate(flags):
        text = text.replace(f"\x02{i}\x03", flag)
    return text, hits


def pass_typographic(text, lex):
    hits = []
    for entry in lex["typographic"]:
        ch = entry["from"]
        n = text.count(ch)
        if not n:
            continue
        hits.append({"name": f"{ch} {entry['name']}", "count": n,
                     "to": entry["to"].strip() or "(espacio)"})
        if ch == "—":
            # " palabra — palabra " y "palabra—palabra" quedan en coma + espacio.
            text = re.sub(r"\s*—\s*", ", ", text)
        elif ch == "–":
            text = re.sub(r"\s*–\s*(?=\d)", "-", text)      # 5–10  -> 5-10
            text = re.sub(r"\s+–\s+", ", ", text)            # usada como raya
            text = text.replace("–", "-")
        else:
            text = text.replace(ch, entry["to"])
    # Una coma insertada antes de otra puntuación queda mal.
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*\n", "\n", text)
    text = re.sub(r"(?m)^[ \t]*,[ \t]*", "", text)
    return text, hits


def _match_case(src, repl):
    if not repl:
        return repl
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def pass_lexical(text, lex):
    """Reemplaza palabras y frases de slop. Las más largas primero, así ganan las frases."""
    hits = []
    entries = sorted(lex["phrases"] + lex["words"],
                     key=lambda e: len(e["find"]), reverse=True)
    for entry in entries:
        find = entry["find"]
        pattern = term_pattern(find)
        found = pattern.findall(text)
        if not found:
            continue
        hits.append({"find": find, "replace": entry["replace"] or "(borrado)",
                     "count": len(found), "family": entry["family"]})
        text = pattern.sub(lambda m: _match_case(m.group(0), entry["replace"]), text)
    # Limpieza después de borrar. Borrar una frase entera deja puntuación
    # huérfana ("sistema. ." o una línea que ahora arranca con coma), y eso se
    # lee peor que el slop.
    text = re.sub(r"¡\s*!|¿\s*\?", "", text)                # "¡No te lo pierdas!" borrado
    text = re.sub(r"[¡¿]\s*(?=[.,;:]|$)", "", text, flags=re.MULTILINE)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^[ \t]*(?:[,.;:]+[ \t]*)+", "", text)
    text = re.sub(r"(?m)^[ \t](?=\S)", "", text)            # un espacio que dejó un borrado.
                                                             # Las sangrías más hondas son a propósito.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = text.replace("...", "\x00ELL\x00")                # protege los puntos suspensivos reales
    text = re.sub(r"\.\s*\.+", ".", text)
    text = re.sub(r"([!?])\s*\.", r"\1", text)
    text = text.replace("\x00ELL\x00", "...")
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Borrar dos ganchos de interacción unidos por "y" deja la "y" sola
    # ("seguime para más y dale RT si estás de acuerdo!" -> "y!"). Una línea que
    # quedó con un conector y puntuación se va; los hashtags que siguen quedan.
    text = re.sub(r"(?im)^[ \t]*(?:y|o|pero|así que|entonces|además)[ \t]*[.!?,]*[ \t]*(?=#|$)", "", text)
    # Una raya que pasó a coma seguida de un conector deja una frase pegada
    # ("es clave, además, demuestra..."). Se convierte en punto.
    text = re.sub(r",\s*(además|así que|igual|al final|en el fondo)\s*,\s*",
                  lambda m: ". " + m.group(1)[0].upper() + m.group(1)[1:] + ", ", text)
    return text, hits


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
    # El largo parejo de las frases también es estructura.
    lens = [len(s.split()) for s in SENT_RE.findall(text) if len(s.split()) > 2]
    if len(lens) >= 4:
        mean = sum(lens) / len(lens)
        var = sum((n - mean) ** 2 for n in lens) / len(lens)
        cv = (var ** 0.5) / mean if mean else 0
        if cv < 0.35:
            flags.append({
                "name": f"Frases todas del mismo largo (variación {cv:.2f})",
                "count": len(lens),
                "fix": "Cortá una frase en dos. Dejá que otra se estire. Las máquinas escriben parejo.",
            })
    return flags


LETTER = r"[^\W\d_]"


def restore_capitals(original, text):
    """Borrar una apertura deja la palabra siguiente en minúscula.

    Solo se corrige para quien escribe con mayúscula al inicio de la frase: una
    voz en minúsculas a propósito es un estilo, no un error, y gritarle encima
    sería justo lo que este script existe para evitar.
    """
    starts = re.findall(r"(?:^|[.!?]\s+|\n)\s*[¿¡]?(" + LETTER + ")", original)
    if not starts or sum(1 for c in starts if c.isupper()) * 2 < len(starts):
        return text
    return re.sub(r"(?:^|(?<=[.!?] )|(?<=[.!?]\n)|(?<=\n))\s*[¿¡]?(" + LETTER + ")",
                  lambda m: m.group(0)[:-1] + m.group(1).upper(), text)


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

    head("INFORME DEL HUMANIZADOR")
    print(f"{total} marcas de máquina eliminadas, "
          f"{len(report['structures'])} señales de estructura marcadas para reescribir", file=out)

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
        print("  No hay nada para sacar.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Le saca la huella de máquina a un borrador.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para leer de stdin")
    ap.add_argument("-o", "--out", help="escribe el texto limpio acá en vez de en stdout")
    ap.add_argument("--report", action="store_true", help="muestra qué cambió (en stderr)")
    ap.add_argument("--json", action="store_true", help="devuelve {text, report} como JSON")
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
