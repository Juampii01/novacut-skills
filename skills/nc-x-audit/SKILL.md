---
name: nc-x-audit
description: >-
  Autopsia de lo que el usuario ya publicó en X: qué posts funcionaron de
  verdad, por qué, y qué dejar de hacer, a partir de su propia exportación de
  estadísticas. Usala cuando el usuario comparta su CSV de estadísticas de X o
  posts anteriores y pregunte "¿qué me funciona?", "¿por qué este no
  anduvo?", "leé mis estadísticas", "auditá mi cuenta", "¿en qué redoblo?", o
  quiera saber si los links, los hilos o el horario le importan de verdad.
  También en inglés: "what's working", "read my analytics", "audit my
  account".
---

# nc-x-audit

La única fuente honesta de lo que funciona para una cuenta es esa cuenta.
Cada regla de cada guía de X, incluidas las de este pack, es una suposición
previa. Los últimos 30 posts del usuario son la evidencia.

En esta carpeta hay una herramienta y funciona:

```bash
python3 audit.py account_analytics_content.csv
```

## Qué pedir

En este orden de preferencia:

1. **La exportación de estadísticas.** En computadora: x.com/i/account_analytics,
   después Exportar. Es una función de Premium. Una fila por post: impresiones
   más las interacciones (likes, respuestas, reposts, guardados, compartidos,
   seguidores nuevos, visitas al perfil). X no documenta los nombres de las
   columnas y ya los cambió, así que `audit.py` los reconoce de forma flexible,
   en inglés o en español ("Impressions" o "Impresiones", "Likes" o "Me
   gusta"); la exportación vieja de analytics.twitter.com también sirve.
2. **Una planilla a mano** con el texto del post, impresiones y los números que
   el usuario pueda ver. Con veinte filas alcanza para una primera pasada. Las
   fechas en día/mes/año y los números con punto de miles ("12.400") se leen
   bien.
3. **Capturas** de los posts con sus números. Pasalas a un CSV.

Leé también `~/.claude/novacut/x-registro.md` si existe: ahí está qué fórmula
de gancho usó cada post.

## Qué mide, y por qué no las impresiones

Las impresiones dependen sobre todo de cuánta gente ya sigue al usuario.
`audit.py` ordena por cosas que no:

| métrica | qué te dice |
| --- | --- |
| **Tasa de interacción** | si el post se ganó el alcance que tuvo |
| **Respuestas cada 1.000 impresiones** | si arrancó una conversación. El ranking de X pesa las respuestas muy por encima de los likes |
| **Compartidos cada 1.000** (reposts + compartidos) | si viajó. Compartir por DM o copiando el link están entre las acciones que más pesan en lo que publica X |
| **Guardados cada 1.000** | si alguien lo piensa usar |
| **Seguidores cada 1.000** | si hizo que alguien quiera más del usuario |

Los posts debajo de un piso de impresiones quedan fuera del ranking, y las
respuestas del usuario en posts de otros (filas que empiezan con @) se cuentan
y se apartan, para que una buena semana respondiendo no tape los posts.

## Después, encontrar el patrón

`audit.py` agrupa los posts por fórmula de gancho (clasificada con
`../nc-x-post/hooks.json`), por largo y por formato (solo texto contra con
link o imagen/video), y muestra cada grupo cuya tasa de interacción esté 1,4
veces arriba o abajo del resto, con su n y una palabra de confianza. Mira el
día de la semana **último**, y solo lo menciona cuando nada más separa. Casi
nunca es la causa, y es donde la gente quiere que esté.

Sumá lo que el script no ve, leyendo los 5 de arriba y los 5 de abajo lado a
lado:

- Tema. ¿Cuáles de los temas del usuario están arriba?
- Si el usuario respondió en la primera hora.
- Si en el post el usuario quedaba bien o quedaba mal.

**La pregunta de los links, respondida con sus datos.** X dice que dejó de
castigar los posts con links hace más de un año. Un análisis independiente de
enero de 2026 todavía les midió menos vistas. Si el hallazgo de formato
muestra los posts con link bastante por debajo del resto con n de 5 o más, esa
es la respuesta para esta cuenta, diga lo que diga quien sea. Si no muestra
nada, los links están bien acá.

Escribí cada hallazgo como una afirmación con su evidencia, y decí qué tan
seguro es. Con 30 posts puede aparecer un patrón. Con 8, decí eso en vez de
inventar uno.

## Salida

```
AUDITORÍA  ·  38 posts  ·  01/07 - 28/08  ·  15 respuestas apartadas

ARRIBA POR TASA DE INTERACCIÓN
    5,8%    8.6 resp/1k    8.6 comp/1k     5.705 imp  "USD 4.000 es lo que me costó una mala..."
    ...

LO QUE DICEN LOS DATOS
  1. formato = solo texto: 2,7% vs 0,8% del resto (3.3x, arriba). n=26, sólido.
  2. fórmula de gancho = La confesión de costo: 3,9% vs 1,9% del resto (2.0x, arriba). n=4, débil.
  El día de la semana no muestra nada. Dejá de optimizarlo.

DEJAR:     los posts con link adelante. Poné el link en una respuesta en los próximos diez y volvé a correrlo.
HACER MÁS: los posts donde pagaste un costo, con el número en la línea 1.
```

Después pasale las conclusiones a `/nc-x-plan`, para que la semana que viene
se arme con la evidencia del usuario en vez de con supuestos. No completes con
datos que el usuario no te dio.
