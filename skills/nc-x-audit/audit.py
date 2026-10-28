#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
audit.py - lee tu propia exportación de estadísticas de X y dice qué funcionó
de verdad, con el tamaño de la muestra pegado a cada afirmación.

La única fuente honesta de lo que funciona para una cuenta es esa cuenta. Cada
regla de cada guía de X, incluidas las de este pack, es una suposición previa.
Tus últimos 30 posts son la evidencia.

Entrada: el CSV de Estadísticas de la cuenta -> Exportar
(x.com/i/account_analytics, función de Premium), la exportación vieja de
analytics.twitter.com, o una planilla armada a mano. Las columnas se reconocen
de forma flexible, en inglés o en español: "Impressions", "Impresiones" y
"Post impressions" sirven igual. Lo mínimo es el texto del post más las
impresiones, más al menos uno de likes / respuestas / reposts / interacciones.

Qué calcula por post, y por qué no las impresiones a secas: las impresiones
dependen sobre todo de cuánta gente ya te sigue. Esto no.

  tasa de interacción   interacciones / impresiones
  respuestas cada 1k    respuestas cada 1.000 impresiones. La señal de charla.
  compartidos cada 1k   reposts + compartidos cada 1.000. La señal de viaje.
  guardados cada 1k     la señal de "esto lo voy a usar"
  follows cada 1k       si el post hizo que alguien quiera más de vos

Las respuestas que escribiste en posts de otros vienen en la misma exportación.
Se cuentan y se apartan, para que una buena semana respondiendo no tape los
posts.

Uso
  python3 audit.py account_analytics_content.csv
  python3 audit.py export.csv --min-impressions 200 --json
