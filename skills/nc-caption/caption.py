#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
caption.py - revisa un caption de Instagram y te muestra exactamente lo que
se ve en el feed antes del "... más".

Instagram le da a un caption unos 125 caracteres en el feed y esconde el resto
detrás de un toque. Casi todos los captions que fallan, fallan ahí: el gancho
está en la tercera oración, la primera línea es un saludo, o todo arranca con
un hashtag. Esto imprime la ventana visible en una caja para que la leas como
la lee un desconocido que está scrolleando, y después revisa lo que vale la
pena revisar.

El corte en 125 caracteres es aproximado. El número real cambia según el
dispositivo, el tamaño de letra y dónde caen tus saltos de línea, por eso
conviene dejar margen en vez de un caption calculado para terminar justo en
125. Cambialo con --truncate si querés probar un corte más corto.

Uso
  python3 caption.py caption.txt
  python3 caption.py caption.txt --keywords "contratos para freelancers,precios de diseño"
  pbpaste | python3 caption.py -
  python3 caption.py caption.txt --json
"""

import argparse
import json
import re
import sys
import textwrap
import unicodedata

LIMIT = 2200             # Límite duro de Instagram para el caption.
TRUNCATE = 125           # Más o menos donde el feed corta con "... más".
HASHTAG_LIMIT = 5        # Tope de Instagram por post o reel desde el 18/12/2025
                         # (antes eran 30), anunciado por la cuenta @creators.
                         # Es un dato de plataforma: puede volver a cambiar.

HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")
MENTION_RE = re.compile(r"(?:^|\s)(@[\w.]+)")
LINK_RE = re.compile(r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|co|io|net|org|ai|app|ar|mx|es|cl|uy|pe|com\.ar|com\.mx|link|ly)/\S*",
                     re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")
# Algo concreto: plata, una cifra, un nombre propio que no abre oración
# (contando ¿ y ¡) o un número dicho en letras.
CONCRETE_RE = re.compile(
    r"(?:\$|€|(?i:usd|u\$s)\s?)\s?\d|\b\d[\d.,]*\b"
    r"|(?<!^)(?<![.!?¿¡]\s)(?<![¿¡\"“«\n])\b[A-ZÁÉÍÓÚÑ][a-záéíóúñü][A-Za-záéíóúñü]+\b"
    r"|(?i:\b(?:dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|quince|veinte|treinta|"
    r"cincuenta|cien|mil|millón|millones|dólares|pesos|lucas|por ciento)\b)",
    re.MULTILINE)

KEYWORD = r"[\"“«']?[A-ZÁÉÍÓÚÑ0-9]{2,}[\"”»']?(?![\wáéíóúñ])"
ASKS = [
    (re.compile(r"(?i:\b(?:coment[áa]|comenta|comenten|escrib[íi]|escribe|escriban|dej[áa]|deja|dejame|d[ée]jame|pon[ée]|pon)"
                r"(?:me)?\s+(?:(?:la palabra|abajo|ac[áa] abajo|en (?:los )?comentarios|en un comentario)\s+)?)" + KEYWORD),
     "comentar una palabra clave"),
    (re.compile(r"(?i)\b(?:mand[áa]me|m[áa]ndame|escrib[íi]me|escr[íi]beme|escribime|habl[áa]me|h[áa]blame)\b"
                r"(?:\s+(?:un|una|por|al)\b)?\s*(?:dm|md|mensaje|privado|whatsapp|wsp)?"),
     "mandar DM"),
    (re.compile(r"(?i)\bgu[áa]rd(?:[áa]|a)(?:lo|la|te|telo|tela|los|las)?\b(?!\s+(?:silencio|distancia|reposo))"),
     "guardar"),
    (re.compile(r"(?i)\bcompart[íi](?:lo|la)?\b|\bcomp[áa]rte(?:lo|la)\b|\bm[áa]nd[áa]?selo\b|\bmand[áa]selo\b|\benvi[áa]selo\b|\benv[íi]aselo\b|\bp[áa]s[áa]?selo\b"),
     "compartir"),
    (re.compile(r"(?i)\bs[ée]gu[íi]me\b|\bseguime\b|\bs[íi]gueme\b|\bsegu[íi]nos\b|\bs[íi]guenos\b|\bsegu[íi] (?:la cuenta|a @)|\bsigue (?:la cuenta|a @)"),
     "seguir"),
    (re.compile(r"(?i)\b(?:link|enlace) (?:en|de) (?:la |mi )?(?:bio|biograf[íi]a|perfil)\b"),
     "link en la bio"),
    (re.compile(r"(?i)\b(?:desliz[áa]|desliza|toc[áa]|toca|pas[áa]) (?:para|a la|hacia|el carrusel|las fotos)\b"),
     "deslizar o tocar"),
    (re.compile(r"(?i)\bcontame\b|\bcu[ée]ntame\b|\bdecime\b|\bd[íi]me\b|\b(?:qu[ée]|cu[áa]l) (?:har[íi]as|elegir[íi]as|eleg[íi]s|eliges|prefer[íi]s|prefieres|usar[íi]as)\b"
                r"|\bte (?:leo|espero) en (?:los )?comentarios\b"),
     "responder una pregunta"),
]

FILLER_TAGS = {"#viral", "#fyp", "#explore", "#explorepage", "#foryou", "#foryoupage",
               "#trending", "#instagood", "#love", "#follow", "#like4like", "#reels",
               "#reelsinstagram", "#viralreels", "#instadaily", "#parati", "#paratí",
               "#explorar", "#tendencia", "#tendencias", "#virales", "#megusta", "#amor",
               "#seguidores", "#followme", "#likeforlike", "#instamood", "#reelsviral",
               "#reelsvirales", "#viralvideo", "#fypシ", "#xyzbca", "#foryourpage"}


def fold(s):
    s = s.lower().replace("ñ", "\x00")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.replace("\x00", "ñ")


def visible_window(text, cut):
    """Lo que muestra el feed. Instagram corta en medio de la palabra, esto también."""
    flat = text.strip()
    return flat if len(flat) <= cut else flat[:cut]


def render_box(window, truncated, out=sys.stdout, width=52):
    print("\n  LO QUE MUESTRA EL FEED", file=out)
    print("  +" + "-" * (width + 2) + "+", file=out)
    lines = []
    for raw in window.split("\n"):
        lines.extend(textwrap.wrap(raw, width) or [""])
    for line in lines[:8]:
        print(f"  | {line:<{width}} |", file=out)
    tail = "... más" if truncated else "(entra entero)"
    print("  +" + "-" * (width + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)


def analyse(text, cut=TRUNCATE, keywords=None):
    text = text.rstrip()
    stripped = text.strip()
    chars = len(stripped)
    lines = [l for l in stripped.split("\n")]
    first_line = lines[0].strip() if lines else ""
    tags = HASHTAG_RE.findall(stripped)
    mentions = MENTION_RE.findall(stripped)
    links = LINK_RE.findall(stripped)
    emoji = EMOJI_RE.findall(stripped)
    window = visible_window(stripped, cut)
    truncated = chars > cut
    asks = [name for pattern, name in ASKS if pattern.search(stripped)]
    filler = [t for t in tags if t.lower() in FILLER_TAGS]
    keywords = [k.strip() for k in (keywords or []) if k.strip()]

    checks = []

    def add(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    add("LARGO", "MAL" if chars > LIMIT else "OK",
        f"{chars} / {LIMIT} caracteres" + (f", {chars - LIMIT} de más"
                                           if chars > LIMIT else ""))

    greeting = re.match(r"(?i)^\s*[¡!]?\s*(?:hola|holis|buenas|buen d[íi]a|buenos d[íi]as|hey|qu[ée] tal|bienvenid[oa]s?)\b",
                        first_line)
    if not first_line:
        add("PRIMERA LÍNEA", "MAL", "el caption arranca con una línea en blanco")
    elif first_line.startswith("#") or first_line.startswith("@"):
        add("PRIMERA LÍNEA", "MAL",
            "arranca con un hashtag o una mención, en el único lugar que vale una frase")
    elif EMOJI_RE.match(first_line):
        add("PRIMERA LÍNEA", "OJO", "arranca con un emoji; la primera palabra tiene que ser una palabra")
    elif greeting:
        add("PRIMERA LÍNEA", "OJO", "arranca con un saludo. Nadie entró al feed para que lo saluden")
    elif len(first_line) > cut:
        add("PRIMERA LÍNEA", "OJO",
            f"{len(first_line)} caracteres, así que se corta en {cut} a mitad de idea. "
            "Bien si el corte deja intriga, mal si corta una subordinada")
    else:
        add("PRIMERA LÍNEA", "OK", f"{len(first_line)} caracteres, entra entera")

    concrete = CONCRETE_RE.findall(window)
    add("GANCHO CONCRETO", "OK" if concrete else "OJO",
        f"{len(concrete)} número(s) o nombre(s) en la ventana visible"
        + ("" if concrete else " - nada chequeable antes del toque"))

    if len(tags) > HASHTAG_LIMIT:
        add("HASHTAGS", "MAL", f"{len(tags)} hashtags, más que el tope de {HASHTAG_LIMIT} de Instagram. "
                               "Los que pasan del quinto no cuentan y el bloque se ve viejo")
    elif len(tags) == HASHTAG_LIMIT and filler:
        add("HASHTAGS", "OJO", f"{len(tags)} hashtags, en el tope, y "
                               f"{len(filler)} genéricos. Usá los cinco en temas")
    elif filler:
        add("HASHTAGS", "OJO", f"{len(tags)} hashtags, {len(filler)} genéricos "
                               f"({', '.join(filler[:3])}). Esos no describen nada")
    else:
        add("HASHTAGS", "OK", f"{len(tags)} hashtag(s)" + (f": {' '.join(tags)}" if tags else ""))

    if not tags:
        add("UBICACIÓN TAGS", "OK", "no hay hashtags que ubicar")
    elif any(re.search(r"(?:^|\s)" + re.escape(t) + r"(?!\w)", window) for t in tags):
        add("UBICACIÓN TAGS", "OJO", "hay un hashtag dentro de la ventana visible, "
                                     "gastando espacio del feed en una etiqueta")
    else:
        add("UBICACIÓN TAGS", "OK", "los hashtags quedan abajo del corte")

    add("LINKS", "OJO" if links else "OK",
        f"{len(links)} link(s) en el caption, y en el caption no se puede hacer clic. "
        f"Llevalo a la bio o al DM" if links else "no hay links muertos en el texto")

    if len(asks) == 1:
        add("UN SOLO PEDIDO", "OK", f"un llamado a la acción: {asks[0]}")
    elif not asks:
        add("UN SOLO PEDIDO", "OJO", "no hay llamado a la acción. Decidí para qué es este post")
    else:
        add("UN SOLO PEDIDO", "OJO", f"{len(asks)} pedidos ({', '.join(asks)}). "
                                     "Dos pedidos es lo mismo que ninguno")

    density = len(emoji) * 100 / max(chars, 1)
    add("EMOJIS", "OJO" if density > 4 else "OK",
        f"{len(emoji)} emoji(s), {density:.1f} cada 100 caracteres"
        + (" - se lee como decoración" if density > 4 else ""))

    if keywords:
        low = fold(stripped)
        win = fold(window)
        found = [k for k in keywords if fold(k) in low]
        missing = [k for k in keywords if fold(k) not in low]
        in_window = [k for k in found if fold(k) in win]
        status = "OK" if not missing else ("OJO" if found else "MAL")
        add("BÚSQUEDA", status,
            f"{len(found)}/{len(keywords)} presentes"
            + (f", {len(in_window)} en la ventana visible" if found else "")
            + (f". Faltan: {', '.join(missing)}" if missing else ""))

    fails = sum(1 for c in checks if c["status"] == "MAL")
    warns = sum(1 for c in checks if c["status"] == "OJO")
    verdict = "CORREGIR" if fails else ("REVISAR" if warns else "LISTO")

    return {
        "characters": chars, "limit": LIMIT, "truncate_at": cut,
        "visible": window, "truncated": truncated,
        "first_line_chars": len(first_line),
        "hashtags": tags, "mentions": mentions, "links": links,
        "emoji": len(emoji), "asks": asks,
        "checks": checks, "verdict": verdict,
    }


def render(a, out=sys.stdout):
    head = (f"REVISIÓN DEL CAPTION  ·  {a['characters']} / {a['limit']} caracteres  ·  "
            f"{len(a['hashtags'])} hashtags  ·  {len(a['asks'])} pedido(s)")
    print("\n" + head, file=out)
    print("=" * max(len(head), 62), file=out)
    render_box(a["visible"], a["truncated"], out=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {c['status']:<4} {c['check']:<16} {c['detail']}", file=out)
    print("-" * max(len(head), 62), file=out)
    print(f"  VEREDICTO  {a['verdict']}\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Revisa un caption de Instagram.")
    ap.add_argument("input", nargs="?", default="-", help="archivo del caption, o - para stdin")
    ap.add_argument("--truncate", type=int, default=TRUNCATE,
                    help=f"caracteres visibles antes del '... más' (default {TRUNCATE})")
    ap.add_argument("--keywords", default="", help="términos separados por coma por los que querés que te encuentren")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, cut=args.truncate, keywords=args.keywords.split(","))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0 if a["verdict"] == "LISTO" else 1)


if __name__ == "__main__":
    main()
