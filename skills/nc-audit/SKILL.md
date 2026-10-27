---
name: nc-audit
description: >-
  Autopsia de lo que el usuario ya publicó: qué reels funcionaron de verdad,
  por qué, y qué dejar de hacer. Usala cuando el usuario pegue sus
  estadísticas de Instagram o sus posts anteriores y pregunte "¿qué está
  funcionando?", "¿por qué no anduvo este reel?", "leé mis métricas",
  "auditá mi contenido", "analizá mis estadísticas", o quiera saber de qué
  hacer más. También en inglés: "what's working", "why did this flop", "audit
  my content".
---

# nc-audit

La única fuente honesta de lo que funciona para una cuenta es esa cuenta. Cada
regla de cada guía de Instagram, incluidas las de este pack, es un supuesto
previo. Los últimos 30 posts del usuario son la evidencia.

## Qué pedir

Pedí lo que el usuario tenga:

- Estadísticas por post: visualizaciones, alcance, interacciones, tiempo de
  reproducción, guardados, compartidos, seguidores ganados y el porcentaje de
  alcance de no seguidores. Las capturas sirven.
- O el gráfico de retención de sus mejores y peores reels recientes. Esa sola
  captura vale más que todo lo demás junto.
- O solo los posts y sus visualizaciones, que alcanza para una primera pasada.

Leé también `~/.claude/novacut/log.md` si existe, porque registra qué fórmula
de gancho usó cada post.

Trabajá solo con los números que te dio el usuario. No completes huecos con
estimaciones: si falta un dato, la métrica queda vacía y lo decís.

## Qué medir de verdad

Las visualizaciones a secas son el número menos útil de la pantalla, porque
dependen sobre todo de cuánta gente ya sigue la cuenta. Calculá esto y mostrá
las cuentas:

| métrica | cómo | qué te dice |
| --- | --- | --- |
| **Múltiplo outlier** | vistas / mediana de vistas de la propia cuenta | si fue un éxito real o un día normal |
| **Alcance a no seguidores** | % del alcance que vino de gente que no sigue | si viajó o no |
| **Retención a los 3 s** | los que siguen a los 3 s / los que empezaron | si el gancho funcionó. Es la nota del gancho. |
| **Tiempo promedio de reproducción** | directo de las estadísticas | si funcionó el medio |
| **Envíos por alcance** | compartidos / alcance | la señal individual más fuerte que podés ganar. Un envío es alguien poniendo su nombre detrás del post. |
| **Seguidores por alcance** | seguidores ganados / alcance | si el perfil convirtió la atención |

Ordená por múltiplo outlier y envíos por alcance, no por vistas. Un reel con
4.000 vistas y 90 envíos le ganó al de 60.000 vistas y 11.

## Después, encontrá el patrón

Con los cinco mejores y los cinco peores lado a lado, buscá qué los separa, y
animate a concluir algo que al usuario no le va a gustar:

- **Retención a los 3 segundos.** Si los de arriba y los de abajo difieren
  acá, es el gancho y nada más, y todo lo que viene después es una
  distracción.
- **Fórmula de gancho.** ¿Qué números de `nc-reel/hooks.json` están entre los
  cinco mejores?
- **Formato.** Reel, carrusel, imagen única.
- **Duración.** Agrupá en menos de 15 s, 15 a 30 s, 30 a 60 s, más de 60 s.
- **Tema.**
- **Si el usuario respondió comentarios en la primera hora.**
- **Día y hora.** Revisalo **al final** y solo si lo demás no muestra nada.
  Casi nunca es la causa y es donde la gente quiere que esté.

Planteá cada hallazgo como una afirmación con la evidencia al lado, y decí qué
tan seguro es. Con 30 posts se puede ver un patrón. Con 6 no, y decirlo es
mejor que inventar uno.

## La distinción que ahorra meses

**Un reel que tiene vistas y no suma seguidores no es un reel fallido, es un
problema de perfil.** Un reel que no tiene vistas es un problema de gancho.
Separá las dos cosas antes de recomendar nada. Si el alcance a no seguidores
es alto y los seguidores por alcance son bajos, dejá de reescribir ganchos y
andá a `/nc-profile`.

## Salida

```
AUDITORÍA  ·  31 posts  ·  12 jun - 5 sep  ·  mediana de vistas 4.100

TOP 5 POR MÚLTIPLO OUTLIER
  18,2x  #3   74.600 vistas  62% no seguidores  ret@3s 71%  128 envíos
   6,4x  #1   26.300 vistas  48% no seguidores  ret@3s 64%   71 envíos
  ...

LOS 5 DE ABAJO
   0,3x  #11   1.200 vistas   9% no seguidores  ret@3s 31%    2 envíos
  ...

LO QUE DICEN LOS DATOS
1. La retención a los 3 segundos es toda la historia. Los cinco de arriba
   promedian 66%, los de abajo 33%. Todo lo demás que te preocupa viene después
   de los dos primeros segundos.
2. Los posts donde el que quedaba mal eras vos: media de 8,1x contra 0,9x del
   resto. n=5. Es la señal más fuerte y no hay comparación.
3. Las listas de herramientas traen vistas y nada más. Mucho alcance, cero
   envíos, cero seguidores. Tres de tus cinco peores.
4. El día de la semana no muestra nada. Las medias de martes y viernes están
   dentro del ruido. Dejá de optimizarlo.

DEJÁ DE HACER: listas de herramientas.
HACÉ MÁS: los que tienen un costo que pagaste y un número.
```

Junto a cada número de fórmula poné el nombre que tiene en
`nc-reel/hooks.json`.

Después pasale las conclusiones a `/nc-plan`, para que la semana que viene se
arme con la evidencia del propio usuario y no con supuestos genéricos, y a
`/nc-viral`, para que el swipe file se filtre a las fórmulas que funcionan
para esta cuenta en particular.
