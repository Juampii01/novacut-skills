#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
swipe.py - ordena los posts que juntaste según cuánto le ganó cada uno a su
propia cuenta, desarma cada uno en gancho, estructura y formato, y escribe el
archivo de referencias del que después escribe el resto del pack.

La única corrección para la que existe este script: los números crudos no son
evidencia. Una cuenta de 900.000 seguidores con 400.000 vistas tuvo un martes
normal. Una cuenta de 6.000 seguidores con 400.000 vistas encontró algo, y ese
algo se puede copiar. Así que todo se ordena por el MÚLTIPLO SOBRE LO NORMAL:
las vistas de un post divididas por la mediana de su propia cuenta.

La mediana sale de las filas mismas, así que juntá los últimos 10-15 posts de
cada cuenta EN ORDEN, incluidos los aburridos. Elegir solo los éxitos infla la
mediana y esconde justo los casos fuera de serie que viniste a buscar. Las
cuentas con menos de --min-posts filas se saltean en vez de rankearse con
ruido. Si ya sabés las vistas típicas de una cuenta, ponelas en una columna
`mediana` y gana esa.

La métrica son las vistas cuando la fila las tiene (son públicas en cada
post). Una fila sin vistas usa los likes, y la salida lo dice.

La entrada es el TSV que escribe pull.py, con los números completados por vos
(también acepta los encabezados en inglés):

    url  cuenta  nombre  fecha  formato  lineas  palabras  vistas  likes  respuestas  reposts  gancho  texto

Uso
  python3 swipe.py swipe.tsv
  python3 swipe.py swipe.tsv --out ~/.claude/novacut/x-swipe.md
  python3 swipe.py swipe.tsv --min-posts 4 --json
