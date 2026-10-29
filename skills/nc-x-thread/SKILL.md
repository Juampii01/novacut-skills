---
name: nc-x-thread
description: >-
  Arma un hilo de X: el primer post que vende todo el hilo, una idea por post,
  cortado para que entre en la cuenta ponderada de X, y un último post que
  lleva a hacer algo. Usala cuando el usuario diga "hilo", "escribime un
  hilo", "pasá esto a un hilo", "armame un hilo de X", o tenga una idea con
  forma de lista o de pasos que quedaría apretada en un post. También en
  inglés: "thread", "write a thread", "tweetstorm".
---

# nc-x-thread

Un hilo es una lista que la gente lee de a un post, y la mayoría frena
después del primero. Así que un hilo es en realidad un post con secuela.
Armalo en ese orden.

En esta carpeta hay una herramienta y funciona:

```bash
python3 thread.py borrador.txt              # lo corta, cuenta cada post y lo revisa
python3 thread.py borrador.txt --number     # agrega 1/7, 2/7 ... (contado en el largo)
python3 thread.py borrador.txt --pack       # junta párrafos cortos en un post
```

Los posts se separan primero en tus propias líneas `---`, después en
párrafos, después en frases. Lo único que se parte entre palabras es una frase
más larga que un post entero, y se avisa cuando pasa. Usa el contador de
`../nc-x-post/count.py`, así que "entra" quiere decir que entra en el editor
de X.

## Hilo, post largo o post único

Decidilo antes de escribir, y decí cuál y por qué:

| la idea | formato |
| --- | --- |
| una afirmación | un solo post. `/nc-x-post` |
| un argumento que necesita espacio, sin pasos naturales | un post largo, si el usuario tiene Premium |
| pasos, una lista, una secuencia, una historia con momentos | un hilo |

La forma más común en que falla un hilo es ser una afirmación cortada en ocho
pedazos. Si eso es lo que tiene el usuario, decíselo y mandalo a `/nc-x-post`.

## Estructura

De 5 a 12 posts. Menos de 3 es un post. Pasados unos 15, llega al final menos
gente de la que lee el post 2.

```
1        EL GANCHO     se sostiene solo. Lo que se promete, dicho en concreto.
                       Fórmula de ../nc-x-post/hooks.json, casi siempre
                       #16 La promesa de hilo, #2 El número revelado o #5 La lista.
2        LO QUE ESTÁ EN JUEGO   por qué le importa al lector, o la prueba de que
                       vos sos quien lo puede decir. El segundo post más leído.
3..N     UNA IDEA CADA UNO   una línea de afirmación, una o dos de por qué. Corto.
N+1      EL RESUMEN    todo el hilo como lista, para que la captura sirva.
ÚLTIMO   EL PEDIDO     uno: seguir, una palabra clave, el link. Uno.
```

## Reglas

- **El post 1 es el 80% del resultado.** Puntualo con
  `python3 ../nc-x-post/hookscore.py --hook "..."` antes de escribir el resto.
- **Nada de "Un hilo 🧵" como gancho.** X ya muestra que es un hilo. Usá la
  línea para lo que prometés. `thread.py` lo marca.
- **Cada post tiene que sobrevivir visto solo.** Los posts del medio de un hilo
  aparecen sueltos en el timeline de otra gente.
- **La numeración es opcional.** Ayuda en una lista y cuesta 5 a 7 caracteres
  por post. `--number` los cuenta por vos.
- **Los links van al final.** Un link en el post 2 es una salida antes de lo
  prometido.
- **El resumen es el post que se captura.** Hacelo independiente.
- **Humanizá cada post.** Pasá el borrador por `/nc-x-human` antes de cortarlo.
  El relleno de hilo ("si este hilo te sirvió, seguime para más") está en el
  lexicón por algo.
- **Nada inventado.** Si un post necesita un dato que el usuario no te dio,
  va `{{tu número}}` y se avisa.

## Salida

El hilo que devuelve `thread.py`, cada post listo para copiar con su cuenta,
después las revisiones y qué hiciste con cada una. Después:

```
HILO LISTO  ·  8 posts
gancho:      #16 La promesa de hilo (puntaje 78 FUERTE)
revisiones:  todos entran · ningún corte a mitad de frase · link solo en el último post
humanizador: 11 marcas sacadas en 8 posts

Respondé "sí" para registrarlo, o decime qué post cambiar.
```

Esta skill no publica nada. El usuario publica el post 1, después le responde
con el post 2, y así, o los pega en el editor de X con el botón +. Con el
"sí", registrá el post 1 en `~/.claude/novacut/x-registro.md` con la fórmula.
