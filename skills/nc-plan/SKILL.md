---
name: nc-plan
description: >-
  Arma la semana en Instagram: qué publicar, en qué formato, cuándo y con quién
  interactuar. Usala cuando el usuario diga "planificame la semana", "¿qué
  publico?", "calendario de contenido", "no tengo de qué publicar", "armame un
  plan de contenido", o quiera un cronograma de publicaciones y una lista de
  cuentas para interactuar. También en inglés: "plan my week", "what should I
  post", "content calendar".
---

# nc-plan

La sala de control. El resto del pack ejecuta; esta skill decide qué se
ejecuta. Usala una vez por semana, siempre el mismo día.

## Qué leer y qué pedir

Si existen `~/.claude/novacut/voz.md`, `~/.claude/novacut/swipe.md` y
`~/.claude/novacut/log.md`, leelos. El swipe file es la evidencia del propio
usuario, sacada con `/nc-viral`, sobre qué fórmulas están funcionando en su
nicho ahora, y pesa más que cualquier cosa de este archivo. El log evita que el
plan repita un tema de las últimas dos semanas.

Si no existen, pedí estas cuatro cosas en una sola pregunta y anotalas:

1. Qué vende el usuario y a quién.
2. Los tres o cuatro temas por los que quiere ser conocido.
3. Qué pasó de verdad esta semana: una llamada con un cliente, un número, un
   error, algo que armó, una discusión que tuvo. De ahí salen los posts.
4. Diez cuentas ante las que vale la pena hacerse ver.

## Qué publicar

Cuatro o cinco publicaciones por semana, y por lo menos tres tienen que ser
Reels. El Reel es el único formato de Instagram que llega de forma confiable a
gente que no sigue la cuenta. Los carruseles profundizan con los que ya te
siguen. Las historias son diarias y se planifican aparte (`/nc-story`).

Mezclá a lo largo de la semana, nunca dos del mismo tipo seguidos:

| tipo | cuántos | trabajo |
| --- | --- | --- |
| **Prueba** | 1 por semana | algo que pasó, con un número. Reel. |
| **Enseñanza** | 1 o 2 por semana | una cosa que el que mira puede hacer hoy. Reel o carrusel. |
| **Opinión** | 1 por semana | una postura que te podría hacer perder seguidores. Reel. |
| **Historia** | 1 cada dos semanas | una escena con un costo. Reel. |
| **Oferta** | 1 cada dos semanas | lo que vendés, dicho claro, sin pedir perdón. Carrusel o historias. |

Para cada lugar dá: el tema, el ángulo concreto sacado de lo que pasó esta
semana, el formato y el número de fórmula de gancho de
`nc-reel/hooks.json` (leé ese archivo para usar el nombre exacto de cada
fórmula). No un tema, un ángulo. "IA" no es un plan. "El presupuesto que
perdimos porque el mail parecía escrito por un robot" es un Reel. "Cómo una
inmobiliaria de Rosario pasó de responder consultas en 2 días a 2 horas" es un
Reel.

Si el ángulo necesita un número que el usuario no te dio, no lo inventes:
`{{tu número}}`.

## Cuándo publicar

Publicá cuando la audiencia está despierta y no está trabajando. Para la
mayoría de las audiencias de consumo es temprano a la noche, hora local; para
una audiencia de negocios, temprano a la mañana.

Pero decilo claro: **la hora importa mucho menos que los primeros dos
segundos.** Instagram sigue mostrando un Reel durante días si funciona, y
entierra uno publicado a la hora perfecta si no funciona. Si el usuario está
optimizando horarios antes de que sus ganchos funcionen, está puliendo lo que
no es, y se lo tenés que decir.

Anclá los horarios a la zona horaria de la audiencia, no a la del usuario, si
son distintas (un creador en Buenos Aires con audiencia en México, por
ejemplo).

## La ronda de interacción, que no es opcional

20 minutos por día, antes de publicar, no después. Armá una lista de 10:

- **5 de alcance**: cuentas con la audiencia que el usuario quiere, donde un
  buen comentario se ve. Comentá temprano, antes de que haya 200 comentarios.
- **3 pares**: mismo tamaño, mismo rubro. Es el grupo que devuelve.
- **2 compradores**: gente que de verdad podría comprar. Comentá durante
  semanas antes de cualquier DM, y nunca vendas en un comentario.

Pasale la lista a `/nc-comment`.

## Salida

```
SEMANA DEL 15 DE SEPTIEMBRE

LUN  solo interacción  (20 min, lista abajo)
MAR  19:30  REEL      PRUEBA     #5   - de 5 horas de presupuesto a 20 minutos
MIÉ  solo historias + interacción
JUE  19:00  CARRUSEL  ENSEÑANZA       - las 4 cláusulas que pongo en cada contrato
VIE  19:30  REEL      OPINIÓN    #2   - dejá de hacer llamadas de diagnóstico gratis
SÁB  -
DOM  18:00  REEL      HISTORIA   #21  - el mail pidiendo el reembolso

HISTORIAS  todos los días, 3 a 5 pantallas, caja de preguntas el jueves.

INTERACCIÓN  (5 alcance / 3 pares / 2 compradores)
  ...

Decime "escribí el martes" y lo redacto.
```

Junto al número de fórmula poné el nombre que tiene en `nc-reel/hooks.json`.

Guardá el plan en `~/.claude/novacut/plan.md` para que las otras skills lo
puedan leer. No se programa ni se publica nada en ningún lado. Es un plan y lo
ejecuta el usuario.
