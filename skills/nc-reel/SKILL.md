---
name: nc-reel
description: >-
  Convierte una idea cruda en un Reel de Instagram: opciones de gancho a partir
  de 26 fórmulas, el guion hablado, el texto en pantalla y una hoja de tiempos,
  en la voz del usuario y puntuado antes de grabar. Usala cuando el usuario
  quiere un Reel, un guion corto, un gancho o una locución: "haceme un reel
  sobre X", "escribime un guion", "qué digo en este video", "necesito un
  gancho", "make a reel about X", "write me a hook", o cuando está por grabar y
  no tiene la primera línea.
---

# nc-reel

Convierte una idea cruda en un Reel que alguien mira hasta el final.

En esta carpeta hay dos herramientas y las dos funcionan. Usalas. No midas el
gancho a ojo ni adivines el largo.

```bash
python3 hookscore.py ganchos.txt               # ordena tus opciones de gancho
python3 hookscore.py --hook "una línea"        # puntúa una sola
python3 beats.py guion.txt --target 30         # hoja de tiempos antes de grabar
```

`hookscore.py` puntúa cinco propiedades (largo, concreción, tensión, arranque,
destinatario) y además nombra la fórmula de `hooks.json` que usa cada gancho.
`beats.py` estima cuánto tarda cada línea en decirse a 160 palabras por minuto
(cambialo con `--wpm` si el usuario habla más rápido o más lento) y cuenta las
cifras como se dicen: "$18.000" son tres palabras habladas, no una.

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario:
   cómo habla a cámara, qué no dice nunca, a quién le habla, si usa voseo o
   tuteo. Si no existe, pedí **tres reels propios**, transcribilos o leelos,
   deducí la voz y escribí el archivo (o derivá a `/nc-voz`). Un guion en la
   voz equivocada no sirve, porque lo tiene que decir en voz alta.
2. Leé `hooks.json` de esta carpeta. 26 fórmulas, cada una con plantilla,
   ejemplo, versión en pantalla, para qué sirve y cómo se arruina. Las regex
   `match` están escritas para cómo se habla en castellano, con y sin tilde,
   con voseo y con tuteo.
3. Si la idea es flaca, no la rellenes. Hacé una sola pregunta agrupada: qué
   pasó, a quién, y cuánto costó o cuánto dejó. Un Reel necesita una cosa
   concreta y verdadera. Conseguila antes de escribir.
4. Si existe `~/.claude/novacut/swipe.md`, leelo. Lo escribe `/nc-viral` y es
   la evidencia del propio usuario sobre qué fórmulas están funcionando en su
   nicho ahora. Pesa más que los defaults de este archivo.

## La forma

Un Reel se decide en los primeros dos segundos y se sostiene en los cinco
siguientes.

```
0:00 - 0:02   GANCHO      la afirmación. Línea hablada y línea en pantalla, escritas
                          por separado. Movimiento en el primer cuadro, no una cara quieta.
0:02 - 0:07   LO QUE ESTÁ EN JUEGO   por qué le importa al que mira. Una línea.
0:07 - ...    EL CUERPO   una idea por beat, y el plano cambia en cada beat.
ÚLTIMOS 3s    EL PAGO     cumplí lo que prometió el gancho, después el único pedido.
ÚLTIMA LÍNEA  EL LOOP     repetí una palabra del gancho para que la segunda vuelta cierre limpia.
```

Largo: entre 15 y 45 segundos es el rango que trabaja. Los Reels pueden durar
hasta 3 minutos (dato de plataforma, puede cambiar) y casi nadie debería usar
eso. Por debajo de 7 segundos se inflan las repeticiones y nada más.

## El circuito

**1. Elegí tres ganchos, no uno.** Pasá la idea por `hooks.json`, elegí tres
fórmulas que de verdad encajen y escribí la línea hablada y la de pantalla de
cada una. Fórmulas distintas, no tres versiones de la misma.

**2. Puntualos.** Poné las tres líneas habladas en un archivo, una por línea,
y corré `hookscore.py`. Mostrale el ranking al usuario. Si el primero está por
debajo de 50, todavía no tenés el gancho y ninguna edición lo arregla.

Decí la verdad sobre qué mide: es una heurística que descarta ganchos
claramente flojos (saludos, preámbulos, nada concreto, frases que tardan cinco
segundos). No predice cuál de dos ganchos decentes va a funcionar; eso lo
deciden la cara, la edición, el audio y a quién se lo muestra Instagram.

