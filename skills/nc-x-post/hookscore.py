#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
hookscore.py - puntúa la primera línea de un post de X en las cinco cosas que
suelen tener los ganchos fuertes, nombra la fórmula que usa y ordena varios.

Qué es:  cinco heurísticas locales, calculadas en tu máquina a partir del
texto. Miden propiedades que comparten las primeras líneas que frenan un
pulgar: corta para leerse de un vistazo, un dato concreto, algo en juego, lo
importante adelante y no al final, y un lector a quien apuntarle. Más el
nombre de la fórmula de hooks.json, para que un gancho que escribiste y uno
que encontraste se describan con el mismo vocabulario.

Qué NO es:  un predictor de alcance. Es un control de calidad: atrapa
etiquetas, preámbulos, ganchos sin nada concreto y primeras líneas que
entierran lo importante. No te va a decir cuál de dos ganchos decentes va a
viajar más. Eso te lo dicen tus propias estadísticas (ver /nc-x-audit).

Cada chequeo devuelve de 0 a 100. Más alto es mejor.

Uso
  python3 hookscore.py ganchos.txt              # un gancho por línea, ordenados
  python3 hookscore.py --hook "Perdí USD 4.000 por una cláusula que no puse."
  pbpaste | python3 hookscore.py -
  python3 hookscore.py ganchos.txt --json
