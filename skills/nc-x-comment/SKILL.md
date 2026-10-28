---
name: nc-x-comment
description: >-
  Escribe respuestas en posts y hilos de X de otras cuentas que suenan a una
  persona con algo para sumar, no a un "reply guy". Usala cuando el usuario
  pegue un post y quiera una respuesta, diga "respondé esto", "comentá este
  hilo", "quiero interactuar con esto", "¿qué le pongo acá?", "citá este
  tweet", o quiera una tanda de respuestas para su ronda diaria. También en
  inglés: "reply to this", "quote tweet this", "what do I say here".
---

# nc-x-comment

En X, responderle a otros es como crecen las cuentas chicas. Una buena
respuesta debajo de un post con 300.000 vistas la ve más gente que la mayoría
de tus propios posts, y la gente que la lee ya se interesa por el tema. Una
mala la ve la misma gente, y ese es el problema.

## Qué pedir

El usuario pega el post (y el usuario del autor y a qué se dedica, si lo
tiene). Las capturas sirven. Si te pasa un link que no podés abrir, pedile que
pegue el texto. No adivines qué decía un post y no uses un navegador para
scrapear el timeline de nadie.

Leé `~/.claude/novacut/voz.md` si existe, para que la respuesta suene al
usuario.

## Respuesta o cita

Decidilo primero, y decí cuál:

- **Respuesta** cuando sumás a su conversación. Tu respuesta vive en su hilo,
  frente a su audiencia.
- **Cita** cuando tenés una opinión para tu propia audiencia que necesita su
  post como contexto. Una cita es tu post. Tiene que sostenerse sola.
- **Nunca cites para burlarte de una cuenta más chica.** Se lee exactamente
  como es, y que te silencien pesa mucho en contra en el ranking que X publica.

## Los nueve tipos de respuesta

Elegí según lo que el post realmente es. Nunca uses el tipo 1 por defecto.

| # | tipo | cuándo | forma |
| --- | --- | --- | --- |
| 1 | **Sumar un dato** | una afirmación que podés respaldar con un número | "Igual acá: el 40% de nuestros..." |
| 2 | **Sumar el caso que falta** | tiene razón, pero está incompleto | "Vale hasta que {condición}. Ahí..." |
| 3 | **Desacuerdo con respeto** | creés que está mal | primero el acuerdo, después la bifurcación |
| 4 | **Extender una línea** | una frase del post es la buena | construí sobre esa frase |
| 5 | **La pregunta de verdad** | el post se salteó la parte difícil | una pregunta, concreta |
| 6 | **El recibo** | hiciste lo que describe | qué pasó, en dos frases |
| 7 | **La corrección** | un error de hecho | tené razón, sé breve, sé amable, estate seguro |
| 8 | **El reencuadre** | datos correctos, marco equivocado | "Otra forma de leerlo:" |
| 9 | **La frase corta** | el post no necesita nada, querés presencia | menos de 12 palabras, graciosa o cierta |

## Reglas

- **De una a tres frases.** La mayoría de las buenas respuestas tienen menos de
  200 caracteres.
- **Nunca arranques con** "Excelente post", "Esto 👆", "Tal cual", "Facts",
  "💯", "Guardado", "No podría estar más de acuerdo", ni con el nombre del
  autor y un signo de exclamación. Son invisibles.
- **Nunca resumas el post.**
- **Decí lo específico.** Si la respuesta podría ir debajo de cualquier post
  del tema, es ruido.
- **Temprano le gana a ingenioso.** Una respuesta en los primeros 15 minutos
  del post de una cuenta grande se ve. Una mejor dos horas después, no. Por
  eso esta skill trabaja en tandas.
- **Las respuestas entre cuentas que se siguen mutuamente tienen un extra** en
  el ranking que X publica (corré `python3 ../nc-x-plan/weights.py`). Los
  colegas importan.
- **Las respuestas de cuentas Premium se ordenan más arriba.** X lo dice y lo
  llama un efecto "leve". Mencionalo solo si el usuario pregunta: es una
  decisión de compra, no un consejo.
- **No inventes experiencias ni números.** Si el tipo 1 o el 6 necesitan un
  dato que no te dio, preguntá o dejá `{{tu número}}`.

## Salida

**Dos opciones de tipos distintos**, con etiqueta, más una línea sobre cuál
publicar. Las dos pasadas por `/nc-x-human` antes: una respuesta con una raya
larga se nota mucho más a máquina que un post, porque las respuestas son
cortas y se leen de cerca.

```
OPCIONES DE RESPUESTA  (en el post de @autora sobre precios)

[6 · El recibo]
Subimos los precios un 40% en marzo y perdimos 2 de 31 clientes. Los dos que
se fueron eran justo con los que más discutíamos.

[5 · La pregunta de verdad]
¿Qué pasó con las bajas en los planes anuales? Ahí fue donde nos dolió.

Publicá el recibo. Es tu número y reconoce un costo, que es lo que la gente
responde.
```

## Modo tanda

Para una ronda de interacción, pedí entre 5 y 15 posts pegados en un mensaje y
devolvé una respuesta por post, en un bloque. Llevá una nota en
`~/.claude/novacut/x-registro.md` de a quién se le respondió esta semana.
Responderle a las mismas tres personas todos los días se nota, y parece lo
que es.

## Nunca

No publiques la respuesta. No manejes un navegador para publicarla. Las reglas
de automatización de X prohíben las respuestas y menciones automatizadas,
incluidas las que se disparan por búsquedas de palabras clave, y los bots de
respuesta con IA necesitan aprobación escrita de X. Esta skill escribe la
respuesta. El usuario la publica a mano.
