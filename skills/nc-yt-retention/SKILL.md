---
name: nc-yt-retention
description: >-
  Lee el export de retención de audiencia de YouTube Studio, encuentra dónde
  se va la gente de verdad y dice qué cambiar. Usala para "por qué la gente
  deja de mirar", "tengo mala retención", "se me van al principio", "arreglá
  el ritmo", o cuando el usuario pega un gráfico o un CSV de retención.
  También: "why do people stop watching", "my retention is bad".
---

# nc-yt-retention

El gráfico de retención es la única devolución honesta que te da YouTube. Casi nadie lo exporta.

```bash
python3 retention.py retencion.csv --duration 600
python3 retention.py retencion.csv --transcript transcripcion.srt
```

Cómo conseguir el archivo: YouTube Studio -> el video -> Estadísticas -> Participación -> el
gráfico de retención de la audiencia -> el ícono de descarga. (Los nombres del menú cambian según el
idioma y la versión de Studio; si el usuario no lo encuentra, que te mande una captura del gráfico y
leelo a ojo, avisando que es menos preciso.) La herramienta acepta coma o punto decimal y separador
coma o punto y coma, como sale de una computadora configurada en español.

## Tres problemas distintos

- **FUGA DEL GANCHO**: lo que se pierde en los primeros 30 segundos. Menos de 25% es sano. Es
  siempre lo primero que se arregla, y siempre son los primeros quince segundos del guion, nunca la
  edición. `/nc-yt-script` reescribe el gancho.
- **PRECIPICIOS**: caídas bruscas puntuales. Un precipicio es un momento: un cambio de tema sin
  aviso, una publicidad leída, una introducción larga, una retoma que quedó en el corte final. Con
  `--transcript` la herramienta imprime qué se estaba diciendo ahí, que es lo que vuelve el informe
  accionable en vez de solo interesante.
- **GOTEO**: la pérdida pareja a lo largo del medio. Un goteo parejo es ritmo. El arreglo es
  recortar, no reescribir: `/nc-yt-edit` encuentra silencios, rellenos y retomas.

## Qué devolver

Nombrá la fuga más grande y UN cambio para ella. No una lista de cinco. Después, solo si te lo
piden, el resto. Y si la fuga del gancho está sana y el goteo es plano, decí que el video está bien
y que el problema es el empaquetado: mandalo a `/nc-yt-package`.

No inventes porcentajes que no estén en el archivo. Si falta la duración y hace falta, pedila.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
