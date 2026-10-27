#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
pull.py - convierte una lista de links de posts de X que elegiste en una
planilla de referencias, con el texto exacto, los saltos de línea, el autor,
la fecha y el formato completos, y las cuatro columnas de números para vos.

Usa la API oEmbed documentada de X (publish.x.com/oembed), el endpoint que
existe para que los sitios web puedan incrustar un post público a partir de
su link. Sin login, sin clave, sin cookies; no se manda nada sobre vos. Una
consulta por post, un post por segundo, y un tope duro por corrida.

Lo que a propósito NO hace:

  - buscar posts. Los elegís vos, abriendo la cuenta y copiando los links.
    Los Términos de X prohíben rastrear o scrapear "de cualquier forma, para
    cualquier fin" sin consentimiento escrito, así que acá no hay recorrido de
    timeline, ni búsqueda, ni lista de seguidores, ni bucles, y no tiene que
    haberlos.
  - traer números. oEmbed no trae vistas ni likes, y los endpoints que sí los
    traen no están documentados. Las vistas son públicas en cada post: las
    leés de la pantalla y las tipeás. Son 30 números.

Uso
  python3 pull.py links.txt > swipe.tsv         # un link por línea
  python3 pull.py https://x.com/a/status/1 https://x.com/b/status/2
  python3 pull.py links.txt --max 60

Después abrí swipe.tsv, completá vistas (y likes, respuestas, reposts si los
tenés) y corré swipe.py.
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://publish.x.com/oembed"
UA = "novacut-skills/1.0"
STATUS_RE = re.compile(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/([A-Za-z0-9_]{1,15})/status(?:es)?/(\d+)")
COLUMNS = ["url", "cuenta", "nombre", "fecha", "formato", "lineas", "palabras", "vistas", "likes",
           "respuestas", "reposts", "gancho", "texto"]


def parse_urls(items):
    out, seen = [], set()
    for item in items:
        for m in STATUS_RE.finditer(item):
            handle, pid = m.group(1), m.group(2)
            if pid not in seen:
                seen.add(pid)
                out.append(f"https://x.com/{handle}/status/{pid}")
    return out


def fetch(url, timeout=15):
    q = urllib.parse.urlencode({"url": url, "omit_script": "true", "dnt": "true"})
    req = urllib.request.Request(f"{ENDPOINT}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_embed(d, url):
    """html de oEmbed -> texto con sus saltos de línea reales, más lo que el
    marcado dice de imágenes/videos, recortes y links."""
    block = d.get("html", "")
    m = re.search(r"<p[^>]*>(.*?)</p>", block, re.S)
    inner = m.group(1) if m else ""
    media = bool(re.search(r">pic\.(?:twitter|x)\.com/", inner))
    inner = re.sub(r"<a[^>]*>pic\.(?:twitter|x)\.com/[^<]*</a>", "", inner)
    links = re.findall(r'<a href="(https://t\.co/[^"]+)"', inner)
    inner = re.sub(r"<br\s*/?>", "\n", inner)
    inner = re.sub(r"<a[^>]*>([^<]*)</a>", r"\1", inner)
    text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
    truncated = text.endswith("…")
    date = ""
    dm = re.search(r"<a href=\"[^\"]+/status/\d+[^\"]*\">([^<]+)</a>\s*</blockquote>", block)
    if dm:
        date = html.unescape(dm.group(1))
    handle = STATUS_RE.search(d.get("url", url)).group(1)
    if truncated:
        fmt = "largo"                     # un post largo de Premium, recortado por el embed
    elif media:
        fmt = "media"                     # imagen o video; el embed no dice cuál
    elif links:
        fmt = "link"
    else:
        fmt = "texto"
    lines = [l for l in text.splitlines() if l.strip()]
    hook = lines[0].strip() if lines else ""
    return {
        "url": d.get("url", url),
        "cuenta": "@" + handle,
        "nombre": d.get("author_name", ""),
        "fecha": date,
        "formato": fmt,
        "lineas": len(lines),
        "palabras": len(re.findall(r"\S+", text)),
        "vistas": "", "likes": "", "respuestas": "", "reposts": "",
        "gancho": hook,
        "texto": text,
    }


def tsv_cell(v):
    return str(v).replace("\t", " ").replace("\r", "").replace("\n", " ⏎ ")


def main():
    ap = argparse.ArgumentParser(description="Links de posts de X -> planilla de referencias, vía la API oEmbed de X.")
    ap.add_argument("inputs", nargs="*", help="links, o un archivo con links, o - para stdin")
    ap.add_argument("--max", type=int, default=100, help="tope duro por corrida (por defecto 100)")
    ap.add_argument("--delay", type=float, default=1.0, help="segundos entre consultas (mínimo 1)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    items = []
    for i in args.inputs or ["-"]:
        if i == "-":
            items.append(sys.stdin.read())
        elif STATUS_RE.search(i):
            items.append(i)
        else:
            items.append(open(i, encoding="utf-8").read())
    urls = parse_urls(items)
    if not urls:
        print("no encontré links del tipo x.com/.../status/...", file=sys.stderr)
        sys.exit(2)
    if len(urls) > args.max:
        print(f"{len(urls)} links, tope en {args.max}. Esto lee posts que elegiste; no es un "
              "rastreador. Si de verdad querés, corrélo de nuevo con el resto.", file=sys.stderr)
        urls = urls[:args.max]

    rows, failed = [], []
    for i, url in enumerate(urls):
        if i:
            time.sleep(max(1.0, args.delay))
        try:
            rows.append(parse_embed(fetch(url), url))
            print(f"  {i + 1:>3}/{len(urls)}  {rows[-1]['cuenta']:<17} {rows[-1]['gancho'][:48]}",
                  file=sys.stderr)
        except urllib.error.HTTPError as e:
            reason = {404: "borrado, privado o protegido", 403: "no se puede incrustar"}.get(e.code, f"HTTP {e.code}")
            failed.append((url, reason))
            print(f"  {i + 1:>3}/{len(urls)}  salteado: {reason}  {url}", file=sys.stderr)
        except Exception as e:                               # red, JSON
            failed.append((url, str(e)[:60]))
            print(f"  {i + 1:>3}/{len(urls)}  salteado: {str(e)[:60]}  {url}", file=sys.stderr)

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        print("\t".join(COLUMNS))
        for r in rows:
            print("\t".join(tsv_cell(r[c]) for c in COLUMNS))
    print(f"\n{len(rows)} traídos, {len(failed)} salteados. Ahora completá la columna de vistas "
          "mirando cada post, y después corré swipe.py.", file=sys.stderr)


if __name__ == "__main__":
    main()