**3. Escribí el guion** sobre el gancho ganador. Lenguaje hablado, como habla
el usuario de verdad. Frases cortas. Ninguna oración que tenga que ensayar.

**4. Medilo.** Corré `beats.py guion.txt --target {largo}`. Arreglá cada
alerta: un gancho de más de 3 segundos, cualquier beat de más de 4 segundos,
una racha de beats sin nada concreto, o la falta de loop. Volvé a correrlo
hasta que quede limpio.

**5. Humanizalo.** Pasá el guion por `/nc-human` antes de mostrarlo. Una línea
que suena escrita se nota en el momento en que alguien la dice en voz alta.

**6. Imprimí el bloque.** El guion en un bloque de código, el texto en pantalla
como lista aparte con sus tiempos, y después:

```
REEL LISTO
gancho:       #3 Nadie te dice, 86 FUERTE
largo:        28,4s en 9 beats a 160 ppm
en pantalla:  6 placas
humanizador:  4 marcas sacadas, puntaje humano 81 PASA
caption:      seguí con /nc-caption

Respondé "sí" para registrarlo, o decime qué cambio.
```

**7. Nunca publiques.** Esta skill produce un guion. El usuario lo graba y lo
publica. Con el "sí", agregá a `~/.claude/novacut/log.md` la fecha, la fórmula
de gancho y la primera línea, así `/nc-audit` tiene historial después.

## El texto en pantalla es otro guion

Escribilo aparte, siempre. Se lee antes de que se escuche.

- **Seis palabras o menos por placa.** Lo está leyendo alguien con el celular
  a un brazo de distancia que todavía no está escuchando.
- **La placa del gancho está desde el cuadro 1**, no después de un silencio.
- **Dentro de la zona segura.** En un cuadro de 1080x1920, nada arriba de
  y=230 ni abajo de y=1440, y dejá libres los 230 píxeles de la derecha. La
  interfaz tapa todo lo que queda afuera: el caption, la barra de acciones, el
  audio. (Las medidas de la interfaz pueden cambiar; si algo se ve tapado,
  lo que manda es lo que ve el usuario en su celular.)
- **Nunca pongas el gancho donde va el caption.** Es la parte de abajo del
  cuadro y queda tapada.
- **Subtítulos quemados en el cuerpo.** La mayoría mira sin sonido primero.

## Reglas que hacen la diferencia

- **Una idea por Reel.** Si el guion tiene dos, tenés dos Reels. Decilo.
- **Números antes que adjetivos.** "USD 4.200" le gana a "un montón". Si el
  usuario no dio el número, pedíselo en vez de escribir alrededor del hueco.
- **Cortá la intro.** Nada de "hola, chicos", "en este video", nombre ni logo.
  El video arranca en la frase a la que normalmente llegarías en el segundo seis.
- **Cambiá el plano en cada beat.** Un plano fijo de 8 segundos es donde la
  gente se va, y `beats.py` lo marca.
- **Un solo pedido al final.** Comentar una palabra clave, guardar, o seguir. Uno.
- **Nunca inventes.** Ni métricas, ni clientes, ni facturación, ni resultados a
  nombre del usuario, ni siquiera de relleno. Si hace falta un número que no
  tenés, dejá `{{tu número}}` en el guion y avisalo.
- **No escribas un guion alrededor de un audio en tendencia que el usuario no
  puede usar.** Si la idea necesita la voz del usuario, decilo.

## Ejemplo

```
/nc-reel bajamos el tiempo de armar presupuestos de 5 horas a 20 minutos con una plantilla
```

```
GANCHOS  (puntuados)
  81  FUERTE  #1  Confesión de costo  "Perdí cuatro horas por semana en formato. Durante dos años."
                                      en pantalla: 2 AÑOS PERDIDOS
  51  ZAFA    #5  Colapso de tiempo   "Los presupuestos me llevaban cinco horas. Ahora, veinte minutos."
                                      en pantalla: 5 HORAS -> 20 MIN
  51  ZAFA    #9  El robo             "Robate la plantilla de presupuesto que lo hizo."
                                      en pantalla: ROBATE ESTO

Grabamos el #1: el costo es del usuario, se dice en tres segundos y deja la
pregunta abierta (¿cómo dejó de perderlas?). El #5 queda como placa en
pantalla para el segundo 2: "5 HORAS -> 20 MIN" se lee de un vistazo.
```
