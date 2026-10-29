---
name: nc-li-repurpose
description: >-
  Convierte una pieza larga (video de YouTube, podcast, newsletter, artículo
  de blog, transcripción, clase o llamada con un cliente) en una semana de
  posts de LinkedIn. Usala cuando el usuario diga "reutilizá esto", "sacame
  posts de este video", "tengo una newsletter/transcripción", "pasá esto a
  LinkedIn", o pegue un contenido largo y lo quiera en LinkedIn. También en
  inglés: "repurpose this", "turn this into posts".
---

# nc-li-repurpose

Una buena pieza larga tiene adentro entre cuatro y seis posts. La mayoría saca
uno y tira el resto.

## Qué pedir

Una transcripción, un artículo, una newsletter, un guion, un resumen de una
llamada. Si el usuario te pasa un link de YouTube y en la sesión hay una
herramienta de transcripción, usala; si no, pedile que pegue el texto. Leé
todo antes de extraer nada.

## Extraer, no resumir

El resumen de un video no es un post. Nadie quiere el resumen. Recorré la
pieza y sacá las cosas que se sostienen solas:

| qué sacar | qué es |
| --- | --- |
| **Afirmaciones** | cada frase que arrancaría una discusión |
| **Números** | cada cifra, costo, duración, porcentaje |
| **Historias** | cada momento con una persona, una escena y un costo |
| **Mecanismos** | cada explicación de "esto funciona así..." |
| **Errores** | cada admisión de algo que salió mal |
| **Frases** | cada frase que ya se puede citar tal cual |

Listá lo que encontraste, con totales, antes de escribir nada. Si la pieza da
menos de cuatro elementos, es flaca, y cuatro posts exprimidos de ahí también
van a ser flacos. Decilo.

## Después, armar la semana

Cada elemento se vuelve un post, y cada post tiene que sostenerse solo: el
lector no vio el video y no lo va a ver. Nunca escribas "como conté en mi
último video". El post es la cosa.

Asigná una fórmula de `../nc-li-post/hooks.json` a cada uno, y variá: cinco
posts de una misma fuente con el mismo gancho se leen como una fábrica de
contenido.

Ordenalos en la semana para que la afirmación más fuerte vaya primero, la
historia a mitad de semana y el mecanismo al final, cuando los que leyeron
los anteriores lo están esperando.

## Salida

```
FUENTE: "Por qué dejamos las llamadas de diagnóstico" (18 min, 3.400 palabras)

ENCONTRÉ  4 afirmaciones, 6 números, 2 historias, 3 mecanismos, 1 error, 5 frases citables

SEMANA
MAR  #1  Contra la corriente  Las llamadas de diagnóstico son el impuesto que pagás por tener una web floja
MIÉ  #17 El ancla de tiempo   Recuperamos 6 horas por semana borrando un link de agenda
JUE  #9  Arranque en frío     "¿Nos hacemos una llamadita rápida?"
VIE  #21 El valor directo     El formulario de 4 preguntas que reemplazó la llamada. Robalo.

Decime "escribí el martes" y lo redacto.
```

Después redactá a pedido, de a uno, cada uno por `/nc-li-post` y
`/nc-li-human`. No tires cuatro posts terminados de golpe: van a sonar todos
iguales, y el usuario no va a editar ninguno. Los números y las historias
salen de la fuente: no agregues datos que la pieza no tiene.
