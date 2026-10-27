#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""retention.py - leé el export de retención de audiencia de YouTube Studio y encontrá las fugas.

    python3 retention.py retencion.csv --duration 600
    python3 retention.py retencion.csv --transcript transcripcion.srt   # dice qué decías en cada caída
    python3 retention.py retencion.csv --json
    python3 retention.py retencion.csv --segundos      # forzar el eje (o --porcentaje)

El archivo sale de YouTube Studio: el video -> Estadísticas -> Participación -> el gráfico de
retención de la audiencia -> el ícono de descarga (los nombres del menú pueden variar según el
idioma y la versión de Studio). Dos columnas: una posición (porcentaje del video o segundos) y el
porcentaje que sigue mirando. Acepta coma o punto decimal ("45,3" o "45.3"), separador coma, punto y
coma o tabulación, y posiciones en formato m:ss. El eje (porcentaje o segundos) se deduce del
encabezado; si no hay encabezado y el video dura menos de 100 segundos, forzalo con --segundos.

Informa tres cosas, porque son tres problemas distintos con tres arreglos distintos:
  FUGA DEL GANCHO   lo que perdiste en los primeros 30 segundos
  PRECIPICIOS       caídas bruscas puntuales: un momento concreto en el que la gente se fue
  GOTEO             la pérdida pareja a lo largo del medio

