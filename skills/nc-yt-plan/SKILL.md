---
name: nc-yt-plan
description: >-
  Planifica una semana o un mes de videos de YouTube: qué subir, cuándo y en
  qué orden, a la medida del tiempo que el creador tiene de verdad. Usala para
  "planificame la semana", "calendario de contenido", "qué subo", "no sé qué
  hacer en el próximo video", "armame el mes de YouTube". También: "plan my
  week", "content calendar".
---

# nc-yt-plan

Un plan que no entra en la semana es una lista de culpas. Hacé dos preguntas antes de escribir nada:
**cuántas horas tenés de verdad**, y **qué está a medio hacer**.

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario: cómo habla a cámara,
   las palabras que nunca usa, a quién le habla, qué no va a afirmar. Si no existe, pedile **tres
   videos suyos**, leelos o transcribilos, deducí la voz y armá el archivo (o mandalo a `/nc-voz`).
   Los títulos de trabajo tienen que sonar a él, no a un calendario genérico.
2. Nunca inventes un número, un resultado ni una fuente. Si un dato fortalecería el plan y no lo
   tenés, pedíselo o dejá el hueco marcado: `{{tu número}}`.

## La forma de una semana

- **Un video ancla.** El video para el que existe la semana. Se lleva la mayor parte del tiempo y
  sale el día que digan las estadísticas del propio canal: preguntalo, no asumas "el martes".
- **Uno barato.** Hecho con algo que ya existe: un recorte, una reacción, una respuesta al
  comentario que más respuestas tuvo la semana pasada.
- **Shorts sacados del ancla.** Tres, cortados del video largo, no escritos aparte. `/nc-yt-shorts`
  los encuentra.

Tres subidas en una semana de siete días, no siete. Un plan de subir todos los días no lo sostiene
nadie, y los días vacíos son los que hacen que los llenos sobrevivan a una semana mala.

## Qué devolver

Una tabla: día, formato, título de trabajo, la oración que promete, y qué existe ya para ese video.
Abajo, la línea honesta: cuántas horas cuesta esto, y qué se cae primero si la semana se complica.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
