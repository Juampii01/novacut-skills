---
name: nc-comment
description: >-
  Escribe comentarios en posts y reels de otras cuentas de Instagram que suenan
  a una persona con opinión, no a un bot. Usala cuando el usuario pegue un post
  o un reel y quiera un comentario, diga "comentá esto", "¿qué le pongo acá?",
  "escribime un comentario", "quiero interactuar con esta cuenta", o quiera una
  tanda para su ronda diaria de interacción. También en inglés: "comment on
  this", "engage with this", "what do I say here".
---

# nc-comment

Comentar son los veinte minutos de más impacto en Instagram y los más fáciles
de hacer mal. Un comentario arriba de todo en un reel con 40.000 vistas lo ve
más gente que la mayoría de los posts propios de una cuenta, y es el único
lugar donde un desconocido puede tocar y caer directo en un perfil.

Un comentario genérico es peor que ninguno. Cuesta un toque que no lleva a
nada y marca la cuenta como "de grupo de engagement" ante la única persona cuya
opinión importaba: el creador.

## Qué pedir

El usuario pega el texto del post o reel, o una captura, con el nombre de la
cuenta. Si te pasa un link que no podés abrir, pedile que lo pegue. No uses una
herramienta de navegador para scrapear el feed y no publiques nada.

## Los nueve tipos de comentario

Elegí según lo que el post realmente es. Nunca uses el tipo 1 por defecto.

| # | tipo | cuándo | forma |
| --- | --- | --- | --- |
| 1 | **Sumar un dato** | el post afirma algo que podés respaldar con un número | "Nos pasó igual: el 40% de..." |
| 2 | **Sumar el caso que falta** | el post tiene razón pero está incompleto | "Esto se cumple hasta que {condición}." |
| 3 | **Desacuerdo con respeto** | de verdad creés que está mal | primero nombrá en qué coincidís, después la bifurcación |
| 4 | **Extender una línea** | una línea del post es la buena | citala y construí sobre ella |
| 5 | **La pregunta de verdad** | el post se salteó la parte difícil | una pregunta, concreta |
| 6 | **El recibo** | hiciste lo que describen | qué pasó, en dos frases |
| 7 | **La corrección** | hay un error de hecho | tené razón, sé breve, sé amable, estate seguro |
| 8 | **El reencuadre** | datos correctos, marco equivocado | "Otra forma de leerlo:" |
| 9 | **La frase corta** | el post no necesita nada, querés presencia | menos de 10 palabras, tiene que ser graciosa o cierta |

## Reglas

- **Una a tres frases.** Los comentarios de Instagram se leen en una columna
  angosta debajo de un video. Un párrafo queda escondido detrás de "más" y
  nadie lo toca.
- **Nunca arranques con** "Excelente post", "Me encantó", "Tal cual", "Esto
  👏", "Necesitaba leer esto hoy", ni con el nombre del creador y un signo de
  exclamación. Todos son invisibles.
- **Nada de comentarios solo con emojis**, y nunca un emoji como primer
  carácter.
- **Nunca resumas el reel.** Todos los que lo están viendo lo acaban de ver.
- **Una sola idea.** Un comentario con dos puntos se lee como un secuestro del
  hilo.
- **Decí lo específico.** Si el comentario podría ir debajo de cualquier post
  sobre el tema, no es un comentario, es ruido.
- **Nunca vendas.** Ni la oferta, ni el link, ni "pasá por mi perfil". Es la
  forma más rápida de que te bloquee justo la persona a la que querías llegar.
- **Temprano importa más acá que en ningún lado.** Un comentario en la primera
  hora de un reel que después explota viaja con él.
- **No inventes experiencias ni números.** Si el tipo 1 o el 6 necesitan un
  dato que el usuario no te dio, dejá `{{tu número}}` o preguntá.

## Salida

Dá **dos opciones de tipos distintos**, con etiqueta, más una línea sobre cuál
publicarías y por qué. Pasá las dos por `/nc-human` antes: los comentarios son
cortos, así que una raya larga o una frase hecha se nota mucho más que en un
caption.

```
OPCIONES DE COMENTARIO  (en el reel de @cuenta sobre precios)

[6 · El recibo]
Subimos los precios un 40% en marzo y perdimos un solo cliente, justo el que
nos llenaba el WhatsApp a las 11 de la noche. Tardé ocho meses en animarme.

[3 · Desacuerdo con respeto]
Coincido con lo del anclaje. Donde no estoy de acuerdo es en hacerlo a mitad
de proyecto. Lo probamos y nos costó una renovación que venía bien.

Publicá el primero. Concede algo y tiene un número.
```

## Modo tanda

Para una ronda de interacción, pedí los 5 a 10 posts pegados en un solo
mensaje, devolvé un comentario por post en un único bloque y llevá una nota en
`~/.claude/novacut/log.md` de a quién se comentó esta semana. Comentar en las
mismas tres cuentas todos los días se nota, y parece exactamente lo que es.

## Nunca

No publiques automáticamente, no automatices comentarios y no uses una
herramienta de navegador para publicar en nombre del usuario. La interacción
automatizada viola los Términos de Uso de Instagram y hace que bloqueen
acciones de la cuenta. Esta skill escribe el comentario. El usuario lo publica.
