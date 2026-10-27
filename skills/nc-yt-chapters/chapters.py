#!/usr/bin/env python3
# Adaptado para NovaCut a partir del trabajo de Jake Schincariol (MIT).
"""chapters.py - capítulos de YouTube a partir de una transcripción con tiempos.

    python3 chapters.py transcripcion.srt            # o .vtt / .json de whisper
    python3 chapters.py transcripcion.srt --target 8 --json

Imprime un bloque para pegar directo en la descripción. Las reglas de YouTube se chequean acá en vez
de suponerlas: la lista tiene que empezar en 0:00, necesita al menos tres capítulos, y cada uno tiene
que durar al menos 10 segundos. Un bloque que rompe cualquiera de esas reglas no se convierte en
capítulos y nadie te avisa; por eso esto chequea en vez de confiar.

Los cortes salen de las pausas (las que hiciste de verdad entre secciones), puntuadas por cuánto
duró la pausa y cuánto cambia el vocabulario de un lado al otro. Es un primer borrador que hay que
retitular, no un resumidor.
"""
import json, os, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nc-yt-edit"))
from deadair import load, parse_ts  # noqa: E402,F401  (mismo parser, una sola implementación)

# Palabras vacías en español (sin tildes) más relleno hablado: no sirven para nombrar un tema.
STOP = set("""
el la los las lo un una unos unas de del al a en con por para sin sobre entre hasta desde hacia
y e o u ni que como pero mas porque cuando donde quien cual cuales cuanto este esta estos estas
ese esa esos esas eso esto aquel aquella aqui aca ahi alli alla muy mucho mucha muchos muchas poco
poca pocos pocas tan tanto todo toda todos todas otro otra otros otras mismo misma cada algo nada
alguien nadie ya aun todavia tambien tampoco siempre nunca entonces bueno digamos tipo sea viste
osea vale pues bien mal solo sola solamente entonces ahora despues antes luego aunque mientras
yo tu vos usted ustedes nosotros ellos ellas mi mis tus su sus nuestro nuestra me te se le les nos
es son era eran fue fueron ser estar esta estan estaba estoy estas estamos sos eres soy hay habia
tiene tienen tenes tienes tengo tenemos tener hace hacen haces haceis hago hacer hacemos hice hizo
puede pueden podes puedes puedo poder quiero queres quieres quiere van vamos voy vas iba ir
dice dicen digo decir dije dijo sabe saben sabes sabia ver veo vemos mira miren mirar mira fijate
cosa cosas parte forma manera vez veces gente video videos canal hola gracias chicos casi
uno una dos tres cuatro cinco seis siete ocho nueve diez primero primera ultimo ultima
""".split())

def plain(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

def keywords(text):
    return {w for w in re.findall(r"[a-zñ]{4,}", plain(text)) if w not in STOP}

def mmss(t):
    t = int(t); h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def main():
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    target = int(a[a.index("--target") + 1]) if "--target" in a else 7
    a = [x for x in a if not x.startswith("--") and not x.isdigit()]
    if not a or not os.path.exists(a[0]): print(__doc__); sys.exit(1)
    cues = load(a[0])
    if len(cues) < 6: print("muy pocos subtítulos para armar capítulos (mínimo 6)"); sys.exit(1)
    dur = cues[-1][1]
    cand = []
    for i in range(1, len(cues)):
        gap = cues[i][0] - cues[i - 1][1]
        before = " ".join(c[2] for c in cues[max(0, i - 12):i])
        after = " ".join(c[2] for c in cues[i:i + 12])
        kb, ka = keywords(before), keywords(after)
        shift = 1 - (len(kb & ka) / len(kb | ka)) if (kb | ka) else 0
        cand.append((gap * 1.6 + shift * 3.2, cues[i][0], i))
    cand.sort(reverse=True)
    picked, MIN = [0.0], 10.0
    for _, t, i in cand:
        if len(picked) >= target: break
        if all(abs(t - p) >= MIN for p in picked) and dur - t >= MIN:
            picked.append(t)
    picked.sort()
    chapters = []
    for n, t in enumerate(picked):
        end = picked[n + 1] if n + 1 < len(picked) else dur
        text = " ".join(c[2] for c in cues if c[0] >= t and c[1] <= end)
        low = plain(text)
        kw = sorted(keywords(text), key=lambda w: (-low.count(w), w))
        # mostrar las palabras con sus tildes originales ("retencion" -> "retención")
        surface = {}
        for tok in re.findall(r"[a-záéíóúüñ]{4,}", text.lower()):
            surface.setdefault(plain(tok), tok)
        top = []   # sin repetir singular y plural ("miniatura" / "miniaturas")
        for w in kw:
            if any(w in (x + "s", x + "es") or x in (w + "s", w + "es") for x in top): continue
            top.append(w)
            if len(top) == 3: break
        title = " ".join(surface.get(w, w) for w in top).capitalize() or "Sección"
        chapters.append({"inicio": round(t, 2), "etiqueta": mmss(t), "titulo_borrador": title,
                         "segundos": round(end - t, 2)})
    ok = len(chapters) >= 3 and chapters[0]["inicio"] == 0 and all(c["segundos"] >= MIN for c in chapters)
    if as_json:
        print(json.dumps({"valido": ok, "capitulos": chapters}, indent=1, ensure_ascii=False)); return
    print()
    for c in chapters: print(f"  {c['etiqueta']} {c['titulo_borrador']}")
    print(f"\n  {len(chapters)} capítulo{'' if len(chapters) == 1 else 's'}"
          f"{'' if ok else '  -- INVÁLIDO: YouTube pide 3 o más, el primero en 0:00 y 10s mínimo cada uno'}")
    print("  Retitulá cada línea antes de pegar. Son las palabras del tema, no tus palabras.\n")

if __name__ == "__main__":
    main()
