#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""deadair.py - una lista de cortes (EDL) a partir de una transcripción con tiempos.

    python3 deadair.py transcripcion.srt            # o .vtt, o .json de whisper
    python3 deadair.py transcripcion.srt --floor 0.35 --json

Encuentra tres cosas y las imprime como una lista de cortes en orden de aparición:
  SILENCIO  huecos entre frases más largos que el piso (--floor, en segundos)
  RELLENO   subtítulos que son solo relleno ("eh", "este...", "o sea", "bueno, nada")
  RETOMA    una frase que se arrancó de nuevo (la primera toma se corta), o una marca
            explícita de retoma ("perdón, arranco de nuevo", "lo digo de nuevo")

Además cuenta las muletillas que quedan DENTRO de las frases ("o sea", "digamos", "tipo,"...).
Esas no se cortan solas: es información para que el editor decida.

LO QUE NO HACE. No corta el archivo. Imprime una EDL, el total que sacaría y la duración con la
que quedarías, y vos la aplicás en el editor que uses. Nada de esto toca archivos de video o audio.
"""
import json, os, re, sys, unicodedata

def plain(t):
    """minúsculas, sin tildes y sin letras estiradas de 3+ ("esteee" -> "este", "mmm" -> "m").
    Solo colapsa 3 o más: "rr", "ll" y "cc" son españoles y tienen que sobrevivir."""
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"([a-z])\1{2,}", r"\1", t)

# Palabras y frases que, solas, no dicen nada. Se comparan contra plain(), sin tildes ni estiramientos.
HESIT = r"(e+h+m*|e+m+|m+|a+h+)"   # eh, ehh, ehm, em, emm, mm, ah
FILLERS = [HESIT, r"aj[aá]?", r"es+te+", r"o+ sea+", r"bue+no+", r"digamos", r"tipo",
           r"nada+", r"viste", r"ok", r"okey", r"dale", r"entonces+", r"a ver", r"ya", r"bah",
           r"pues", r"vale", r"listo", r"en fin", r"como que", r"que se yo", r"no se", r"perdon",
           r"bueno nada", r"y nada", r"y bueno", r"esto", r"mira", r"fijate"]
_SEP = r"[\s,.;:¿?¡!…\-]*"
FILLER_ONLY_RE = re.compile(r"^" + _SEP + r"((" + "|".join(FILLERS) + r")\b" + _SEP + r")+$")

def is_filler(t):
    return bool(t.strip()) and bool(FILLER_ONLY_RE.match(plain(t)))

# Marcas habladas de retoma: quien graba avisa que vuelve a decir algo.
RETAKE_MARK = re.compile(r"\b(arranco de nuevo|empiezo de nuevo|vuelvo a empezar|lo digo de nuevo|"
                         r"lo repito|lo vuelvo a decir|me equivoque|de nuevo,? de nuevo|"
                         r"perdon,? (arranco|empiezo|lo digo|de nuevo|otra vez)|"
                         r"corto,? (y )?(arranco|empiezo|vuelvo)|va de nuevo|otra toma|repito)\b")

# Muletillas dentro de frases con contenido: se cuentan, no se cortan.
MULETILLAS = [("eh / em / mmm", re.compile(r"\b" + HESIT + r"\b")),
              ("o sea", re.compile(r"\bo sea\b")),
              ("digamos", re.compile(r"\bdigamos\b")),
              ("viste", re.compile(r"\bviste\b")),
              ("este (pausa)", re.compile(r"\bes+te+\s*(,|\.\.\.|…)|\bestee+\b")),
              ("tipo (muletilla)", re.compile(r"(,\s*tipo\b|\btipo\s*,)")),
              ("bueno (al arrancar)", re.compile(r"(^|[.?!]\s*)bueno\s*,")),
              ("como que", re.compile(r"\bcomo que\b"))]

def parse_ts(s):
    s = s.strip().replace(",", ".")
    p = s.split(":")
    return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2]) if len(p) == 3 else int(p[0]) * 60 + float(p[1])

def load(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        raw = fh.read()
    if path.endswith(".json"):
        d = json.loads(raw)
        segs = d.get("segments", []) if isinstance(d, dict) else d
        return [(float(s["start"]), float(s["end"]), (s.get("text") or "").strip()) for s in segs]
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", line)
        if m:
            cur = [parse_ts(m.group(1)), parse_ts(m.group(2)), []]
            cues.append(cur)
        elif cur is not None and line.strip() and not line.strip().isdigit():
            cur[2].append(re.sub(r"<[^>]+>", "", line.strip()))   # saca etiquetas de estilo de .vtt
    return [(a, b, " ".join(t)) for a, b, t in cues if t]

LEAD = {"este", "bueno", "entonces", "y", "o", "sea", "a", "ver", "nada",
        "mira", "dale", "ok", "okey", "pues"}

def norm(t):
    """palabras para comparar retomas: sin tildes, sin puntuación y sin el relleno del arranque."""
    w = [x for x in re.sub(r"[^a-zñ ]", " ", plain(t)).split() if not re.fullmatch(HESIT, x)]
    while w and w[0] in LEAD: w = w[1:]
    return w

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    floor = float(a[a.index("--floor") + 1]) if "--floor" in a else 0.45
    a = [x for x in a if not x.startswith("--") and not re.match(r"^[\d.]+$", x)]
    if not a or not os.path.exists(a[0]): print(__doc__); sys.exit(1)
    cues = load(a[0])
    if not cues: print("no encontré subtítulos: ¿es un .srt, .vtt o .json de whisper?"); sys.exit(1)
    dur = cues[-1][1]
    cuts, mule = [], {}
    for i, (s, e, t) in enumerate(cues):
        filler = is_filler(t)
        if filler:
            cuts.append({"tipo": "RELLENO", "inicio": s, "fin": e, "motivo": t.strip()[:48]})
        elif RETAKE_MARK.search(plain(t)):
            cuts.append({"tipo": "RETOMA", "inicio": s, "fin": e, "motivo": f'marca de retoma: "{t.strip()[:40]}"'})
        else:
            for name, rx in MULETILLAS:
                n = len(rx.findall(plain(t)))
                if n: mule[name] = mule.get(name, 0) + n
        if i:
            gap = s - cues[i - 1][1]
            if gap > floor:
                keep = floor / 2   # se recorta del MEDIO: los dos lados conservan un respiro
                cuts.append({"tipo": "SILENCIO", "inicio": round(cues[i - 1][1] + keep, 3),
                             "fin": round(s - keep, 3), "motivo": f"hueco de {gap:.2f}s"})
        # Una retoma se compara contra el último subtítulo que fue HABLA de verdad. Comparar contra el
        # anterior literal se pierde toda retoma con un "eh" en el medio, que son casi todas.
        if t.strip() and not filler:
            j = i - 1
            while j >= 0 and (is_filler(cues[j][2]) or RETAKE_MARK.search(plain(cues[j][2]))
                              or not cues[j][2].strip()):
                j -= 1
            if j >= 0:
                a1, b1 = norm(cues[j][2]), norm(t)
                k = min(5, len(a1), len(b1))
                if k >= 3 and a1[:k] == b1[:k]:
                    cuts.append({"tipo": "RETOMA", "inicio": cues[j][0], "fin": cues[j][1],
                                 "motivo": f'arranca de nuevo con "{" ".join(a1[:k])}"'})
    cuts = [c for c in cuts if c["fin"] > c["inicio"]]
    cuts.sort(key=lambda c: c["inicio"])
    # dos cortes que se pisan no restan dos veces
    removed, last = 0.0, -1.0
    for c in cuts:
        st = max(c["inicio"], last)
        if c["fin"] > st: removed += c["fin"] - st
        last = max(last, c["fin"])
    if as_json:
        print(json.dumps({"fuente": a[0], "duracion": dur, "cortes": cuts, "muletillas": mule,
                          "quitado": round(removed, 3), "queda": round(dur - removed, 3)},
                         indent=1, ensure_ascii=False)); return
    print(f"\n  {a[0]}   {dur:.2f}s de entrada, {len(cues)} subtítulos, piso de silencio {floor}s\n")
    for c in cuts:
        print(f"    {c['tipo']:<8} {c['inicio']:8.2f} -> {c['fin']:8.2f}   {c['fin']-c['inicio']:5.2f}s   {c['motivo']}")
    print(f"\n  {len(cuts)} cortes, {removed:.2f}s fuera, quedan {dur - removed:.2f}s "
          f"({removed / dur * 100:.1f}% más corto)")
    if mule:
        print("\n  muletillas dentro de frases (no se cortan solas, revisalas en la edición)")
        for name, n in sorted(mule.items(), key=lambda x: -x[1]):
            print(f"    {n:3d}x  {name}")
    print()

if __name__ == "__main__":
    main()
