---
name: nc-x-human
description: >-
  Le saca la huella de máquina a cualquier borrador para X en español (rayas
  largas, frases hechas de IA, caracteres invisibles, relleno de hilo) y lo
  puntúa con un panel de cinco chequeos antes de que salga. Usala siempre que
  un texto tenga que sonar humano, cuando el usuario diga "humanizá esto",
  "¿esto suena a IA?", "sacale las rayas", "esto parece ChatGPT", o antes de
  mostrar cualquier post, hilo, respuesta o mensaje de X de este pack.
  También en inglés: "humanize this", "does this sound like AI", "de-slop
  this".
---

# nc-x-human

El humanizador de X del pack. Para textos que no son de X, el humanizador
general es `/nc-human`; este trae además el bloque propio de X: relleno de
hilo ("si este hilo te sirvió"), cebo de RT ("dale RT si estás de acuerdo",
"seguime para más") y el gancho "Un hilo 🧵".

En esta carpeta hay dos herramientas y las dos funcionan de verdad. Usalas. No
lo hagas a ojo.

```bash
python3 humanize.py borrador.txt --report        # lo limpia y muestra qué cambió
python3 detect.py borrador.txt                    # lo puntúa, cinco chequeos
python3 detect.py antes.txt despues.txt           # muestra la diferencia
```

Las dos leen `slop.json`: más de 250 palabras y frases típicas de texto
generado por IA en español con reemplazos llanos, 18 clases de caracteres
invisibles, 11 sustituciones tipográficas y 18 señales de estructura. El
último bloque de cada lista es propio de X. Está hecho para editarse: si el
usuario usa de verdad una palabra que el lexicón le saca, borrala del archivo.

## Por qué esto importa más en X de lo que parece

Un post tiene 280 caracteres. Una raya larga en un post de dos líneas es una
parte mucho más grande del texto que la misma raya en un ensayo, y la gente en
X lleva años aprendiendo a reconocer la forma. La marca no es un detector que
te señala. La marca es una respuesta que dice "esto lo escribió ChatGPT", y
queda abajo de tu post para que la lean todos.

## Qué se arregla solo

**1. Caracteres invisibles.** Espacios de ancho cero, unidores, guiones
blandos, BOM, caracteres de etiqueta Unicode, separadores invisibles,
espacios duros y angostos. Un teclado no los produce. Sobreviven al copiar y
pegar y no se ven en ningún editor. `humanize.py` los borra todos, incluido
cualquier carácter de formato que no tenga nombrado.

**Salvo dentro de los emojis.** X está lleno, y dos caracteres invisibles
hacen falta ahí: el unidor que hace que 👨‍💻 sea un solo dibujo y no 👨💻, y
las etiquetas que forman las banderas de Inglaterra, Escocia y Gales. Esos se
conservan. Un unidor o una etiqueta en cualquier otro lado se borra igual, y
`detect.py` no cuenta los que se conservan.

**2. Tipografía.** Raya larga a coma, raya media a guion, comillas curvas a
rectas, "…" a tres puntos, viñeta a guion. La pasada que importa es la de la
raya.

**3. El lexicón.** "En el mundo actual", "potenciar", "desbloquear", "sin
lugar a dudas", "cabe destacar que", "al siguiente nivel", "esto lo cambió
todo", "nadie está hablando de esto", "dejá que eso se asiente", más el
bloque de X. Cada uno cambiado por una palabra normal o borrado, respetando
mayúsculas y sin tocar links.

## Qué NO se arregla solo

Las señales de estructura se **marcan, no se reescriben**, porque cambiar la
forma de una frase necesita criterio:

- "No es solo X, es Y" y "No solo X, sino también Y"
- "No se trata de X. Se trata de Y."
- Tríadas: "rápido, simple y efectivo."
- Línea de pregunta retórica: "¿El resultado?"
- "Un hilo 🧵" como gancho, y el cierre de hilo de manual
- El preámbulo: "en este hilo te voy a mostrar"
- "Dejá de scrollear" como apertura
- Dos líneas seguidas que arrancan con emoji
- Tres o más palabras gritadas en mayúsculas seguidas
- Muros de hashtags
- Cebo reflejo: "dale RT si estás de acuerdo", "seguime para más", "¿Qué
  opinan?"

Esa lista es tu trabajo. Reescribí cada línea marcada a mano, conservando el
sentido, y volvé a correr `detect.py`.

## Los cinco chequeos

`detect.py` puntúa cinco señales de 0 a 100. Más alto es más humano:

| chequeo | qué mide | cómo se ve la máquina |
| --- | --- | --- |
| VARIACIÓN | variación del largo de las frases | todas del mismo largo |
| CONCRECIÓN | números, nombres y datos cada 100 palabras | sustantivos abstractos, ninguna cifra |
| SLOP | frases hechas del lexicón cada 100 palabras | vocabulario de manual |
| HUELLA | invisibles, rayas largas, "…" cada 1.000 caracteres | tipografía perfecta |
| VOZ | registro hablado, persona, señales de estructura | neutro de manual, revelaciones montadas |

En español VOZ mide **registro hablado** en lugar de contracciones: voseo o
tuteo conjugado ("tenés", "fijate", "dime"), muletillas ("ojo", "la verdad",
"igual") y pronombres de primera y segunda persona.

El veredicto pondera el promedio al 60% y el **chequeo más flojo** al 40%,
porque con una señal alcanza. PASA necesita 70 o más en total y ningún
chequeo debajo de 55.

**Los posts cortos se puntúan con lo que un post corto puede mostrar.**
VARIACIÓN necesita cuatro frases y CONCRECIÓN unas 25 palabras; por debajo
dicen n/d y no cuentan, en vez de valer un 50 neutro. VOZ se queda solo con
su mitad de señales de estructura. La salida dice "puntuado con 3 de 5
chequeos" cuando pasa, para que nadie lo confunda con el panel completo.

**Las comillas curvas cuentan un cuarto.** El iPhone las escribe solas y la
mayoría de los posts se escriben en el celular, así que por sí solas dicen
poco. Igual se enderezan.

## Decilo con honestidad

Son cinco heurísticas locales, modeladas sobre las señales que miran los
detectores públicos. Corren enteras en la máquina del usuario y no se sube
nada. **No son** GPTZero, Originality, Copyleaks, Winston ni Turnitin, no
llaman a esas APIs y no pueden prometer sus veredictos. No hagas una
afirmación más grande en nombre del usuario y nunca le digas que su texto es
"indetectable".

## Orden de trabajo

1. `humanize.py borrador.txt -o limpio.txt --report`
2. Leé las señales de estructura. Reescribí esas líneas vos.
3. `detect.py borrador.txt limpio.txt` para mostrar el antes y el después.
4. Si el veredicto no es PASA, arreglá el chequeo más flojo que nombra la
   salida y volvé a pasar. Dos vueltas es normal. Cinco quiere decir que el
   borrador se escribió con fórmula, y la solución es otro borrador.
5. Mostrale al usuario el texto limpio y el puntaje. Nunca el puntaje solo.

Si el entorno no puede correr Python, hacé las pasadas a mano con `slop.json`
como lista y decí que el puntaje no se pudo calcular. No inventes un número.
