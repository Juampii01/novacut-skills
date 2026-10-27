---
name: nc-profile
description: >-
  Puntúa un perfil de Instagram sobre 100 con una rúbrica de 12 partes y
  reescribe lo que pierde puntos: campo de nombre, bio, link, destacadas, los
  tres fijados y la grilla. Usala cuando el usuario diga "optimizá mi perfil",
  "arreglame la bio", "puntuá mi Instagram", "¿por qué no me siguen?", "revisá
  mi perfil", o pegue su perfil y pregunte cómo se lee. También en inglés:
  "optimize my profile", "fix my bio", "score my Instagram".
---

# nc-profile

Casi todo el mundo optimiza lo que no es. El perfil no es una vidriera que la
gente recorre con calma. Es una **pantalla de decisión**: la persona llega desde
un solo reel y el perfil tiene unos tres segundos para responder una pregunta:
¿hay más de eso acá, y es para mí?

## Qué pedir

Pedile al usuario que pegue o mande captura de: el campo de nombre, el usuario
(@), la bio, adónde lleva el link, los nombres de las destacadas, qué tiene
fijado y las primeras nueve portadas de la grilla. Con una captura de la parte
de arriba del perfil más las dos primeras filas de la grilla alcanza para una
primera pasada.

No entres a Instagram en su nombre ni le pidas la contraseña.

## Puntuá

Leé `rubric.json` en esta carpeta. Son doce ítems, 100 puntos, cada uno con
cómo se ve el puntaje completo y cómo suele fallar. Puntuá todos, mostrá la
tabla y el total. Sé honesto: la mayoría de los perfiles queda entre 30 y 49 en
la primera pasada, y un puntaje generoso no le sirve a nadie.

```
PUNTAJE DEL PERFIL  38/100

  campo de nombre       2/12   solo el nombre, ninguna palabra que alguien busque
  primera línea bio     3/12   tres sustantivos y un emoji de café
  los tres fijados      0/10   nada fijado
  destacadas            2/8    "Random", "Vida", "2023"
  grilla legible        4/8    seis de nueve portadas son una cara a mitad de frase
  ...
```

Usá las etiquetas en español del campo `label` de cada ítem de la rúbrica.

## Después reescribí, en este orden

Arreglá de mayor a menor según los puntos perdidos. No reescribas todo de una:
el usuario tiene que ir y cambiar cada cosa a mano.

**1. El campo de nombre (30 caracteres).** La línea en negrita debajo de la
foto, no el @. Es el campo con el que matchea la búsqueda de Instagram, y la
mayoría pone solo su nombre. Formato que funciona:
`{Nombre} | {qué hacés, con palabras que la gente busca}`. Ejemplos:
`Caro Medina | Nutrición deportiva`, `Martín Ríos | Inmobiliaria en Córdoba`.
Dá tres opciones.

**2. Primera línea de la bio.** Para quién es y qué le cambia. No un cargo, no
adjetivos, no una lista de identidades separadas por barras. El resto de los
150 caracteres lleva una sola prueba o una oferta clara.

**3. Los tres fijados.** Tres lugares, tres trabajos distintos: la mejor
prueba, la explicación más clara de la oferta y la mejor presentación de la
persona. Es el arreglo de más impacto de todo el perfil y son cuatro toques.
Una grilla sin fijados muestra lo último que se subió, que es tirar una moneda.

**4. Destacadas.** Entre cuatro y seis, con el nombre de las preguntas que hace
un comprador: Precios, Resultados, Cómo funciona, Sobre mí. Nada de "Random".
Borrá el resto.

**5. El link.** Un solo destino que cumpla lo que la bio acaba de prometer.
Instagram permite hasta cinco (puede cambiar); con dos ya es un menú, y un menú
convierte peor que una puerta.

**6. Portadas de la grilla.** Las primeras nueve en tamaño miniatura. La
portada de un reel se elige, no se deja el fotograma que tocó. Cuatro palabras
de texto en la portada hacen que la grilla se lea de un vistazo.

## Salida

La tabla de puntaje y después las reescrituras como bloques listos para
copiar, en orden de prioridad, cada una pasada por `/nc-human`. Al final volvé
a puntuar y mostrá la diferencia con honestidad. Si la reescritura llega a 84
y no a 98, decí 84, y decí qué falta, que casi siempre es la grilla, el hábito
de historias y un post fijado que todavía no existe. Nada de eso se arregla
reescribiendo.

Si no hay un dato (un resultado, un número de clientes), no lo inventes:
dejá `{{tu número}}` y avisá.

Esta skill no guarda nada en Instagram. El usuario edita cada campo.
