#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
weights.py - muestra los pesos de interacción que usa ahora mismo el ranking
"Para ti" de X, leídos del código que X publica, con la fecha del último
cambio.

En enero de 2026 X liberó su sistema de recomendación actual en
github.com/xai-org/x-algorithm, y desde agosto de 2026 ese repositorio trae
los pesos de producción en home-mixer/params/param.rs, sincronizados con
producción por una tarea programada. Cambian. Por eso esto lee el archivo en
vivo en vez de pegar una tabla que el mes que viene va a estar mal. Sin cuenta
de X y sin clave: lee un archivo público de GitHub (una sola consulta).

CÓMO LEERLOS, con las palabras de los comentarios de ese archivo: cada peso
multiplica la PROBABILIDAD PREDICHA de que un usuario haga esa acción, no una
cantidad de acciones. Así que "una respuesta vale 10 likes" es la lectura
equivocada, y el archivo lo dice. La lectura útil es la dirección: qué acciones
premia el ranking y cuáles castiga fuerte.

Uso
  python3 weights.py
  python3 weights.py --json
  python3 weights.py --offline        # la foto de abajo, marcada como tal
"""

import argparse
import json
import re
import sys
import urllib.request

REPO = "xai-org/x-algorithm"
PATH = "home-mixer/params/param.rs"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/{PATH}"
COMMITS = f"https://api.github.com/repos/{REPO}/commits?path={PATH}&per_page=1"
UA = "novacut-skills/1.0"

# Qué significa cada peso en palabras simples. Lo que no está acá sale con su nombre de código.
LABELS = {
    "Favorite": "like",
    "Reply": "respuesta",
    "BidirectionalFollowReplyWeightBoost": "+ extra a una respuesta entre mutuos",
    "Retweet": "repost",
    "Quote": "cita",
    "Share": "compartir (cualquiera)",
    "ShareViaDm": "compartir por DM",
    "ShareViaCopyLink": "compartir copiando el link",
    "FollowAuthor": "seguir al autor",
    "Click": "tocar el post",
    "OpenLink": "abrir un link",
    "ProfileClick": "tocar el perfil",
    "PhotoExpand": "ampliar una foto",
    "VideoOpen": "abrir un video",
    "Dwell": "frenar y leer",
    "ContClickDwellTime": "tiempo después de entrar",
    "NotInterested": "\"no me interesa\"",
    "BlockAuthor": "bloquear al autor",
    "MuteAuthor": "silenciar al autor",
    "Report": "denunciar",
    "NotDwelled": "pasar de largo",
}

# Foto para --offline o para cuando no se puede llegar a GitHub.
SNAPSHOT_DATE = "2026-09-29 (commit a707cc2)"
SNAPSHOT = {
    "Favorite": 0.5, "Reply": 5.0, "BidirectionalFollowReplyWeightBoost": 15.0, "Retweet": 1.0,
    "PhotoExpand": 0.05, "VideoOpen": 0.07, "Click": 0.3, "OpenLink": 0.2, "ProfileClick": 0.0,
    "Share": 2.0, "ShareViaDm": 5.0, "ShareViaCopyLink": 20.0, "Dwell": 0.05, "Quote": 5.0,
    "FollowAuthor": 4.0, "ContClickDwellTime": 0.4, "NotInterested": -47.52, "BlockAuthor": -31.2,
    "MuteAuthor": -58.8, "Report": -234.0, "NotDwelled": -0.02,
}

PARAM_RE = re.compile(r"param!\(\s*(\w+)\s*,\s*f64\s*,\s*\"[^\"]+\"\s*,\s*(-?\d+(?:\.\d+)?)\s*\)", re.S)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def fetch():
    src = get(RAW)
    weights = {}
    for name, val in PARAM_RE.findall(src):
        if name.endswith("Weight") or name.endswith("WeightBoost"):
            key = name[:-6] if name.endswith("Weight") else name
            weights[key] = float(val)
    date = "fecha desconocida"
    try:
        c = json.loads(get(COMMITS))[0]
        date = f"{c['commit']['committer']['date'][:10]} (commit {c['sha'][:7]})"
    except Exception:
        pass
    return weights, date


def render(weights, date, source, out=sys.stdout):
    like = weights.get("Favorite") or 0.5
    shown = {k: v for k, v in weights.items() if k in LABELS and v != 0}
    pos = sorted(((k, v) for k, v in shown.items() if v > 0), key=lambda kv: -kv[1])
    neg = sorted(((k, v) for k, v in shown.items() if v < 0), key=lambda kv: kv[1])
    print(f"\nRANKING \"PARA TI\" DE X  ·  pesos por acción  ·  {source}, último cambio {date}")
    print("=" * 78)
    print("PREMIA" + " " * 36 + "  peso   vs un like")
    for k, v in pos:
        print(f"  {LABELS[k]:<40} {v:>7g}   {v / like:>6.1f}x")
    print("\nCASTIGA")
    for k, v in neg:
        print(f"  {LABELS[k]:<40} {v:>7g}")
    print("-" * 78)
    print("  Multiplican la probabilidad PREDICHA de cada acción para cada usuario, no")
    print("  cantidades. El comentario de X en el archivo: leer las proporciones como")
    print("  equivalencias de cantidad es \"incorrecto\". Leé la dirección: escribí cosas que")
    print("  la gente responda, cite y le mande a una persona. Evitá lo que te hace silenciar")
    print("  o marcar como \"no me interesa\". Los pesos cambian: volvé a correrlo cada tanto.")
    print("  Fuente: github.com/" + REPO + "/blob/main/" + PATH + "\n")


def main():
    ap = argparse.ArgumentParser(description="Los pesos de ranking que X publica hoy.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    if args.offline:
        weights, date, source = SNAPSHOT, SNAPSHOT_DATE, "foto sin conexión"
    else:
        try:
            weights, date = fetch()
            source = "en vivo desde GitHub"
            if not weights:
                raise ValueError("no se leyó ningún peso; puede que haya cambiado el formato del archivo")
        except Exception as e:
            print(f"no pude leer el archivo en vivo ({e}). Muestro la foto guardada.", file=sys.stderr)
            weights, date, source = SNAPSHOT, SNAPSHOT_DATE, "foto sin conexión"
    if args.json:
        print(json.dumps({"source": source, "date": date, "weights": weights}, indent=2))
    else:
        render(weights, date, source)


if __name__ == "__main__":
    main()
