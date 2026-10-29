---
name: nc-li-reply
description: >-
  Maneja las respuestas debajo de los posts de LinkedIn del propio usuario:
  ordena cada comentario según si vale la pena contestarlo y escribe las
  respuestas. Usala cuando el usuario pegue los comentarios de su post, diga
  "respondé estos comentarios", "ayudame con los comentarios", "alguien me
  puso tal cosa en el post", o tenga un crítico o un posible cliente en los
  comentarios. También en inglés: "reply to these", "handle my comments".
---

# nc-li-reply

El hilo de comentarios debajo de tu propio post es donde se decide el
alcance. Cada respuesta es otro evento de interacción en el post, y la
primera hora de respuestas hace la mayor parte del trabajo. Pero no todos los
comentarios valen lo mismo, así que esta skill ordena antes de escribir.

## Qué pedir

El usuario pega los comentarios, idealmente con nombre y cargo. Las capturas
sirven. No scrapees el hilo con una herramienta de navegador.

Leé `~/.claude/novacut/voz.md` si existe: las respuestas tienen que sonar al
usuario, con su registro (vos, tú o usted).

## Primero, ordenar

Poné cada comentario en uno de cinco grupos y decí los totales:

| grupo | qué es | qué recibe |
| --- | --- | --- |
| **CLIENTE POSIBLE** | alguien que describe el problema que el usuario resuelve | una respuesta de verdad + una puerta abierta suave |
| **SUSTANCIA** | suma un dato, discrepa, extiende | la respuesta más larga del hilo |
| **COLEGA** | un nombre junto al que conviene aparecer | una respuesta que le da algo |
| **APOYO** | "excelente post", 🔥, una etiqueta | un like, y como mucho una respuesta de 3 a 8 palabras |
| **RUIDO** | venta, spam, mala fe | nada, o una línea y listo |

Escribí en ese orden, y cortá cuando se acaba el valor.

## Cómo responder

- **Respondé la pregunta de verdad.** Si alguien pregunta cómo, decile cómo, en
  la respuesta. No lo mandes al privado a escuchar algo que podía tener acá.
- **Usá su nombre una vez**, al principio, y nunca con signo de exclamación.
- **Igualá el largo.** Un comentario de dos líneas no recibe seis.
- **A un crítico:** primero concedé la parte cierta, con sus palabras; después
  sostené la parte que creés. Nunca borres, nunca te pongas a la defensiva,
  nunca respondas dos veces en el mismo hilo.
- **A un cliente posible:** respondé completo, en público. La puerta abierta
  es una frase al final, y es una oferta de ayuda, no una venta. El valor en
  público es lo que hace que el próximo te escriba por privado.
- **A una venta en tus comentarios:** ignorala. Responderle le da alcance.
- **No inventes.** Si la respuesta necesita un dato que el usuario no dio,
  dejá `{{tu dato}}` o preguntá.

## Salida

Un bloque, agrupado, cada respuesta lista para copiar y ya pasada por
`/nc-li-human`:

```
RESPUESTAS  ·  17 comentarios  ·  1 CLIENTE POSIBLE, 3 SUSTANCIA, 4 COLEGA, 8 APOYO, 1 RUIDO

CLIENTE POSIBLE
Mariana Gómez - "nos pasa lo mismo con los presupuestos"
> Lo que nos lo resolvió fue sacar la tabla de precios del documento y
> mandarla como una página aparte. Nos ahorró una ronda entera de revisión.
> Si te sirve, te paso la plantilla.

SUSTANCIA
Diego Fernández - no está de acuerdo con la frecuencia
> Es justo: publicar 4 veces por semana me funcionó porque ya tenía 8 meses
> de posts atrás. Arrancando de cero haría lo que decís vos.

APOYO  (dales like, respondé a los tres primeros)
Lucía "Muy bueno" -> Gracias, Lucía.
...

RUIDO  (1)
Salteado: una agencia ofreciendo leads. Responderle le da alcance.
```

Después, el control: **no se publica nada hasta que el usuario diga que sí.**
Las respuestas las pega él.
