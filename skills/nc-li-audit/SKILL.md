---
name: nc-li-audit
description: >-
  Autopsia de lo que el usuario ya publicó en LinkedIn: qué posts funcionaron
  de verdad, por qué, y qué dejar de hacer. Usala cuando el usuario pegue sus
  estadísticas de LinkedIn o posts anteriores y pregunte "¿qué me está
  funcionando?", "¿por qué este no anduvo?", "leé mis estadísticas",
  "auditá mi contenido", o quiera saber en qué redoblar. También en inglés:
  "what's working", "read my analytics", "audit my content".
---

# nc-li-audit

La única fuente honesta de lo que funciona para una cuenta es esa cuenta.
Cada regla de cada guía de LinkedIn, incluidas las de este pack, es una
suposición previa. Los últimos 30 posts del usuario son la evidencia.

## Qué pedir

Lo que el usuario tenga:

- La exportación de estadísticas de los posts (LinkedIn: Estadísticas ->
  Contenido -> Exportar). Un Excel o CSV.
- O una captura por post con impresiones, reacciones, comentarios y
  compartidos.
- O solo los posts y sus reacciones, que alcanza para una primera pasada.

Leé también `~/.claude/novacut/li-registro.md` si existe: ahí está qué
fórmula de gancho usó cada post.

## Qué medir de verdad

Las impresiones a secas son el número menos útil de la página, porque
dependen sobre todo de cuánta gente ya sigue al usuario. Calculá esto en su
lugar, y mostrá la cuenta:

| métrica | cómo | qué te dice |
| --- | --- | --- |
| **Tasa de interacción** | (reacciones + comentarios + compartidos) / impresiones | si el post se ganó el alcance que tuvo |
| **Proporción de comentarios** | comentarios / reacciones | si arrancó algo o solo recibió un gesto |
| **Múltiplo de alcance** | impresiones / seguidores | si viajó más allá de la audiencia que ya tenía |
| **Guardados / envíos** | si están disponibles | el mejor indicador individual de alcance futuro |

Ordená por tasa de interacción y múltiplo de alcance, no por impresiones. Un
post con 900 impresiones y 40 comentarios le ganó al de 12.000 impresiones y
6 comentarios.

## Después, encontrar el patrón

Con los 5 de arriba y los 5 de abajo lado a lado, buscá qué los separa de
verdad, y animate a una conclusión que al usuario no le guste:

- Fórmula de gancho. ¿Qué números de `../nc-li-post/hooks.json` están arriba?
- Formato. Texto, documento, imagen, video.
- Largo.
- Tema.
- Día y hora: miralo **último**, y solo si los otros cuatro no muestran nada.
  Casi nunca es la causa, y es donde la gente quiere que esté.
- Comentarios de la primera hora. Posts que el usuario respondió dentro de la
  primera hora contra los que no.

Escribí cada hallazgo como una afirmación con su evidencia, y decí qué tan
seguro es. Con 30 posts se puede ver un patrón; con 6 no, y tenés que decir
eso en vez de inventar uno. Nunca completes con datos que el usuario no te dio.

## Salida

```
AUDITORÍA  ·  31 posts  ·  12 jun - 5 sep

ARRIBA POR TASA DE INTERACCIÓN
  8,1%  #3  La confesión  "USD 4.000 es lo que me costó no tener contrato"   1.940 imp
  6,4%  #20 El portazo    "Despedí a mi cliente que más pagaba"            2.210 imp
  ...

ABAJO
  0,4%  #5  La lista      "7 herramientas que todo emprendedor necesita"   11.400 imp
  ...

LO QUE DICEN LOS DATOS
1. Los posts donde el que quedó mal fuiste vos: promedio 6,2% contra 1,1% del
   resto. n=6. Es tu señal más fuerte y no está ni cerca.
2. Las listas de herramientas consiguen impresiones y nada más. Mucho alcance,
   cero comentarios, cero clientes. Tres de tus cinco de abajo.
3. El día de la semana no muestra nada. Tu promedio del martes y el del viernes
   están dentro del ruido. Dejá de optimizarlo.

DEJAR: listas de herramientas.
HACER MÁS: los posts con un costo que pagaste, y un número.
```

Después pasale las conclusiones a `/nc-li-plan`, para que el plan de la
semana que viene se arme con la evidencia del usuario y no con supuestos.
