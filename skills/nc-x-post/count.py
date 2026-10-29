#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
count.py - cuenta un post como lo cuenta X y revisa las seis cosas que vale
la pena revisar antes de publicar.

X no cuenta caracteres. Cuenta caracteres PONDERADOS, con las reglas de su
librería abierta twitter-text (config v3):

  - cada link vale 23, sea del largo que sea, porque X lo envuelve en t.co
  - cada emoji vale 2, incluidos los que se arman con varios puntos de código
    (una familia, una bandera, un tono de piel), que si no contarían 4 a 11
  - el alfabeto latino (con tildes, ñ, ¿ y ¡), griego, cirílico, árabe, hebreo,
    devanagari y casi toda la puntuación general valen 1. Eso incluye la raya
    larga y las comillas curvas.
  - todo lo demás vale 2: chino, japonés, coreano, la mayoría de los símbolos,
    y el carácter "…", que cuesta más que los tres puntos que reemplaza
  - antes se normaliza el texto a NFC

Una cuenta normal tiene 280 caracteres ponderados. X Premium tiene 25.000,
pero el timeline muestra más o menos los primeros 280 y esconde el resto
detrás de "Mostrar más", así que un post largo igual vive o muere en sus
primeros 280. (Límites de X a 2026; pueden cambiar.)

La detección de links es aproximada: los que tienen http(s):// cuentan siempre,
los dominios sueltos cuentan cuando terminan en un dominio común (.com, .ar,
.mx, .es, .co...). twitter-text conoce todos; este script, unos setenta. Si
escribís "herramienta.museum" sin https://, revisalo en el editor de X.

Uso
  python3 count.py post.txt
  python3 count.py post.txt --premium
  pbpaste | python3 count.py -
  python3 count.py post.txt --json
