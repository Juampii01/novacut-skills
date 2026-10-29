---
name: nc-yt-edit
description: >-
  Convierte la transcripción de una grabación cruda en una lista de cortes
  (EDL): silencios, rellenos ("eh", "este", "o sea", "bueno, nada") y
  retomas, con tiempos. Usala para "editá esto", "sacá los silencios",
  "ajustá este video", "me fui por las ramas", "limpiá la grabación", o
  cualquier pedido de acortar material a partir de una transcripción.
  También: "edit this", "cut the dead air", "tighten this video".
---

# nc-yt-edit

Una lista de cortes a partir de una transcripción con tiempos. Imprime los cortes. Vos los aplicás.

```bash
python3 deadair.py transcripcion.srt              # srt, vtt o json de whisper
python3 deadair.py transcripcion.srt --floor 0.35 --json
```

¿No hay transcripción todavía? Pedila, o generala primero: `whisper` o `faster-whisper` con
`--language es`, o los subtítulos automáticos que YouTube genera al subir el video como oculto. No
adivines tiempos.

## Qué encuentra

- **SILENCIO**: huecos más largos que el piso, recortados del MEDIO para que los dos lados conserven
  un respiro. Cortar pegado a la voz es lo que hace que una toma ajustada suene sin aire.
- **RELLENO**: subtítulos que son solo relleno: "eh", "mmm", "este...", "o sea", "bueno, nada",
  "digamos", "a ver", "viste". Tolera letras estiradas ("esteee", "ehhh").
- **RETOMA**: una frase arrancada de nuevo. Se compara contra el último subtítulo que fue habla de
  verdad, no contra el anterior literal, porque casi todas las retomas tienen un "eh" en el medio.
  Se corta la primera toma. También marca las retomas avisadas en voz alta ("perdón, arranco de
  nuevo", "lo digo de nuevo", "me equivoqué").
- **Muletillas dentro de frases** ("o sea", "digamos", "tipo,", "viste"): las cuenta pero no las
  corta, porque sacarlas a mitad de frase suele romper el audio. Es información para el editor.

## Qué no hace

No toca archivos de video ni de audio. No opina sobre tu material de apoyo. Un 40% de recorte en el
informe es un 40% de HABLA: si el video tiene una demo larga sin voz, ese número está mal. Revisá
el informe contra el material antes de confiar en la duración final.

Revisá también las RETOMA antes de aplicarlas: dos frases que empiezan igual a propósito (una
anáfora, una lista) pueden aparecer como retoma.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
