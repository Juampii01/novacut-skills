#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""title.py - revisá el par título + miniatura de YouTube antes de publicarlo.

    python3 title.py --title "..." --thumb "SIN EDITOR"
    python3 title.py titulos.txt                        # uno por línea, rankeados
    python3 title.py --title "..." --clave "pan casero sin amasar"
    python3 title.py --title "..." --json

La unidad es el par, no el título. Un título que repite el texto de la miniatura desperdicia la mitad
de la superficie de clic, y ese es el error más común que esto chequea.

Largo: YouTube corta cerca de 60 caracteres en la búsqueda de escritorio y cerca de 40 en el inicio
del celular. Se informan los dos porque fallan distinto: el corte de escritorio pierde la cola, el
del celular puede perder el tema. En español los títulos salen más largos que en inglés, así que el
frente del título importa todavía más.

--clave "consulta": la búsqueda que este video debería ganar. Chequea que sus palabras estén en el
título (sin importar tildes) y que entren antes del corte del celular.

Mayúsculas: en español solo va mayúscula al principio y en nombres propios. Un Título Con Cada
Palabra En Mayúscula se lee como traducido del inglés, y se marca.
"""
import json, re, sys, os, unicodedata

DESKTOP, MOBILE, HARD = 60, 40, 100
# Adjetivos que prometen mucho y no dicen nada concreto (sin tildes, se comparan normalizados).
VAGUE = {"increible", "impresionante", "brutal", "loco", "locura", "enorme", "masivo", "definitivo",
         "mejor", "poderoso", "secreto", "secretos", "revolucionario", "alucinante", "epico",
         "perfecto", "perfecta", "completo", "completa", "todo", "tremendo", "bestial", "espectacular",
         "infalible", "magico", "magia", "potenciar", "desbloquear", "genial", "top"}
STOP = {"el", "la", "los", "las", "lo", "un", "una", "unos", "unas", "de", "del", "al", "a", "en",
        "con", "por", "para", "sin", "y", "o", "que", "es", "son", "tu", "tus", "te", "mi", "mis",
        "yo", "vos", "este", "esta", "esto", "como", "por", "que", "cuando", "se", "su", "sus", "le"}
NUMWORDS = {"dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once",
            "doce", "quince", "veinte", "treinta", "cuarenta", "cincuenta", "cien", "mil", "millon",
            "millones"}
MONTHS = {"enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
          "setiembre", "octubre", "noviembre", "diciembre"}
# Palabras que en español van en minúscula aunque el título use Mayúscula En Cada Palabra.
MINOR = {"de", "del", "la", "el", "los", "las", "y", "o", "en", "con", "para", "por", "un", "una",
         "a", "al", "que", "sin", "tu", "mi", "es"}

def plain(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

def words(t): return re.findall(r"[a-z0-9ñ']+", plain(t))

def stem(w):
    """plural simple, para que 'miniatura' y 'miniaturas' cuenten como la misma palabra."""
    if len(w) > 4 and w.endswith("es"): return w[:-2]
    if len(w) > 3 and w.endswith("s"): return w[:-1]
    return w

def check(title, thumb=None, clave=None):
    t = title.strip()
    n = len(t)
    issues, good = [], []
    if n > HARD: issues.append(("largo", f"{n} caracteres: el límite duro de YouTube es {HARD}"))
    elif n > DESKTOP: issues.append(("largo", f"{n} caracteres: la búsqueda de escritorio corta cerca de {DESKTOP}"))
    else: good.append(f"{n} caracteres, dentro del corte de escritorio ({DESKTOP})")
    if n > MOBILE:
        head = t[:MOBILE].rsplit(" ", 1)[0]
        issues.append(("celular", f'en el inicio del celular se ve más o menos "{head}...": fijate que el tema sobreviva'))
    toks = t.split()
    caps = [w for w in toks if len(re.sub(r"\W", "", w)) > 2 and w.isupper()]
    if len(caps) > 2: issues.append(("mayúsculas", f"{len(caps)} palabras en MAYÚSCULAS: con más de dos se lee como spam"))
    elif caps: good.append(f"{len(caps)} palabra en mayúsculas para enfatizar" if len(caps) == 1
                           else f"{len(caps)} palabras en mayúsculas para enfatizar")
    # Mayúscula En Cada Palabra: calco del inglés
    rest = [w for w in toks[1:] if re.sub(r"[^\w]", "", w) and not w.isupper()]
    titled = [w for w in rest if w.lstrip("¿¡\"'(")[:1].isupper()]
    minor_up = [w for w in rest if plain(w.strip("¿¡?!\"'(),.:")) in MINOR and w.lstrip("¿¡\"'(")[:1].isupper()]
    if len(rest) >= 3 and (len(titled) / len(rest) >= 0.6 or minor_up):
        issues.append(("estilo-inglés", "Mayúscula En Cada Palabra: en español va solo al principio y en nombres propios"))
    if t.endswith("?") and "¿" not in t:
        issues.append(("signos", "falta el ¿ de apertura: en español la pregunta abre y cierra"))
    v = sorted({w for w in words(t) if w in VAGUE})
    if v: issues.append(("vago", f"{', '.join(v)}: cambialo por un número, un nombre o una fecha"))
    nums = re.findall(r"\d[\d.,]*%?", t)
    wnums = [w for w in words(t) if w in NUMWORDS or w in MONTHS]
    if nums or wnums: good.append(f"tiene un dato concreto ({', '.join((nums + wnums)[:3])})")
    else: issues.append(("sin-número", "no tiene número, fecha ni nombre: es el arreglo más confiable"))
    if t.endswith("?"): good.append("pregunta abierta en el título")
    front = [w for w in words(t)[:3] if w not in STOP]
    if not front: issues.append(("frente", "las tres primeras palabras son relleno: traé el tema adelante"))
    if clave:
        need = [w for w in words(clave) if w not in STOP]
        have = {stem(w) for w in words(t)}
        miss = [w for w in need if stem(w) not in have]
        if miss:
            issues.append(("clave", f"a la búsqueda \"{clave}\" le faltan en el título: {', '.join(miss)}"))
        else:
            head_words = {stem(w) for w in words(t[:MOBILE])}
            late = [w for w in need if stem(w) not in head_words]
            if late:
                issues.append(("clave-tarde", f"{', '.join(late)} queda(n) después del corte del celular: adelantalo"))
            else:
                good.append(f"la búsqueda \"{clave}\" entra completa antes del corte del celular")
    if thumb:
        tw = {stem(w) for w in words(t) if w not in STOP}
        hw = {stem(w) for w in words(thumb) if w not in STOP}
        shared = tw & hw
        if shared:
            surface = {stem(plain(w)): w for w in re.findall(r"[\wñ']+", t.lower())}
            shared = {surface.get(w, w) for w in shared}
            issues.append(("duplicado", f"la miniatura repite el título en: {', '.join(sorted(shared))}. "
                                        "La miniatura tiene que decir lo que el título no dice"))
        else:
            good.append("miniatura y título usan palabras distintas")
        if len(words(thumb)) > 4:
            issues.append(("miniatura-larga", f"{len(words(thumb))} palabras en la miniatura: tres es el techo a tamaño de feed"))
    score = max(0, min(100, 100 - 14 * len(issues) + 4 * len(good)))
    return {"titulo": t, "caracteres": n, "puntaje": score, "problemas": issues, "bien": good}

def show(r):
    print(f'\n  "{r["titulo"]}"')
    print(f"  {r['caracteres']} caracteres   puntaje {r['puntaje']}/100")
    for k, m in r["problemas"]: print(f"    x  {k:<15} {m}")
    for m in r["bien"]:         print(f"    ok                 {m}")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    thumb = a[a.index("--thumb") + 1] if "--thumb" in a else None
    clave = a[a.index("--clave") + 1] if "--clave" in a else None
    if "--title" in a:
        rows = [check(a[a.index("--title") + 1], thumb, clave)]
    elif a and os.path.exists(a[0]):
        with open(a[0], encoding="utf-8", errors="replace") as fh:
            rows = [check(l, thumb, clave) for l in fh.read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1)
    rows.sort(key=lambda r: -r["puntaje"])
    if as_json: print(json.dumps(rows, indent=1, ensure_ascii=False)); return
    for r in rows: show(r)
    print()

if __name__ == "__main__":
    main()