"""

import argparse
import json
import re
import sys
import textwrap
import unicodedata

LIMIT = 280
PREMIUM_LIMIT = 25000
FOLD = 280               # más o menos donde el timeline corta un post largo con "Mostrar más"
URL_WEIGHT = 23
HASHTAG_LIMIT = 1

# twitter-text v3: los puntos de código en estos rangos pesan 1, todo lo demás 2.
LIGHT_RANGES = [(0, 4351), (8192, 8205), (8208, 8223), (8242, 8247)]

_TLDS = ("com|net|org|io|ai|co|dev|app|me|xyz|gg|so|tv|us|uk|ca|de|fr|es|it|nl|se|no|au|nz|in|"
         "jp|ly|sh|to|fm|info|biz|edu|gov|news|blog|site|tech|studio|design|link|page|pro|"
         "store|shop|club|live|world|today|online|space|cloud|run|build|ink|is|am|be|cc|ws|"
         "ar|mx|cl|pe|uy|ec|bo|py|ve|gt|cr|do|pr|br|pt|com\\.ar|com\\.mx|lat|tienda|online")
URL_RE = re.compile(
    r"https?://[^\s<>\"]+"
    r"|(?<![@\w.-])(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:" + _TLDS + r")\b(?::\d+)?(?:/[^\s<>\"]*)?",
    re.IGNORECASE)
TRAILING = ".,!?:;)]}'\""

_PICTO = "\U0001F000-\U0001FAFF☀-➿⌀-⏿⬀-⯿←-⇿〰〽㊗㊙©®™ℹ"
_MOD = "\U0001F3FB-\U0001F3FF"
EMOJI_RE = re.compile(
    "[\U0001F1E6-\U0001F1FF]{2}"                                     # banderas
    "|[0-9#*]️?⃣"                                          # keycaps
    "|\U0001F3F4[\U000E0020-\U000E007E]+\U000E007F"                  # Inglaterra, etc.
    f"|[{_PICTO}]️?[{_MOD}]?(?:‍[{_PICTO}]️?[{_MOD}]?)*")

HASHTAG_RE = re.compile(r"(?:^|(?<=\s))#\w+")
MENTION_RE = re.compile(r"(?:^|(?<=[\s(]))@[A-Za-z0-9_]{1,15}\b")
BAIT_RE = re.compile(r"(?i)(?:qu[eé] opinan|qu[eé] opin[aá]s|qu[eé] piensan|est[aá]n de acuerdo|est[aá]s de acuerdo"
                     r"|me equivoco|qui[eé]n m[aá]s|alguien m[aá]s)\s*\?\s*$"
                     r"|\b(?:dale )?(?:rt|repost|retweet|like) si\b|\bsegu[ií]me para m[aá]s\b|\bs[ií]gueme para m[aá]s\b")
LABEL_RE = re.compile(r"(?i)^\s*(?:un\s+)?(?:(?:mega|mini|breve|corto|largo|nuevo)\s+)?(?:hilo|thread)\b|^\s*🧵")


def _light(cp):
    return any(a <= cp <= b for a, b in LIGHT_RANGES)


def find_urls(text):
    out = []
    for m in URL_RE.finditer(text):
        url = m.group(0).rstrip(TRAILING)
        out.append((m.start(), m.start() + len(url), url))
    return out


def weighted(text):
    """Devuelve (largo_ponderado, detalle, corte): corte es el índice del
    carácter donde el post pasa LIMIT por primera vez (None si entra)."""
    text = unicodedata.normalize("NFC", text)
    urls = find_urls(text)
    total, i, cut = 0, 0, None
    emoji_n, heavy = 0, []
    url_at = {a: (b, u) for a, b, u in urls}
    while i < len(text):
        if i in url_at:
            end, _ = url_at[i]
            total += URL_WEIGHT
            i = end
        else:
            m = EMOJI_RE.match(text, i)
            if m and m.end() > i:
                total += 2
                emoji_n += 1
                i = m.end()
            else:
                cp = ord(text[i])
                w = 1 if _light(cp) else 2
                if w == 2:
                    heavy.append(text[i])
                total += w
                i += 1
        if cut is None and total > LIMIT:
            cut = i - 1
    return total, {"urls": [u for _, _, u in urls], "emoji": emoji_n, "heavy": heavy}, cut


def visible_prefix(text, budget):
    """El prefijo más largo del texto que entra en `budget` caracteres ponderados."""
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if weighted(text[:mid])[0] <= budget:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]


def first_line(text):
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def analyse(text, premium=False):
    text = unicodedata.normalize("NFC", text.strip())
    limit = PREMIUM_LIMIT if premium else LIMIT
    total, detail, _ = weighted(text)
    checks = []

    def add(status, name, msg):
        checks.append({"status": status, "check": name, "detail": msg})

    over = total - limit
    if over > 0:
        add("FALLA", "LARGO", f"{total} / {limit}, sobran {over}. X no te deja publicarlo.")
    elif total > LIMIT:
        add("OJO", "LARGO", f"{total} / {limit} (post largo de Premium). El timeline muestra más o menos "
            f"los primeros {FOLD} y después \"Mostrar más\". Todo lo que importa va antes del corte.")
    else:
        add("OK", "LARGO", f"{total} / {limit}, quedan {limit - total}")

    hook = first_line(text)
    hw = weighted(hook)[0]
    if LABEL_RE.search(hook):
        add("OJO", "1ª LÍNEA", "arranca con \"hilo\". Eso es envoltorio, no un gancho. Arrancá con lo que prometés.")
    elif hw > 110:
        add("OJO", "1ª LÍNEA", f"{hw} caracteres. En el celular pasa a una tercera línea antes de que llegue la idea.")
    else:
        add("OK", "1ª LÍNEA", f"{hw} caracteres, se lee de un vistazo")

    urls = detail["urls"]
    if urls:
        in_hook = any(u in hook for u in urls)
        add("OJO" if in_hook else "NOTA", "LINKS",
            f"{len(urls)} link(s), {URL_WEIGHT} caracteres cada uno. "
            + ("Hay uno en la primera línea: le das al lector una salida antes de que el post llegue. "
               if in_hook else "")
            + "X dice que ya no castiga los posts con links (julio 2026). Un análisis independiente de "
              "enero 2026 todavía les midió menos vistas. Tu propio /nc-x-audit te dice cuál es verdad "
              "para tu cuenta.")
    else:
        add("OK", "LINKS", "ninguno")

    tags = HASHTAG_RE.findall(text)
    if len(tags) > HASHTAG_LIMIT:
        add("OJO", "HASHTAGS", f"{len(tags)}: {' '.join(tags[:5])}. Cada uno es un link para irse de tu "
            "propio post. Elon Musk, dic 2024: el sistema ya no los necesita. Dejá uno, o ninguno.")
    else:
        add("OK", "HASHTAGS", f"{len(tags)}" + (f": {tags[0]}" if tags else ""))

    mentions = MENTION_RE.findall(text)
    late = []
    if total > LIMIT and mentions:
        head = visible_prefix(text, LIMIT)
        late = [m for m in mentions if m not in head]
    if late:
        add("OJO", "MENCIONES", f"{' '.join(late)} está después del carácter {LIMIT}. X no notifica "
            "una mención tan adentro de un post largo. Subila si querés que la vean.")
    else:
        add("OK", "MENCIONES", f"{len(mentions)}")

    if BAIT_RE.search(text):
        add("OJO", "CIERRE", "termina en cebo reflejo (\"¿Qué opinan?\", \"dale RT si\"). Hacé una pregunta "
            "que solo este post podría hacer, o terminá en la última frase cierta.")
    else:
        add("OK", "CIERRE", "sin cebo reflejo")

    em = text.count("—")
    if em:
        add("OJO", "RAYA LARGA", f"{em}. Pasalo por /nc-x-human antes de que salga a algún lado.")

    return {
        "weighted": total,
        "limit": limit,
        "fits": total <= limit,
        "urls": urls,
        "emoji": detail["emoji"],
        "double_weight_chars": len(detail["heavy"]),
        "fold": visible_prefix(text, FOLD) if total > FOLD else None,
        "checks": checks,
    }


def render(text, a, out=sys.stdout, width=52):
    text = text.strip()
    print("\n  LO QUE ENTRA" if a["weighted"] > a["limit"] else "\n  LO QUE MUESTRA EL TIMELINE", file=out)
    print("  +" + "-" * (width + 2) + "+", file=out)
    shown = a["fold"] if a["fold"] is not None else text
    lines = []
    for raw in shown.split("\n"):
        lines.extend(textwrap.wrap(raw, width) or [""])
    for line in lines[:14]:
        print(f"  | {line:<{width}} |", file=out)
    if len(lines) > 14:
        print(f"  | {'...':<{width}} |", file=out)
    if a["weighted"] > a["limit"] or (a["limit"] == LIMIT and a["fold"] is not None):
        tail = f"corte acá, sobran {a['weighted'] - a['limit']}"
    elif a["fold"] is not None:
        tail = "Mostrar más"
    else:
        tail = f"{a['weighted']}/{a['limit']}"
    print("  +" + "-" * (width + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)
    extras = []
    if a["urls"]:
        extras.append(f"{len(a['urls'])} link(s) a {URL_WEIGHT}")
    if a["emoji"]:
        extras.append(f"{a['emoji']} emoji(s) a 2")
    if a["double_weight_chars"]:
        extras.append(f"{a['double_weight_chars']} carácter(es) más de peso doble")
    if extras:
        print("  contado como: " + ", ".join(extras), file=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {c['status']:<5} {c['check']:<11} {c['detail']}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Cuenta y revisa un post de X como lo cuenta X.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("--premium", action="store_true", help="usa el límite de 25.000 de Premium")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    if not raw.strip():
        print("no hay nada para contar", file=sys.stderr)
        sys.exit(2)
    a = analyse(raw, premium=args.premium)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(raw, a)
    sys.exit(0 if a["fits"] else 1)


if __name__ == "__main__":
    main()
