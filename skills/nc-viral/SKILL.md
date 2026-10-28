---
name: nc-viral
description: >-
  Sale a buscar los reels que de verdad están funcionando ahora en el nicho del
  usuario, los ordena por cuánto superó cada uno a su propia cuenta, nombra la
  fórmula de gancho que usó cada uno y lo convierte en un swipe file para
  grabar. Usala cuando el usuario dice "buscame videos virales", "qué está
  funcionando ahora", "qué publica la gente de mi nicho", "analizá esta cuenta",
  "armame un swipe file", "por qué este reel la está rompiendo", "find viral
  reels", "what's working in my niche", o pregunta qué hacer después y no tiene
  evidencia para responderlo.
---

# nc-viral

La skill de investigación. Todas las demás del pack escriben; esta sale a
mirar. Usala una vez por mes, no todos los días: las fórmulas duran una
temporada.

En esta carpeta hay una herramienta y funciona:

```bash
python3 swipe.py capturados.tsv --out ~/.claude/novacut/swipe.md
```

Usa las 26 fórmulas y el puntaje de `../nc-reel/` (hooks.json y hookscore.py).
Si `nc-viral` se copió sola, sin `nc-reel` al lado, igual ordena por múltiplo
pero no nombra fórmulas; pasale `--hooks` con la ruta a `hooks.json`.

## La idea que hace que valga la pena

**Las vistas en bruto no son evidencia.** Una cuenta con dos millones de
seguidores que hace 400.000 vistas tuvo un martes flojo. Una cuenta con cuatro
mil seguidores que hace 400.000 vistas encontró algo, y ese algo se puede
copiar.

Por eso todo acá se ordena por el **múltiplo sobre su propia cuenta**: vistas
divididas por la mediana reciente de esa cuenta. Arriba de 3x es una señal.
Debajo de 1,5x es un día normal de esa cuenta y no te enseña nada, por más
grande que se vea el número.

Juntá cuentas **de hasta unas 10 veces el tamaño del usuario**. Una fórmula que
funciona con 2 millones de seguidores muchas veces funciona porque tiene 2
millones de seguidores.

## Paso 1: elegir las cuentas

Pedile al usuario entre 6 y 12 cuentas, o proponelas y conseguí su aprobación:

- **4 directas**: mismo nicho, misma oferta, un poco más adelante.
- **4 vecinas**: otro nicho, mismo público. Ahí es donde se toman prestados
  los formatos antes de que los tenga alguien del nicho.
- **2 a 4 grandes**: cuentas mucho más grandes, solo por el formato, nunca por
  la frecuencia ni el tono.

Pedile también que abra su colección de **Guardados**. Es el corpus más rápido
y más relevante que existe, y ya viene filtrado por su gusto.

## Paso 2: ir a mirar

Usá la herramienta de navegación que tenga esta sesión: un navegador dentro de
la app, una extensión conectada al Chrome del propio usuario, o una herramienta
de uso de computadora. No hay API para esto y no hace falta, porque el volumen
es chico y se puede leer.

**Reglas que no se negocian:**

- **Nunca te logueás en Instagram en nombre del usuario y nunca pedís una
  contraseña.** Si una página pide login, el que ya está logueado es el
  usuario. Manejá su navegador con él presente, o pedile que pegue los datos.
- **Esto es leer, no scrapear.** Diez cuentas, una docena de reels cada una, a
  velocidad humana. La recolección automática a volumen viola las Condiciones
  de uso de Instagram y hace que bloqueen cuentas. No armes un crawler, no uses
  un servicio de scraping, no lo dejes corriendo en segundo plano.
- **Copiá la fórmula, nunca el video.** La forma del gancho, la estructura, el
  largo, el patrón de cortes. No su guion, no su voz, no su edición. Atribuí
  cada fila del swipe file a la cuenta de la que salió.

**Qué anotar de cada reel**, con las palabras del creador:

| campo | notas |
| --- | --- |
| cuenta | el @ |
| seguidores | del perfil |
| mediana | mirá los últimos 12 reels y quedate con la cantidad de vistas del medio |
| vistas | las de este reel |
| gancho | la primera línea, dicha o en pantalla, textual, con errores y todo |
| pantalla | la primera placa de texto, si es distinta |
| duración | en segundos |
| cta | qué pidió al final |

La mediana es la importante. Sin ella volvés a ordenar por cantidad de
seguidores, que es justo lo que esta skill existe para evitar.

