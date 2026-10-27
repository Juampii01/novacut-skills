#!/usr/bin/env python3
# NovaCut Skills · nc-cortar · candidatos.py
"""Detecta, SIN IA, lo que probablemente hay que cortar en una grabación hablada.

Lee el JSON de palabras de transcribir.py y encuentra:
- Retomas: la misma secuencia de 3 o más palabras vuelve a aparecer dentro de 30 s. Se marca la PRIMERA toma
  (desde su inicio hasta justo antes de que arranca la siguiente): queda la última.
- Arranques en falso: 1 a 3 palabras, una pausa y el reinicio con las mismas palabras ("Hoy te... hoy te cuento"),
  o una palabra cortada que es el comienzo de la siguiente ("con... contarte").
- Muletillas: "eh", "em", "mmm" siempre; "este", "bueno", "o sea", "nada", "tipo", "digamos", "viste", "pues"
  solo cuando aparecen sueltas entre pausas (si no, pueden ser parte de la frase).
- Silencios largos: pausas de 1 s o más (informativo: render.py ya acorta solo las pausas largas).

Cada candidato trae un nivel de confianza. Claude decide cuáles se cortan y la persona tiene la última palabra.

Uso:
  python3 candidatos.py palabras.json                      # imprime la transcripción con IDs y los candidatos
  python3 candidatos.py palabras.json --salida cand.json   # además guarda el JSON
  python3 candidatos.py palabras.json --plan-base plan.json  # arma un borrador de plan v2 con los candidatos seguros
Solo usa la biblioteca estándar de Python.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

VENTANA_RETOMA = 30.0
NGRAMA_MAX = 8
NGRAMA_MIN = 3
PAUSA = 0.25
SILENCIO_LARGO = 1.0

# Muletillas puras: no tienen otro significado ("eh", "eeeh", "mmm", "ehm"...).
# Ojo: "e" y "u" solas son conjunciones ("padres e hijos", "siete u ocho"): no se marcan.
MULETILLA_PURA = re.compile(r"^(e{2,}h*|e+h+|e+h*m+|m{2,}|m+h+m+|u{2,}h*|u+h+m*|u+m+|a+h+|h+m+|ah+m+|ejem)$")
# A veces muletilla, a veces no: solo cuentan sueltas entre pausas.
MULETILLA_BLANDA = {"este", "bueno", "pues", "osea", "digamos", "tipo", "nada", "viste", "sabes", "onda", "dale"}
# Pares que funcionan como una sola muletilla.
MULETILLA_DOBLE = {("o", "sea"), ("bueno", "nada"), ("a", "ver"), ("es", "decir"), ("no", "se"), ("como", "que")}
DOBLE_CONF = {("o", "sea"): 0.65, ("bueno", "nada"): 0.7, ("a", "ver"): 0.45, ("es", "decir"): 0.4, ("no", "se"): 0.4, ("como", "que"): 0.4}
# Palabras que no alcanzan para decir que una frase se repitió ("de la que", "y en el").
VACIAS = {
    "a", "al", "de", "del", "el", "la", "lo", "los", "las", "un", "una", "unos", "unas", "y", "o", "u", "e", "que", "en", "es", "se",
    "su", "sus", "no", "si", "me", "te", "le", "les", "mi", "tu", "por", "para", "con", "como", "mas", "pero", "ya", "muy", "eso",
    "esto", "esta", "este", "yo", "vos", "nos",
}
# Palabras típicas de cuando alguien se corrige antes de repetir la toma.
CORRECCION = {"perdon", "perdona", "perdoname", "espera", "esperá", "corta", "corto", "otravez", "denuevo", "repito", "mal", "uy", "ups", "no"}

MOTIVOS = {"retake": "retoma", "false_start": "arranque en falso", "filler": "muletilla", "silence": "silencio"}


def norm(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]+", "", t).replace("_", "")


def cargar_palabras(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: no pude leer {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    palabras = data.get("palabras") if isinstance(data, dict) else data
    if not isinstance(palabras, list) or not palabras:
        print("ERROR: el JSON no tiene una lista 'palabras'.", file=sys.stderr)
        sys.exit(1)
    out = []
    for i, w in enumerate(palabras):
        out.append({"id": int(w.get("id", i)), "texto": str(w.get("texto", w.get("text", ""))), "inicio": float(w.get("inicio", w.get("start", 0))), "fin": float(w.get("fin", w.get("end", 0)))})
    for i, w in enumerate(out):
        if w["id"] != i:
            print("ERROR: los IDs de palabra tienen que ser 0, 1, 2... en orden. Volvé a correr transcribir.py.", file=sys.stderr)
            sys.exit(1)
    return out


def hueco_antes(p: list[dict], i: int) -> float:
    return float("inf") if i <= 0 else p[i]["inicio"] - p[i - 1]["fin"]


def hueco_despues(p: list[dict], i: int) -> float:
    return float("inf") if i >= len(p) - 1 else p[i + 1]["inicio"] - p[i]["fin"]


def misma_secuencia(n: list[str], a: int, b: int, largo: int) -> bool:
    for k in range(largo):
        if a + k >= len(n) or b + k >= len(n) or not n[a + k] or n[a + k] != n[b + k]:
            return False
    return True


def cand(kind: str, p: list[dict], desde: int, hasta: int, conf: float, nota: str, inicio: float | None = None, fin: float | None = None) -> dict:
    return {
        "kind": kind,
        "motivo": MOTIVOS[kind],
        "from_word": desde,
        "to_word": hasta,
        "inicio": round(p[desde]["inicio"] if inicio is None else inicio, 3),
        "fin": round(p[hasta]["fin"] if fin is None else fin, 3),
        "confidence": round(max(0.3, min(0.97, conf)), 2),
        "nota": nota,
    }


def texto(p: list[dict], a: int, b: int) -> str:
    return " ".join(w["texto"] for w in p[a : b + 1])


def retomas(p: list[dict], n: list[str], guion: list[str] | None) -> list[dict]:
    out = []
    i = 0
    while i < len(p):
        hallado = None
        for largo in range(min(NGRAMA_MAX, len(p) - i), NGRAMA_MIN - 1, -1):
            seq = n[i : i + largo]
            if any(not t for t in seq) or all(t in VACIAS for t in seq):
                continue
            j = i + largo
            while j + largo <= len(p) and p[j]["inicio"] - p[i]["inicio"] <= VENTANA_RETOMA:
                if misma_secuencia(n, i, j, largo):
                    hallado = (largo, j)
                    break
                j += 1
            if hallado:
                break
        if not hallado:
            i += 1
            continue
        largo, j = hallado
        palabras_tramo = j - i
        segundos = p[j]["inicio"] - p[i]["inicio"]
        entre = n[i + largo : j]
        conf = 0.45 + min(0.24, 0.08 * (largo - NGRAMA_MIN))
        # Casi toda retoma tiene una pausa antes de volver a empezar; sin pausa suele ser una repetición a propósito.
        conf += 0.2 if hueco_antes(p, j) >= 0.35 else -0.1
        if palabras_tramo <= largo + 6:
            conf += 0.1
        if segundos > 15:
            conf -= 0.2
        if any(t in CORRECCION for t in entre):
            conf += 0.1
        if guion and contar(guion, seq_de(n, i, largo)) == 1:
            conf += 0.15
        out.append(cand("retake", p, i, j - 1, conf, f"Repite «{texto(p, i, i + largo - 1)}» {segundos:.1f} s después; queda la última toma."))
        i = j  # la toma nueva puede volver a repetirse: gana la última completa
    return out


def seq_de(n: list[str], i: int, largo: int) -> list[str]:
    return n[i : i + largo]


def contar(guion: list[str], seq: list[str]) -> int:
    return sum(1 for i in range(len(guion) - len(seq) + 1) if guion[i : i + len(seq)] == seq)


def arranques(p: list[dict], n: list[str]) -> list[dict]:
    out = []
    for k in range(len(p) - 1):
        if hueco_despues(p, k) < PAUSA:
            continue
        hallado = False
        # 1) El fragmento (1 a 3 palabras, después de una pausa) se repite igual: "Esto es… Esto es lo que…".
        for largo in (3, 2, 1):
            i = k - largo + 1
            if i < 0 or k + largo >= len(p):
                continue
            if not misma_secuencia(n, i, k + 1, largo):
                continue
            if i > 0 and hueco_antes(p, i) < 0.2:
                continue
            if largo == 1 and n[i] in VACIAS and hueco_despues(p, k) < 0.4:
                continue
            out.append(cand("false_start", p, i, k, 0.85, f"Arranque en falso: «{texto(p, i, k)}» y vuelve a empezar."))
            hallado = True
            break
        # 2) La palabra quedó cortada y es el comienzo de la siguiente: "con… contarte".
        if not hallado and len(n[k]) >= 3 and len(n[k + 1]) > len(n[k]) and n[k + 1].startswith(n[k]):
            # "que… quería" puede ser natural: con palabras vacías baja la confianza.
            conf = 0.6 if n[k] in VACIAS else 0.8
            out.append(cand("false_start", p, k, k, conf, f"Palabra cortada: «{p[k]['texto']}» antes de «{p[k + 1]['texto']}»."))
    return out


def muletillas(p: list[dict], n: list[str]) -> list[dict]:
    out = []
    i = 0
    while i < len(p):
        tok = n[i]
        suelta = hueco_antes(p, i) >= 0.2 and hueco_despues(p, i) >= 0.2
        par = (tok, n[i + 1]) if i + 1 < len(p) else None
        if tok and MULETILLA_PURA.match(tok):
            out.append(cand("filler", p, i, i, 0.9, f"Muletilla «{p[i]['texto']}»."))
        elif par in MULETILLA_DOBLE and hueco_antes(p, i) >= 0.2 and hueco_despues(p, i + 1) >= 0.2:
            out.append(cand("filler", p, i, i + 1, DOBLE_CONF[par], f"Muletilla «{texto(p, i, i + 1)}» entre pausas."))
            i += 1
        elif tok in MULETILLA_BLANDA and suelta:
            out.append(cand("filler", p, i, i, 0.6, f"«{p[i]['texto']}» suelto entre pausas."))
        i += 1
    return out


def silencios(p: list[dict], duracion: float | None) -> list[dict]:
    out = []
    if p and p[0]["inicio"] >= SILENCIO_LARGO:
        out.append({"kind": "silence", "motivo": "silencio", "from_word": 0, "to_word": 0, "inicio": 0.0, "fin": round(p[0]["inicio"], 3), "confidence": 0.99, "nota": f"Silencio de {p[0]['inicio']:.1f} s al principio (se recorta solo)."})
    for k in range(len(p) - 1):
        hueco = p[k + 1]["inicio"] - p[k]["fin"]
        if hueco >= SILENCIO_LARGO:
            out.append(cand("silence", p, k, k + 1, 0.99, f"Pausa de {hueco:.1f} s (render.py la acorta sola).", inicio=p[k]["fin"], fin=p[k + 1]["inicio"]))
    if duracion and p and duracion - p[-1]["fin"] >= SILENCIO_LARGO:
        k = len(p) - 1
        out.append({"kind": "silence", "motivo": "silencio", "from_word": k, "to_word": k, "inicio": round(p[k]["fin"], 3), "fin": round(duracion, 3), "confidence": 0.99, "nota": f"Silencio de {duracion - p[k]['fin']:.1f} s al final (se recorta solo)."})
    return out


def se_pisan(a: dict, b: dict) -> bool:
    return a["from_word"] <= b["to_word"] and b["from_word"] <= a["to_word"]


def detectar(p: list[dict], guion: str | None = None, duracion: float | None = None) -> list[dict]:
    if not p:
        return []
    n = [norm(w["texto"]) for w in p]
    g = [t for t in (norm(x) for x in guion.split())] if guion else None
    g = [t for t in g if t] if g else None
    r = retomas(p, n, g)
    a = [c for c in arranques(p, n) if not any(se_pisan(x, c) for x in r)]
    m = [c for c in muletillas(p, n) if not any(se_pisan(x, c) for x in r + a)]
    s = silencios(p, duracion)
    todos = sorted(r + a + m + s, key=lambda c: (c["from_word"], c["to_word"]))
    for i, c in enumerate(todos):
        c["id"] = f"C{i + 1}"
    return todos


def vista(p: list[dict], cands: list[dict]) -> str:
    """Transcripción legible con IDs: una línea por frase o pausa, con el tiempo de inicio."""
    marca: dict[int, str] = {}
    for c in cands:
        if c["kind"] == "silence":
            continue
        for k in range(c["from_word"], c["to_word"] + 1):
            marca.setdefault(k, c["id"])
    lineas, actual = [], []
    for i, w in enumerate(p):
        if actual and (hueco_antes(p, i) >= 0.5 or re.search(r"[.?!…]$", p[i - 1]["texto"])):
            lineas.append(actual)
            actual = []
        actual.append(i)
    if actual:
        lineas.append(actual)
    out = []
    for ids in lineas:
        t0 = p[ids[0]]["inicio"]
        partes = []
        for k in ids:
            tag = f"[{k}]{p[k]['texto']}"
            if k in marca:
                tag += f"<{marca[k]}>"
            partes.append(tag)
        out.append(f"{int(t0 // 60):02d}:{t0 % 60:05.2f}  " + " ".join(partes))
    return "\n".join(out)


def plan_base(cands: list[dict], umbral: float, formato: str | None) -> dict:
    seguros = [c for c in cands if c["kind"] != "silence" and c["confidence"] >= umbral]
    removals = []
    for c in seguros:
        if removals and c["from_word"] <= removals[-1]["to_word"]:
            continue
        removals.append({"from_word": c["from_word"], "to_word": c["to_word"], "reason": c["kind"], "confidence": c["confidence"], "nota": c["nota"]})
    plan = {"version": 2, "removals": removals, "pausa_max": 0.5, "captions": {"emphasis_words": []}, "summary": "Borrador automático: solo candidatos con confianza alta. Revisalo antes de renderizar."}
    if formato:
        plan["format"] = formato
    return plan


def main() -> None:
    ap = argparse.ArgumentParser(description="Detecta sin IA retomas, arranques en falso, muletillas y silencios en un JSON de palabras.")
    ap.add_argument("palabras", help="JSON de transcribir.py")
    ap.add_argument("--guion", help="archivo de texto con el guion (opcional: refuerza las retomas)")
    ap.add_argument("--salida", help="guardar los candidatos en este JSON (default: candidatos.json al lado de las palabras)")
    ap.add_argument("--plan-base", help="escribir un borrador de plan v2 con los candidatos de confianza alta")
    ap.add_argument("--umbral", type=float, default=0.75, help="confianza mínima para el borrador de plan (default 0.75)")
    ap.add_argument("--sin-vista", action="store_true", help="no imprimir la transcripción con IDs")
    args = ap.parse_args()

    path = Path(args.palabras).expanduser()
    p = cargar_palabras(path)
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
        duracion = float(meta.get("duracion") or 0) if isinstance(meta, dict) else None
    except (ValueError, AttributeError):
        duracion = None
    guion = Path(args.guion).expanduser().read_text(encoding="utf-8") if args.guion else None
    cands = detectar(p, guion, duracion)

    salida = Path(args.salida).expanduser() if args.salida else path.with_name("candidatos.json")
    salida.write_text(json.dumps({"version": 1, "palabras": len(p), "candidatos": cands}, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.sin_vista:
        print("TRANSCRIPCIÓN CON IDS  ([id]palabra<candidato>)")
        print(vista(p, cands))
        print()
    print(f"CANDIDATOS ({len(cands)})")
    for c in cands:
        rango = f"{c['from_word']}" if c["from_word"] == c["to_word"] else f"{c['from_word']}-{c['to_word']}"
        print(f"  {c['id']:>4}  {c['motivo']:<17} palabras {rango:<9} {c['inicio']:7.2f}-{c['fin']:7.2f} s  conf {c['confidence']:.2f}  {c['nota']}")
    resumen = {}
    for c in cands:
        resumen[c["motivo"]] = resumen.get(c["motivo"], 0) + 1
    print("Resumen: " + (", ".join(f"{v} {k}" for k, v in resumen.items()) or "nada para cortar"))
    print(f"Guardado: {salida}")
    if args.plan_base:
        plan = plan_base(cands, args.umbral, None)
        Path(args.plan_base).expanduser().write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Borrador de plan ({len(plan['removals'])} cortes): {args.plan_base}")


if __name__ == "__main__":
    main()
