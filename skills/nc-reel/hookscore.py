#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
hookscore.py - puntúa la primera línea de un Reel en las cinco cosas que
tienen en común los ganchos fuertes, nombra la fórmula que usa (de hooks.json)
y ordena un lote de ganchos entre sí.

Qué es:  cinco heurísticas locales, calculadas en tu máquina a partir del texto
solo. Miden propiedades que suelen compartir los ganchos que retienen: un largo
que se dice en menos de tres segundos, algo concreto (un número, un nombre),
algo en juego, lo interesante adelante y no al final, y alguien a quien
hablarle.

Qué NO es:  un predictor de vistas. Sirve para descartar los ganchos
claramente flojos (saludos, preámbulos, nada concreto, frases que tardan cinco
segundos en decirse). No te va a decir cuál de dos ganchos decentes va a
funcionar, porque eso lo deciden tu cara, tu edición, tu audio y a quién se lo
muestra Instagram. Confiá más en tu gráfico de retención que en este script.

Cada chequeo devuelve de 0 a 100. Más alto es mejor.

Uso
  python3 hookscore.py ganchos.txt               # un gancho por línea, ordenados
  python3 hookscore.py --hook "Perdí 18 mil dólares por una cláusula."
  pbpaste | python3 hookscore.py -
  python3 hookscore.py ganchos.txt --json
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = os.path.join(HERE, "hooks.json")

WORD_RE = re.compile(r"[\w$%'’€-]+")
MONEY_RE = re.compile(r"(?:\$|€|usd|u\$s|us\$)\s?\d", re.IGNORECASE)
NUMBER_RE = re.compile(
    r"(?:\$|€|usd\s?|u\$s\s?|us\$\s?)\d[\d.,]*"                 # plata
    r"|\b\d[\d.,]*\s?"                                         # una cifra, con
    r"(?:%|k\b|mil\b|x\b|hs?\b|horas?\b|min(?:utos?)?\b"         # o sin unidad
    r"|seg(?:undos?)?\b|d[íi]as?\b|semanas?\b|mes(?:es)?\b|a[ñn]os?\b"
    r"|usd\b|d[óo]lares\b|pesos\b|euros\b|lucas\b|palos\b)?",
    re.IGNORECASE)
# Nombre propio: mayúscula que no está al principio de la línea ni después de
# un punto, una pregunta o una exclamación (en castellano se abre con ¿ y ¡).
PROPER_RE = re.compile(r"(?<!^)(?<![.!?¿¡]\s)(?<![¿¡\"“«])\b[A-ZÁÉÍÓÚÑ][a-záéíóúñü][A-Za-záéíóúñü]+\b")
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# Los ganchos hablados dicen los números en voz alta. "Cero pesos" y "veinte
# lucas" son tan concretos como "$0" y "$20.000". "Uno/una" y "primero" quedan
# afuera a propósito: casi siempre son relleno, no una cantidad.
SPOKEN_NUMBERS = {
    "cero", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
    "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "dieciseis",
    "veinte", "veinticinco", "treinta", "cuarenta", "cincuenta", "sesenta",
    "setenta", "ochenta", "noventa", "cien", "ciento", "cientos", "doscientos",
    "trescientos", "quinientos", "mil", "miles", "millón", "millon", "millones",
    "docena", "mitad", "doble", "triple", "dieciocho", "diecisiete", "diecinueve",
}
MONEY_WORDS = {
    "dólares", "dolares", "dólar", "dolar", "pesos", "euros", "lucas", "palos",
    "guita", "plata", "centavos", "porciento", "usd", "facturación", "facturacion",
    "facturé", "facture", "ganancia", "ganancias", "sueldo", "salario", "alquiler",
    "millonario", "millonaria", "deuda", "deudas",
}