Con --transcript imprime qué estabas diciendo en cada precipicio, que es la única versión de este
informe sobre la que podés actuar sin revisar el video a mano.
"""
import csv, io, json, os, re, sys

def to_num(c):
    c = c.strip().replace("%", "").replace(" ", "").strip()
    if not c: return None
    m = re.fullmatch(r"(\d+):(\d{1,2})(?::(\d{1,2}))?", c)      # 1:30 o 0:01:30
    if m:
        p = [int(x) for x in m.groups() if x is not None]
        return float(p[0] * 60 + p[1]) if len(p) == 2 else float(p[0] * 3600 + p[1] * 60 + p[2])
    if re.fullmatch(r"-?\d+,\d+", c): c = c.replace(",", ".")    # coma decimal: 45,3
    else: c = c.replace(",", "")                                 # miles con coma: 1,200 / 45.3
    try: return float(c)
    except ValueError: return None

def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        text = fh.read()
    sample = "\n".join(text.splitlines()[:20])
    lines = [l for l in sample.splitlines() if l.strip()]
    # con coma decimal ("45,3") el separador suele ser ";": si está en todas las líneas, gana
    if lines and all("\t" in l for l in lines): delim = "\t"
    elif lines and all(";" in l for l in lines): delim = ";"
    else:
        try: delim = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
        except csv.Error: delim = ","
    rows, hint = [], None
    for r in csv.reader(io.StringIO(text), delimiter=delim):
        vals = [n for n in (to_num(c) for c in r) if n is not None]
        if len(vals) >= 2:
            rows.append((vals[0], vals[1]))
            if r and re.fullmatch(r"\s*\d+:\d{1,2}(:\d{1,2})?\s*", r[0]): hint = "segundos"
        elif not rows and r:
            # encabezado: "Posición del video (%)" vs "Tiempo (s)" / "segundos" / "seconds"
            h = r[0].lower()
            if "%" in h or "porcentaje" in h or "percent" in h: hint = "porcentaje"
            elif re.search(r"\(s\)|seg|sec|tiempo|time", h): hint = "segundos"
    # algunos exports dan la retención como fracción (0,45) y no como porcentaje (45)
    if rows and max(y for _, y in rows) <= 1.5:
        rows = [(x, y * 100) for x, y in rows]
    return rows, hint

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    tr = a[a.index("--transcript") + 1] if "--transcript" in a else None
    dur = float(a[a.index("--duration") + 1]) if "--duration" in a else None
    skip = {tr, str(a[a.index("--duration") + 1]) if "--duration" in a else None}
    files = [x for x in a if not x.startswith("--") and x not in skip]
    if not files or not os.path.exists(files[0]): print(__doc__); sys.exit(1)
    rows, hint = load_csv(files[0])
    if len(rows) < 8: print("no pude leer al menos 8 puntos de datos de ese csv"); sys.exit(1)
    xs = [r[0] for r in rows]; ys = [r[1] for r in rows]
    if "--segundos" in a: hint = "segundos"
    if "--porcentaje" in a: hint = "porcentaje"
    pct_axis = (hint == "porcentaje") if hint else max(xs) <= 100.5
    def at(x): return (x / 100.0 * dur) if (pct_axis and dur) else x
    start = ys[0] or 100.0
    # GANCHO: los primeros 30 segundos, o el primer 10% si el eje es porcentaje y no hay duración
    cutoff = 30.0 if not pct_axis else (30.0 / dur * 100 if dur else 10.0)
    hook_end = min((y for x, y in rows if x <= cutoff), default=start)
    hook_leak = start - hook_end
    drops = []
    for i in range(1, len(rows)):
        d = ys[i - 1] - ys[i]
        span = xs[i] - xs[i - 1] or 1
        drops.append((d / span, xs[i - 1], xs[i], d))
    drops.sort(reverse=True)
    cliffs = [{"desde": round(a1, 2), "hasta": round(b1, 2), "perdido": round(d, 2),
               "en_segundos": round(at(a1), 1) if (not pct_axis or dur) else None}
              for _, a1, b1, d in drops[:5] if d > 0.8]
    mid = [r[0] for r in drops if r[1] > cutoff]
    slide = sum(mid) / len(mid) if mid else 0
    said = {}
    if tr and os.path.exists(tr):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nc-yt-edit"))
        from deadair import load as load_cues
        cues = load_cues(tr)
        for c in cliffs:
            if c["en_segundos"] is None: continue
            t = c["en_segundos"]
            near = [q[2] for q in cues if q[0] <= t + 4 and q[1] >= t - 4]
            said[str(c["desde"])] = " ".join(near)[:140]
    out = {"puntos": len(rows), "inicio": start, "fuga_gancho": round(hook_leak, 2), "final": round(ys[-1], 2),
           "precipicios": cliffs, "goteo_por_unidad": round(slide, 3),
           "unidad_eje": "porcentaje" if pct_axis else "segundos", "dicho": said}
    if as_json: print(json.dumps(out, indent=1, ensure_ascii=False)); return
    print(f"\n  {files[0]}   {len(rows)} puntos   {ys[0]:.1f}% -> {ys[-1]:.1f}%\n")
    verdict = "sana" if hook_leak < 25 else "con fuga" if hook_leak < 40 else "grave"
    print(f"  FUGA DEL GANCHO   {hook_leak:.1f}% perdido en la apertura   [{verdict}]")
    print( "                    menos de 25 es sano. Arreglá la primera línea antes que cualquier otra cosa.\n")
    print( "  PRECIPICIOS       los momentos en que la gente se fue de verdad")
    for c in cliffs:
        where = f"{c['en_segundos']:.0f}s" if c["en_segundos"] is not None else f"{c['desde']}%"
        print(f"    -{c['perdido']:5.1f}%  en {where:>8}" + (f"   \"{said.get(str(c['desde']), '')}\"" if said else ""))
    if not cliffs: print("    ninguna caída mayor a 0,8%: la pérdida es goteo, no momentos")
    if pct_axis and not dur and cliffs:
        print("    (pasá --duration <segundos> para ver los tiempos en segundos y cruzarlos con la transcripción)")
    print(f"\n  GOTEO             {slide:.3f}% por {'cada 1% del video' if pct_axis else 'segundo'} en el medio")
    print( "                    un goteo parejo es ritmo, no contenido. Recortá el medio, no lo reescribas.\n")

if __name__ == "__main__":
    main()
