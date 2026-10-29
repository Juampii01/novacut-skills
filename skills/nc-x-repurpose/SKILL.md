---
name: nc-x-repurpose
description: >-
  Convierte una pieza larga (video de YouTube, podcast, newsletter, artículo,
  transcripción, post de LinkedIn o llamada con un cliente) en una semana de
  posts de X y un hilo. Usala cuando el usuario diga "reutilizá esto",
  "sacame tweets de este video", "tengo una newsletter/transcripción", "pasá
  esto a X", o pegue un contenido largo y lo quiera en X. También en inglés:
  "repurpose this", "turn this into tweets".
---

# nc-x-repurpose

Una buena pieza larga tiene adentro entre cinco y ocho posts de X y un hilo.
La mayoría publica un link y tira el resto.

## Qué pedir

Una transcripción, un artículo, una newsletter, un guion o el resumen de una
llamada. Si el usuario te pasa un link de YouTube y en la sesión hay una
herramienta de transcripción, usala; si no, pedile que pegue el texto. Leé
todo antes de extraer nada.

## Extraer, no resumir

Un resumen no es un post. Nadie en X quiere el resumen. Sacá las cosas que se
sostienen solas:

| qué sacar | qué es | en qué se convierte |
| --- | --- | --- |
| **Afirmaciones** | cada frase que arrancaría una discusión | un #1 Contra la corriente o un #21 La frase sola |
| **Números** | cada cifra, costo, duración, porcentaje | un #13 La estadística o un #9 El ancla de tiempo |
| **Historias** | una persona, una escena, un costo | un #3 La confesión de costo o un hilo corto |
| **Mecanismos** | "esto funciona así..." | un hilo, un paso por post |
| **Errores** | lo que salió mal | un #17 El arrepentimiento |
| **Frases** | una frase que ya se puede citar tal cual | un post propio, casi textual |

Listá lo que encontraste, con totales, antes de escribir nada. Si la pieza da
menos de cuatro elementos, es flaca, y los posts exprimidos de ahí también.
Decilo.

## Después, armar la semana

Cada elemento se vuelve un post, y cada uno tiene que sostenerse solo. El
lector no vio el video y no lo va a ver. Nunca escribas "como dije en mi
último video". El post es la cosa.

- Asigná una fórmula de `../nc-x-post/hooks.json` a cada uno, y variá. Seis
  posts de una misma fuente con la misma forma se leen como una fábrica de
  contenido.
- La afirmación más fuerte va primero en la semana. El mecanismo se vuelve el
  hilo, a mitad de semana. El link al original va en una respuesta debajo del
  último post del hilo, si va en algún lado.
- Desde un post de LinkedIn: cortalo hasta la única línea que lo sostiene.
  LinkedIn premia la versión larga; X premia la frase que sobrevive sola.
- Los números y las historias salen de la fuente. No agregues datos que la
  pieza no tiene.

## Salida

```
FUENTE: "Por qué dejamos las llamadas de diagnóstico" (18 min, 3.400 palabras)

ENCONTRÉ  4 afirmaciones, 6 números, 2 historias, 3 mecanismos, 1 error, 5 frases

SEMANA
LUN  #1  Contra la corriente   Las llamadas de diagnóstico son el impuesto que pagás por tener una web floja.
MAR  #9  El ancla de tiempo    Recuperamos 6 horas por semana borrando un link de agenda.
MIÉ  HILO                      El formulario de 4 preguntas que reemplazó la llamada, una pregunta por post.
JUE  #21 La frase sola         Nadie agenda una llamada para enterarse de tu precio.
VIE  #3  La confesión de costo USD 9.000 en ventas perdidas por una "llamadita rápida" que nunca pasó.

Decime "escribí el lunes" y lo redacto.
```

Después redactá a pedido, de a uno, cada uno por `/nc-x-post` (o
`/nc-x-thread`) y `/nc-x-human`. No tires seis posts terminados de golpe: van
a sonar todos iguales, y el usuario no va a editar ninguno.