# Palabras que ponen algo en juego. Un gancho sin ninguna es una afirmación;
# con una, es una razón para seguir mirando. Se comparan sin tildes.
STAKES = {
    "deja", "dejen", "nunca", "jamas", "mal", "error", "errores", "equivocado",
    "equivocada", "perdi", "perder", "perdiendo", "perdes", "pierden", "pierdes",
    "costo", "cuesta", "cuestan", "fundi", "fundido", "quebre", "quiebra",
    "fracase", "fracaso", "fracasos", "falle", "nadie", "no", "ni", "sin",
    "renuncie", "renuncia", "despidieron", "despedido", "borre", "borra",
    "borrar", "mato", "mata", "matar", "reemplazo", "reemplaza", "reemplace",
    "corte", "gratis", "pague", "pagas", "cobre", "cobras", "cobran", "contrate",
    "ahorre", "ahorras", "primero", "prohibido", "ilegal", "peor", "odio",
    "odiaba", "tire", "desperdicie", "estafa", "mentira", "menti", "mienten",
    "verdad", "secreto", "oculto", "escondido", "robe", "robaron", "robate",
    "antes", "hasta", "pero", "excepto", "salvo", "problema", "riesgo",
    "peligro", "cuidado", "ojo", "arrepiento", "arrepenti", "ojala", "deberias",
    "deberia", "todavia", "solo", "unico", "unica", "versus", "vs", "basta",
    "nunca", "dejo", "deje", "pare", "para", "culpa", "miedo", "vergüenza",
    "verguenza", "fallo", "rechazo", "rechazaron", "ya", "apenas", "recien",
}
# "para" es preposición casi siempre; se saca acá y queda "pará" (imperativo)
# que se detecta antes de quitar tildes.
STAKES.discard("para")

# Arranques que gastan el primer segundo sin decir nada. Se comparan por
# palabras enteras al principio de la línea, sin tildes.
WEAK_OPENERS = [
    "bueno", "hola", "holis", "buenas", "hey", "che", "ok", "okey", "dale",
    "chicos", "chicas", "gente", "amigos", "amigas", "bienvenidos", "bienvenidas",
    "hoy", "basicamente", "sinceramente", "honestamente", "eh", "em", "emm",
    "o sea", "entonces", "asi que", "quería", "queria", "quiero", "vamos a",
    "les quiero", "te quiero contar", "uno de", "una de", "alguna vez", "sabias",
    "te paso", "en este", "en el video", "hay", "esto es", "es", "como", "cuando",
    "ustedes saben", "sabes", "bue", "nada", "a ver", "la verdad", "en mi opinion",
    "les cuento", "te cuento", "y bueno", "mira,", "escucha,", "pues",
]

# Imperativos que se ganan el primer lugar (voseo y tuteo).
IMPERATIVES = {
    "deja", "roba", "robate", "copia", "copiate", "borra", "proba", "prueba",
    "mira", "lee", "guarda", "guardate", "usa", "arma", "hace", "haz", "escribi",
    "escribe", "manda", "empeza", "empieza", "renuncia", "nunca", "siempre",
    "no", "pone", "pon", "revisa", "cobra", "subi", "sube", "frena",
    "olvidate", "anota", "evita", "cambia", "saca", "corta", "llevate",
    "fijate", "jamas", "basta",
}

DEALBREAKERS = [
    (re.compile(r"(?i)^\s*[¡!]?\s*(?:dej[áa] de (?:scrollear|deslizar|pasar)|deja de (?:scrollear|deslizar)"
                r"|no (?:scrollees|scroll[ée]s|deslices|pases de largo|sigas (?:pasando|scrolleando|bajando))"
                r"|par[áa] de (?:scrollear|deslizar)|par[áa] ah[íi]|fren[áa] (?:ah[íi]|el scroll)|stop scrolling)"),
     "Arranca con \"dejá de scrollear\". Pedir atención demuestra que todavía no te la ganaste."),
    (re.compile(r"(?i)\ben (?:este|el) (?:video|reel|post)(?: de hoy)?\b|\b(?:hoy )?(?:te|les) voy a (?:mostrar|ense[ñn]ar|contar|explicar|hablar)\b"
                r"|\bvamos a hablar (?:de|sobre)\b|\bhoy (?:vamos a|quiero|les quiero|te quiero) (?:hablar|contar|mostrar)\b"),
     "Preámbulo de video. Borralo y arrancá por la recompensa."),
    (re.compile(r"(?i)^\s*[¡!]?\s*(?:hola|holis|buenas|buen d[íi]a|buenos d[íi]as|buenas tardes|buenas noches|hey|qu[ée] tal"
                r"|qu[ée] onda|bienvenid[oa]s?|c[óo]mo (?:est[áa]n|andan|va|les va))\b"),
     "Saludo. Nadie entró al feed para que lo saluden."),
    (HASHTAG_RE,
     "Hashtag en el gancho. Los hashtags van al final del caption, si es que van."),
    (EMOJI_RE,
     "Emoji en el gancho. El texto en pantalla a tamaño gancho tiene lugar para palabras o para un emoji, no para los dos."),
]

