#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
thread.py - corta un borrador largo en un hilo de X que entra, post por post,
y revisa los cinco lugares donde los hilos suelen fallar.

Nunca corta donde no hace falta. Los posts se separan primero en tus propios
separadores (una línea que es solo ---), después en párrafos, después en
frases. Solo una frase más larga que un post entero se parte entre palabras, y
cuando pasa se avisa, porque un post que arranca a mitad de frase parece un
error.

Cada post se mide como lo mide X (links 23, emojis 2, ver
../nc-x-post/count.py), así que "entra" acá quiere decir que entra en el editor.

Uso
  python3 thread.py borrador.txt
  python3 thread.py borrador.txt --number       # agrega 1/7, 2/7 ... (contado)
  python3 thread.py borrador.txt --pack         # junta párrafos cortos
  python3 thread.py borrador.txt --json
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "nc-x-post"))
try:
    from count import weighted, find_urls, LABEL_RE     # noqa: E402
except Exception:                                        # nc-x-thread copiada sola
    LABEL_RE = re.compile(r"(?i)^\s*(?:un\s+)?(?:hilo|thread)\b|^\s*🧵")

    def weighted(text):
        return len(text), {}, None

    def find_urls(text):
        return [(m.start(), m.end(), m.group(0))
                for m in re.finditer(r"https?://\S+", text)]

LIMIT = 280
SENT_RE = re.compile(r"[^.!?\n]+(?:[.!?]+[\"')\]]*|$)\s*")
SEP_RE = re.compile(r"(?m)^\s*-{3,}\s*$")
ASK_RE = re.compile(r"(?i)\?|\b(?:segu[ií]me|s[ií]gueme|guard[aá]|guarda|guardalo|compart[ií]|comparte|"
                    r"respond[eé]|responde|coment[aá]|comenta|escrib[ií]me|escr[ií]beme|mandame|m[aá]ndame|"
                    r"suscrib\w*|sumate|s[uú]mate|descarg\w*|baj[aá]|link (?:abajo|en la respuesta|ac[aá])|"
                    r"probalo|pru[eé]balo|robalo|r[oó]balo|pedime|p[ií]deme)\b")


def w(text):
    return weighted(text)[0]


def split_sentences(par):
    parts = [s.strip() for s in SENT_RE.findall(par) if s.strip()]
    return parts or [par.strip()]


def split_words(sentence, limit):
    out, cur = [], ""
    for word in sentence.split():
        trial = (cur + " " + word).strip()
        if w(trial) <= limit:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def fit(par, limit):
    """Un párrafo en la menor cantidad de posts que entren, cortando en frases.
    Devuelve [(texto, cortado_a_mitad_de_frase)]."""
    if w(par) <= limit:
        return [(par, False)]
    posts, cur = [], ""
    for sent in split_sentences(par):
        trial = (cur + " " + sent).strip()
        if w(trial) <= limit:
            cur = trial
            continue
        if cur:
            posts.append((cur, False))
            cur = ""
        if w(sent) <= limit:
            cur = sent
        else:
            pieces = split_words(sent, limit)
            posts += [(p, True) for p in pieces[:-1]]
            cur = pieces[-1]
    if cur:
        posts.append((cur, False))
    return posts


def build(text, limit=LIMIT, number=False, pack=False):
    text = text.strip()
    reserve = 7 if number else 0              # "\n\n12/15" son 7 caracteres ponderados
    budget = limit - reserve
    if SEP_RE.search(text):
        blocks = [b.strip() for b in SEP_RE.split(text) if b.strip()]
        explicit = True
    else:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        explicit = False
    posts = []
    for b in blocks:
        if explicit and w(b) <= budget:
            posts.append((b, False))
        else:
            posts += fit(b, budget)
    if pack and not explicit:
        merged = []
        for p, cut in posts:
            if merged and not cut and not merged[-1][1] and w(merged[-1][0] + "\n\n" + p) <= budget:
                merged[-1] = (merged[-1][0] + "\n\n" + p, False)
            else:
                merged.append((p, cut))
        posts = merged
    n = len(posts)
    out = []
    for i, (p, cut) in enumerate(posts, 1):
        body = f"{p}\n\n{i}/{n}" if number else p
        out.append({"n": i, "text": body, "weighted": w(body), "split_mid_sentence": cut})
    return out, explicit


