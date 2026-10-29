#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
detect.py - un panel de cinco chequeos que puntúa cuánto parece escrito por
una máquina un borrador en castellano.

Qué es:  cinco heurísticas locales, modeladas sobre las señales que miran los
detectores públicos de IA: variación en el largo de las oraciones, cosas
concretas, vocabulario de relleno, huella tipográfica y voz. Todo se calcula en
tu máquina a partir del texto. No se sube nada.

Qué NO es:  GPTZero, Originality, Copyleaks, Winston ni Turnitin. No llama a
sus APIs y no puede prometer su veredicto. Detecta las cosas en las que todos
se fijan, por eso arreglarlas suele mover también sus números, pero la única
afirmación honesta es la de esta línea.

Sobre la VOZ en castellano: en inglés se mide con contracciones ("don't");
en castellano no existen, así que se mide la oralidad: muletillas, voseo o
tuteo coloquial, interjecciones. Un texto generado casi nunca dice "che",
"o sea", "posta", "mirá", "neta" o "la verdad".

Cada chequeo devuelve un puntaje HUMANO de 0 a 100. Más alto es mejor.

Uso
  python3 detect.py borrador.txt
  pbpaste | python3 detect.py -
  python3 detect.py borrador.txt --json
  python3 detect.py antes.txt despues.txt      # comparar dos versiones
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")
sys.path.insert(0, HERE)
from humanize import build_pattern, lexicon_entries  # noqa: E402

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü']+")
PRONOUNS = re.compile(
    r"\b(?:yo|me|mi|mis|m[íi]o|m[íi]a|conmigo|nosotros|nosotras|nos|nuestro|nuestra|"
    r"nuestros|nuestras|vos|te|tu|tus|t[úu]|ti|contigo|usted|ustedes|tuyo|tuya)\b",
    re.IGNORECASE)
# Oralidad: lo que dice una persona y casi nunca escribe un modelo.
# Panlatino a propósito: voseo rioplatense, pero también tuteo de México,
# Colombia, Chile, etc.
ORAL = re.compile(
    r"\b(?:che|o sea|posta|re|capaz|la verdad|ojo|dale|nah|onda|"
    r"ni idea|ja(?:ja)+|je(?:je)+|jaja|mir[áa]|fijate|f[íi]jate|vist[eo]|viste|ponele|"
    r"obvio|bah|uf|ufa|pucha|ni ah[íi]|neta|wey|g[üu]ey|chido|bac[áa]n|parce|"
    r"ch[ée]vere|oye|al toque|literal|nada que ver|ni en pedo|qu[ée] s[ée] yo|"
    r"digamos|en fin|tal cual|ahre|bancame|banc[áa]|laburo|laburar|plata|guita|lucas|"
    r"pa'|pa|pal|q|xq|tmb|tb|porfa|xd)\b",
    re.IGNORECASE)
# "Bueno," abriendo una oración es oral; "bueno" como adjetivo no.
ORAL_START = re.compile(r"(?im)(?:^|[.!?]\s+)[¡¿]?\s*(?:bueno|nada|igual|tipo|mir[áa]),")
# Voseo: "tenés", "querés", "sabés", "mirá", "hacelo". Marca muy fuerte de
# texto escrito por una persona rioplatense; se suma a la oralidad.
VOSEO = re.compile(r"\b(?:sos|ten[ée]s|quer[ée]s|sab[ée]s|pod[ée]s|hac[ée]s|dec[íi]s|"
                   r"ven[íi]|pens[áa]|mir[áa]|prob[áa]|dej[áa]|fij[áa]te|"
                   r"hacelo|decime|contame|avisame|escribime|mandame)\b", re.IGNORECASE)
NUMBERS = re.compile(r"\b\d[\d.,]*%?|[$€]\s?\d|\b(?:dos|tres|cuatro|cinco|seis|siete|ocho|"
                     r"nueve|diez|quince|veinte|treinta|cincuenta|cien|mil|millones|"
                     r"d[óo]lares|pesos|lucas)\b", re.IGNORECASE)
