---
name: nc-reply
description: >-
  Maneja los comentarios debajo de los reels y posts propios del usuario:
  redacta respuestas para los que vale la pena contestar, ordenados por cuáles
  valen más. Usala cuando el usuario pegue sus comentarios, diga "respondé
  estos", "ayudame con los comentarios", "alguien me puso X en el reel", "¿qué
  le contesto?", o esté lidiando con un crítico, un hater o un posible cliente
  en los comentarios. También en inglés: "reply to these", "handle my
  comments".
---

# nc-reply

El hilo de comentarios debajo de tu propio post es donde se decide el alcance.
Cada respuesta es otra interacción en el post, las respuestas de la primera
hora hacen la mayor parte del trabajo, y en Instagram una respuesta también
puede ser un Reel, que es el movimiento más desaprovechado de toda la
plataforma.

Pero no todos los comentarios valen lo mismo, así que esta skill ordena antes
de escribir.

## Qué pedir

El usuario pega los comentarios, idealmente con el @. Las capturas sirven. No
scrapees el hilo con una herramienta de navegador.

## Primero, clasificar

Ordená cada comentario en uno de seis grupos y decí cuántos hay de cada uno:

| grupo | qué es | qué recibe |
| --- | --- | --- |
| **PALABRA CLAVE** | la palabra que pediste que comenten | lo prometido, enviado a mano o con tu herramienta aprobada |
| **CLIENTE POTENCIAL** | alguien que describe el problema que resolvés | una respuesta de verdad en público, y después una puerta |
| **APORTE** | suma datos, discrepa, extiende | la respuesta más larga del hilo |
| **PREGUNTA** | una pregunta que tiene mucha gente | se convierte en un Reel, no solo en una respuesta |
| **APOYO** | "🔥", "buenísimo", una etiqueta | un like y de 3 a 8 palabras como mucho |
| **RUIDO** | autopromoción, spam, mala fe, provocación | nada, o una línea y listo |

Escribí en ese orden y frená cuando deja de valer la pena.

## El movimiento que casi nadie hace

Si una pregunta en los comentarios es una que también tienen otras treinta
personas, **respondela con un Reel**. Instagram engancha el comentario al video
nuevo como sticker, a quien preguntó le llega la notificación, y una pregunta
con demanda real se convierte en un post con el gancho ya escrito. Marcá cada
PREGUNTA que califique y pasásela a `/nc-reel` como fórmula #16 (la pregunta
textual; fijate el nombre exacto en `nc-reel/hooks.json`).

## Cómo responder

- **Respondé lo que preguntan.** Si alguien pregunta cómo, decile cómo, en la
  respuesta. No lo mandes al DM para escuchar algo que podía tener ahí.
- **Usá su nombre una vez**, al principio, sin signo de exclamación.
- **Igualá el largo.** Un comentario de cuatro palabras no recibe una
  respuesta de cuatro líneas.
- **A un crítico:** primero concedé la parte que es cierta, con sus palabras,
  y después sostené tu postura. Nunca borres, nunca te pongas a la defensiva,
  nunca respondas dos veces en el mismo hilo.
- **A un hater:** nada. Una respuesta es alcance, y alcance es lo que vino a
  buscar. Si es agresivo, ocultá el comentario. Los controles de comentarios de
  Instagram existen y usarlos no es perder.
- **A un cliente potencial:** respondé completo en público. La puerta es una
  frase al final y es un ofrecimiento de ayuda, no una venta. La respuesta
  pública es lo que hace que la próxima persona te escriba por DM.

## Comentarios con palabra clave

Si el post pedía comentar una palabra clave, esos comentarios son todo el
sentido del post. Cada uno es una persona que levantó la mano. Respondé a cada
uno y después mandá lo prometido. Si el usuario tiene la automatización armada
con las herramientas propias de Instagram o con un partner aprobado (como
ManyChat), decilo y dejala correr; si no, las respuestas son a mano y a este
volumen está bien. Nunca mandes DMs masivos a gente que no comentó. Para el
mensaje de entrega, usá `/nc-dm`.

## Salida

Un bloque, agrupado por tipo, cada respuesta lista para copiar y ya
humanizada con `/nc-human`:

```
RESPUESTAS  ·  84 comentarios  ·  41 PALABRA CLAVE, 2 CLIENTE POTENCIAL, 3 APORTE, 2 PREGUNTA, 34 APOYO, 2 RUIDO

PALABRA CLAVE  (41)  mandá la plantilla. Una línea a cada uno, mismo tono, no copiar y pegar.

CLIENTE POTENCIAL
@lucia.inmuebles - "nos pasó exactamente esto en junio con un propietario"
> Lucía, lo que a nosotros nos lo arregló fue no cobrar contra "aprobación"
> sino contra entrega. Si te sirve, te paso el texto de la cláusula.

PREGUNTA -> REEL
@nico_fitcoach - "¿y si el cliente se niega a firmarlo?"
  34 likes en este comentario. Eso es un Reel, no una respuesta. Fórmula #16.

RUIDO  (2)  salteados. Responder les da alcance.
```

Después, la compuerta: no se publica nada hasta que el usuario dice que sí. Él
pega las respuestas.