"""

import argparse
import csv
import json
import os
import re
import statistics
import sys
import unicodedata
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "nc-x-post"))
try:
    from hookscore import classify, first_line          # noqa: E402
except Exception:
    classify = None

    def first_line(t):
        return (t or "").strip().splitlines()[0] if (t or "").strip() else ""

FIELDS = {
    "text":        ["post text", "tweet text", "text", "content", "texto del post", "texto del tweet",
                    "texto", "contenido", "post"],
    "link":        ["post link", "tweet permalink", "permalink", "url", "link", "enlace del post",
                    "enlace", "vinculo"],
    "date":        ["date", "time", "created at", "created", "fecha", "hora", "fecha de creacion"],
    "impressions": ["impressions", "views", "impresiones", "visualizaciones", "vistas"],
    "engagements": ["engagements", "interacciones"],
    "likes":       ["likes", "favorites", "me gusta", "favoritos"],
    "replies":     ["replies", "respuestas"],
    "reposts":     ["reposts", "retweets", "republicaciones", "retuits"],
    "bookmarks":   ["bookmarks", "guardados", "elementos guardados"],
    "shares":      ["shares", "compartidos", "veces compartido"],
    "follows":     ["new follows", "follows", "nuevos seguidores", "seguidores nuevos"],
    "visits":      ["profile visits", "user profile clicks", "visitas al perfil"],
}
# Las exportaciones y planillas en español traen meses y días abreviados en
# español. Se pasan a inglés antes de leer la fecha.
ES_EN = {"ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr", "may": "May", "jun": "Jun",
         "jul": "Jul", "ago": "Aug", "sep": "Sep", "sept": "Sep", "set": "Sep", "oct": "Oct",
         "nov": "Nov", "dic": "Dec", "lun": "Mon", "mié": "Wed", "mie": "Wed", "jue": "Thu",
         "vie": "Fri", "sáb": "Sat", "sab": "Sat", "dom": "Sun"}
DIAS = {"Mon": "lun", "Tue": "mar", "Wed": "mié", "Thu": "jue", "Fri": "vie", "Sat": "sáb", "Sun": "dom"}
# En LATAM y España las planillas a mano usan día/mes/año, así que ese formato
# va antes que el mes/día de Estados Unidos.
DATE_FORMATS = ["%a, %b %d, %Y", "%Y-%m-%d %H:%M %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%d-%m-%Y",
                "%m/%d/%Y %H:%M", "%m/%d/%Y", "%b %d, %Y", "%d %b %Y", "%d %b, %Y", "%a %d %b %Y"]
TCO = re.compile(r"https?://t\.co/\S+|https?://\S+")


def _plain(h):
    h = unicodedata.normalize("NFKD", h.lower())
    h = "".join(c for c in h if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", h).strip()


def map_columns(header):
    norm = [_plain(h) for h in header]
    out = {}
    for field, names in FIELDS.items():
        for name in names:                 # exact first, then contains
            if name in norm:
                out[field] = norm.index(name)
                break
        else:
            for i, h in enumerate(norm):
                if any(h.startswith(n) or h.endswith(n) for n in names) and i not in out.values():
                    out[field] = i
                    break
    return out


def to_num(v):
    v = (v or "").strip().replace(" ", "")
    # "1.234" y "1,234" son mil doscientos treinta y cuatro; "3,5" es tres y medio.
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", v):
        v = re.sub(r"[.,]", "", v)
    else:
        v = v.replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


def parse_date(v):
    v = (v or "").strip()
    v = re.sub(r"(?i)\b(" + "|".join(sorted(ES_EN, key=len, reverse=True)) + r")\.?\b",
               lambda m: ES_EN[m.group(1).lower()], v)
    v = re.sub(r"\s+de\s+", " ", v)
    for f in DATE_FORMATS:
        try:
            return datetime.strptime(v, f)
        except ValueError:
            continue
    return None


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return [], {}
    cols = map_columns(rows[0])
    posts = []
    for raw in rows[1:]:
        get = lambda f: raw[cols[f]] if f in cols and cols[f] < len(raw) else ""
        p = {f: to_num(get(f)) for f in FIELDS if f not in ("text", "link", "date")}
        p["text"], p["link"], p["date"] = get("text"), get("link"), parse_date(get("date"))
        if p["impressions"]:
            posts.append(p)
    return posts, cols


def derive(p):
    imp = p["impressions"]
    parts = [p.get(k) or 0 for k in ("likes", "replies", "reposts", "bookmarks", "shares")]
    eng = p["engagements"] if p.get("engagements") is not None else sum(parts)
    p["er"] = eng / imp
    per1k = lambda v: (v or 0) * 1000 / imp
    p["replies_1k"] = per1k(p.get("replies"))
    p["shares_1k"] = per1k((p.get("reposts") or 0) + (p.get("shares") or 0))
    p["bookmarks_1k"] = per1k(p.get("bookmarks"))
    p["follows_1k"] = per1k(p.get("follows"))
    hook = first_line(p["text"])
    p["hook"] = hook
    p["formula"] = classify(hook)[1] if classify else "sin clasificar"
    body = TCO.sub("", p["text"]).strip()
    p["has_tco"] = "con link o imagen/video" if TCO.search(p["text"]) else "solo texto"
    n = len(body)
    p["length"] = ("menos de 100" if n < 100 else "100-199" if n < 200 else "200-280" if n <= 280
                   else "largo (280+)")
    p["weekday"] = DIAS.get(p["date"].strftime("%a")) if p["date"] else None
    return p


def groups(posts, key):
    out = {}
    for p in posts:
        k = p.get(key)
        if k is not None:
            out.setdefault(k, []).append(p)
    return out


def findings(posts, key, label):
    """Grupos cuya tasa de interacción media está lejos de la del resto."""
    res = []
    for k, items in groups(posts, key).items():
        rest = [p for p in posts if p.get(key) != k]
        if len(items) < 3 or len(rest) < 3:
            continue
        a, b = statistics.mean(p["er"] for p in items), statistics.mean(p["er"] for p in rest)
        if b == 0:
            continue
        ratio = a / b
        if ratio >= 1.4 or ratio <= 0.7:
            res.append({"dimension": label, "group": str(k), "n": len(items), "mean_er": a,
                        "rest_er": b, "ratio": ratio})
    if len(groups(posts, key)) == 2 and len(res) == 2:
        res = [max(res, key=lambda f: f["ratio"])]       # dos grupos son un hallazgo, no dos
    return res


def confidence(n):
    return "sólido" if n >= 10 else "moderado" if n >= 5 else "débil"


def pct(v):
    return f"{v * 100:.1f}%".replace(".", ",")


def main():
    ap = argparse.ArgumentParser(description="Audita una exportación de estadísticas de X.")
    ap.add_argument("input", help="CSV exportado")
    ap.add_argument("--min-impressions", type=int, default=None,
                    help="ignora posts con menos impresiones que esto al rankear (por defecto: percentil 10, mínimo 50)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows, cols = read(args.input)
    if not rows:
        print("no hay filas con impresiones. ¿Es la exportación de contenido (una fila por post)?", file=sys.stderr)
        sys.exit(2)
    missing = [f for f in ("text", "impressions") if f not in cols]
    if missing:
        print(f"no encontré la(s) columna(s): {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)

    rows = [derive(p) for p in rows]
    replies_out = [p for p in rows if p["text"].lstrip().startswith("@")]
    posts = [p for p in rows if not p["text"].lstrip().startswith("@")]
    if not posts:
        print("todas las filas son respuestas. No hay posts para auditar.", file=sys.stderr)
        sys.exit(2)
    imps = sorted(p["impressions"] for p in posts)
    floor = args.min_impressions if args.min_impressions is not None else max(
        50, imps[len(imps) // 10] if len(imps) >= 10 else 50)
    ranked = sorted([p for p in posts if p["impressions"] >= floor], key=lambda p: -p["er"])

    dims = [("formula", "fórmula de gancho"), ("length", "largo"), ("has_tco", "formato")]
    found = []
    for key, label in dims:
        found += findings(ranked, key, label)
    found.sort(key=lambda f: -abs(f["ratio"] - 1) * min(f["n"], 10))
    days = findings(ranked, "weekday", "día de la semana")

    dates = [p["date"] for p in posts if p["date"]]
    span = f"{min(dates):%d/%m} - {max(dates):%d/%m}" if dates else "fechas sin leer"

    if args.json:
        clean = lambda p: {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in p.items()}
        print(json.dumps({"posts": len(posts), "replies_set_aside": len(replies_out),
                          "floor": floor, "ranked": [clean(p) for p in ranked],
                          "findings": found, "day_of_week": days}, indent=2, default=str))
        return

    print(f"\nAUDITORÍA  ·  {len(posts)} posts  ·  {span}  ·  {len(replies_out)} respuestas apartadas")
    print("=" * 78)
    print("ordenado por tasa de interacción; los posts con menos de " + f"{floor:,.0f}".replace(",", ".")
          + " impresiones quedan afuera como ruido\n")

    def row(p):
        hook = p["hook"] if len(p["hook"]) <= 44 else p["hook"][:41] + "..."
        imp = f"{p['impressions']:,.0f}".replace(",", ".")
        return (f"  {pct(p['er']):>6}  {p['replies_1k']:5.1f} resp/1k  {p['shares_1k']:5.1f} comp/1k  "
                f"{imp:>8} imp  \"{hook}\"")

    k = min(5, max(1, len(ranked) // 3))
    print("ARRIBA POR TASA DE INTERACCIÓN")
    for p in ranked[:k]:
        print(row(p))
    print("\nABAJO")
    for p in ranked[-k:]:
        print(row(p))

    most_seen = max(posts, key=lambda p: p["impressions"])
    if ranked and most_seen is not ranked[0]:
        rank = next((i for i, p in enumerate(ranked, 1) if p is most_seen), None)
        where = f"#{rank} de {len(ranked)}" if rank else "debajo del piso de ruido"
        print(f"\n  Tu post más visto queda {where} por tasa de interacción. Alcance y resonancia no son "
              "el mismo número.")

    print("\nLO QUE DICEN LOS DATOS")
    if len(ranked) < 12:
        print(f"  {len(ranked)} posts son muy pocos para encontrar un patrón. Publicá 20 más y volvé a "
              "correrlo. Lo que salga abajo es una pista, no un hallazgo.")
    if not found:
        print("  Nada separa limpio. Ninguna fórmula de gancho, largo o grupo con link/imagen está 1,4x arriba "
              "o abajo del resto con 3 posts o más. Esa es una respuesta real: tu tema y tu primera línea "
              "pesan más que cualquier palanca de formato acá.")
    for i, f in enumerate(found[:4], 1):
        direction = "arriba" if f["ratio"] > 1 else "abajo"
        print(f"  {i}. {f['dimension']} = {f['group']}: {pct(f['mean_er'])} vs {pct(f['rest_er'])} del "
              f"resto ({f['ratio']:.1f}x, {direction}). n={f['n']}, {confidence(f['n'])}.")
    if days and not found:
        f = max(days, key=lambda d: abs(d["ratio"] - 1))
        print(f"  Día de la semana: {f['group']} a {f['ratio']:.1f}x, n={f['n']}. Se mira último a propósito. "
              "Casi nunca es la causa, y es donde la gente quiere que esté.")
    elif not days:
        print("  El día de la semana no muestra nada. Dejá de optimizarlo.")
    if replies_out:
        rimp = sum(p["impressions"] for p in replies_out)
        pimp = sum(p["impressions"] for p in posts)
        rtxt = f"{rimp:,.0f}".replace(",", ".")
        print(f"\n  Respuestas: {len(replies_out)} sumaron {rtxt} impresiones, "
              f"el {rimp / max(pimp, 1) * 100:.0f}% de lo que sumaron tus posts.")
    print("")


if __name__ == "__main__":
    main()