# Palabras terminadas en -ás/-és/-ís que NO son verbos en voseo.
NOT_VOSEO = {"mas", "jamas", "ademas", "atras", "demas", "detras", "ingles",
             "despues", "traves", "pais", "maiz", "adios", "interes", "reves",
             "compas", "cortes", "japones", "portugues", "frances", "mes", "tres",
             "seis", "dios", "paris", "anis", "estres", "cafes", "bebes"}
NOT_PRETERITE = {"que", "porque", "cafe", "bebe", "jose", "fue", "ole", "pure",
                 "bide", "chale", "se", "de", "te", "me", "le", "fe", "sé", "re"}


def clamp(n):
    return max(0.0, min(100.0, n))


def fold(s):
    """minúsculas y sin tildes (la ñ se queda), para comparar palabras."""
    s = s.lower().replace("ñ", "\x00")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.replace("\x00", "ñ")


def words(text):
    # "$18.000" es una sola palabra cuando se lee la cifra, acá también.
    flat = re.sub(r"(?<=\d)[.,](?=\d{3}(?!\d))", "", text)
    return [w for w in WORD_RE.findall(flat) if w.strip("-'’")]


def load_formulas(path=HOOKS):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    by_id = {h["id"]: h for h in d["hooks"]}
    order = d.get("classify_order") or sorted(by_id)
    return [(by_id[i]["id"], by_id[i]["name"], re.compile(by_id[i]["match"], re.IGNORECASE))
            for i in order if i in by_id]


def classify(text, formulas):
    for fid, name, pattern in formulas or []:
        if pattern.search(text):
            return fid, name
    return None, "sin clasificar"


def check_length(text):
    """El gancho tiene que llegar antes de que se mueva el pulgar. Unos dos segundos."""
    w = words(text)
    n = len(w)
    secs = n / 2.67                      # ~160 palabras por minuto, hablado
    chars = len(text.strip())
    # En castellano una idea lleva alguna palabra más que en inglés
    # (artículos, preposiciones), así que la ventana es 5-13.
    if 5 <= n <= 13:
        score = 100.0
    elif n < 5:
        score = clamp(100 - (5 - n) * 20)
    else:
        score = clamp(100 - (n - 13) * 11)
    if chars > 70:                       # dos renglones de texto grande en pantalla
        score -= 12
    return clamp(score), f"{n} palabras, {chars} caracteres, ~{secs:.1f}s dicho (ideal 5-13 palabras)"


def check_specificity(text):
    """Una cosa concreta le gana a tres abstractas."""
    flat = re.sub(r"(?<=\d)[.,](?=\d{3}(?!\d))", "", text)
    nums = [n.strip() for n in NUMBER_RE.findall(flat) if n.strip()]
    propers = set(PROPER_RE.findall(text))
    low = [w.lower().strip("'’") for w in words(text)]
    spoken = [w for w in low if w in SPOKEN_NUMBERS or w in MONEY_WORDS]
    if re.search(r"(?i)\bpor ?ciento\b", text):
        spoken.append("por ciento")
    hits = len(nums) + len(propers) + len(spoken)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(propers)[:2] + spoken[:2])
    return score, (f"{hits} dato(s) concreto(s)" + (f": {found}" if found else
                   " - ni número, ni nombre, nada que se pueda chequear"))


