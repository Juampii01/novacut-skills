---
name: nc-caption
description: >-
  Escribe el caption de Instagram (la línea que sobrevive al corte de "... más",
  el cuerpo, el único pedido, los términos de búsqueda y los hashtags) y lo
  revisa antes de que salga. Usala cuando el usuario dice "escribime el
  caption", "poné el texto de este post", "qué pongo en la descripción",
  "cuántos hashtags uso", "write the caption", "caption this", o tiene un reel o
  un carrusel listo y le falta el texto.
---

# nc-caption

En esta carpeta hay una herramienta y funciona:

```bash
python3 caption.py caption.txt
python3 caption.py caption.txt --keywords "presupuestos para clientes,precios de diseño"
```

Imprime el caption como lo imprime el feed: los primeros 125 caracteres en una
caja, todo lo demás detrás del toque. Leé esa caja antes que cualquier otra
cosa que hayas escrito.

## Primero, decidí qué trabajo tiene este caption

Es la decisión que arruina captions cuando se saltea.

**Trabajo A: el video ya los enganchó.** Un Reel trae su propio gancho en los
primeros dos segundos, dicho y en pantalla. El caption no es un segundo gancho,
y competir con el video es la forma de perder los dos. Su trabajo es el pedido,
el contexto que hace que el pedido tenga sentido, y las palabras que la gente
busca.

**Trabajo B: el caption es el contenido.** Una foto, una imagen sola, la
portada de un carrusel que deja algo abierto. Acá la primera línea es el
gancho y funciona igual que el de un Reel: concreta, corta, y cortada en un
precipicio, no a mitad de una subordinada.

Preguntá cuál estás escribiendo. Si el usuario tiene un Reel con un gancho
fuerte, escribí el A y decí por qué.

## La forma

```
Línea 1     125 caracteres visibles. Trabajo A: el pedido, sin vueltas.
            Trabajo B: el gancho.
            Nunca un saludo, nunca un hashtag, nunca un emoji como primer carácter.
Cuerpo      párrafos cortos, una línea en blanco entre cada uno. De dos a seis.
            Acá viven los términos de búsqueda.
El pedido   uno. Comentar una palabra clave, guardar, o mandar DM. Uno.
Hashtags    hasta cinco, en su propia línea al final, o ninguno.
```

El límite es de 2.200 caracteres y casi nada necesita 2.200. Un caption que se
gana el toque y después entrega 600 caracteres le gana a uno que entrega 1.800.

## Hashtags, con honestidad

Los hashtags ya no son una palanca de alcance, y la plataforma lo dijo con un
cambio de producto: **Instagram limitó los hashtags a cinco por publicación el
18 de diciembre de 2025**, cuando antes eran treinta, y les dijo a los
creadores que usar menos y más específicos funciona mejor que muchos
genéricos. Ya antes, en 2025, Adam Mosseri había dicho que los hashtags no
aumentan el alcance: son una etiqueta, no una forma de distribución. Es un dato
de plataforma y puede cambiar; si Instagram muestra otra cosa cuando leas esto,
Instagram tiene razón.

Entonces: hasta cinco, específicos, como etiquetas de tema. Si el usuario tiene
un bloque de veinte guardado en las notas del celular, ese bloque ahora es peso
muerto y el revisor lo va a marcar.

`#viral`, `#fyp`, `#parati`, `#explorar` no describen nada. Sacalos.

## Los términos de búsqueda importan más que los hashtags

El buscador de Instagram lee el texto del caption. Así que la frase por la que
el usuario quiere que lo encuentren va en el caption como la escribiría una
persona, dentro de una oración normal. "Presupuestos para clientes" como
palabras en la línea tres, no "#presupuestosparaclientes" en un bloque al
final.

Pedí dos o tres de esos términos y pasáselos al revisor (no le importan las
tildes ni las mayúsculas al buscar):

```bash
python3 caption.py borrador.txt --keywords "presupuestos para clientes,precios de diseño"
```

## Reglas

- **Nada de links en el caption.** En el caption no se puede hacer clic. Una
  URL en el texto es texto muerto que dice "no uso esta plataforma". Bio o DM.
- **Un solo pedido.** Dos pedidos es lo mismo que ninguno. `caption.py` los
  cuenta (y reconoce voseo y tuteo: "comentá/comenta", "guardalo/guárdalo",
  "escribime/escríbeme").
- **El pedido de palabra clave necesita una palabra que se pueda tipear.** Una
  sola, sin espacios, sin emoji, en mayúsculas, y decila también en el video.
  `Comentá CONTRATO` funciona. `Comentá "la guía del contrato"` no.
- **Escribí el primer comentario aparte** si hay un link. Decilo en el resumen.
- **Emojis como puntuación, no como decoración.** El revisor marca más de 4
  cada 100 caracteres.
- **El texto alternativo vale 20 segundos.** En carruseles y fotos, escribilo.
  Lo leen los lectores de pantalla y lo lee Instagram.
- **Nunca inventes datos.** Si el caption necesita un número que el usuario no
  te dio, dejá `{{tu número}}` y avisalo.

## El circuito

1. Decidí Trabajo A o B y decí cuál.
2. Escribí el borrador.
3. Pasalo por `/nc-human`. Los captions son cortos, así que el relleno suena
   más fuerte acá que en cualquier otra parte del pack.
4. Corré `caption.py` con los términos de búsqueda del usuario. Arreglá cada
   MAL. Decidí en voz alta qué hacer con cada OJO, no en silencio.
5. Imprimí el bloque listo para copiar y después el resumen:

```
CAPTION LISTO
trabajo:      A - el reel lleva el gancho
visible:      118 de 125 caracteres usados antes del corte
pedido:       uno, comentar CONTRATO
hashtags:     3
búsqueda:     "presupuestos para clientes" en la línea 3, "precios de diseño" en la línea 5
revisor:      LISTO
```

No se publica nada. El usuario lo pega.
