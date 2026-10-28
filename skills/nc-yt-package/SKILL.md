---
name: nc-yt-package
description: >-
  Escribe y revisa el título y la miniatura de un video de YouTube como un
  solo par, chequeando largo, repeticiones, mayúsculas, palabras clave y
  vaguedad antes de publicar. Usala para "ideas de título", "cómo le pongo a
  este video", "texto para la miniatura", "tengo bajo CTR", "nadie hace
  clic", o cualquier pedido de renombrar o reempaquetar un video. También:
  "title ideas", "thumbnail text".
---

# nc-yt-package

El título y la miniatura son UNA unidad. Escribirlos por separado es por qué falla la mayoría del
empaquetado: la miniatura repite el título, y la mitad de la superficie de clic dice dos veces lo
mismo.

```bash
python3 title.py --title "..." --thumb "SIN AMASAR"
python3 title.py titulos.txt                                   # uno por línea, rankeados
python3 title.py titulos.txt --clave "pan casero sin amasar"   # chequea la búsqueda objetivo
```

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario: cómo habla a cámara,
   las palabras que nunca usa, a quién le habla, qué no va a afirmar. Si no existe, pedile **tres
   videos suyos**, leelos o transcribilos, deducí la voz y armá el archivo (o mandalo a `/nc-voz`).
   Un título que no suena a él promete un video que no es el suyo.
2. Nunca inventes un número, un resultado ni una fuente. Si un dato fortalecería el título y no lo
   tenés, pedíselo o dejá el hueco marcado: `{{tu número}}`.

## Reglas que chequea la herramienta, y por qué

- **60 caracteres** es donde corta la búsqueda de escritorio, **40** el inicio en el celular. Se
  informan los dos porque fallan distinto: el corte de escritorio pierde la cola, el del celular
  puede perder el tema. En español los títulos salen más largos que en inglés: poné el tema al
  principio. (Son cortes aproximados y YouTube los puede cambiar.)
- **La miniatura no repite el título.** Palabras distintas, misma promesa.
- **Tres palabras como máximo en la miniatura.** A tamaño de feed, una cuarta palabra es una mancha.
- **Un número, un nombre o una fecha** le ganan a cualquier adjetivo ("increíble", "brutal",
  "el secreto definitivo").
- **Dos palabras en MAYÚSCULAS es el techo** antes de que se lea como spam.
- **Mayúscula solo al principio.** "Cómo Hacer Pan Casero En Casa" es un calco del inglés; en español
  va "Cómo hacer pan casero en casa" (los nombres propios, como WhatsApp, sí van con mayúscula).
- **Signos de pregunta de apertura y cierre**: "¿Por qué...?", no "Por qué...?".
- **Palabras clave** (`--clave`): si el video apunta a una búsqueda, sus palabras tienen que estar en
  el título y, mejor, antes del corte del celular. Para decidir cuál es esa búsqueda, `/nc-yt-seo`.

## Escribí diez, quedate con dos

Generá diez títulos, pasalos todos por `title.py`, y mostrale al usuario los tres mejores con su
puntaje y el problema puntual de cada uno. Para el ganador, escribí el brief de la miniatura: la
expresión, el encuadre, las tres palabras, y qué tiene que hacer el fondo para mantener contraste a
tamaño de feed.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
