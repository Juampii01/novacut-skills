---
name: nc-yt-viral
description: >-
  Encuentra qué está funcionando de verdad en el nicho del usuario en
  YouTube, lo rankea por cuánto le ganó cada video a su propio canal y nombra
  la fórmula del título. Usala para "qué está funcionando ahora", "buscame
  videos virales de mi nicho", "por qué explotó este video", investigar a la
  competencia o armar un archivo de referencias. También: "find viral videos
  in my niche", "what's working on YouTube".
---

# nc-yt-viral

Las vistas en bruto rankean el tamaño del canal, no las ideas. Esto rankea por **múltiplo sobre la
mediana de cada canal**, que es la única versión de la pregunta que habla del video.

```bash
python3 swipe.py recolectados.json --min 2.0
```

## Juntar la entrada

Necesitás al menos **cuatro videos por canal**, o la mediana no significa nada; la herramienta
saltea el canal y te avisa. Juntalos como prefiera el usuario: `yt-dlp --flat-playlist -J` contra la
URL de un canal es lo más rápido, la página pública sirve, una lista a mano también sirve.

```json
[{"channel":"Cocina con Vale","title":"...","views":212000,"url":"...","duration":613}]
```

(Las claves en español `canal`, `titulo`, `vistas` también funcionan.)

**Se lee, no se scrapea.** Solo listados públicos, a velocidad humana, nunca una sesión iniciada,
nunca las credenciales del usuario. Si el usuario busca referentes en español, priorizá canales del
mismo idioma: un formato que explota en inglés no siempre viaja.

## Leer la salida

El múltiplo es la señal. La línea de fórmula es un juicio sobre el TÍTULO, comparado contra
[las 21 fórmulas](../nc-yt-script/hooks.json): no explica por qué funcionó el video, y tenés que
decirlo así cuando lo presentes.

Qué devolver: los cinco primeros con su múltiplo, la fórmula de cada uno y la ÚNICA cosa
estructural que comparten. Después, la línea difícil: cuál de esos podría hacer el usuario esta
semana, en su voz (`~/.claude/novacut/voz.md`), con lo que ya tiene.

Si el usuario quiere guardarlos, sumá los cinco (título, canal, múltiplo, fórmula, link) al final de
`~/.claude/novacut/yt-swipe.md`, sin pisar lo que ya haya.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