def _stake_tokens(text):
    raw = [x.lower().strip("'’") for x in words(text)]
    out = []
    for x in raw:
        if x in ("pará", "pará"):
            out.append("pará")
        elif fold(x) in STAKES:
            out.append(fold(x))
    return out


def check_stakes(text):
    """Tensión, costo, negación. Algo que el espectador podría perder."""
    markers = sorted(set(_stake_tokens(text)))
    if MONEY_RE.search(text) or re.search(r"(?i)\b(?:d[óo]lares|pesos|euros|lucas)\b", text):
        markers.append("un precio")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"{n} marcador(es) de tensión" + (f": {', '.join(markers[:4])}" if markers else
                                               " - no hay nada en juego en esta línea")
    return clamp(score), detail


def _weak_opener(text):
    question = text.strip().lstrip("\"“«'").startswith("¿")
    stripped = text.strip().lstrip("¿¡\"“«'").lower()
    toks = [fold(t) for t in words(stripped)]
    for weak in WEAK_OPENERS:
        wt = fold(weak)
        if wt.endswith(","):                      # "mirá," sí; "mirá lo que" no
            if fold(stripped).startswith(wt):
                return weak
            continue
        parts = wt.split()
        if question and parts[0] in ("como", "que", "cuando"):
            continue                              # "¿Cómo...?" es pregunta, no relleno
        if toks[:len(parts)] == parts:
            return weak
    return None


def check_frontload(text):
    """La palabra interesante no puede estar en la posición nueve."""
    w = words(text)
    if not w:
        return 0.0, "vacío"
    low = [x.lower().strip("'’") for x in w]
    hit_opener = _weak_opener(text)
    penalty = 30 if hit_opener else 0
    payload = None
    for i, token in enumerate(low):
        if (fold(token) in STAKES or token in SPOKEN_NUMBERS or token in MONEY_WORDS
                or re.match(r"[$€]?\d", w[i]) or (i and PROPER_RE.match(w[i]))):
            payload = i
            break
    if payload is None:
        base, where = 30.0, "ninguna palabra con peso en toda la línea"
    elif payload <= 3:
        base, where = 100.0, f"lo interesante está en la palabra {payload + 1}"
    elif payload <= 6:
        base, where = 70.0, f"lo interesante está en la palabra {payload + 1}, se puede adelantar"
    else:
        base, where = 40.0, f"lo interesante está en la palabra {payload + 1}, demasiado tarde"
    detail = where + (f"; arranque flojo \"{hit_opener.rstrip(',')}\"" if hit_opener else "")
    return clamp(base - penalty), detail


SECOND_PERSON = re.compile(
    r"\b(?:vos|te|tu|tus|t[úu]|ti|contigo|usted|ustedes|tuyo|tuya|tuyos|tuyas|sos|eres|"
    r"est[áa]s|ten[ée]s|tienes|quer[ée]s|quieres|pod[ée]s|puedes|sab[ée]s|sabes|"
    r"necesit[áa]s|necesitas|hac[ée]s|haces|vend[ée]s|vendes|cobr[áa]s|cobras)\b",
    re.IGNORECASE)
FIRST_PERSON = re.compile(
    r"\b(?:yo|me|mi|mis|m[íi]o|m[íi]a|conmigo|nosotros|nosotras|nos|nuestro|nuestra|"
    r"nuestros|nuestras|perd[íi]|gan[ée]|hice|tuve|aprend[íi]|estuve|llevo|tengo|hago|"
    r"vendo|cobro|uso|vend[íi]|pas[ée]|trabaj[ée])\b",
    re.IGNORECASE)