"""

import argparse
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "nc-x-post"))
try:
    import hookscore                                    # noqa: E402
    HOOKS = {h["id"]: h for h in json.load(open(os.path.join(HERE, "..", "nc-x-post", "hooks.json"),
                                                  encoding="utf-8"))["hooks"]}
except Exception:                                       # nc-x-viral copiada sola
    hookscore, HOOKS = None, {}

LIST_LINE = re.compile(r"^\s*(?:\d{1,2}[.)]|[-•*→>]|[\U0001F300-\U0001FAFF✅➡✔])\s*\S")


# Encabezados en español (los de pull.py) -> nombres internos.
ALIASES = {"cuenta": "account", "nombre": "name", "fecha": "date", "formato": "format",
           "lineas": "lines", "líneas": "lines", "palabras": "words", "vistas": "views",
           "respuestas": "replies", "gancho": "hook", "texto": "text", "mediana": "median",
           "seguidores": "followers", "me gusta": "likes"}
FORMATS = {"texto": "texto", "text": "texto", "media": "media", "link": "link", "largo": "largo",
           "long": "largo", "hilo": "hilo", "thread": "hilo"}


def num(v):
    """'12.400', '12,4k', '1.2M', '3 mil' -> entero."""
    v = (v or "").strip().lower().replace(" mil", "k").replace(" ", "")
    m = re.match(r"^(\d+(?:[.,]\d+)*)([km]?)$", v)
    if not m:
        return None
    digits, unit = m.group(1), m.group(2)
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", digits) and not unit:
        digits = re.sub(r"[.,]", "", digits)               # 12.400 o 12,400
    else:
        digits = digits.replace(",", ".")                  # 12,4k
        if digits.count(".") > 1:
            digits = digits.replace(".", "", digits.count(".") - 1)
    n = float(digits) * {"": 1, "k": 1e3, "m": 1e6}[unit]
    return int(n)


def read_rows(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    lines = [l for l in raw.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        return []
    cols = [ALIASES.get(c.strip().lower(), c.strip().lower()) for c in lines[0].split("\t")]
    rows = []
    for line in lines[1:]:
        cells = line.split("\t") + [""] * len(cols)
        r = dict(zip(cols, (c.strip() for c in cells)))
        r["text"] = (r.get("text") or r.get("hook") or "").replace(" ⏎ ", "\n").replace("⏎", "\n")
        for k in ("views", "likes", "replies", "reposts", "median", "followers"):
            r[k] = num(r.get(k))
        r["metric_name"] = "views" if r["views"] else ("likes" if r["likes"] else None)
        r["metric"] = r["views"] or r["likes"]
        if r["metric"] and (r.get("hook") or r["text"]):
            rows.append(r)
    return rows


def hook_of(r):
    hook = (r.get("hook") or "").strip()
    if not hook:
        hook = next((l.strip() for l in r["text"].splitlines() if l.strip()), "")
    if len(hook) > 140:                        # un párrafo largo: el gancho es su primera frase
        m = re.match(r"(.+?[.!?])(?:\s|$)", hook)
        if m:
            hook = m.group(1)
    return hook


def structure_of(r):
    lines = [l for l in r["text"].splitlines() if l.strip()]
    listy = sum(1 for l in lines if LIST_LINE.match(l))
    fmt = FORMATS.get((r.get("format") or "").lower(), (r.get("format") or "").lower())
    if fmt == "hilo":
        return "hilo"
    if fmt == "largo" or len(r["text"]) > 280:
        return "post largo"
    if listy >= 3:
        return f"lista ({listy} ítems)"
    if len(lines) <= 1:
        return "una línea" if len(r["text"].split()) <= 20 else "un párrafo"
    return f"{len(lines)} líneas cortas"


def analyse(rows, min_posts):
    by_acct = {}
    for r in rows:
        by_acct.setdefault(r.get("account", "?"), []).append(r)
    ranked, skipped = [], []
    for acct, items in by_acct.items():
        explicit = [r["median"] for r in items if r.get("median")]
        if explicit:
            base = explicit[0]
        elif len(items) >= min_posts:
            # mediana dentro de la métrica que tiene cada fila
            base = None
        else:
            skipped.append((acct, len(items)))
            continue
        for r in items:
            b = base
            if b is None:
                same = [x["metric"] for x in items if x["metric_name"] == r["metric_name"]]
                if len(same) < min_posts:
                    skipped.append((acct + f" ({r['metric_name']})", len(same)))
                    continue
                b = statistics.median(same)
            r["baseline"] = b
            r["outlier"] = round(r["metric"] / b, 2) if b else None
            r["hook_line"] = hook_of(r)
            if hookscore:
                p = hookscore.score_payload(r["hook_line"])
                r["formula_id"], r["formula"] = p["formula_id"], p["formula"]
                r["hook_score"] = p["score"]
            else:
                r["formula_id"], r["formula"], r["hook_score"] = None, "sin clasificar", None
            r["structure"] = structure_of(r)
            r["format"] = FORMATS.get((r.get("format") or "texto").lower(), r.get("format") or "texto")
            r["reply_ratio"] = (round(r["replies"] / r["likes"], 3)
                                if r.get("replies") is not None and r.get("likes") else None)
            ranked.append(r)
    ranked.sort(key=lambda r: -(r["outlier"] or 0))
    third = max(1, len(ranked) // 3)
    top, bottom = ranked[:third], ranked[-third:]

    def tally(items, key):
        out = {}
        for r in items:
            out[r[key]] = out.get(r[key], 0) + 1
        return sorted(out.items(), key=lambda kv: -kv[1])

    def med(items, f, digits=1):
        vals = [f(r) for r in items if f(r) is not None]
        return round(statistics.median(vals), digits) if vals else None

    words = lambda r: len(r["hook_line"].split())
    return {
        "n": len(ranked),
        "accounts": len({r.get("account") for r in ranked}),
        "metrics": sorted({r["metric_name"] for r in ranked}),
        "posts": ranked,
        "skipped": skipped,
        "top": {"formulas": tally(top, "formula"), "formats": tally(top, "format"),
                "structures": tally(top, "structure"), "hook_words": med(top, words),
                "reply_ratio": med(top, lambda r: r["reply_ratio"], 3)},
        "bottom": {"formulas": tally(bottom, "formula"), "formats": tally(bottom, "format"),
                   "structures": tally(bottom, "structure"), "hook_words": med(bottom, words),
                   "reply_ratio": med(bottom, lambda r: r["reply_ratio"], 3)},
        "unclassified": [r["hook_line"] for r in ranked if r["formula"] == "sin clasificar"],
    }


def fmt_tally(t, k=3):
    return ", ".join(f"{name} x{c}" for name, c in t[:k]) or "-"


def render(a, out=sys.stdout):
    metric = "/".join({"views": "vistas", "likes": "likes"}.get(m, m) for m in a["metrics"])
    head = (f"REFERENCIAS  ·  {a['n']} posts  ·  {a['accounts']} cuentas  ·  "
            f"múltiplo sobre la mediana de {metric} de cada cuenta")
    print("\n" + head, file=out)
    print("=" * max(len(head), 78), file=out)
    for r in a["posts"]:
        mult = f"{r['outlier']:.1f}x" if r["outlier"] else "  ?"
        fid = f"#{r['formula_id']:<2}" if r["formula_id"] else "-  "
        print(f"  {mult:>6}  {fid} {r['formula'][:20]:<20} {r['structure'][:15]:<15} "
              f"{r['format']:<6} {r.get('account', '')[:16]:<16} {r['metric']:>9,} "
              f"{ {'views': 'vistas'}.get(r['metric_name'], r['metric_name']) }".replace(",", "."),
              file=out)
        hook = r["hook_line"] if len(r["hook_line"]) <= 92 else r["hook_line"][:89] + "..."
        print(f"          \"{hook}\"", file=out)
    print("-" * max(len(head), 78), file=out)
    t, b = a["top"], a["bottom"]
    print("TERCIO DE ARRIBA vs TERCIO DE ABAJO", file=out)
    print(f"  gancho     arriba: {fmt_tally(t['formulas'])}", file=out)
    print(f"             abajo: {fmt_tally(b['formulas'])}", file=out)
    print(f"  estructura arriba: {fmt_tally(t['structures'])}   abajo: {fmt_tally(b['structures'])}", file=out)
    print(f"  formato    arriba: {fmt_tally(t['formats'])}   abajo: {fmt_tally(b['formats'])}", file=out)
    print(f"  palabras del gancho  arriba: {t['hook_words']}   abajo: {b['hook_words']}", file=out)
    if t["reply_ratio"] is not None and b["reply_ratio"] is not None:
        print(f"  respuestas por like  arriba: {t['reply_ratio']}   abajo: {b['reply_ratio']}", file=out)
    if a["unclassified"]:
        print(f"\n  SIN CLASIFICAR ({len(a['unclassified'])}). Leelos a mano. O son ruido, o son una "
              "fórmula que hooks.json todavía no tiene:", file=out)
        for h in a["unclassified"][:8]:
            print(f"    \"{h[:90]}\"", file=out)
    if a["skipped"]:
        print("\n  SALTEADAS (muy pocos posts para saber lo normal de la cuenta): "
              + ", ".join(f"{acct} ({n})" for acct, n in a["skipped"]), file=out)
    print(f"\n  {a['n']} posts es {'una muestra que vale la pena leer' if a['n'] >= 40 else 'una primera mirada, no un hallazgo'}."
          " Cuarenta en seis cuentas te muestra algo; doce no te muestra nada.\n", file=out)


def to_markdown(a):
    lines = ["# Archivo de referencias (X)", "",
             f"{a['n']} posts de {a['accounts']} cuentas, ordenados por múltiplo sobre la mediana de "
             "cada cuenta. Copiá la forma, nunca las palabras.", ""]
    for r in a["posts"]:
        mult = f"{r['outlier']:.1f}x" if r["outlier"] else "?"
        h = HOOKS.get(r["formula_id"], {})
        lines += [f"## {mult}  {r['formula']}  ·  {r.get('account', '')}",
                  f"- { {'views': 'vistas'}.get(r['metric_name'], r['metric_name']) }: {r['metric']:,}  (mediana de la cuenta {r['baseline']:,.0f})".replace(",", "."),
                  f"- gancho: \"{r['hook_line']}\"",
                  f"- estructura: {r['structure']}  ·  formato: {r['format']}",
                  f"- fuente: {r.get('url', '')}"]
        if h:
            lines.append(f"- forma para reusar: {h['template']}")
        lines += ["- tu versión: ", ""]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Ordena posts de X juntados por múltiplo sobre lo normal.")
    ap.add_argument("input", nargs="?", default="-", help="TSV de pull.py, o - para stdin")
    ap.add_argument("--min-posts", type=int, default=5,
                    help="posts necesarios por cuenta para confiar en su mediana (por defecto 5)")
    ap.add_argument("--out", help="además escribe el archivo de referencias en markdown acá")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = read_rows(args.input)
    if not rows:
        print("no hay filas usables. Completá primero la columna de vistas (o likes).", file=sys.stderr)
        sys.exit(2)
    a = analyse(rows, args.min_posts)
    if not a["posts"]:
        print(f"todas las cuentas tienen menos de {args.min_posts} posts. Juntá los últimos 10-15 posts "
              "de cada cuenta, en orden, y corrélo de nuevo.", file=sys.stderr)
        sys.exit(2)
    if hookscore is None:
        print("nota: no encontré ../nc-x-post/hookscore.py, las fórmulas quedan sin nombre.", file=sys.stderr)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False, default=str))
    else:
        render(a)
    if args.out:
        path = os.path.expanduser(args.out)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(to_markdown(a))
        print(f"escrito: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
