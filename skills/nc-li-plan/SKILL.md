---
name: nc-li-plan
description: >-
  Arma la semana en LinkedIn: qué publicar, cuándo y con quién interactuar.
  Usala cuando el usuario diga "planificá mi semana", "¿qué publico?",
  "calendario de contenido para LinkedIn", "no tengo de qué publicar", o
  quiera un cronograma de publicación y una lista de personas con las que
  interactuar. También en inglés: "plan my week", "what should I post",
  "content calendar".
---

# nc-li-plan

La sala de control. Todo lo demás del pack ejecuta; esto decide qué se
ejecuta. Corrélo una vez por semana, siempre el mismo día.

## Qué leer o pedir

Si existen `~/.claude/novacut/voz.md`, `~/.claude/novacut/li-registro.md` y
el último resultado de `/nc-li-audit`, leelos: el plan no tiene que repetir un
tema de las últimas dos semanas, y tiene que apoyarse en lo que la evidencia
del propio usuario dice que funciona. Si no existen, pedí cuatro cosas y
anotalas:

1. Qué vende el usuario, y a quién.
2. Los tres o cuatro temas por los que quiere que lo conozcan.
3. Qué pasó de verdad esta semana: una llamada con un cliente, un número, un
   error, algo que construyó, una discusión. De ahí salen los posts.
4. Diez a veinte personas o empresas ante las que vale la pena ser visible.

## Qué publicar

Cuatro posts por semana le ganan a siete. La constancia es un piso, no una
meta, y el quinto post de la semana casi siempre es el flojo que tira el
promedio abajo.

Mezclá a lo largo de la semana, nunca dos del mismo tipo seguidos:

| tipo | cuántos | para qué |
| --- | --- | --- |
| **Prueba** | 1 por semana | algo que pasó, con un número |
| **Opinión** | 1 por semana | una postura que te podría costar seguidores |
| **Enseñanza** | 1 por semana | una cosa que el lector puede hacer hoy |
| **Historia** | 1 cada dos semanas | una escena con diálogo y un costo |
| **Oferta** | 1 cada dos semanas | lo que vendés, dicho claro, sin pedir perdón |

Para cada lugar dá: el tema, el ángulo concreto sacado de lo que pasó esta
semana, y el número de fórmula de `../nc-li-post/hooks.json` que le calza. No
un tema: un ángulo. "IA" no es un plan. "El presupuesto que perdimos porque el
borrador de la IA tenía rayas largas por todos lados" es un post.

## Cuándo publicar

Publicá cuando la audiencia del usuario está frente a la computadora. Para
una audiencia B2B en un solo huso horario, martes a jueves entre 7:30 y 9:30
hora local es el punto de partida, con lunes a la tarde y viernes a la mañana
como segunda opción. Los fines de semana, posts de historia personal o nada.

Ojo con los husos: si el usuario está en Argentina y vende a España, la
audiencia está 4 o 5 horas adelante; si vende a México, 2 o 3 horas atrás.
Anclá los horarios al huso de la audiencia, no al del usuario.

Y decilo claro: **el día y la hora importan mucho menos que la primera
línea.** Si el usuario está optimizando horarios antes de que sus ganchos
funcionen, está puliendo lo equivocado, y se lo tenés que decir.

## Con quién interactuar

Una lista de 10, en tres grupos:

- **5 de alcance**: gente con la audiencia que el usuario quiere, a cuyos posts
  puede aportar de verdad. Comentar antes de que tengan 20 comentarios, o
  nadie lo ve.
- **3 colegas**: mismo nivel, mismo rubro. Es el grupo que devuelve la
  interacción.
- **2 compradores**: gente que podría comprar de verdad. Comentar en sus posts
  durante semanas antes de cualquier mensaje privado, y nunca vender en un
  comentario.

20 minutos por día, antes de publicar, no después. Los comentarios en posts
ajenos son lo que hace que el post propio llegue.

## Salida

```
SEMANA DEL 8 DE SEPTIEMBRE

LUN  solo interacción  (20 min, lista abajo)
MAR  8:15  PRUEBA     #17 El ancla de tiempo  - el presupuesto que pasó de 5 horas a 20 minutos
MIÉ  solo interacción
JUE  8:00  OPINIÓN    #1  Contra la corriente - por qué dejamos las llamadas de diagnóstico
VIE  8:30  ENSEÑANZA  #21 El valor directo    - el mail de 4 líneas para reabrir ventas, regalado
SÁB  -
DOM  16:00 HISTORIA   #9  Arranque en frío    - el mail de "nos vamos con alguien más barato"

INTERACCIÓN  (5 alcance / 3 colegas / 2 compradores)
  ...

Decime "escribí el martes" y lo redacto.
```

Escribí el plan en `~/.claude/novacut/li-plan.md` para que las otras skills lo
lean. No se programa ni se publica nada en ningún lado: es un plan, y lo
ejecuta el usuario.
