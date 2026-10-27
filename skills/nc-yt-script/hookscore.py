#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""hookscore.py - puntuá un gancho de YouTube antes de gastar una toma en él.

Cinco propiedades, de 0 a 100 cada una, y un veredicto que es 60% el promedio y 40% la más débil.
El peso del eslabón más débil es a propósito: un gancho con cuatro propiedades fuertes y una muerta
es un gancho que pierde gente justo en la muerta, y el promedio lo esconde.

    python3 hookscore.py ganchos.txt            # un gancho por línea, rankeados
    python3 hookscore.py --hook "una línea"     # puntuar uno solo
    python3 hookscore.py --json ganchos.txt     # salida para máquinas

LO QUE PUEDE Y LO QUE NO PUEDE DECIRTE. Es una heurística, no un predictor. Sirve para separar
ganchos claramente flojos (vagos, largos, sin nada en juego) de ganchos trabajados. NO sabe cuál de
tus ganchos buenos va a rendir más. Un puntaje bajo es una razón para mirarlo de nuevo; un puntaje
alto no es una promesa. Entiende español (voseo y tuteo, con y sin tilde).
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as _fh:
    FORMULAS = json.load(_fh)["hooks"]

# Relleno: palabras que ocupan aire en un gancho hablado sin decir nada.
FILLER = {"basicamente", "literalmente", "realmente", "simplemente", "obviamente", "bueno", "entonces",
          "tipo", "onda", "hola", "holaa", "chicos", "chicas", "gente", "amigos", "bienvenidos",
          "bienvenidas", "hoy", "video", "suscribite", "suscribete", "suscribirte", "canal", "eh",
          "ehh", "em", "digamos", "nada", "viste", "che", "bah", "ok", "okey", "dale"}
FILLER_PHRASES = re.compile(r"\b(o sea|en el video de hoy|antes de arrancar|antes de empezar|"
                            r"dale like|no te olvides)\b", re.I)
# Adjetivos que suenan a mucho y no dicen nada concreto.
VAGUE = {"increible", "impresionante", "brutal", "loco", "locura", "enorme", "masivo", "epico",
         "secreto", "poderoso", "definitivo", "mejor", "revolucionario", "alucinante", "tremendo",
         "bestial", "espectacular", "perfecto", "potenciar", "potencia", "desbloquear", "magia",
         "magico", "infalible", "top", "genial", "unico"}
NUMWORDS = (r"dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|quince|veinte|treinta|"
            r"cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|doscientos|"
            r"trescientos|quinientos|mil|millon|millones")
CONCRETE = re.compile(
    r"(\$\s?\d|\busd\s?\d|\b\d[\d.,]*\s?(%|k\b|mil\b|x\b|usd\b|d[oó]lares\b|pesos\b|"
    r"(segundos?|minutos?|horas?|d[ií]as?|semanas?|mes(es)?|años?)\b)?|"
    r"\b(" + NUMWORDS + r")\b)", re.I)
# Segunda persona: voseo, tuteo y usted.
YOU = re.compile(r"\b(vos|te|tu|tus|tú|ti|contigo|usted|ustedes|ten[eé]s|tienes|sos|eres|est[áa]s|"
                 r"quer[eé]s|quieres|pod[eé]s|puedes|sab[eé]s|sabes|hac[eé]s|haces|sub[ií]s|subes|"
                 r"necesit[áa]s|necesitas|perd[eé]s|pierdes|grab[áa]s|grabas|vend[eé]s|vendes|"
                 r"segu[ií]s|sigues|dej[áa]|deja|mir[áa]|mira|tuyo|tuya|subas|publiques|hagas|grabes|"
                 r"compres|uses|pierdas|empieces|arranques|tengas|necesites|revises)\b", re.I)
STAKE = re.compile(r"\b(perd\w*|pierd\w*|tir(ando|[áa]s|ar)|desperdici\w*|abandon\w*|renunci\w*|"
                   r"fall(ar|a|an|ando)|fracas\w*|fund(ir|irse|ido|iste)|quebr\w*|cost(o|ar|ando|[óo])|"
                   r"cuesta|riesgo|antes|dej[áa]|par[áa]|nunca|muer(e|en|to|ta)|mor[íi]\w*|"
                   r"errore?s?|error|plata|caro|gratis)\b", re.I)
CURIOSITY = re.compile(r"(\bpor qu[ée]\b|\bc[óo]mo\b|\bqué\b|\bcu[áa]l\b|\bhasta\b|\bantes\b|\bpero\b|"
                       r"\bnadie\b|\bcasi\b|\bexcepto\b|\bsalvo\b|\bmotivo\b|\braz[óo]n\b|"
                       r"\ben realidad\b|\bni siquiera\b|\bresulta que\b|\best[oa] (es|fue) lo que\b|"
                       r"\blo que pas[óo]\b|\bte cuento\b)", re.I)
# Un gancho que se responde solo no deja nada abierto.
CLOSED = re.compile(r"\b(porque|as[ií] que|lo que significa|o sea que|por eso)\b", re.I)