def check_address(text):
    """Le habla a un espectador, o queda flotando en el aire."""
    toks = [x.lower().strip("'’") for x in words(text)]
    folded = [fold(t) for t in toks]
    if SECOND_PERSON.search(text):
        return 100.0, "le habla al espectador"
    # Voseo sin pronombre: "publicás", "querés", "vivís".
    for t, f in zip(toks, folded):
        if re.search(r"(?:ás|és|ís)$", t) and len(f) > 4 and f not in NOT_VOSEO:
            return 100.0, f"le habla al espectador (\"{t}\")"
    if folded and folded[0] in IMPERATIVES:
        return 90.0, f"arranca con imperativo (\"{toks[0]}\")"
    if FIRST_PERSON.search(text):
        return 70.0, "primera persona, sin nombrar al espectador"
    # Pretérito en primera persona sin pronombre: "publiqué", "cobré".
    for t, f in zip(toks, folded):
        if t.endswith("é") and len(f) > 3 and f not in NOT_PRETERITE:
            return 70.0, f"primera persona (\"{t}\"), sin nombrar al espectador"
    return 35.0, "tercera persona, no hay nadie en la sala"


CHECKS = ["LARGO", "CONCRECIÓN", "TENSIÓN", "ARRANQUE", "DESTINATARIO"]


def run(text):
    results = {
        "LARGO": check_length(text),
        "CONCRECIÓN": check_specificity(text),
        "TENSIÓN": check_stakes(text),
        "ARRANQUE": check_frontload(text),
        "DESTINATARIO": check_address(text),
    }
    flags = [msg for pattern, msg in DEALBREAKERS if pattern.search(text)]
    scores = [results[c][0] for c in CHECKS]
    # La propiedad más floja pone el techo: con una sola mala alcanza para que
    # el pulgar siga de largo.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15
    overall = clamp(overall)
    verdict = "FUERTE" if overall >= 70 and min(scores) >= 55 and not flags else (
        "ZAFA" if overall >= 50 else "FLOJO")
    return results, overall, verdict, flags


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, formula, out=sys.stdout):
    print("\nPUNTAJE DEL GANCHO", file=out)
    print("=" * 62, file=out)
    print(f"  \"{text.strip()}\"", file=out)
    fid, fname = formula
    print(f"  fórmula: {('#' + str(fid) + ' ') if fid else ''}{fname}\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'TOTAL':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    for f in flags:
        print(f"\n  DESCALIFICA  {f}", file=out)
    if verdict != "FUERTE":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Lo más flojo: {weakest}. Arreglá eso y volvé a correrlo.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nRANKING DE GANCHOS\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 62 else r["hook"][:59] + "..."
        print(f"{mark} {r['score']:5.1f} {r['verdict']:<7} {hook}", file=out)
        fid = f"#{r['formula_id']} " if r["formula_id"] else ""
        print(f"        fórmula: {fid}{r['formula']}  ·  más flojo: {r['weakest']} "
              f"({r['checks'][r['weakest']]['score']:.0f})", file=out)
        for f in r["flags"]:
            print(f"        descalifica: {f}", file=out)
    print("\nGrabá el primero. Si el primero está debajo de 50, ninguno de estos es el gancho.\n",
          file=out)


def main():
    ap = argparse.ArgumentParser(description="Puntúa un gancho de Reel en cinco propiedades.")
    ap.add_argument("input", nargs="?", default="-", help="archivo con un gancho por línea, o -")
    ap.add_argument("--hook", help="puntuar un solo gancho pasado por línea de comandos")
    ap.add_argument("--hooks-json", default=HOOKS, help="ruta a hooks.json (para nombrar la fórmula)")
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

    formulas = load_formulas(args.hooks_json)
    payload = []
    for line in lines:
        results, overall, verdict, flags = run(line)
        fid, fname = classify(line, formulas)
        payload.append({
            "hook": line,
            "formula_id": fid,
            "formula": fname,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "weakest": min(CHECKS, key=lambda c: results[c][0]),
            "flags": flags,
            "score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
        return

    if len(payload) == 1:
        results, overall, verdict, flags = run(lines[0])
        p = payload[0]
        render_one(lines[0], results, overall, verdict, flags, (p["formula_id"], p["formula"]))
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))
    if formulas is None:
        print("aviso: no encontré hooks.json, no se nombran las fórmulas.", file=sys.stderr)

    sys.exit(0 if max(p["score"] for p in payload) >= 70 else 1)


if __name__ == "__main__":
    main()