PROPER = re.compile(r"(?<![.!?]\s)(?<![¿¡\"“«\n])(?<!^)\b[A-ZÁÉÍÓÚÑ][a-záéíóúñü][A-Za-záéíóúñü]+\b",
                    re.MULTILINE)


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Lleva value a 0-100 donde `human` -> 100 y `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return WORD_RE.findall(text)


def check_burstiness(text):
    """Las personas varían mucho el largo de las oraciones. Los modelos escriben parejo."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, "muy corto para juzgar"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, f"variación {cv:.2f} en {len(lens)} oraciones (ideal 0.55 o más)"


def check_specificity(text):
    """Números, nombres y cosas concretas. El slop es abstracto."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "muy corto para juzgar"
    per100 = 100 / len(w)
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * per100
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} datos concretos, {density:.1f} cada 100 palabras (ideal 4 o más)"


def count_slop(text, lex):
    """Cuenta las apariciones del lexicón sin contar dos veces la misma porción
    de texto ("sin duda alguna" no suma también "sin duda")."""
    hits, found = 0, []
    work = text
    for fuzzy in (False, True):
        for entry in lexicon_entries(lex):
            pattern = build_pattern(entry["find"], fuzzy=fuzzy)
            n = len(pattern.findall(work))
            if n:
                hits += n
                if entry["find"] not in found:
                    found.append(entry["find"])
                work = pattern.sub(" \x00 ", work)
    return hits, found


def check_slop(text, lex):
    """Densidad de vocabulario de relleno contra el lexicón."""
    w = words(text)
    if not w:
        return 50.0, "vacío"
    hits, found = count_slop(text, lex)
    density = hits * 100 / len(w)
    score = scale(density, human=0.0, machine=4.0)
    detail = f"{hits} términos de relleno, {density:.1f} cada 100 palabras"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Caracteres que un teclado de celular no produce. Los ¿ y ¡ no cuentan:
    son castellano y cualquier teclado en español los tiene."""
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "    ")
    total = invisible * 4 + em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisibles, {em} rayas, {curly} comillas curvas, "
              f"{ellip} suspensivos de un carácter, {nbsp} espacios duros")
    return score, detail


def check_voice(text, lex):
    """Oralidad, persona y las formas por defecto de los modelos."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "muy corto para juzgar"
    per100 = 100 / len(w)
    oral = (len(ORAL.findall(text)) + len(ORAL_START.findall(text))
            + len(VOSEO.findall(text))) * per100
    person = len(PRONOUNS.findall(text)) * per100
    tells = 0
    names = []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    score = (scale(oral, human=2.5, machine=0.0) * 0.35
             + scale(person, human=8.0, machine=1.0) * 0.35
             + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("viñetas-parejas")
    detail = (f"{oral:.1f} marcas de oralidad, {person:.1f} pronombres personales "
              f"cada 100 palabras, {tells} señal(es) de estructura")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["VARIACIÓN", "CONCRECIÓN", "RELLENO", "HUELLA", "VOZ"]


def run(text, lex):
    results = {}
    results["VARIACIÓN"] = check_burstiness(text)
    results["CONCRECIÓN"] = check_specificity(text)
    results["RELLENO"] = check_slop(text, lex)
    results["HUELLA"] = check_fingerprint(text)
    results["VOZ"] = check_voice(text, lex)
    scores = [results[c][0] for c in CHECKS]
    # El chequeo más flojo arrastra el veredicto: a un detector le alcanza una señal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "PASA" if overall >= 70 and min(scores) >= 55 else (
        "REVISAR" if overall >= 50 else "MARCADO")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "PANEL DE DETECCIÓN" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'HUMANO':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "PASA":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Señal más floja: {weakest}. Arreglá eso primero.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Puntúa cuánto parece escrito por máquina un borrador.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("compare", nargs="?", help="segundo archivo, para ver antes/después")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=LEX)
    args = ap.parse_args()

    lex = json.load(open(args.lexicon, encoding="utf-8"))
    read = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex)
        payload.append({
            "source": name,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex)
        render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(f"  {a['human_score']:.1f} {a['verdict']}  ->  "
              f"{b['human_score']:.1f} {b['verdict']}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "PASA" else 1)


if __name__ == "__main__":
    main()
