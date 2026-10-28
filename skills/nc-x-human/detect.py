#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
detect.py - un panel de cinco chequeos que puntúa cuánto parece escrito por
una máquina un borrador en español.

Qué es:  cinco heurísticas locales, modeladas sobre las señales que miden los
detectores públicos de IA: variación del largo de las frases, cosas concretas,
vocabulario de relleno, huella tipográfica y voz. Todo se calcula en tu
máquina, a partir del texto. No se sube nada.

Qué NO es:  GPTZero, Originality, Copyleaks, Winston ni Turnitin. No llama a
sus APIs y no puede prometer su veredicto. Mide las mismas cosas de fondo, por
eso arreglarlas suele mover sus números también; pero lo único honesto que se
puede afirmar es lo que dice esta línea.

La mayoría de los posts cortos (un comentario, un post de X) no le alcanzan a
dos de los cinco chequeos: la variación necesita cuatro frases y la densidad
de datos concretos necesita unas 25 palabras. Por debajo de eso esos dos
chequeos dicen n/d y no cuentan, y el veredicto se apoya en los que sí pueden
juzgar. VOZ se queda solo con su mitad de señales de estructura.

Cada chequeo devuelve un puntaje HUMANO de 0 a 100. Más alto es mejor.

Uso
  python3 detect.py borrador.txt
  pbpaste | python3 detect.py -
  python3 detect.py borrador.txt --json
  python3 detect.py antes.txt despues.txt      # compara dos borradores
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

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[^\W\d_]+")
# Pronombres de primera y segunda persona: una persona le habla a otra.
PRONOUNS = re.compile(
    r"(?<!\w)(?:yo|me|mi|mis|m[ií]o|m[ií]a|conmigo|nosotros|nosotras|nos|nuestr[oa]s?"
    r"|vos|t[uú]|tus|te|ti|contigo|usted|ustedes|vosotros|vosotras|os|vuestr[oa]s?)(?!\w)",
    re.IGNORECASE)
# Marcas de registro hablado. En inglés serían las contracciones ("don't",
# "I'm"); en español la señal equivalente es el registro: voseo o tuteo
# conjugado, imperativos con pronombre pegado y muletillas de conversación.
# Un texto generado casi nunca las usa: escribe en un neutro de manual.
INFORMAL = re.compile(
    r"(?<!\w)(?:"
    # voseo rioplatense / centroamericano
    r"sos|ten[eé]s|sab[eé]s|quer[eé]s|pod[eé]s|hac[eé]s|dec[ií]s|ven[ií]s|ten[eé]s que"
    r"|mir[aá]|fijate|pens[aá]|prob[aá]|and[aá]|ven[ií]|dale|che|contame|decime|escribime"
    r"|mandame|avisame|pasame|bancame|imaginate"
    # tuteo con pronombre pegado (sin ambigüedad con sustantivos)
    r"|f[ií]jate|cu[eé]ntame|dime|escr[ií]beme|m[aá]ndame|av[ií]same|p[aá]same|imag[ií]nate"
    # muletillas y registro de charla
    r"|la verdad|posta|ojo|bueno|igual|capaz|obvio|ni idea|ni loco|qu[eé] s[eé] yo|en serio"
    r"|tal cual|un mont[oó]n|una banda|re\s+(?:bien|f[aá]cil|caro|barato|lindo|util|[uú]til)"
    r"|laburo|laburar|curro|chamba|plata|guita|venga|t[ií]o|wey|g[uü]ey|neta|chido"
    r"|ja(?:ja)+|uf+|nah|bah|eh|ok|listo|onda|tipo que|o sea"
    r")(?!\w)",
    re.IGNORECASE)
NUMBERS = re.compile(r"(?<!\w)\d[\d.,]*%?|(?:US\$|USD|ARS|MXN|COP|CLP|€|\$)\s?\d")
PROPER = re.compile(r"(?<![.!?¿¡]\s)(?<![¿¡])(?<!^)(?<!\w)[A-ZÁÉÍÓÚÑ][a-záéíóúüñ]{2,}(?!\w)", re.MULTILINE)

# El unidor dentro de 👨‍💻 y las etiquetas de las tres banderas regionales son
# caracteres invisibles haciendo un trabajo legítimo. No son una huella.
_PICTO = "\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿"
EMOJI_ZWJ_RE = re.compile(f"(?<=[{_PICTO}️\U0001F3FB-\U0001F3FF])‍(?=[{_PICTO}])")
FLAG_TAG_RE = re.compile(
    "\U0001F3F4\U000E0067\U000E0062"
    "(?:\U000E0065\U000E006E\U000E0067|\U000E0073\U000E0063\U000E0074|\U000E0077\U000E006C\U000E0073)"
    "\U000E007F")