"""

import argparse
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = os.path.join(HERE, "hooks.json")

WORD_RE = re.compile(r"[\w$%€'’-]+")
NUMBER_RE = re.compile(
    r"(?:US\$|USD|ARS|MXN|COP|CLP|€|\$)\s?\d[\d.,]*(?:\s?(?:k|mil|M)\b)?"   # plata
    r"|\b\d[\d.,]*\s?€"
    r"|\b\d[\d.,]*(?:[.,]\d+)?\s?"                                          # una cifra, con
    r"(?:%|k\b|mil\b|x\b|hs?\b|horas?\b|min\b|minutos?\b"                   # o sin unidad
    r"|d[ií]as?\b|semanas?\b|mes(?:es)?\b|años?\b)?",
    re.IGNORECASE)
CAP_RE = re.compile(r"(?<!\w)[A-ZÁÉÍÓÚÑ][a-záéíóúüñ]{2,}(?!\w)")
ACRONYM_RE = re.compile(r"(?<!\w)(?:[A-ZÁÉÍÓÚÑ]{2,6}|X)(?!\w)")   # IA, GPT, MRR, CRM, y X
# Una mayúscula al comienzo de una frase es gramática, no un nombre, salvo que
# la palabra no sea común. "Hoy" y "Todos" no son concretos. "Claude" sí.
COMMON = set("""
a al algo algunos alguien ahora antes así aun aunque bien bueno cada casi como con contra cosa
cosas cual cuando cuanto de del desde después donde dos el ella ellos en entre era es esa ese
eso esta este esto estos estas estoy fue fueron gente hace hay hoy la las le les lo los más mas
me mi mis mucho muchos muy nada nadie ni no nos nunca o otra otro para pero poco por porque
puede qué que quien quiero se ser si sí siempre sin sobre solo son su sus también tan te tengo
tiene todo todos tu tus un una uno unos usted vos y ya yo cuál cómo dónde cuándo quién hoy
mañana ayer estaba estuve tenía todas tenés tienes sabés sabes podés puedes hacé haz esto
""".split())
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
MENTION_RE = re.compile(r"(?:^|\s)@\w+")
LINK_RE = re.compile(r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|io|ai|co|dev|app|net|org|me|xyz|so|gg|ar|mx|cl|es|pe|uy)\b(?:/\S*)?",
                     re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

SPELLED_NUMBERS = {
    "cero", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
    "diez", "once", "doce", "quince", "veinte", "treinta", "cuarenta",
    "cincuenta", "sesenta", "setenta", "ochenta", "noventa", "cien", "ciento",
    "mil", "millón", "millon", "millones", "docena", "mitad", "doble", "triple",
}
MONEY_WORDS = {
    "dólares", "dolares", "dólar", "dolar", "pesos", "euros", "lucas", "palos",
    "luca", "verdes", "por ciento", "facturación", "facturacion", "ganancia",
    "sueldo", "mrr", "arr", "seguidores", "vistas", "impresiones", "clientes",
}

# Palabras que ponen algo en juego.
STAKES = {
    "dejá", "deja", "nunca", "mal", "equivocado", "equivocada", "error",
    "errores", "perdí", "perdimos", "perder", "perdiendo", "costó", "cuesta",
    "cuestan", "fundí", "rompí", "roto", "falló", "fracasé", "fracaso",
    "nadie", "no", "ni", "renuncié", "despedí", "echaron", "borré", "borrá",
    "maté", "mata", "matan", "reemplacé", "reemplaza", "corté", "gané",
    "gratis", "pagué", "cobré", "cobrar", "contraté", "ahorré", "primero",
    "primera", "prohibido", "ilegal", "peor", "odio", "odiaba", "desperdicié",
    "tiré", "estafa", "mentira", "mentí", "verdad", "secreto", "oculto",
    "antes", "hasta", "en vez", "pero", "excepto", "salvo", "problema", "riesgo",
    "ojo", "cuidado", "arrepiento", "ojalá", "debería", "deberías", "todavía",
    "ya", "solo", "sin", "versus", "vs", "realmente", "nuevo", "nueva",
    "sobrevalorado", "sobrevalorada", "subestimado", "subestimada", "buscado",
    "buscada", "codiciado", "codiciada", "caliente", "muerto", "murió", "lancé", "lanzamos",
    "salió", "anunció", "presentamos", "último", "filtrado", "nadie", "jamás",
}

# Bucles abiertos: frases que prometen algo por lo que hay que seguir leyendo.
LOOPS = re.compile(r"(?i)\b(?:esto es lo que|ac[aá] va|te cuento|as[ií] (?:es como|fue como))\b|\blo que pas[oó]\b"
                   r"|\bresulta que\b|\bla (?:verdad|raz[oó]n|parte|trampa)\b|\bnadie\b"
                   r"|\btodos (?:dicen|piensan|creen)\b|\btodo el mundo (?:dice|piensa|cree)\b"
                   r"|\bla mayor[ií]a\b|\bopini[oó]n impopular\b"
                   r"|\b(?:me )?(?:llevaba|tardaba)\b[^.!?]*[.!?]?[^.!?]*\bahora\b|\bhace\b[^.!?]*[.!?]?[^.!?]*\bhoy\b")

# Aperturas que gastan la línea sin decir nada.
WEAK_OPENERS = [
    "bueno", "ok", "okey", "hola", "holis", "buenas", "buen día", "buenos días",
    "gente", "chicos", "che", "hoy", "básicamente", "sinceramente", "mirá", "mira",
    "escuchá", "escucha", "solo", "quería", "quiero", "uno de", "una de",
    "alguna vez", "sabías", "sabes", "sabés", "te pasa", "en este", "en el día",
    "la cosa", "un montón", "hay", "esto es", "es que", "como", "cuando se",
    "si alguna", "un hilo", "hilo", "mini hilo", "recordatorio", "pequeño recordatorio",
]

IMPERATIVES = {
    "dejá", "deja", "robá", "roba", "copiá", "copia", "borrá", "borra", "probá",
    "prueba", "mirá", "mira", "leé", "lee", "guardá", "guarda", "usá", "usa",
    "armá", "arma", "hacé", "haz", "escribí", "escribe", "mandá", "manda",
    "tomá", "toma", "empezá", "empieza", "nunca", "siempre", "no", "poné",
    "pon", "corré", "corre", "revisá", "revisa", "cobrá", "cobra", "subí",
    "sube", "silenciá", "andá", "anda", "pará", "para",
}

DEALBREAKERS = [
    (re.compile(r"(?i)^\s*(?:un\s+)?(?:(?:mega|mini|breve|corto|largo|nuevo)\s+)?(?:hilo|thread)\b|^\s*🧵"),
     "Arranca con la palabra \"hilo\". Eso es envoltorio. Poné lo que prometés en la línea 1 y dejá que la interfaz de X muestre que es un hilo."),
    (re.compile(r"(?i)^\s*(?:dej[aá] de scrollear|deja de scrollear|no sigas scrolleando|par[aá] de scrollear|no scrollees)"),
     "Arranca con \"dejá de scrollear\". Pedir atención demuestra que no te la ganaste."),
    (re.compile(r"(?i)\b(?:en (?:este|el) (?:hilo|post|video)(?: de hoy)?|te (?:voy a|vamos a) (?:mostrar|enseñar|contar)|hoy te (?:muestro|enseño|cuento))\b"),
     "Preámbulo. Borralo y arrancá por lo que prometés."),
    (re.compile(r"(?i)^\s*(?:hola|holis|buenas|buen d[ií]a|buenos d[ií]as|gente[,!]|qu[eé] onda|bienvenid)"),
     "Saludo. Nadie abrió X para que lo saluden."),
    (re.compile(r"^\s*\(?\d+\s*/\s*(?:\d+|n)\)?\s"),
     "Arranca con un contador de hilo. \"1/12\" adelante del gancho gasta los caracteres más caros que tenés en un número de página."),
    (LINK_RE,
     "Link en el gancho. Ponelo en una respuesta. Acá cuesta 23 caracteres y le da al lector una forma de irse."),
    (HASHTAG_RE,
     "Hashtag en el gancho. En X un hashtag es un link para irse de tu propio post."),
]


def clamp(n):
    return max(0.0, min(100.0, n))


def propers(text):
    """Palabras con mayúscula que son nombres, no comienzos de frase."""
    found = set()
    for m in CAP_RE.finditer(text):
        before = text[:m.start()].rstrip()
        sentence_start = not before or before[-1] in ".!?:\n\"“(¿¡"
        if sentence_start and m.group(0).lower() in COMMON:
            continue
        found.add(m.group(0))
    found.update(ACRONYM_RE.findall(text))
    return found


def words(text):
    # "USD 4.000" y "18,5" se leen como un número, así que acá también.
    return WORD_RE.findall(re.sub(r"(?<=\d)[.,](?=\d)", "", text))


def first_line(post):
    """El gancho de un post es su primera línea no vacía."""
    for line in post.splitlines():
        if line.strip():
            return line.strip()
    return post.strip()


# ----------------------------------------------------------------- fórmulas

def load_formulas(path=HOOKS):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    by_id = {h["id"]: h for h in d["hooks"]}
    order = d.get("classify_order") or sorted(by_id)
    return [(by_id[i]["id"], by_id[i]["name"], re.compile(by_id[i]["match"], re.IGNORECASE))
            for i in order if i in by_id]


FORMULAS = load_formulas()


def classify(hook, formulas=None):
    """Nombra la fórmula de un gancho. Devuelve (id, nombre) o (None, 'sin clasificar')."""
    formulas = FORMULAS if formulas is None else formulas
    if not formulas:
        return None, "sin clasificar"
    for fid, name, pattern in formulas:
        if pattern.search(hook):
            return fid, name
    return None, "sin clasificar"


# ------------------------------------------------------------------ chequeos

def check_length(text):
    """Un gancho tiene que entrar de un vistazo. En el celular, eso es una línea y algo."""
    w = words(text)
    n = len(w)
    chars = len(text.strip())
    # El español usa más palabras que el inglés para decir lo mismo: 4 a 16.
    if 4 <= n <= 16:
        score = 100.0
    elif n < 4:
        score = clamp(100 - (4 - n) * 20)
    else:
        score = clamp(100 - (n - 16) * 9)
    if chars > 110:                      # pasa a una tercera línea en el celular
        score -= 12
    return clamp(score), f"{n} palabras, {chars} caracteres (lo ideal: 4-16 palabras, menos de 110 caracteres)"


def check_specificity(text):
    """Una cosa concreta le gana a tres abstractas."""
    nums = [n.strip() for n in NUMBER_RE.findall(text) if n.strip()]
    names = propers(text)
    low = [w.lower().strip("'’") for w in words(text)]
    spelled = [w for w in low if w in SPELLED_NUMBERS or w in MONEY_WORDS]
    hits = len(nums) + len(names) + len(spelled)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(names)[:2] + spelled[:2])
    return score, (f"{hits} dato(s) concreto(s)" + (f": {found}" if found else
                   " - ni un número, ni un nombre, nada que se pueda chequear"))


def check_stakes(text):
    """Tensión, costo, negación, novedad. Algo que el lector se podría perder."""
    w = [x.lower().strip("'’") for x in words(text)]
    markers = sorted({x for x in w if x in STAKES})
    if re.search(r"(?:US\$|USD|€|\$)\s?\d|\d\s?(?:d[oó]lares|pesos|euros|lucas)", text, re.IGNORECASE):
        markers.append("un precio")
    if LOOPS.search(text):
        markers.append("un bucle abierto")
    if text.rstrip().endswith("?") and re.search(r"(?i)(?<!\w)(?:vos|t[uú]|tu|tus|te|usted|ustedes)(?!\w)|\w+(?:[aá]s|[eé]s|[ií]s)\b", text):
        markers.append("una pregunta que solo el lector puede responder")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"{n} marca(s) de tensión" + (f": {', '.join(markers[:4])}" if markers else
                                           " - no hay nada en juego en esta línea")
    return clamp(score), detail


QUESTION_WORDS = {"qué", "que", "cuál", "cual", "cuáles", "quién", "quien", "por", "cómo",
                  "como", "cuándo", "cuando", "dónde", "donde", "cuánto", "cuanto", "cuántos"}


def check_frontload(text):
    """La palabra interesante no puede estar en el puesto nueve."""
    w = words(text)
    if not w:
        return 0.0, "vacío"
    low = [x.lower().strip("'’") for x in w]
    opener = " ".join(low[:2])
    penalty, hit_opener = 0, None
    for weak in WEAK_OPENERS:
        if opener.startswith(weak + " ") or opener == weak or low[0] == weak:
            penalty, hit_opener = 30, weak
            break
    payload = None
    names = propers(text)
    if text.rstrip().endswith("?") and low[0] in QUESTION_WORDS:
        payload = 0                      # una pregunta arranca con su propia carga
    for i, token in enumerate(low):
        if payload is not None:
            break
        if (token in STAKES or token in SPELLED_NUMBERS or token in MONEY_WORDS
                or NUMBER_RE.match(w[i]) and any(c.isdigit() for c in w[i]) or w[i] in names):
            payload = i
    if payload is None:
        base, where = 30.0, "no hay ninguna palabra con carga en toda la línea"
    elif payload <= 3:
        base, where = 100.0, f"carga en la palabra {payload + 1}"
    elif payload <= 6:
        base, where = 70.0, f"carga en la palabra {payload + 1}, se puede adelantar"
    else:
        base, where = 40.0, f"carga en la palabra {payload + 1}, demasiado tarde"
    detail = where + (f"; apertura floja \"{hit_opener}\"" if hit_opener else "")
    return clamp(base - penalty), detail


SECOND = re.compile(r"(?i)(?<!\w)(?:vos|t[uú]|tu|tus|te|ti|contigo|usted|ustedes|su negocio"
                    r"|ten[eé]s|tienes|sab[eé]s|sabes|quer[eé]s|quieres|pod[eé]s|puedes|hac[eé]s|haces"
                    r"|sos|eres|est[aá]s|vend[eé]s|vendes|cobr[aá]s|cobras|public[aá]s|publicas)(?!\w)")
FIRST = re.compile(r"(?i)(?<!\w)(?:yo|me|mi|mis|nosotros|nosotras|nos|nuestr[oa]s?|conmigo)(?!\w)"
                   r"|\b\w+(?:é|í)\b|\b\w+(?:amos|imos|emos)\b")


def check_address(text):
    """Apuntado a un lector, o flotando en el aire."""
    w = [x.lower().strip("'’") for x in words(text)]
    if SECOND.search(text):
        return 100.0, "le habla al lector"
    if w and w[0] in IMPERATIVES:
        return 90.0, f"arranca en imperativo (\"{w[0]}\")"
    if FIRST.search(text):
        return 75.0, "primera persona, sin lector nombrado"
    if len(w) <= 12:
        # "El empleado de marketing más buscado es un archivo de texto" no nombra
        # a nadie y no le hace falta. Una afirmación corta es su propio destinatario.
        return 70.0, "afirmación corta, sin lector nombrado"
    return 35.0, "tercera persona, no hay nadie en la sala"


CHECKS = ["LARGO", "CONCRECIÓN", "TENSIÓN", "ADELANTE", "DESTINATARIO"]


def run(text):
    text = first_line(text)
    results = {
        "LARGO": check_length(text),
        "CONCRECIÓN": check_specificity(text),
        "TENSIÓN": check_stakes(text),
        "ADELANTE": check_frontload(text),
        "DESTINATARIO": check_address(text),
    }
    flags = [msg for pattern, msg in DEALBREAKERS if pattern.search(text)]
    scores = [results[c][0] for c in CHECKS]
    # La propiedad más floja pone el techo, igual que en detect.py: con una sola
    # propiedad mala alcanza para que el pulgar siga de largo.
    overall = clamp(statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15)
    verdict = "FUERTE" if overall >= 70 and min(scores) >= 55 and not flags else (
        "OK" if overall >= 50 else "FLOJO")
    return results, overall, verdict, flags


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, out=sys.stdout):
    line = first_line(text)
    fid, fname = classify(line)
    print("\nPUNTAJE DEL GANCHO", file=out)
    print("=" * 62, file=out)
    print(f"  \"{line}\"", file=out)
    print(f"  fórmula: {('#' + str(fid) + ' ') if fid else ''}{fname}\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'GANCHO':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    for f in flags:
        print(f"\n  DESCALIFICA  {f}", file=out)
    if verdict != "FUERTE":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Propiedad más floja: {weakest}. Arreglá esa y volvé a correrlo.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nRANKING DE GANCHOS\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 60 else r["hook"][:57] + "..."
        print(f"{mark} {r['score']:5.1f} {r['verdict']:<7} {hook}", file=out)
        tag = f"#{r['formula_id']} {r['formula']}" if r["formula_id"] else r["formula"]
        print(f"        {tag}  ·  más floja: {r['weakest']} "
              f"({r['checks'][r['weakest']]['score']:.0f})", file=out)
        for f in r["flags"]:
            print(f"        descalifica: {f}", file=out)
    print("\nPublicá el primero. Si el primero está debajo de 50, ninguno de estos es el gancho.\n",
          file=out)


def score_payload(line):
    results, overall, verdict, flags = run(line)
    fid, fname = classify(first_line(line))
    return {
        "hook": first_line(line),
        "formula_id": fid,
        "formula": fname,
        "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
        "weakest": min(CHECKS, key=lambda c: results[c][0]),
        "flags": flags,
        "score": round(overall, 1),
        "verdict": verdict,
    }


def main():
    ap = argparse.ArgumentParser(description="Puntúa la primera línea de un post de X.")
    ap.add_argument("input", nargs="?", default="-", help="archivo con un gancho por línea, o -")
    ap.add_argument("--hook", help="puntúa un solo gancho pasado por línea de comandos")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        print("no hay nada para puntuar", file=sys.stderr)
        sys.exit(2)

    payload = [score_payload(l) for l in lines]
    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
        return
    if len(payload) == 1:
        results, overall, verdict, flags = run(lines[0])
        render_one(lines[0], results, overall, verdict, flags)
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))
    sys.exit(0 if max(p["score"] for p in payload) >= 70 else 1)


if __name__ == "__main__":
    main()
