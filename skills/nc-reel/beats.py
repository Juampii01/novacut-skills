#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""
beats.py - convierte el guion de un Reel en una hoja de tiempos antes de
grabarlo.

Estima cuánto tarda cada línea en decirse, las apila en códigos de tiempo y
marca las cuatro cosas que matan un Reel en la edición: un gancho que se pasa
de los tres segundos, un beat tan largo que da tiempo a irse, una racha de
líneas sin nada concreto, y un largo total que no coincide con lo que dijiste
que ibas a hacer.

Los tiempos son una estimación por cantidad de palabras a un ritmo de palabras
por minuto. Alcanzan para planificar la edición, no reemplazan grabarlo.
Poné tu propio ritmo con --wpm cuando te hayas cronometrado leyendo un guion en
voz alta: en castellano la mayoría cae entre 140 y 190, y acá el default es 160.

Las cifras escritas con dígitos se cuentan como se dicen: "$18.000" son tres
palabras habladas ("dieciocho mil pesos"), no una.

Uso
  python3 beats.py guion.txt
  python3 beats.py guion.txt --target 30
  python3 beats.py guion.txt --wpm 180 --target 45
  pbpaste | python3 beats.py -
  python3 beats.py guion.txt --json
"""

import argparse
import json
import re
import sys
import unicodedata

WORD_RE = re.compile(r"[\w$%'’€-]+")
SENT_RE = re.compile(r"[^.!?]+[.!?]*")
DIGIT_RE = re.compile(r"\d")
# Algo concreto: plata, una cifra, un nombre propio (no a principio de frase,
# teniendo en cuenta los ¿ y ¡ del castellano) o un número dicho en letras.
# Los nombres propios necesitan la mayúscula, así que van en una regex aparte.
PROPER_RE = re.compile(r"(?<!^)(?<![.!?¿¡]\s)(?<![¿¡\"“«])\b[A-ZÁÉÍÓÚÑ][a-záéíóúñü][A-Za-záéíóúñü]+\b",
                       re.MULTILINE)
CONCRETE_CI_RE = re.compile(
    r"(?:\$|€|usd\s?)\s?\d|\b\d[\d.,]*\b"
    r"|\b(?:cero|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|quince|"
    r"veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|"
    r"doscientos|trescientos|quinientos|mil|millón|millon|millones|"
    r"dólares|dolares|pesos|euros|lucas|palos|por ?ciento)\b",
    re.IGNORECASE)
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "e", "o", "u",
    "pero", "si", "de", "del", "a", "al", "en", "por", "para", "con", "sin",
    "que", "esto", "este", "esta", "eso", "ese", "esa", "es", "son", "era",
    "fue", "ser", "estar", "esta", "estan", "vos", "tu", "tus", "te", "ti",
    "yo", "mi", "mis", "me", "nos", "nosotros", "ellos", "ellas", "el", "ella",
    "le", "les", "lo", "se", "ya", "no", "ni", "hay", "tiene", "tenes", "tengo",
    "hace", "hago", "como", "mas", "muy", "todo", "toda", "todos", "todas",
    "asi", "ahi", "aca", "aqui", "cuando", "donde", "porque", "entonces",
    "bueno", "solo", "tambien", "uno", "otra", "otro", "su", "sus",
}

HOOK_WINDOW = 3.0        # segundos. Pasado esto, el pulgar ya decidió.
MAX_BEAT = 4.0           # segundos en una misma idea sin cambio en pantalla.
ABSTRACT_RUN = 3         # beats seguidos sin nada que se pueda chequear.


def fold(s):
    s = s.lower().replace("ñ", "\x00")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.replace("\x00", "ñ")


def words(text):
    # "$18.000" se escribe como una sola palabra.
    flat = re.sub(r"(?<=\d)[.,](?=\d{3}(?!\d))", "", text)
    return [w for w in WORD_RE.findall(flat) if w.strip("-'’")]


def spoken_len(token):
    """Cuántas palabras se dicen en voz alta por este token escrito.

    "18000" se dice "dieciocho mil" (2), "$18000" agrega "pesos/dólares",
    "35%" agrega "por ciento", "1500000" es "un millón quinientos mil" (4).
    Es una aproximación: alcanza para que una cifra no cuente como una
    palabra de una sílaba.
    """
    digits = re.sub(r"\D", "", token)
    if not digits:
        return 1
    n = len(digits.lstrip("0") or "0")
    base = 1 if n <= 2 else 2 if n <= 4 else 3 if n <= 6 else 4
    if any(c in token for c in "$€"):
        base += 1
    if "%" in token:
        base += 2
    return base


def count_spoken(text):
    return sum(spoken_len(w) for w in words(text))


def count_concrete(text):
    return len(CONCRETE_CI_RE.findall(text)) + len(PROPER_RE.findall(text))


def pretty(token):
    """Vuelve a poner el separador de miles (punto, como en castellano)."""
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1.", token)


def tc(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:04.1f}"


def split_beats(raw, wps):
    """Una línea es un beat, salvo que sea demasiado larga para serlo."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if count_spoken(line) / wps <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        # Párrafo largo: se corta en los finales de oración para que los
        # tiempos signifiquen algo.
        parts = []
        for sent in [p.strip() for p in SENT_RE.findall(line) if p.strip()]:
            if count_spoken(sent) / wps <= MAX_BEAT:
                parts.append(sent)
            else:
                # Una sola oración larguísima: se parte en las comas.
                parts.extend(p.strip() for p in re.findall(r"[^,;:]+[,;:]?", sent) if p.strip())
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and count_spoken(candidate) / wps > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def loop_key(w):
    k = fold(w).strip("$€%")
    if len(k) > 4 and k.endswith("es") and not k.endswith("mes"):
        k = k[:-2]
    elif len(k) > 3 and k.endswith("s"):
        k = k[:-1]
    return k


