---
name: nc-yt-comment
description: >-
  Redacta respuestas a comentarios de YouTube en la voz del creador,
  ordenadas por cuáles vale la pena contestar. Usala para "respondé mis
  comentarios", "ayudame con los comentarios", "alguien preguntó tal cosa",
  "qué comentario fijo", o cuando el usuario pega un hilo de comentarios.
  También: "reply to my comments", "handle my comment section".
---

# nc-yt-comment

La sección de comentarios es una superficie de retención, no un trámite. Las respuestas de las
primeras horas son las que deciden si un hilo se vuelve una conversación que otros leen.

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario: cómo habla, las
   palabras que nunca usa, a quién le habla, qué no va a afirmar. Si no existe, pedile **tres videos
   suyos** (o, mejor para esto, diez respuestas que ya haya escrito), deducí la voz y armá el archivo
   (o mandalo a `/nc-voz`).
2. Nunca inventes un número, un resultado ni una fuente. Si la respuesta necesita un dato que no
   tenés, preguntalo o respondé sin él.

## Primero, clasificar. Siempre.

Ordená lo que pegue el usuario en cuatro pilas y decí cuántos hay en cada una antes de escribir nada:

1. **Preguntas**: respondelas. Son los temas de tus próximos videos, así que anotá las que se
   repiten.
2. **Correcciones**: si tienen razón, decilo de frente y agradecé. Nunca discutas un dato que no
   podés chequear.
3. **Elogios**: respondé algunos, corto, con algo específico de lo que escribieron. Una pared de
   "¡gracias!" idénticos se lee como automática, porque lo es.
4. **Provocaciones**: no se responden. Decilo y seguí. Nunca escribas una chicana, por más merecida
   que sea.

## Escribir la respuesta

- Menos de 30 palabras. Una respuesta larga en un hilo es un artículo que nadie pidió.
- Respondé la pregunta en la primera oración.
- Una pregunta de vuelta, solo si es genuina.
- Sin emojis, salvo que el usuario los use en sus propias respuestas. Fijate en su voz.
- Voseo o tuteo según hable el usuario, no según hable quien comenta.
- Nunca prometas un video que el usuario no acordó hacer.
- Nada de "¡Excelente pregunta!" ni frases de manual: si una respuesta suena a texto generado,
  pasala por `/nc-human`.

## El corazón y el comentario fijado

Decí qué UN comentario fijar y por qué. Fijá la pregunta que más gente también tiene, no el
comentario más lindo. Corazones, generosos: no cuestan nada y se ven.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