def plain(t):
    """minúsculas y sin tildes, para comparar contra los léxicos."""
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

def words(t): return re.findall(r"[a-z0-9ñ'%$.]+", plain(t))

def specificity(t):
    w = words(t)
    if not w: return 0
    nums = len(CONCRETE.findall(t))
    vague = sum(1 for x in w if x in VAGUE)
    filler = sum(1 for x in w if x in FILLER) + len(FILLER_PHRASES.findall(t))
    s = 34 + nums * 22 - vague * 16 - filler * 5
    # nombres propios que no están al principio de la oración se leen como cosas con nombre
    toks = t.split()
    proper = 0
    for i, x in enumerate(toks[1:], 1):
        prev = toks[i - 1]
        if x.lstrip("¿¡\"'(")[:1].isupper() and not prev.endswith((".", "?", "!", ":")):
            proper += 1
    s += min(18, 6 * proper)
    return max(0, min(100, s))

def address(t):
    n = len(YOU.findall(t))
    first = 30 if YOU.search(" ".join(t.split()[:6])) else 0
    return max(0, min(100, 26 + n * 20 + first))

def stakes(t):
    n = len(STAKE.findall(t))
    return max(0, min(100, 22 + n * 26 + (14 if CONCRETE.search(t) else 0)))

def curiosity(t):
    n = len(CURIOSITY.findall(t))
    q = 18 if (t.strip().endswith("?") or "¿" in t) else 0
    closed = -18 if CLOSED.search(t) else 0
    return max(0, min(100, 24 + n * 17 + q + closed))

def brevity(t):
    n = len(words(t))
    if n == 0: return 0
    # 9-26 palabras: lo que entra en ~10 segundos hablados a ~160 palabras por minuto en español
    if 9 <= n <= 26: return 100
    if n < 9:  return max(30, 100 - (9 - n) * 11)
    return max(10, 100 - (n - 26) * 7)

PROPS = [("ESPECIFICIDAD", specificity), ("INTERPELACIÓN", address), ("RIESGO", stakes),
         ("CURIOSIDAD", curiosity), ("BREVEDAD", brevity)]

def classify(t):
    best, hits = None, 0
    for f in FORMULAS:
        n = sum(1 for p in f["match"] if re.search(p, t.strip(), re.I))
        if n > hits: best, hits = f, n
    return (best["name"] if best else "Sin clasificar"), hits

def score(t):
    parts = {n: fn(t) for n, fn in PROPS}
    vals = list(parts.values())
    verdict = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    name, hits = classify(t)
    return parts, verdict, name, hits

def band(v): return "FUERTE" if v >= 72 else "SIRVE" if v >= 55 else "FLOJO"

FIX = {
 "ESPECIFICIDAD": "cambiá un adjetivo por un número, un nombre o una fecha",
 "INTERPELACIÓN": "hablale de 'vos' (o 'tú') en las primeras seis palabras",
 "RIESGO": "decí qué le cuesta seguir haciéndolo como lo hace hoy",
 "CURIOSIDAD": "cortá la mitad de la oración que se responde sola",
 "BREVEDAD": "entre 9 y 26 palabras. Leelo en voz alta y cortá donde te quedás sin aire",
}

def report(t, parts, verdict, name, hits):
    print(f"\n  {t.strip()}")
    print(f"  {'-' * min(72, max(20, len(t.strip())))}")
    for k, v in parts.items():
        print(f"    {k:<14} {v:3d}  {'#' * (v // 5)}")
    print(f"    {'VEREDICTO':<14} {verdict:3d}  {band(verdict)}")
    if hits:
        print(f"    fórmula        {name}  ({hits} {'patrón coincidente' if hits == 1 else 'patrones coincidentes'})")
    else:
        print("    fórmula        Sin clasificar  (no coincide ninguna fórmula: suele ser un resumen, no un gancho)")
    low = min(parts, key=parts.get)
    print(f"    más débil      {low} - {FIX[low]}")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    if "--hook" in a:
        lines = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        with open(a[0], encoding="utf-8", errors="replace") as fh:
            lines = [l for l in fh.read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1 if not a else 0)
    out = []
    for t in lines:
        parts, verdict, name, hits = score(t)
        out.append({"gancho": t.strip(), "propiedades": parts, "veredicto": verdict,
                    "banda": band(verdict), "formula": name, "coincidencias": hits})
    out.sort(key=lambda r: -r["veredicto"])
    if as_json:
        print(json.dumps([{k: v for k, v in r.items() if k != "coincidencias"} for r in out],
                         indent=1, ensure_ascii=False)); return
    for r in out:
        report(r["gancho"], r["propiedades"], r["veredicto"], r["formula"], r["coincidencias"])
    if len(out) > 1:
        print(f"\n  ganador: {out[0]['gancho']}  ({out[0]['veredicto']}, {out[0]['banda']})\n")

if __name__ == "__main__":
    main()
