---
name: nc-x-profile
description: >-
  Puntúa un perfil de X sobre 100 con una rúbrica de 12 partes y reescribe lo
  que pierde puntos: bio, post fijado, nombre visible, encabezado, link. Usala
  cuando el usuario diga "optimizá mi perfil de X", "arreglá mi bio",
  "puntuá mi perfil de Twitter", "¿qué fijo?", "reescribime la bio", o pegue
  su perfil y pregunte cómo se lee. También en inglés: "optimize my profile",
  "fix my X bio", "what should I pin".
---

# nc-x-profile

Nadie lee tu perfil a propósito. Llegan desde una respuesta o un post que les
gustó, le dan unos cuatro segundos, y te siguen o se van. Esos cuatro segundos
son la primera línea de la bio, el post fijado y las dos últimas cosas que
publicaste. Todo lo de acá está al servicio de esa visita.

## Qué pedir

Pedile al usuario que pegue: nombre visible, usuario, bio, sitio web, lo que
tiene fijado (pegá el texto), y sus últimos diez posts; o una captura de la
parte de arriba del perfil más la primera pantalla de posts. No te loguees en
X por él y no le pidas la contraseña.

## Puntuarlo

Leé `rubric.json` en esta carpeta. Doce ítems, 100 puntos, cada uno con cómo
se ve el puntaje completo. Puntuá cada ítem, mostrá la tabla y dá el total.
Sé honesto: la mayoría de los perfiles quedan en los 40 en la primera pasada,
y un puntaje generoso no sirve.

```
PUNTAJE DEL PERFIL  46/100

  bio, primera línea  4/14   títulos de puesto, sin lector, sin resultado
  post fijado         0/14   no hay nada fijado
  coherencia de tema  6/12   4 de los últimos 10 posts son del tema
  respuestas          8/10   responde casi todos los días
  prueba en la bio    0/8    ni un número, nada que se pueda chequear
  encabezado          2/8    el gris por defecto
  ...
```

## Después, reescribir en este orden

Arreglá de mayor a menor según los puntos perdidos. El usuario tiene que
pegar cada cosa a mano, así que dáselas en el orden que más rinde primero.

**1. La primera línea de la bio (160 caracteres para toda la bio).** A quién
ayudás y qué cambia, con las palabras que usaría el lector. Tres opciones.
Después una línea de prueba. Después, si entra, de qué publicás. No una pila
de títulos, no "apasionado por", no tres hashtags. Ejemplo para un consultor
de Bogotá: `Ayudo a restaurantes a dejar de perder plata en el delivery. 23
locales, margen promedio +{{tu número}}%. Acá: números de gastronomía sin
humo.` (Lo que no está en `~/.claude/novacut/voz.md` va como `{{tu número}}`.)

**2. El post fijado.** El post más leído de la cuenta, porque es el primero
que ve cada visitante. O el post que mejor le funcionó al usuario y sigue
siendo cierto, o un post de "empezá por acá" escrito para un desconocido:
quién sos, de qué publicás y lo primero que hay que leer. Si hay que
escribirlo, pasalo por `/nc-x-post`.

**3. Coherencia de tema.** Si los últimos diez posts van para cualquier lado,
decilo claro. Una reescritura de perfil no lo arregla; las próximas dos
semanas de posts sí, y eso se planifica en `/nc-x-plan`.

**4. Encabezado (1500x500).** Una línea de posicionamiento o de prueba, y nada
importante abajo a la izquierda, donde la foto de perfil lo tapa. Escribí la
línea; decí qué va dónde.

**5. Nombre visible, foto, link.** Nombre real más una palabra si ayuda. Una
cara que se reconozca a 40px en un hilo de respuestas, porque es el tamaño en
que la va a ver casi todo el mundo. Un link a la única página que cumple lo
que promete la bio.

Los límites (bio 160, nombre 50, usuario 15, encabezado 1500x500) son los de
X a septiembre de 2026 y pueden cambiar.

## Salida

Tabla de puntajes, después las reescrituras como bloques listos para copiar
en orden de arreglo, cada una pasada por `/nc-x-human`. Volvé a puntuar al
final y mostrá la diferencia con honestidad: si la reescritura llega a 81,
decí 81, y decí qué necesitan los puntos que faltan (casi siempre un post
fijado que haya funcionado de verdad y semanas publicando sobre el tema, nada
de lo cual lo crea una reescritura).

Nunca inventes logros ni números para la bio. Esta skill no guarda nada en X.
El usuario pega cada sección.
