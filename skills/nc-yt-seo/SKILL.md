---
name: nc-yt-seo
description: >-
  Escribe la descripción, las etiquetas y el texto pensado para la búsqueda
  de un video de YouTube, apuntando a lo que una persona real escribe en el
  buscador. Usala para "escribime la descripción", "tags", "etiquetas",
  "SEO", "que este video se encuentre", "nadie lo encuentra". También:
  "write my description", "YouTube SEO".
---

# nc-yt-seo

La búsqueda es una palanca más chica que el empaquetado y más grande de lo que la gente cree para
los videos que no vencen (tutoriales, recetas, "cómo hacer"). Si el video apunta al feed de
suscriptores, decilo y poné el esfuerzo en `/nc-yt-package`.

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario: cómo habla, las
   palabras que nunca usa, a quién le habla, qué no va a afirmar. Si no existe, pedile **tres
   videos suyos**, leelos o transcribilos, deducí la voz y armá el archivo (o mandalo a `/nc-voz`).
2. Nunca inventes un número, un resultado ni una fuente. Si un dato fortalecería la descripción y no
   lo tenés, pedíselo o dejá el hueco marcado: `{{tu número}}`.

## La descripción

- **Las dos primeras líneas son las únicas que alguien lee.** Se ven antes del "...más" y son el
  fragmento que aparece en la búsqueda. Decí qué le da el video, con las palabras que esa persona
  habría escrito en el buscador.
- Después, el link o el recurso, si hay, para que quede arriba del corte.
- Después, los capítulos (`/nc-yt-chapters` los escribe).
- Después, la versión larga: qué se cubre, para quién es, qué da por sabido.

Nada de "¡No te olvides de dar like y suscribirte!" en la primera línea, ni frases de relleno tipo
"en el video de hoy vamos a sumergirnos en...". Si la descripción suena a texto generado, pasala
por `/nc-human`.

## Etiquetas, con honestidad

Las etiquetas son una señal débil y YouTube lo dijo. Usalas para desambiguar y listo: variantes de
escritura, nombres de herramientas, abreviaturas que la gente realmente escribe. En español sumá las
variantes que la gente tipea de verdad: **sin tildes** ("como hacer pan casero"), regionalismos
("palta" / "aguacate", "celular" / "móvil", "departamento" / "piso") y la versión en inglés si el
término técnico se busca así ("CapCut tutorial"). Quince alcanzan. Una pared de etiquetas no es una
estrategia, y meter etiquetas que no tienen que ver va contra las normas de YouTube.

## La prueba de la búsqueda

Antes de entregar, escribí las tres búsquedas que este video debería ganar y chequeá que el título y
las dos primeras líneas de la descripción tengan esas palabras. Para el título podés usar
`python3 ../nc-yt-package/title.py --title "..." --clave "la búsqueda"`. Si no las tienen, el
problema es el título, no la descripción.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