def lint(posts, limit=LIMIT):
    checks = []

    def add(status, name, msg):
        checks.append({"status": status, "check": name, "detail": msg})

    n = len(posts)
    if n < 3:
        add("OJO", "LARGO", f"{n} post(s). Eso es un post, no un hilo. Usá /nc-x-post, o un solo post "
            "largo si tenés Premium.")
    elif n > 15:
        add("OJO", "LARGO", f"{n} posts. Pasados unos 15, llega al final menos gente de la que lee el "
            "post 2. Recortá, o partilo en dos hilos con una semana de diferencia.")
    else:
        add("OK", "LARGO", f"{n} posts")

    over = [p["n"] for p in posts if p["weighted"] > limit]
    if over:
        add("FALLA", "ENTRA", f"los posts {over} pasan de {limit}. X no los va a publicar.")
    else:
        add("OK", "ENTRA", f"todos los posts tienen {limit} o menos")

    hook = posts[0]["text"].strip().splitlines()[0] if posts else ""
    if LABEL_RE.search(hook):
        add("OJO", "POST 1", "arranca con \"hilo\". El post 1 es el único que lee la mayoría. Poné ahí lo "
            "que prometés y dejá que la interfaz de X muestre que es un hilo.")
    elif w(hook) > 110:
        add("OJO", "POST 1", f"la primera línea tiene {w(hook)} caracteres. Tiene que llegar de un vistazo.")
    else:
        add("OK", "POST 1", f"primera línea de {w(hook)} caracteres. Puntuala: "
            "python3 ../nc-x-post/hookscore.py --hook \"...\"")

    cuts = [p["n"] for p in posts if p["split_mid_sentence"]]
    if cuts:
        add("OJO", "CORTES", f"los posts {cuts} terminan a mitad de frase porque una frase es más larga "
            "que un post. Reescribí esa frase en dos.")
    else:
        add("OK", "CORTES", "todos los posts terminan en una frase completa")

    mid_links = [p["n"] for p in posts[:-1] if find_urls(p["text"])]
    if mid_links:
        add("NOTA", "LINKS", f"link(s) en los posts {mid_links}. Un link antes del último post es una "
            "salida antes de lo prometido. Movelo al final, salvo que el link SEA el punto.")
    else:
        add("OK", "LINKS", "ninguno antes del último post")

    if posts and not ASK_RE.search(posts[-1]["text"]):
        add("NOTA", "ÚLTIMO", "sin pedido. El último post es el que se captura y el que lleva a hacer "
            "algo: un resumen, después un solo próximo paso. Uno.")
    else:
        add("OK", "ÚLTIMO", "tiene un pedido")

    heavy = [p for p in posts if p["weighted"] > limit * 0.85]
    if n >= 4 and len(heavy) > n * 0.6:
        add("NOTA", "RITMO", f"{len(heavy)} de {n} posts están a menos de 15% del límite. Los hilos que se "
            "leen hasta el final tienen posts cortos. Una idea por post, y cortá.")
    return checks


def render(posts, checks, out=sys.stdout):
    total = sum(p["weighted"] for p in posts)
    print(f"\nHILO  ·  {len(posts)} posts  ·  {total:,} caracteres ponderados".replace(",", "."), file=out)
    print("=" * 62, file=out)
    for p in posts:
        mark = "  ! cortado a mitad de frase" if p["split_mid_sentence"] else ""
        print(f"\n[{p['n']}/{len(posts)}]  {p['weighted']}/{LIMIT}{mark}", file=out)
        print(p["text"], file=out)
    print("\n" + "-" * 62, file=out)
    for c in checks:
        print(f"  {c['status']:<5} {c['check']:<10} {c['detail']}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Corta un borrador en un hilo de X que entra.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("--number", action="store_true", help="agrega i/n a cada post")
    ap.add_argument("--pack", action="store_true", help="junta párrafos cortos en un post")
    ap.add_argument("--limit", type=int, default=LIMIT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    if not raw.strip():
        print("no hay nada para convertir en hilo", file=sys.stderr)
        sys.exit(2)
    posts, _ = build(raw, args.limit, args.number, args.pack)
    checks = lint(posts, args.limit)
    if args.json:
        print(json.dumps({"posts": posts, "checks": checks}, indent=2, ensure_ascii=False))
    else:
        render(posts, checks)
    sys.exit(1 if any(c["status"] == "FALLA" for c in checks) else 0)


if __name__ == "__main__":
    main()
