---
name: nc-human
description: >-
  Le saca la huella de máquina a cualquier borrador en castellano (rayas,
  palabras de relleno típicas de la IA, caracteres invisibles) y lo puntúa con
  un panel de cinco chequeos antes de que salga. Usala siempre que un texto
  tenga que sonar humano, cuando el usuario dice "humanizalo", "¿esto suena a
  IA?", "sacale las rayas", "suena a ChatGPT", "que no parezca escrito por un
  robot", "humanize this", "does this sound like AI", y antes de mostrarle
  cualquier caption, guion, comentario, respuesta o DM.
---

# nc-human

En esta carpeta hay dos herramientas y las dos funcionan. Usalas. No lo midas a
ojo.

```bash
python3 humanize.py borrador.txt --report       # lo limpia y muestra qué cambió
python3 detect.py borrador.txt                  # lo puntúa, cinco chequeos
python3 detect.py antes.txt despues.txt         # muestra la diferencia
```

Las dos leen `slop.json`: más de 350 palabras y frases de relleno típicas de
texto generado en castellano, con su reemplazo simple; 18 clases de caracteres
invisibles; 11 sustituciones tipográficas; y 18 señales de estructura. No es
una traducción del inglés: son las muletillas que escribe un modelo en español
("en el mundo actual", "es importante destacar que", "sin lugar a dudas",
"potenciar", "sumergirse en", "llevar al siguiente nivel", "en conclusión",
"¡No te lo pierdas!", "seguime para más"). El último bloque es propio de
Instagram: lo que solo aparece en captions y locuciones.

Al buscar no importan las tildes ni las mayúsculas: "increible" y "Increíble"
caen igual. Primero se busca la forma exacta, así el voseo se respeta
("optimizá" pasa a "mejorá", "optimiza" a "mejora").

El archivo está para editarlo. Si el usuario tiene una palabra que usa siempre
y el lexicón se la saca, borrala de `slop.json`.

## Por qué importa más en Instagram de lo que parece

Los captions son cortos y los guiones se dicen en voz alta. Una línea que suena
escrita en un caption de 600 caracteres es una parte más grande del texto que
la misma línea en un ensayo, y una locución que nadie diría naturalmente se
nota en la primera toma. Lo que delata acá no es un detector marcando el post:
es una persona que pasa de largo porque suena a folleto, o un creador que se
traba con su propio guion.

## Qué se arregla solo

**1. Caracteres invisibles.** Espacios de ancho cero y unidores, guiones
blandos, marcas de orden de bytes, caracteres de etiqueta Unicode, separadores
invisibles, espacios duros y finos. Un teclado no los produce. Sobreviven al
copiar y pegar, no se ven en ningún editor, y son lo más mecánico del texto
generado. `humanize.py` los borra todos, incluido cualquier carácter de formato
que no tenga nombrado.

**2. Tipografía.** Raya a coma (una raya de diálogo al principio de línea pasa
a guion), semirraya a guion, comillas curvas a rectas, puntos suspensivos de un
carácter a tres puntos, viñeta a guion. Los signos de apertura `¿` y `¡` NO se
tocan: son castellano y cualquier teclado en español los tiene. Las comillas
latinas `« »` tampoco.

**3. El lexicón.** Cada término se cambia por una palabra simple o se borra,
respetando mayúsculas y sin tocar links, `#hashtags` ni `@menciones`. Después
limpia la puntuación que queda huérfana (un "¡!" vacío, una coma al principio
de línea, una "y" suelta).

## Qué NO se arregla solo

Las señales de estructura se **marcan, no se reescriben**, porque cambiar la
forma de una oración necesita criterio:

- "No es solo X, es Y" y "No solo X, sino también Y"
- "No se trata de X. Se trata de Y."
- Tríadas: "la constancia, la disciplina y la pasión."
- Preguntas retóricas para revelar algo: "¿El resultado?"
- El preámbulo de video: "en este video te voy a mostrar"
- Listas con emojis de viñeta
- Tres o más palabras gritadas seguidas
- Títulos Con Mayúscula En Cada Palabra (calco del inglés)
- Exclamaciones en cadena: "¡Increíble! ¡No te lo pierdas!"
- Paredes de hashtags
- Carnadas de reflejo: "seguime para más", "etiquetá a alguien que", "dale like si"

Esa lista es tu trabajo. Reescribí cada línea marcada a mano, manteniendo el
sentido, y volvé a correr `detect.py`. Es la parte que mueve el puntaje de
REVISAR a PASA, y es la parte que un script no puede hacer.

## Los cinco chequeos

`detect.py` puntúa cinco señales de 0 a 100; más alto es más humano:

| chequeo | qué mide | cómo se ve la máquina |
| --- | --- | --- |
| VARIACIÓN | variación del largo de las oraciones | todas las oraciones del mismo largo |
| CONCRECIÓN | números, nombres, datos cada 100 palabras | sustantivos abstractos, sin cifras |
| RELLENO | apariciones del lexicón cada 100 palabras | vocabulario de folleto |
| HUELLA | invisibles, rayas, comillas curvas cada 1.000 caracteres | tipografía perfecta |
| VOZ | oralidad, persona, señales de estructura | sin muletillas, revelaciones montadas |

En inglés la voz se mide con contracciones; en castellano no existen, así que
`detect.py` mide **oralidad**: muletillas y marcas de habla ("o sea", "posta",
"la verdad", "che", "neta", "oye", "mirá,") y voseo ("tenés", "fijate",
"contame"). La lista es panlatina a propósito. Si el usuario escribe en un
registro formal porque su marca es así, la VOZ va a dar más baja y está bien:
decilo en vez de llenarle el texto de muletillas que no usa. Lo que manda es
`~/.claude/novacut/voz.md`.

El veredicto pesa el promedio en un 60% y el **chequeo más flojo** en un 40%,
porque con una sola señal alcanza. PASA necesita 70 o más en total y ningún
chequeo debajo de 55.

## Decilo con honestidad

Son cinco heurísticas locales modeladas sobre las señales que miran los
detectores públicos. Corren enteras en la máquina del usuario y no se sube
nada. **No** son GPTZero, Originality, Copyleaks, Winston ni Turnitin, no
llaman a esas APIs y no pueden prometer su veredicto. Arreglar lo que miden
suele mover esos números, porque miden las mismas cosas de fondo. Esa es toda
la afirmación. No hagas una más grande en nombre del usuario, y nunca le digas
que su texto es "indetectable".

## Orden de trabajo

1. `humanize.py borrador.txt -o limpio.txt --report`
2. Leé las señales de estructura. Reescribí esas líneas vos.
3. `detect.py borrador.txt limpio.txt` para mostrar el antes y el después.
4. Si el veredicto no es PASA, arreglá el chequeo más flojo que nombra la
   salida y volvé a correrlo. Dos vueltas es normal. Cinco quiere decir que el
   borrador se escribió con fórmula, y el arreglo es otro borrador, no más
   pasadas.
5. Mostrale al usuario el texto limpio y el puntaje. Nunca el puntaje solo.

Si un reemplazo dejó una oración rara (pasa: un borrado puede dejar "5 cosas
que funcionan para..." sin verbo), arreglala a mano antes de mostrarla. El
script saca el relleno; la frase final la decidís vos.
