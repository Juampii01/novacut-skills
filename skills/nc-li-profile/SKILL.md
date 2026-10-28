---
name: nc-li-profile
description: >-
  Puntúa un perfil de LinkedIn sobre 100 con una rúbrica de 12 partes y
  reescribe lo que pierde puntos: titular, acerca de, experiencia, destacados,
  portada. Usala cuando el usuario diga "optimizá mi perfil", "puntuá mi
  LinkedIn", "reescribime el titular", "arreglá mi acerca de", "¿cómo se lee
  mi perfil?", o pegue su perfil. También en inglés: "optimize my profile",
  "score my LinkedIn", "rewrite my headline".
---

# nc-li-profile

Un perfil no es un CV. Un CV responde "qué hiciste". Un perfil responde
"¿le escribo a esta persona?", y lo responde en unos cuatro segundos, con el
titular y las dos primeras líneas del acerca de.

## Qué pedir

Pedile al usuario que pegue: titular, acerca de, puesto actual y las dos
últimas experiencias, y si tiene portada y sección de destacados. Para una
primera pasada alcanza con una captura de la parte de arriba del perfil. No
te loguees en LinkedIn por él.

## Puntuarlo

Leé `rubric.json` en esta carpeta. Doce ítems, 100 puntos, cada uno con cómo
se ve el puntaje completo. Puntuá cada ítem, mostrá la tabla y dá el total.
Sé honesto: la mayoría de los perfiles quedan entre 30 y 49 en la primera
pasada, y un puntaje generoso no sirve.

```
PUNTAJE DEL PERFIL  41/100

  titular              3/12   solo el puesto, sin resultado, sin a quién
  acerca de, 2 líneas  2/10   arranca con "apasionado por"
  acerca de, cuerpo    4/10   historia, no oferta
  destacados           0/8    vacío
  portada              0/6    el fondo azul por defecto
  ...
```

## Después, reescribir en este orden

Arreglá de mayor a menor según los puntos perdidos. No reescribas todo de
una: el usuario tiene que pegar cada parte a mano.

**1. Titular (220 caracteres).** La fórmula que funciona:
`{qué hacés y para quién} | {prueba} | {cómo empezar}`. No tu puesto. Tampoco
"Ayudo a X a lograr Y" como primeras palabras, que es como arranca uno de cada
dos perfiles. Dá tres opciones. Ejemplo para una contadora de Rosario:
`Ordeno los números de pymes de servicios para que el dueño sepa cuánto gana
de verdad | 40 empresas, 0 sorpresas con ARCA | Diagnóstico gratis por mensaje`.
(Los números son del ejemplo: en el real van los del usuario o `{{tu número}}`.)

**2. Acerca de, dos primeras líneas.** Todo lo que viene después de la línea 2
queda detrás de "ver más" en el celular, así que esas dos líneas son todo el
acerca de para la mayoría. Tienen que decir a quién ayudás y qué cambia. Nada
de "apasionado", nada de "orientado a resultados", nada de biografía en
tercera persona, no arrancar con tu propio nombre.

**3. Acerca de, cuerpo.** Escrito a un lector, en segunda persona (vos, tú o
usted, según `~/.claude/novacut/voz.md`). Estructura: el problema que tiene,
qué hacés al respecto, una prueba con un número, qué hacer después. Menos de
1.400 caracteres aunque el límite sea 2.600.

**4. Destacados.** Tres elementos: el mejor post, la prueba (un caso, un
testimonio), la forma de contacto. Una sección de destacados vacía son ocho
puntos y es el único lugar del perfil que controlás por completo.

**5. Experiencia.** Cada puesto, una línea de alcance y dos o tres viñetas que
sean resultados con números, no tareas. Lo de hace más de diez años, a una
línea.

**6. Portada.** Una frase de posicionamiento y una forma de contacto. El fondo
azul por defecto es la señal más clara de la página de que no hay nadie en
casa.

Los límites de caracteres (titular 220, acerca de 2.600) son los de 2026 y
pueden cambiar.

## Salida

Tabla de puntajes, después las reescrituras como bloques listos para copiar
en orden de arreglo, cada una pasada por `/nc-li-human`. Volvé a puntuar al
final y mostrá la diferencia con honestidad: si la reescritura llega a 88 y
no a 98, decí 88, y decí qué necesitan los puntos que faltan (casi siempre
recomendaciones, una portada real e historial de publicaciones, nada de lo
cual lo crea una reescritura).

Nunca inventes logros, clientes ni números para el perfil. Si falta la
prueba, va `{{tu número}}` y un aviso.

Esta skill no guarda nada en LinkedIn. El usuario pega cada sección.
