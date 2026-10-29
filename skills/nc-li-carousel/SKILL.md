---
name: nc-li-carousel
description: >-
  Arma un carrusel de LinkedIn (post de documento): el texto slide por slide,
  la portada que se gana el deslizamiento y el PDF para subir. Usala cuando el
  usuario diga "carrusel", "post de documento", "slides para LinkedIn",
  "pasá esto a un carrusel", o tenga una idea con forma de lista que se
  moriría como post de texto. También en inglés: "carousel", "document post",
  "slides for LinkedIn".
---

# nc-li-carousel

Los posts de documento son el formato con más tiempo de lectura en LinkedIn,
porque cada deslizamiento cuenta y un scroll no. El formato premia una idea
partida en pasos. Castiga un post de texto cortado en pedazos.

## Cuándo usarlo en vez de un post de texto

Usá un carrusel cuando la idea tiene **secuencia**: pasos, una cuenta
regresiva, una progresión antes/después, un método con partes. Usá un post de
texto cuando la idea es una sola afirmación. Partir una afirmación en ocho
slides es la forma más común en que fallan los carruseles, y si eso es lo que
tiene el usuario, decíselo y mandalo a `/nc-li-post`.

## Estructura

De 8 a 12 slides. Menos de 8 es un post de texto. Más de 12 y la tasa de
llegada al final se cae.

```
1        PORTADA     el gancho, 6 palabras o menos, más una línea de promesa
2        LO QUE ESTÁ EN JUEGO   por qué importa, en una frase
3-N      UNA IDEA POR SLIDE. Un título de 3 a 7 palabras y como mucho 25
                     palabras abajo. Si una slide necesita un párrafo, son dos.
N+1      RESUMEN     todo como lista, para que la captura sirva sola
ÚLTIMA   LLAMADO     una acción. Seguir, comentar una palabra clave, o el link. Una.
```

## Reglas del texto de las slides

- **La slide 1 es el 80% del resultado.** Seis palabras. Grande. El resto no
  puede salvar una portada que nadie desliza.
- **Numerá cada slide** (3/10). La gente llega más al final cuando ve dónde
  termina.
- **Ninguna slide es un párrafo.** Si no lo podés decir en 25 palabras,
  partilo.
- **La slide de resumen es la que se captura.** Hacela independiente.
- **El usuario o nombre en cada slide**, chico, en una esquina de abajo. Las
  capturas viajan sin vos.
- **Nada inventado.** Si una slide necesita un dato que no tenés, va
  `{{tu número}}` y se avisa.

## Armar el PDF

LinkedIn pide un PDF; 1080x1350 (4:5) ocupa el máximo de pantalla en el
feed, menos de 100 MB y menos de 300 páginas (límites de 2026, pueden
cambiar). Armalo como HTML e imprimilo a PDF:

```bash
# una página por slide, 1080x1350, sin márgenes
# después: Chrome headless --print-to-pdf, o el conversor HTML a PDF que ya uses
```

Escribí el HTML con un `<section>` por slide, `width:1080px; height:1350px;
page-break-after:always`, un solo color de acento y letra de 28px como mínimo:
la gente los lee en el celular en tamaño miniatura. Si el usuario tiene una
marca o un sistema de diseño en el proyecto, usalo y no inventes una paleta.
Ojo con las tildes y la ñ: declará `<meta charset="utf-8">` y usá una
tipografía que las tenga.

## Salida

Primero el texto slide por slide, como lista numerada que el usuario pueda
leer en diez segundos. Después el **texto del post** que acompaña: un
carrusel igual necesita 2 o 3 líneas arriba, que son el gancho real en el
feed. Pasá las dos cosas por `/nc-li-human`. Armá el PDF solo si el usuario
aprueba el texto.

No se sube nada a LinkedIn. El usuario publica el PDF.
