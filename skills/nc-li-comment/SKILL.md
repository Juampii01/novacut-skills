---
name: nc-li-comment
description: >-
  Escribe comentarios en posts de LinkedIn de otras personas que suenan a
  alguien con opinión, no a un bot. Usala cuando el usuario pegue un post y
  quiera un comentario, diga "comentá esto", "¿qué le pongo acá?", "quiero
  interactuar con este post", "escribime un comentario para LinkedIn", o
  quiera una tanda de comentarios para su ronda de interacción. También en
  inglés: "comment on this", "engage with this", "what do I say here".
---

# nc-li-comment

Comentar es lo de más impacto en LinkedIn y lo más fácil de hacer mal. Un
comentario en un post con 400 reacciones lo ve más gente que la mayoría de
los posts propios. Uno genérico no lo ve nadie y le cuesta credibilidad ante
el autor.

## Qué pedir

El usuario pega el texto del post (y el nombre y cargo del autor si los
tiene). Si pega una captura, leela. Si te pasa un link que no podés abrir,
pedile que pegue el texto: no adivines qué decía el post y no uses
automatización de navegador para scrapear el feed.

Leé `~/.claude/novacut/voz.md` si existe, para que el comentario suene al
usuario (voseo, tuteo o usted; si dice malas palabras; qué temas evita).

## Los nueve tipos de comentario

Elegí según lo que el post realmente es. Nunca uses el tipo 1 por defecto.

| # | tipo | cuándo | forma |
| --- | --- | --- | --- |
| 1 | **Sumar un dato** | el post afirma algo que podés respaldar con un número | "Nos pasó igual: el 40% de nuestros..." |
| 2 | **Sumar el caso que falta** | tiene razón pero está incompleto | "Esto se cumple hasta que {condición}. Ahí..." |
| 3 | **Desacuerdo con respeto** | de verdad creés que está mal | primero en qué coincidís, después la bifurcación |
| 4 | **Extender una línea** | una frase del post es la buena | citala y construí sobre ella |
| 5 | **La pregunta de verdad** | el post se salteó la parte difícil | una pregunta, concreta, sin "me interesa saber" |
| 6 | **El recibo** | hiciste lo que describe | qué pasó, en dos frases |
| 7 | **La corrección** | hay un error de hecho | tené razón, sé breve, sé amable, estate seguro |
| 8 | **El reencuadre** | datos correctos, marco equivocado | "Otra forma de leerlo:" |
| 9 | **La frase corta** | el post no necesita nada, querés presencia | menos de 12 palabras, graciosa o cierta |

## Reglas

- **De 2 a 4 frases.** Más largo se lee como secuestro del post. Más corto, como
  relleno.
- **Nunca arranques con** "Excelente post", "Me encantó", "Tal cual", "No
  podría estar más de acuerdo", "Gran reflexión", "Muy interesante" ni con el
  nombre del autor y un signo de exclamación. Son invisibles.
- **Nada de emoji al principio.** Ni 🔥 ni 👏 como primer carácter.
- **Nunca resumas el post.** El autor sabe lo que escribió y los lectores
  también.
- **Una sola idea.** Un comentario con dos puntos se lee como un intento de
  artículo.
- **Decí lo específico.** Si el comentario podría ir debajo de cualquier post
  del tema, no es un comentario, es ruido.
- **El desacuerdo está permitido y funciona**, pero primero va el acuerdo, y
  tiene que ser real.
- **Nunca vendas en un comentario.** Ni la oferta, ni el link, ni "te escribo
  por privado".
- **No inventes experiencias ni números.** Si el tipo 1 o el 6 necesitan un
  dato que el usuario no te dio, preguntá o dejá `{{tu número}}`.

## Salida

Dá **dos opciones de tipos distintos**, con etiqueta, más una línea sobre cuál
publicarías. Pasá las dos por `/nc-li-human` antes: un comentario con una raya
larga se nota mucho más a máquina que un post, porque los comentarios son
cortos y se leen de cerca.

```
OPCIONES DE COMENTARIO  (en el post de Carolina Ruiz sobre contratación)

[6 · El recibo]
Probamos contratar sin CV para 3 puestos el año pasado. Dos fueron las mejores
contrataciones que hicimos. La tercera fue un desastre, y la diferencia fue si
ya habían hecho el trabajo antes, no cómo les fue en la entrevista.

[3 · Desacuerdo con respeto]
Coincido con el problema de la señal. Pero lo que nos funcionó no fue sacar el
CV, fue darle a cada candidato la misma tarea paga de 90 minutos. Mismo
resultado y muchas menos discusiones internas.

Publicá el primero. Son datos tuyos y reconoce un error, que es la parte que
la gente responde.
```

## Modo tanda

Si el usuario quiere una ronda de interacción, pedí los 5 a 10 posts pegados
en un solo mensaje, devolvé un comentario por post en un único bloque, y llevá
una nota en `~/.claude/novacut/li-registro.md` de a quién se comentó esta
semana. Comentar a las mismas tres personas todos los días se nota, y parece
exactamente lo que es.

## Nunca

No publiques automáticamente. No uses una herramienta de navegador para
publicar comentarios en nombre del usuario. La publicación automatizada y el
scraping violan el Acuerdo de Usuario de LinkedIn y ponen la cuenta en riesgo
de restricción. Esta skill escribe el comentario. El usuario lo publica.