def term_pattern(find):
    body = re.escape(find).replace(r"\ ", r"\s+")
    left = r"(?<!\w)" if find[:1].isalnum() else ""
    right = r"(?!\w)" if find[-1:].isalnum() else ""
    return re.compile(left + body + right, re.IGNORECASE)


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Lleva value a 0-100, donde `human` -> 100 y `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return WORD_RE.findall(text)


def check_burstiness(text):
    """La gente varía mucho el largo de las frases. Los modelos escriben parejo."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return None, f"n/d: {len(lens)} frase(s), hacen falta 4 para medir variación"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, f"variación {cv:.2f} en {len(lens)} frases (lo ideal: 0.55 o más)"


def check_specificity(text):
    """Números, nombres y cosas concretas. El slop es abstracto."""
    w = words(text)
    if len(w) < 25:
        return None, f"n/d: {len(w)} palabras, hacen falta 25 para una densidad"
    per100 = 100 / len(w)
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * per100
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} datos concretos, {density:.1f} cada 100 palabras (lo ideal: 4 o más)"


def check_slop(text, lex):
    """Densidad de vocabulario de relleno según el lexicón."""
    w = words(text)
    if not w:
        return 50.0, "vacío"
    hits, found = 0, []
    for entry in lex["words"] + lex["phrases"]:
        n = len(term_pattern(entry["find"]).findall(text))
        if n:
            hits += n
            found.append(entry["find"])
    density = hits * 100 / len(w)
    score = scale(density, human=0.0, machine=4.0)
    detail = f"{hits} frases hechas, {density:.1f} cada 100 palabras"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Caracteres que un teclado no produce por sí solo."""
    bare = FLAG_TAG_RE.sub("", EMOJI_ZWJ_RE.sub("", text))
    invisible = sum(1 for c in bare if unicodedata.category(c) == "Cf")
    em = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "   ")
    # Las comillas curvas pesan un cuarto: el iPhone las escribe solo y la
    # mayoría de los posts se escriben en el celular, así que por sí solas dicen
    # poco. Una raya larga o un carácter invisible dicen mucho.
    total = invisible * 4 + em * 2 + curly * 0.25 + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisibles, {em} rayas largas, {curly} comillas curvas, "
              f"{ellip} puntos suspensivos de un carácter, {nbsp} espacios duros")
    return score, detail


def check_voice(text, lex):
    """Registro hablado, persona y las formas que los modelos usan por defecto."""
    w = words(text)
    short = len(w) < 25
    per100 = 100 / max(len(w), 1)
    informal = len(INFORMAL.findall(text)) * per100
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
    if short:
        # En una frase, la tasa de registro y de pronombres es ruido. Las
        # señales de estructura no: "Un hilo 🧵" es una señal a cualquier largo.
        detail = f"texto corto: solo señales de estructura, {tells} encontrada(s)"
        if names:
            detail += " [" + ", ".join(names[:4]) + "]"
        return clamp(100 - tells * 50), detail
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    score = (scale(informal, human=2.0, machine=0.0) * 0.35
             + scale(person, human=8.0, machine=1.0) * 0.35
             + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("viñetas-parejas")
    detail = (f"{informal:.1f} marcas de registro hablado, {person:.1f} pronombres personales "
              f"cada 100 palabras, {tells} señal(es) de estructura")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["VARIACIÓN", "CONCRECIÓN", "SLOP", "HUELLA", "VOZ"]


def run(text, lex):
    results = {}
    results["VARIACIÓN"] = check_burstiness(text)
    results["CONCRECIÓN"] = check_specificity(text)
    results["SLOP"] = check_slop(text, lex)
    results["HUELLA"] = check_fingerprint(text)
    results["VOZ"] = check_voice(text, lex)
    scores = [results[c][0] for c in CHECKS if results[c][0] is not None]
    # El chequeo más flojo arrastra el veredicto: a un detector le alcanza una señal.
    # Los que no pueden juzgar (n/d) no cuentan, en vez de valer 50.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "PASA" if overall >= 70 and min(scores) >= 55 else (
        "REVISAR" if overall >= 50 else "MARCADO")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "PANEL DE DETECCIÓN DE IA" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        if score is None:
            print(f"  {name:<13} {'-' * 24}   n/d", file=out)
        else:
            print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'PUNTAJE HUMANO':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    sat_out = [c for c in CHECKS if results[c][0] is None]
    if sat_out:
        print(f"  {'':<13} texto corto: puntuado con {len(CHECKS) - len(sat_out)} de 5 chequeos",
              file=out)
    if verdict != "PASA":
        judged = [c for c in CHECKS if results[c][0] is not None]
        weakest = min(judged, key=lambda c: results[c][0])
        print(f"\n  Señal más floja: {weakest}. Arreglá esa primero.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Puntúa cuánto parece escrito por una máquina un borrador.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("compare", nargs="?", help="segundo archivo, para ver antes y después")
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
            "checks": {k: {"score": None if v[0] is None else round(v[0], 1), "detail": v[1]}
                       for k, v in results.items()},
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
