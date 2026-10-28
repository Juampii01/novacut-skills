---
name: nc-yt-shorts
description: >-
  Encuentra los Shorts escondidos dentro de un video largo y los escribe,
  usando la transcripción para elegir momentos que se sostienen solos. Usala
  para "cortá esto en shorts", "sacame clips", "reutilizá este video", "qué
  partes recorto", "pasame esto a verticales". También: "cut this into
  shorts", "clip this".
---

# nc-yt-shorts

Un Short sacado de un video largo no es un recorte del mejor momento. Es un momento que **sobrevive
sin el video alrededor**, y eso es un grupo mucho más chico.

## Elegir

Leé la transcripción y buscá tramos de 20 a 55 segundos donde se cumplan las tres:

1. Arranca con una idea completa. Si la primera oración necesita el minuto anterior, no es un Short.
2. Tiene un giro adentro: una afirmación, y después algo que la complica o la prueba.
3. Termina en una frase, no en algo que se apaga ("y bueno, nada, eso").

Rankeá los candidatos y mostrale al usuario los cinco mejores con su tiempo de inicio y fin y su
primera línea, para que pueda descartar uno sin leer toda la transcripción.

## Escribir cada uno

- **Una primera línea NUEVA.** La del video largo da por sentado un contexto que este espectador no
  tiene. Escribí la de reemplazo y pasala por `../nc-yt-script/hookscore.py`.
- **Texto en pantalla para los primeros dos segundos**, con palabras distintas a las que se dicen.
- **Un punto de loop**: qué deja planteado la última línea para que la primera lo responda.
- Nota de encuadre vertical: qué se pierde al recortar un cuadro 16:9 y si eso importa.

Usá la voz del usuario (`~/.claude/novacut/voz.md`). Si la línea nueva te quedó con tono de texto
generado, pasala por `/nc-human`.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
