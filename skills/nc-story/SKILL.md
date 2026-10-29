---
name: nc-story
description: >-
  Escribe las historias de Instagram del día: la secuencia cuadro por cuadro,
  qué sticker va en cada lugar y el que lleva a la gente a los mensajes. Usala
  cuando el usuario dice "historias", "qué subo a mis historias", "secuencia de
  stories", "idea para una encuesta", "no tengo nada para subir a historias",
  "write my stories", "story sequence", o quiere vender algo sin hacer un post
  sobre eso.
---

# nc-story

Las historias no son un feed más chico. El feed es donde te encuentran los
desconocidos. Las historias son donde la gente que ya te sigue decide si sos
alguien a quien comprarle, y son el único lugar de Instagram donde un toque se
convierte en una conversación en un solo movimiento.

Nadie fuera de tus seguidores las ve, así que el trabajo es totalmente
distinto: profundidad, no alcance.

## La forma del día

De tres a siete cuadros por día. Pasando los siete, sube la tasa de toques para
adelantar y los últimos cuadros se reproducen para nadie, que es justo donde la
gente pone el pedido.

```
1       LA APERTURA   algo que está pasando hoy, con una cara o una mano.
2-3     EL MEDIO      el contenido en sí: el proceso, el resultado, el error.
4       EL PEDIDO     un sticker. Encuesta, caja de preguntas, quiz o link.
5       EL CIERRE     la respuesta, el resultado, o lo que viene mañana.
```

Poné el pedido en el cuadro 4, no en el 7. La retención cae con cada toque y el
pedido tiene que verlo la gente que todavía está.

## Los stickers, y para qué sirve cada uno

| sticker | trabajo | usalo cuando |
| --- | --- | --- |
| **Encuesta** | el toque más barato que existe | querés cantidad de respuestas, no información |
| **Caja de preguntas** | juntar las palabras exactas que usa la gente | necesitás ideas de contenido u objeciones, textuales |
| **Quiz** | enseñar dejando que se equivoquen | hay una creencia equivocada común en el nicho |
| **Deslizador** | medir el clima | nada importante. Divertido, poco valor |
| **Link** | la única superficie con clic además de la bio | hay un lugar real a donde ir |
| **Cuenta regresiva** | una fecha límite a la que la gente se puede suscribir | un lanzamiento, un vivo, un cierre de inscripciones |
| **Agregá la tuya** | alcance más allá de tus seguidores, de vez en cuando | la consigna la puede responder cualquiera del nicho |

(Los nombres y la disponibilidad de los stickers son datos de plataforma y
pueden cambiar.)

La caja de preguntas es la más subestimada de la lista. Cada respuesta es un
caption, un gancho de Reel o un primer mensaje escrito con las palabras de la
audiencia. Pasáselas a `/nc-reel` como fórmula #16 (La pregunta textual).

## Reglas

- **Una cara o una mano en el primer cuadro.** Texto sobre fondo de color se
  adelanta con un toque, y el primer cuadro decide si se ven los demás.
- **Una idea por cuadro.** Nadie lee un párrafo en una historia.
- **El texto en el centro.** En 1080x1920, nada arriba de y=250 ni abajo de
  y=1600. Arriba está la fila del perfil y abajo la barra de respuesta.
- **Hablale a una persona.** "Vos" (o "tú", según `voz.md`), en singular. Las
  historias son lo más parecido a un DM que no es un DM.
- **No compartas tu propio post en historias sin decir nada.** Es el cuadro más
  ignorado de la plataforma. Si apuntás a un post, contá qué pasó en los
  comentarios y por qué vale la pena volver.
- **Vendé en historias, no en posts.** Tres cuadros de contexto, uno de oferta,
  uno de prueba. Esa secuencia vende más que un post sobre lo mismo y no te
  cuesta alcance. La prueba tiene que ser real: si el usuario no tiene un
  testimonio o un número, va `{{tu prueba}}` y se avisa, no se inventa.

## El embudo a DM, bien hecho

La secuencia que funciona: una historia que nombra un problema, una caja de
preguntas o una encuesta que le permite a la gente decir "ese soy yo", y
después una respuesta a cada persona que contestó. La conversación arranca
porque ellos hablaron primero.

Las respuestas automáticas por palabra clave en DM son una función real y
permitida para cuentas profesionales, a través de las herramientas de
Instagram y de partners aprobados. Mandar DMs masivos a gente que no
interactuó no lo es, y es lo que hace que restrinjan cuentas. La regla es
simple: **ellos actúan primero, después respondés vos.** Esta skill escribe los
mensajes; no los manda. Para el primer mensaje y los seguimientos, usá
`/nc-dm`.

## Salida

Los cuadros en orden, cada uno con qué se ve, qué se dice y qué sticker, más
qué hacer con las respuestas:

```
HISTORIAS  ·  martes  ·  5 cuadros

1  [selfie, caminando]      "Tercer pedido de devolución en el año. Mismo motivo."
2  [grabación de pantalla]  la cláusula, resaltada
3  [hablando a cámara]      "La aprobación es una sensación. La entrega es una fecha."
4  [encuesta]               "¿Alguna vez te clavaron con una aprobación tardía?"  Sí / Todavía no
5  [texto sobre foto]       "Respondeme y te paso la cláusula."

Después: a todos los que votaron Sí, una respuesta. Ese es todo el embudo.
```

No se publica nada. El usuario lo sube.
