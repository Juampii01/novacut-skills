---
name: nc-carousel
description: >-
  Arma un carrusel de Instagram: la portada que se gana el deslizamiento, el
  texto placa por placa y los archivos de 1080x1350 para subir. Usala cuando el
  usuario dice "carrusel", "placas", "hacé un post de varias imágenes", "pasá
  esto a carrusel", "make a carousel", "turn this into slides", o tiene una idea
  con forma de lista o de pasos que se muere como imagen sola.
---

# nc-carousel

Los carruseles son el formato de la grilla donde más tiempo se queda la gente,
porque deslizar es una interacción y scrollear no. Además tienen una segunda
oportunidad: Instagram puede volver a mostrar un carrusel arrancando desde una
placa posterior a alguien que no interactuó la primera vez, así que la placa
dos también tiene que sostenerse sola.

El formato premia una idea partida en pasos. Castiga un caption cortado en
pedazos.

## Cuándo usarlo en vez de un Reel

Usá carrusel cuando la idea tiene **secuencia y hay que volver a leerla**:
pasos, un método con partes, un antes y después, una lista que vale una
captura. Usá Reel cuando la idea tiene movimiento, una cara, o una recompensa
que hay que ver pasar.

Si la idea es una sola afirmación, no es ninguno de los dos. Pasásela a
`/nc-reel` y decilo.

## Estructura

De 6 a 10 placas. El tope es 20 (dato de plataforma, puede cambiar) y 20 casi
siempre es un libro que nadie termina. Con menos de 5 el deslizamiento no
arranca.

```
1         PORTADA       el gancho. 6 palabras o menos, a un tamaño que se lea en la
                        grilla en miniatura. Una línea de promesa abajo.
2         LO QUE ESTÁ   por qué importa, en una oración. Esta placa también es una
          EN JUEGO      segunda portada, así que no puede ser preparación.
3 a N     UNA IDEA POR PLACA. Un título de 3 a 7 palabras y, como mucho, 25
                        palabras abajo. Si una placa necesita un párrafo, son dos placas.
N+1       RESUMEN       todo junto, como lista. Es la placa que se captura.
ÚLTIMA    CTA           una acción. Guardar, comentar una palabra clave, o seguir. Una.
```

## Reglas para el texto de las placas

- **La portada es el 80% del resultado.** Seis palabras. Grandes. Nada del
  resto del carrusel salva una portada que nadie desliza.
- **Diseñá para el recorte de la grilla.** La grilla del perfil recorta a un
  rectángulo vertical, y la proporción exacta ya cambió más de una vez.
  Armalo en 1080x1350 y dejá el texto de la portada bien en el centro, lejos de
  los 120 píxeles de cada borde, y el recorte deja de importar.
- **Numerá las placas** (3/8). La gente termina más cuando ve dónde termina.
- **Ninguna placa es un párrafo.** Si no se puede decir en 25 palabras,
  partila.
- **La placa de resumen es la que se captura y se manda.** Los envíos son la
  señal más fuerte que te podés ganar. Que se entienda sola, sin contexto.
- **El @ en cada placa**, chiquito, en una esquina de abajo. Las capturas
  viajan sin vos.
- **Texto alternativo al menos en la portada.** Lo leen los lectores de
  pantalla y lo lee Instagram.
- **Nada inventado.** Si una placa necesita un número que el usuario no dio,
  va `{{tu número}}` y se avisa.

## Armar los archivos

Instagram pide 1080x1350 (4:5), JPG o PNG, hasta 20 elementos. Armalo en HTML
e imprimí cada placa:

```bash
# una <section> por placa, 1080x1350, page-break-after: always
# después Chrome headless --print-to-pdf, o el conversor de HTML a imagen que ya uses
```

Escribí el HTML con `width:1080px; height:1350px`, un solo color de acento, y
ninguna letra de menos de 32px, porque se lee en un celular a un tercio de su
tamaño real. Si el proyecto tiene una skill de marca o un sistema de diseño,
usalo y no inventes una paleta. Revisá que las tildes y la ñ se vean bien en la
tipografía elegida (`<meta charset="utf-8">` y una fuente con soporte para
español).

## Salida

Primero el texto placa por placa, como lista numerada que el usuario pueda
leer en diez segundos y corregir antes de que se renderice nada. Después el
**caption**, que en un carrusel es el Trabajo B de `/nc-caption`: el caption
trabaja, porque la portada ya gastó sus seis palabras.

Pasá las dos cosas por `/nc-human`. Armá los archivos recién cuando el usuario
apruebe el texto.

```
CARRUSEL  ·  8 placas

1  PORTADA   LA CLÁUSULA DE USD 18.000
             Una línea que ahora pongo en cada contrato.
2  EN JUEGO  Aprobé el trabajo. Nueve días después me pidieron la plata de vuelta.
3            QUÉ DICE
             Se paga contra entrega, no contra aprobación.
...
7  RESUMEN   Las cuatro líneas, en orden.
8  CTA       Comentá CONTRATO y te mando la cláusula completa.

Caption: Trabajo B, gancho en la línea 1, un pedido, 3 hashtags.
```

No se sube nada. El usuario lo publica.
