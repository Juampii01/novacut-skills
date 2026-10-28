---
name: nc-yt-chapters
description: >-
  Escribe los capítulos de un video de YouTube a partir de la transcripción,
  validados contra las reglas de YouTube para que aparezcan de verdad. Usala
  para "agregá capítulos", "marcas de tiempo", "timestamps", "dividí este
  video en secciones", "armame los capítulos para la descripción". También:
  "add chapters", "write my timestamps".
---

# nc-yt-chapters

```bash
python3 chapters.py transcripcion.srt --target 8
```

## Las reglas, que no son opcionales

Una lista de capítulos que rompe cualquiera de estas, en silencio, no se convierte en capítulos: el
bloque queda en la descripción sin hacer nada.

- La primera entrada tiene que ser **0:00**.
- Tiene que haber **al menos tres**.
- Cada uno tiene que durar **al menos 10 segundos**.

La herramienta chequea las tres y te avisa cuando una lista es inválida, en vez de dejarte pegarla.
(Son las reglas de YouTube al momento de escribir esto; si YouTube las cambia, manda YouTube.)

## Retitulá cada línea

`chapters.py` encuentra bien los CORTES: puntúa las pausas que hiciste de verdad según cuánto cambia
el vocabulario de un lado al otro. Los títulos que imprime son las palabras del tema, y son un
borrador. Un capítulo que se llama "Miniatura comida ahorrar" es un relleno. Reescribí cada uno
como la promesa de esa sección, en la voz del usuario (`~/.claude/novacut/voz.md`), de tres a cinco
palabras, con mayúscula solo al principio (en español no se escribe Cada Palabra Con Mayúscula).

Los capítulos también diagnostican retención: si una sección no se puede nombrar en cinco palabras,
son dos secciones o es relleno.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
