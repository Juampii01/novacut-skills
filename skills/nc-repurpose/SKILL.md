---
name: nc-repurpose
description: >-
  Convierte un contenido largo (un video de YouTube, un podcast, un vivo, un
  newsletter, un artículo o una llamada con un cliente) en una semana de reels
  y carruseles. Usala cuando el usuario diga "reutilizá esto", "pasá esto a
  reels", "tengo un video/podcast/transcripción", "cortá esto", "sacame
  contenido de este vivo", o pegue algo largo y lo quiera en Instagram. También
  en inglés: "repurpose this", "turn this into reels", "cut this up".
---

# nc-repurpose

Un buen contenido largo tiene adentro entre cuatro y seis posts. La mayoría
saca uno y tira el resto.

## Qué pedir

Una transcripción, un artículo, un newsletter, un guion, el resumen de una
llamada, un vivo. Si el usuario pasa un link y en esta sesión hay una
herramienta de transcripción, usala; si no, pedile que lo pegue. Leé todo
antes de extraer nada.

Si la fuente es un video del propio usuario, pedile también el archivo. Un
Reel armado con su propio material gana siempre a uno armado releyendo sus
propias palabras.

## Extraé, no resumas

El resumen de un video no es un Reel. Nadie quiere el resumen. Recorré el
material y sacá las cosas que se sostienen solas:

| qué sacar | qué es |
| --- | --- |
| **Afirmaciones** | cada frase que arrancaría una discusión |
| **Números** | cada cifra, costo, duración, porcentaje |
| **Historias** | cada momento con una persona, una escena y un costo |
| **Mecanismos** | cada "en realidad esto funciona así..." |
| **Errores** | cada vez que admite algo que salió mal |
| **Frases** | cada frase que ya se puede citar tal cual |

Listá lo que encontraste, con cantidades, antes de escribir nada. Si el
material da menos de cuatro cosas, es flojo, y cuatro posts exprimidos de ahí
también van a ser flojos. Decilo.

## Después, elegí el formato para cada cosa

No todo es un Reel.

- **Afirmación, error, historia**: Reel (`/nc-reel`). Necesitan voz y cara.
- **Mecanismo, lista numerada**: carrusel (`/nc-carousel`). Necesitan
  releerse.
- **Una frase citable**: una pantalla de historia (`/nc-story`), no un post.

## Después, armá la semana

Cada cosa extraída se convierte en un post, y cada post se sostiene
completamente solo. El que mira no vio la fuente y nunca la va a ver. Nunca
escribas "como dije en mi último video". El post es la cosa.

Asigná a cada uno una fórmula de gancho de `nc-reel/hooks.json` y variá.
Cinco posts de la misma fuente con la misma forma de gancho se leen como una
fábrica de contenido, porque lo son.

Si la fuente es un video del usuario, **usá el material real**. El clip donde
dijo la cosa, con la reacción real, le gana siempre a regrabarlo. Cortá en la
frase, no en la respiración.

Ordená la semana así: la afirmación más fuerte primero, la historia a mitad de
semana y el mecanismo al final, cuando los que engancharon con los anteriores
ya lo están esperando.

No agregues números ni resultados que no estén en la fuente. Si un post
necesita uno, `{{tu número}}`.

## Salida

```
FUENTE: "Por qué dejamos de hacer llamadas de diagnóstico" (podcast de 42 min, 8.900 palabras)

ENCONTRÉ  5 afirmaciones, 9 números, 3 historias, 4 mecanismos, 2 errores, 7 frases citables

SEMANA
MAR  REEL      #2   Dejá de hacer llamadas de diagnóstico gratis
                    usá el clip del 14:20, se ríe al final
MIÉ  CARRUSEL       El formulario de 4 preguntas que reemplazó a la llamada
VIE  REEL      #21  "...y nueve días después me pidió el reembolso"
DOM  REEL      #5   Seis horas por semana recuperadas, un link borrado

Decime "escribí el martes" y lo redacto.
```

Junto a cada número de fórmula poné el nombre que tiene en
`nc-reel/hooks.json`.

Después redactá a pedido, de a uno, cada uno pasando por `/nc-reel` (o
`/nc-carousel`) y `/nc-human`. No largues cuatro guiones terminados de golpe.
Van a sonar todos iguales y el usuario no va a grabar ninguno.