**Cuando Instagram no te muestra lo suficiente:** la misma gramática de gancho
corre en YouTube Shorts, donde las vistas y las transcripciones son públicas y
no hace falta login. Es un segundo corpus legítimo, y ahí el gancho hablado es
más fácil de conseguir (si el usuario tiene `yt-dlp` instalado):

```bash
# vistas de los shorts de un canal
python3 -m yt_dlp --flat-playlist --playlist-end 40 -J \
  "https://www.youtube.com/@CANAL/shorts" > canal.json

# la primera línea hablada de un short, desde los subtítulos automáticos
python3 -m yt_dlp --skip-download --write-auto-subs --sub-langs "es.*" \
  --sub-format json3 -o gancho "https://www.youtube.com/watch?v=ID_DEL_VIDEO"
```

Quedate con cada palabra del subtítulo que tenga marca de tiempo menor a 3,0
segundos. Ese es el gancho, como se dijo, no como se escribió.

## Paso 3: ordenarlo

Llená un archivo separado por tabulaciones, con una fila de encabezado, y
corré el script. Acepta encabezados en castellano o en inglés, y cifras como
`412.000`, `412000`, `412k` o `1,2M`:

```
cuenta	seguidores	mediana	vistas	gancho
@coach_vale	48000	11000	412000	nadie te dice que tus primeros 30 reels van a fallar
```

```bash
python3 swipe.py capturados.tsv --out ~/.claude/novacut/swipe.md
```

Calcula el múltiplo, nombra la fórmula de gancho con las mismas 26 fórmulas
con las que escribe `/nc-reel`, puntúa cada gancho con `hookscore.py` e imprime
qué separa al tercio de arriba del tercio de abajo.

## Paso 4: decir qué significa, con cuidado

Informá tres cosas y nada más:

1. **Qué fórmulas aparecen de más** en el tercio de arriba, con conteos. Dos
   fórmulas que aparecen cuatro veces cada una en seis cuentas es un hallazgo.
   Una que aparece dos veces, no.
2. **Qué tiene en común el tercio de arriba en la estructura** que el de abajo
   no: largo del gancho, si la recompensa es visual, si el primer cuadro se
   mueve, dónde está el pedido.
3. **Las filas sin clasificar.** Cada gancho que el clasificador no pudo
   nombrar es ruido o una fórmula que todavía no está en `hooks.json`. Leelos a
   mano. Es la columna más valiosa de la salida y es la razón por la que el
   script imprime el conteo.

Después decí el tamaño de la muestra y la confianza con palabras simples.
Cuarenta reels en seis cuentas sostienen una afirmación. Doce no, y decirlo es
la diferencia entre investigar y leer el horóscopo. Las fórmulas y el puntaje
son heurísticas: describen la forma del gancho, no predicen ganadores.

## Paso 5: convertirlo en algo para grabar

Para las tres fórmulas de arriba, escribí **la versión del usuario**: su propia
historia, su propio número, en la forma que está funcionando. Pasale cada una a
`/nc-reel` con el número de fórmula ya elegido.

Nunca devuelvas "hacé un reel como este". Devolvé un gancho que pueda decir
mañana. Si para el gancho hace falta un dato que el usuario no te dio, dejá
`{{tu número}}` y avisalo; no lo inventes.

## Salida

```
SWIPE  ·  38 reels  ·  7 cuentas  ·  base: mediana de la cuenta

OUTLIERS (arriba de 3x)
  38,4x  gancho 81  #3  Nadie te dice     @coach_vale     412.000  (mediana 10.700)
  11,2x  gancho 79  #9  El robo           @inmo.ruiz      180.000  (mediana 16.100)
  ...

QUÉ APARECE DE MÁS
  #3 Nadie te dice     x5 en el tercio de arriba, 0 en el de abajo
  #2 Orden negativa    x4
  largo mediano del gancho: 8 palabras arriba, 19 abajo

SIN CLASIFICAR (6)
  Dos tienen la misma forma y no está en hooks.json: un gancho que arranca
  leyendo en voz alta el comentario de otra persona. Vale la pena sumarla.

TU VERSIÓN
  #3  "Nadie te dice que los primeros 20 presupuestos están para perderse."
  ...
```

Escribí el swipe file en `~/.claude/novacut/swipe.md`. `/nc-reel` y `/nc-plan`
lo leen, y esa es la idea: después de correr esto una vez, el resto del pack
trabaja con la evidencia del propio usuario en vez de con los defaults.

Esta skill no publica, no sigue, no da like ni manda mensajes. Lee.
