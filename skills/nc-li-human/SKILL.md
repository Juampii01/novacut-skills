---
name: nc-li-human
description: >-
  Le saca la huella de máquina a cualquier borrador de LinkedIn en español
  (rayas largas, frases hechas de IA, caracteres invisibles) y lo puntúa con un
  panel de cinco chequeos antes de que salga. Usala siempre que un texto tenga
  que sonar humano, cuando el usuario diga "humanizá esto", "¿esto suena a
  IA?", "sacale las rayas", "que no parezca ChatGPT", "¿me lo van a marcar?",
  o antes de mostrar cualquier post, comentario, respuesta o mensaje de
  LinkedIn de este pack. También en inglés: "humanize this", "does this sound
  like AI", "de-slop this".
---

# nc-li-human

El humanizador de LinkedIn del pack. Para textos que no son de LinkedIn, el
humanizador general es `/nc-human`; este trae además el bloque propio de
LinkedIn ("me complace anunciar que", "apasionado por", "orientado a
resultados", "¿Qué opinan?").

En esta carpeta hay dos herramientas y las dos funcionan de verdad. Usalas. No
lo hagas a ojo.

```bash
python3 humanize.py borrador.txt --report        # lo limpia y muestra qué cambió
python3 detect.py borrador.txt                    # lo puntúa, cinco chequeos
python3 detect.py antes.txt despues.txt           # muestra la diferencia
```

Las dos leen `slop.json`, que es el lexicón: más de 250 palabras y frases
típicas de texto generado por IA en español, con reemplazos llanos; 18 clases
de caracteres invisibles; 11 sustituciones tipográficas y 14 señales de
estructura. Está hecho para editarse. Si el usuario usa de verdad una palabra
que el lexicón le saca ("fundamental", "integral"), borrala del archivo.

## Qué se arregla solo

**1. Caracteres invisibles.** Espacios de ancho cero, unidores, guiones
blandos, BOM, caracteres de etiqueta Unicode, espacios duros y angostos. Un
teclado no los produce. Sobreviven al copiar y pegar, no se ven en ningún
editor y son lo más mecánico de un texto generado. `humanize.py` borra todos,
incluido cualquier carácter de formato que no tenga nombrado. Los que hacen
falta dentro de un emoji compuesto (👨‍💻) se conservan.

**2. Tipografía.** Raya larga a coma, raya media a guion, comillas curvas a
rectas, "…" a tres puntos, viñeta a guion. La pasada que importa es la de la
raya: en un post de LinkedIn en español, la raya larga para incisos es hoy una
de las marcas más reconocidas de texto de IA.

**3. El lexicón.** "En el mundo actual", "potenciar", "desbloquear", "sin
lugar a dudas", "cabe destacar que", "sinergia", "ecosistema", "al siguiente
nivel", "me complace anunciar", "la decisión es tuya" y el resto, cada uno
cambiado por una palabra normal (o borrado), respetando mayúsculas y sin tocar
links.

## Qué NO se arregla solo

Las señales de estructura se **marcan, no se reescriben**, porque cambiar la
forma de una frase necesita criterio:

- "No es solo X, es Y" y "No solo X, sino también Y"
- "No se trata de X. Se trata de Y."
- Tríadas: "eficientes, productivos y felices."
- La línea de pregunta retórica: "¿El resultado?"
- "Esto es lo que aprendí"
- Emojis de cohete, fuego, lamparita, brillos y diana
- Muros de hashtags
- Cierres de ensayo: "En conclusión", "En resumen"
- Cebo reflejo: "¿Qué opinan?", "¿Están de acuerdo?", "¿Quién más?"
- Frases todas del mismo largo y viñetas todas del mismo largo

Esa lista es tu trabajo. Reescribí cada línea marcada a mano, conservando el
sentido, y volvé a correr `detect.py`. Esta es la parte que lleva el puntaje
de REVISAR a PASA, y es la parte que un script no puede hacer.

## Los cinco chequeos

`detect.py` puntúa cinco señales de 0 a 100. Más alto es más humano:

| chequeo | qué mide | cómo se ve la máquina |
| --- | --- | --- |
| VARIACIÓN | variación del largo de las frases | todas las frases del mismo largo |
| CONCRECIÓN | números, nombres y datos cada 100 palabras | sustantivos abstractos, ninguna cifra |
| SLOP | frases hechas del lexicón cada 100 palabras | vocabulario de manual |
| HUELLA | invisibles, rayas largas, comillas curvas cada 1.000 caracteres | tipografía perfecta |
| VOZ | registro hablado, persona, señales de estructura | neutro de manual, revelaciones montadas |

VOZ en español no mide contracciones (no existen como en inglés): mide
**registro hablado**, es decir voseo o tuteo conjugado ("tenés", "fijate",
"cuéntame"), muletillas de conversación ("ojo", "la verdad", "igual") y
pronombres de primera y segunda persona. Un texto generado suele escribir en
un neutro impersonal que no usa ninguna.

El veredicto pondera el promedio al 60% y el **chequeo más flojo** al 40%,
porque a un detector le alcanza una señal. PASA necesita 70 o más en total y
ningún chequeo debajo de 55. En textos cortos (un comentario, una nota de
invitación) VARIACIÓN y CONCRECIÓN dicen n/d y no cuentan; la salida avisa con
cuántos chequeos se puntuó.

## Decilo con honestidad

Son cinco heurísticas locales, modeladas sobre las señales que miran los
detectores públicos. Corren enteras en la máquina del usuario y no se sube
nada. **No son** GPTZero, Originality, Copyleaks, Winston ni Turnitin, no
llaman a esas APIs y no pueden prometer sus veredictos. Arreglar lo que miden
suele mover esos números, porque miden lo mismo de fondo. Esa es toda la
afirmación. No hagas una más grande en nombre del usuario y nunca le digas
que su texto es "indetectable".

## Orden de trabajo

1. `humanize.py borrador.txt -o limpio.txt --report`
2. Leé las señales de estructura. Reescribí esas líneas vos.
3. `detect.py borrador.txt limpio.txt` para mostrar el antes y el después.
4. Si el veredicto no es PASA, arreglá el chequeo más flojo que nombra la
   salida y volvé a pasar. Dos vueltas es normal. Cinco quiere decir que el
   borrador se escribió con fórmula, y la solución es otro borrador, no más
   vueltas.
5. Mostrale al usuario el texto limpio y el puntaje. Nunca el puntaje solo.

Si el entorno no puede correr Python (por ejemplo, una skill pegada en un chat
sin ejecución de código), hacé las tres pasadas a mano con `slop.json` como
lista y decí que el puntaje no se pudo calcular. No inventes un número.
