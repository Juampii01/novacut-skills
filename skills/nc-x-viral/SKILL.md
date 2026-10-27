---
name: nc-x-viral
description: >-
  El motor de viralidad de X. Encuentra los posts que de verdad están rindiendo
  por encima de lo normal en el nicho del usuario, los ordena según cuánto le
  ganó cada uno a su propia cuenta, los desarma en gancho, estructura y
  formato, y recrea los ganadores en la voz del usuario para su audiencia.
  Usala cuando el usuario diga "buscame posts virales", "¿qué está funcionando
  en X ahora?", "¿qué publica la gente de mi nicho?", "desarmame esta cuenta",
  "armame un archivo de referencias", "¿por qué explotó este tweet?",
  "recreame este post", o no tenga de qué publicar ni evidencia para decidir.
  También en inglés: "find viral posts", "what's working on X", "build me a
  swipe file".
---

# nc-x-viral

La skill de investigación. Todo lo demás del pack escribe; esta primero va y
mira, y después escribe a partir de lo que encontró. Corrélo una vez por
mes, no todos los días. Los formatos en X duran una temporada.

En esta carpeta hay dos herramientas y las dos funcionan:

```bash
python3 pull.py links.txt > swipe.tsv                              # links que elegiste -> texto exacto, formato, fecha
python3 swipe.py swipe.tsv --out ~/.claude/novacut/x-swipe.md      # ordena, desarma y escribe el archivo de referencias
```

## La única idea que hace que valga la pena

**Los números crudos no son evidencia.** Una cuenta con 900.000 seguidores y
400.000 vistas tuvo un martes normal. Una cuenta con 6.000 seguidores y
400.000 vistas encontró algo, y ese algo se puede copiar.

Así que todo se ordena por el **múltiplo sobre lo normal**: las vistas de un
post divididas por la mediana de su propia cuenta. Arriba de 3x es una señal.
Debajo de 1,5x es un día normal de esa cuenta, y no enseña nada por más grande
que parezca el número.

## Paso 1: elegir las cuentas

Pedile al usuario entre 6 y 10 cuentas, o proponelas y conseguí su aprobación:

- **4 directas**: mismo nicho, misma audiencia, un poco adelante del usuario.
- **3 vecinas**: otro nicho, misma audiencia. Los formatos llegan primero ahí.
- **2 o 3 enormes**: mucho más grandes, solo para el formato. Nunca para la
  frecuencia ni el tono.

Para un público latino conviene mezclar: si el usuario le habla a pymes de
Argentina y México, que haya cuentas de los dos países, y alguna en inglés
solo como vecina de formato.

Pedile también sus propios **Guardados**. Es el material más relevante que hay
y ya viene filtrado por su gusto.

## Paso 2: juntar, a mano, en orden

De cada cuenta, los **últimos 10 a 15 posts en orden**, incluidos los
aburridos. No los éxitos. La mediana sale de estas filas, y una muestra de
solo bombazos la infla y esconde justo los casos fuera de serie que viniste a
buscar.

Copiá el link de cada post y leé su **cantidad de vistas** en el post (es
pública en cada post, debajo del texto). Likes, respuestas y reposts también,
si se ven fácil.

El usuario puede hacer esto en su propio navegador en unos diez minutos. Si
esta sesión tiene una herramienta de navegador conectada al navegador del
usuario ya logueado, podés abrir los perfiles y leerlos con el usuario
presente, a velocidad humana. Reglas que no se negocian:

- **Nunca te loguees en X por el usuario, nunca le pidas la contraseña**, y
  nunca uses su sesión para otra cosa que leer las páginas que pidió.
- **Esto es leer, no scrapear.** Diez cuentas, una docena de posts cada una.
  Los Términos de X prohíben rastrear o scrapear "de cualquier forma, para
  cualquier fin" sin consentimiento escrito, y prevén daños por acceso masivo.
  Nada de rastreadores, nada de servicios de scraping, nada de bucles en
  segundo plano, nada de cosechar resultados de búsqueda.
- **Copiá la forma, nunca las palabras.** Fórmula de gancho, estructura,
  formato, largo. No sus frases. Atribuí cada fila a su cuenta.

