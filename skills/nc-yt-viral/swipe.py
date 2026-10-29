#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""swipe.py - rankeá videos por cuánto le ganaron a SU PROPIO canal, y nombrá la fórmula.

    python3 swipe.py recolectados.json
    python3 swipe.py recolectados.json --min 2.0 --json

La entrada es una lista que juntaste vos, un objeto por video:

    [{"channel":"Un Canal","title":"...","views":412000,"url":"...","duration":613}, ...]

(también acepta las claves en español: "canal", "titulo", "vistas").

Las vistas en bruto rankean el tamaño del canal, no las ideas. Un video de 400 mil en un canal de 2
millones de suscriptores es un martes cualquiera; un video de 400 mil en un canal cuya mediana es 30
mil es lo que vale la pena estudiar. Por eso cada video se mide como MÚLTIPLO DE LA MEDIANA DE SU
CANAL, y para que eso signifique algo hacen falta al menos cuatro videos por canal. La herramienta
lo avisa en vez de rankear ruido en silencio.

La fórmula sale de ../nc-yt-script/hooks.json, comparada contra el TÍTULO. Es un juicio sobre las
palabras que se ven, no una explicación de por qué funcionó el video.
"""
import json, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "..", "nc-yt-script", "hooks.json"), encoding="utf-8") as _fh:
    FORMULAS = json.load(_fh)["hooks"]

def classify(title):
    scored = []
    for f in FORMULAS:
        n = sum(1 for p in f["match"] if re.search(p, title.strip(), re.I))
        if n: scored.append((n, -FORMULAS.index(f), f["name"]))
    scored.sort(reverse=True)
    return scored[0][2] if scored else "Sin clasificar"

def get(v, *keys, default=None):
    for k in keys:
        if k in v and v[k] not in (None, ""): return v[k]
    return default

def num(x):
    """vistas como número; tolera '412.000' y '412,000' (no entiende '1,2 M': pasalo entero)."""
    if isinstance(x, (int, float)): return float(x)
    d = re.sub(r"[^\d]", "", str(x or ""))
    return float(d) if d else 0.0

def miles(n): return f"{n:,}".replace(",", ".")

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    lo = float(a[a.index("--min") + 1]) if "--min" in a else 1.5
    files = [x for x in a if not x.startswith("--") and not re.match(r"^[\d.]+$", x)]
    if not files or not os.path.exists(files[0]): print(__doc__); sys.exit(1)
    with open(files[0], encoding="utf-8") as fh:
        rows = json.load(fh)
    if isinstance(rows, dict): rows = rows.get("videos", [])
    by = {}
    for r in rows: by.setdefault(get(r, "channel", "canal", default="?"), []).append(r)
    out, thin = [], []
    for ch, vids in by.items():
        views = [num(get(v, "views", "vistas", default=0)) for v in vids]
        med = statistics.median(views) if views else 0
        if len(vids) < 4:
            thin.append((ch, len(vids)))
            continue
        for v, vw in zip(vids, views):
            title = get(v, "title", "titulo", "título", default="")
            m = (vw / med) if med else 0
            out.append({"canal": ch, "titulo": title, "vistas": int(vw), "mediana": int(med),
                        "multiplo": round(m, 2), "formula": classify(title), "url": v.get("url", "")})
    out = [r for r in out if r["multiplo"] >= lo]
    out.sort(key=lambda r: -r["multiplo"])
    if as_json:
        print(json.dumps({"outliers": out, "canales_salteados": thin}, indent=1, ensure_ascii=False)); return
    print(f"\n  {len(rows)} videos de {len(by)} canales, outliers desde {lo}x\n")
    for r in out[:25]:
        print(f"    {r['multiplo']:5.2f}x  {miles(r['vistas']):>11}  vs {miles(r['mediana']):>11} de mediana   "
              f"{r['canal'][:22]:<22} {r['titulo'][:52]}")
        print(f"            {r['formula']}")
    if not out: print("    nada pasó el umbral: juntá más videos por canal o bajá --min")
    if thin:
        print(f"\n  salteé {len(thin)} canal(es) con menos de 4 videos: una mediana de uno o dos")
        print( "  videos no es una mediana: " + ", ".join(f"{c} ({n})" for c, n in thin[:6]))
    counts = {}
    for r in out: counts[r["formula"]] = counts.get(r["formula"], 0) + 1
    if counts:
        print("\n  fórmulas entre los outliers")
        for f, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {n:2d}x  {f}")
    print()

if __name__ == "__main__":
    main()