def analyse(raw, wpm=160, target=None):
    wps = wpm / 60.0
    beats = split_beats(raw, wps)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        n = count_spoken(text)
        dur = n / wps
        rows.append({
            "n": i + 1,
            "start": round(clock, 2),
            "dur": round(dur, 2),
            "words": n,
            "text": text,
            "concrete": count_concrete(text),
            "label": "",
            "flags": [],
        })
        clock += dur
    total = clock

    # Etiquetas para las posiciones sobre las que se arma un Reel.
    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "GANCHO"
    rows[-1]["label"] = "CTA" if rows[-1]["label"] != "GANCHO" else "GANCHO/CTA"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "MITAD"

    notes = []
    if rows[0]["dur"] > HOOK_WINDOW:
        rows[0]["flags"].append(f"el gancho dura {rows[0]['dur']:.1f}s, pasa la marca de {HOOK_WINDOW:.0f}s")
        notes.append(f"El beat 1 tarda {rows[0]['dur']:.1f}s en decirse. Bajalo a "
                     f"{int(HOOK_WINDOW * wps)} palabras o menos, o el gancho llega cuando "
                     "la decisión ya está tomada.")
    if rows[0]["concrete"] == 0:
        notes.append("El beat 1 no tiene ni un número ni un nombre. Los ganchos sin algo "
                     "chequeable son los que se pasan de largo.")

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(f"{r['dur']:.1f}s en un solo beat")
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(f"Beat(s) {', '.join(map(str, long_beats))} pasan los {MAX_BEAT:.0f}s. "
                     "Partí la línea o cambiá lo que se ve en pantalla en el medio. "
                     "Un plano quieto es donde la gente se va.")

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(f"Los beats {start}-{r['n']} no tienen nada concreto. "
                             "Poné un número, un nombre o un precio en alguno.")
        else:
            run, start = 0, None

    # ¿La última línea te devuelve a la primera?
    def keyed(text):
        out = {}
        for w in words(text):
            if fold(w) in STOPWORDS or len(fold(w)) < 3 and not DIGIT_RE.search(w):
                continue
            out.setdefault(loop_key(w), w)
        return out
    first, last = keyed(rows[0]["text"]), keyed(rows[-1]["text"])
    loop = sorted(pretty(first[k]) for k in set(first) & set(last))
    if len(rows) == 1:
        pass
    elif loop:
        notes.append(f"Loop: el último beat repite \"{', '.join(loop[:3])}\" del gancho. "
                     "Las segundas vueltas son alcance gratis.")
    else:
        notes.append("Sin loop. El último beat no comparte ninguna palabra con el gancho, "
                     "así que el video termina plano. Repetir una palabra del beat 1 es la "
                     "segunda vuelta más barata que vas a conseguir.")

    if target:
        delta = total - target
        if abs(delta) <= target * 0.1:
            notes.append(f"El largo está en objetivo ({total:.1f}s contra {target:g}s).")
        elif delta > 0:
            notes.append(f"{delta:.1f}s por encima del objetivo. Sacá unas {int(delta * wps)} palabras.")
        else:
            notes.append(f"{-delta:.1f}s por debajo del objetivo. O agregás {int(-delta * wps)} "
                         "palabras o lo grabás corto. Corto casi siempre está bien.")

    return {
        "wpm": wpm, "target": target,
        "total_seconds": round(total, 2),
        "total_words": sum(r["words"] for r in rows),
        "beats": rows,
        "notes": notes,
    }


def render(a, out=sys.stdout):
    head = (f"HOJA DE BEATS  ·  {a['total_words']} palabras habladas  ·  ~{a['total_seconds']:.1f}s "
            f"a {a['wpm']:g} ppm" + (f"  ·  objetivo {a['target']:g}s" if a["target"] else ""))
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{r['label']:<11}" if r["label"] else " " * 11
        print(f"  {tc(r['start'])}  {r['dur']:4.1f}s  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<11}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Convierte un guion de Reel en una hoja de tiempos.")
    ap.add_argument("input", nargs="?", default="-", help="archivo del guion, o - para stdin")
    ap.add_argument("--wpm", type=float, default=160, help="palabras por minuto al hablar (default 160)")
    ap.add_argument("--target", type=float, help="largo objetivo en segundos")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, wpm=args.wpm, target=args.target)
    if not a:
        print("guion vacío", file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()