## Paso 3: completar la planilla

```bash
python3 pull.py links.txt > swipe.tsv
```

`pull.py` usa la API oEmbed documentada de X, la que existe para que los
sitios web puedan incrustar un post a partir de su link. Completa el texto
exacto con sus saltos de línea, la cuenta, la fecha y el formato (texto /
media / link / largo). Una consulta por segundo, tope de 100 por corrida. No
trae números, porque oEmbed no los tiene, así que la columna `vistas` (y
likes, respuestas y reposts si los tenés) se completa con lo que se ve en
pantalla. Los números con punto de miles ("12.400") o con "k" ("12,4k") se
leen bien.

Si la red de la sesión no llega a publish.x.com, `pull.py` saltea cada link y
lo dice. En ese caso armá la planilla a mano con las mismas columnas (`url`,
`cuenta`, `vistas`, `gancho`, `texto` como mínimo).

## Paso 4: ordenar y desarmar

```bash
python3 swipe.py swipe.tsv --out ~/.claude/novacut/x-swipe.md
```

Para cada post calcula el múltiplo sobre la mediana de su cuenta, y después
el desarme:

| | qué nombra |
| --- | --- |
| **gancho** | la fórmula de `../nc-x-post/hooks.json` (21) y el puntaje del gancho |
| **estructura** | una línea, un párrafo, líneas cortas, una lista, un post largo, un hilo |
| **formato** | texto, media, link, largo |

Después compara el tercio de arriba con el de abajo en las tres cosas. Las
cuentas con menos de 5 posts juntados se saltean en vez de ordenarse con
ruido.

## Paso 5: decir qué significa, con cuidado

Reportá tres cosas y nada más:

1. **Qué fórmulas de gancho aparecen de más** en el tercio de arriba, con
   cantidades. Dos fórmulas que aparecen cuatro veces cada una en seis cuentas
   es un hallazgo. Una que aparece dos veces, no.
2. **Qué comparte en estructura el tercio de arriba** que el de abajo no:
   largo de la primera línea, una línea contra lista, media contra texto, con
   link o sin link.
3. **Los ganchos sin clasificar.** Cada gancho que el clasificador no pudo
   nombrar es ruido o una fórmula que `hooks.json` todavía no tiene. Leelos a
   mano. Es la parte más valiosa de la salida. Las regex están pensadas para
   español; un gancho en inglés casi siempre va a caer acá, y eso está bien.

Después decí el tamaño de la muestra en palabras simples. Cuarenta posts en
seis cuentas sostienen una afirmación. Doce no, y decirlo es la diferencia
entre investigar y leer el horóscopo.

## Paso 6: recrearlos para el usuario

Para los tres de arriba, escribí **la versión del usuario**: su propia
historia, su propio número, su audiencia, con la forma que está funcionando.
Leé `~/.claude/novacut/voz.md` primero. Cada uno:

```
ENCONTRADO  @algunacuenta · 6,4x · #7 Lo nuevo · una línea · texto
            "La herramienta de diseño más buscada de este año es un archivo de texto."
FORMA       {El/la} {categoría conocida} más buscada es {algo inesperado}.
TUYO        El empleado de marketing más buscado de 2026 es un archivo de skills.
```

Quedate con la estructura del post encontrado y con ninguna de sus palabras
más allá del molde. Pasá cada uno por `/nc-x-post` (cuenta, puntaje del
gancho) y `/nc-x-human` antes de mostrarlo. Nunca devuelvas "hacé un post como
este". Devolvé un post que pueda publicar mañana. Si la versión del usuario
necesita un número que no te dio, va `{{tu número}}`.

## Salida

La lista ordenada, los tres hallazgos, los ganchos sin clasificar y tres
posts recreados. El archivo de referencias va a `~/.claude/novacut/x-swipe.md`,
donde lo leen `/nc-x-post` y `/nc-x-plan`, así que después de correr esto una
vez el resto del pack trabaja con el nicho del usuario en vez de con
supuestos.

Esta skill no publica, no da like, no sigue a nadie y no manda mensajes. Lee.
