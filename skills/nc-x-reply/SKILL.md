---
name: nc-x-reply
description: >-
  Maneja las respuestas debajo de los posts de X del propio usuario: ordena
  cada una y escribe las contestaciones en el orden que importa. Usala cuando
  el usuario pegue las respuestas de su post, diga "contestá estas
  respuestas", "ayudame con las menciones", "alguien me puso tal cosa debajo
  del post", "¿cómo le respondo a esto?", o tenga un crítico, un troll o un
  posible cliente en las menciones. También en inglés: "reply to these",
  "handle my replies".
---

# nc-x-reply

Las respuestas debajo de tu propio post son donde un post sigue andando o se
frena. El ranking que publica X pesa una respuesta predicha muy por encima de
un like predicho, y suma un extra cuando las dos personas se siguen
mutuamente (corré `python3 ../nc-x-plan/weights.py` para los valores de hoy).
Un hilo con el autor adentro se sigue mostrando. Un post que el autor
abandonó, no.

Pero no todas las respuestas valen lo mismo, así que esta skill ordena antes
de escribir.

## Qué pedir

El usuario pega las respuestas, idealmente con los usuarios. Las capturas
sirven. No scrapees el hilo con una herramienta de navegador.

Leé `~/.claude/novacut/voz.md` si existe, para que las contestaciones suenen
al usuario.

## Primero, ordenar

Poné cada respuesta en un grupo y decí los totales:

| grupo | qué es | qué recibe |
| --- | --- | --- |
| **CLIENTE POSIBLE** | alguien que describe el problema que resolvés | una respuesta de verdad, después una frase de puerta abierta |
| **SUSTANCIA** | suma un dato, discrepa, extiende | la mejor respuesta del hilo |
| **COLEGA** | una cuenta junto a la que conviene aparecer | una respuesta que le devuelve algo |
| **PREGUNTA** | pregunta cómo, qué, cuál | la respuesta, ahí mismo, no "te mando DM" |
| **APOYO** | "buenísimo", un emoji, una etiqueta | un like. Una respuesta corta a las primeras, como mucho |
| **RUIDO** | spam, bots, cebo, mala fe | nada |

Escribí en ese orden y cortá cuando se acaba el valor.

## Cómo responder

- **Dentro de la primera hora.** Es cuando responder más le suma al post.
- **Respondé la pregunta en la respuesta.** Mandar a la gente al privado por
  algo que podía tener en público es como se muere un hilo.
- **Igualá el largo.** Una respuesta de una línea no recibe seis.
- **A un crítico:** primero concedé la parte cierta, con sus palabras; después
  sostené la parte que creés. Una vez. Nunca dos en el mismo hilo.
- **A un cliente posible:** respondé completo, en público. La puerta abierta es
  una frase, una oferta de ayuda, no una venta. El valor en público es lo que
  hace que el próximo te escriba.
- **A cebo, un bot o una avalancha:** nada. Responder le da alcance. Si es
  abusivo: ocultar la respuesta, silenciar o bloquear, en ese orden de fuerza.
- **Nunca cites una respuesta para burlarte.** Es un segundo post con su
  nombre adentro, y que te silencien pesa mucho en contra.
- **No inventes datos.** Si una contestación necesita un número que el usuario
  no dio, dejá `{{tu número}}` o preguntá.

## Salida

Un bloque, agrupado, cada contestación lista para copiar y ya pasada por
`/nc-x-human`:

```
RESPUESTAS  ·  23  ·  2 CLIENTE POSIBLE, 3 SUSTANCIA, 2 COLEGA, 4 PREGUNTA, 9 APOYO, 3 RUIDO

CLIENTE POSIBLE
@vale_consultora  "nos pasa lo mismo con el onboarding"
> Lo que nos lo resolvió fue borrar la llamada de bienvenida y mandar un video
> de 4 minutos. Más gente terminó el onboarding, no menos. Si te sirve, te
> paso el guion.

PREGUNTA
@nico_dev  "¿qué modelo usaste para esto?"
> Claude, con el archivo de skill haciendo casi todo el trabajo. El modelo
> importó menos que el archivo.

APOYO  (dales like; respondé a las tres primeras)
...

RUIDO  (3)
Salteado: dos bots y una cuenta que junta respuestas. Responderles les da alcance.
```

Después, el control: **no se publica nada hasta que el usuario diga que sí**,
y después el usuario publica cada contestación a mano. Las reglas de
automatización de X solo permiten respuestas automatizadas a quien lo pidió,
y esto no es eso.
