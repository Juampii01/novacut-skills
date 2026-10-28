---
name: nc-x-plan
description: >-
  Planifica la semana del usuario en X: qué publicar, cuándo y con quién
  interactuar. Usala cuando el usuario diga "planificá mi semana en X", "¿qué
  publico?", "calendario de contenido", "cronograma de publicación", "no
  tengo de qué publicar", o quiera una mezcla semanal de posts, hilos y
  respuestas y una lista de cuentas con las que interactuar. También en
  inglés: "plan my week", "what should I post", "posting schedule".
---

# nc-x-plan

La sala de control. Todo lo demás del pack ejecuta; esto decide qué se
ejecuta. Corrélo una vez por semana, siempre el mismo día.

En esta carpeta hay una herramienta:

```bash
python3 weights.py              # qué premia y qué castiga el ranking de X, leído del código de X
python3 weights.py --offline    # la última foto guardada, si no hay conexión
```

`weights.py` hace una sola consulta a un archivo público de GitHub (el código
de ranking que publica X). No usa ninguna cuenta ni clave. Si no hay red,
muestra la foto guardada y lo dice.

## Qué leer o pedir

Leé estos si existen: `~/.claude/novacut/voz.md`, `~/.claude/novacut/x-registro.md`
(qué se publicó, con qué fórmula), `~/.claude/novacut/x-swipe.md` (qué está
funcionando en el nicho, de `/nc-x-viral`) y el último resultado de
`/nc-x-audit`. El plan no tiene que repetir un tema de las últimas dos
semanas, y tiene que apoyarse en lo que dice la evidencia del propio usuario.

Si no existen, pedí cuatro cosas y anotalas:

1. Qué vende el usuario, y a quién.
2. Los tres o cuatro temas por los que quiere que lo conozcan.
3. Qué pasó de verdad esta semana: un número, un cliente, un error, algo que
   construyó, una discusión. De ahí salen los posts.
4. Veinte cuentas de su nicho, de mucho más grandes a más o menos de su tamaño.

## Qué publicar

X se mueve más rápido que otras redes y premia estar presente, pero el volumen
no es la palanca que la gente cree. Un punto de partida para una cuenta de
una persona:

| formato | por semana | para qué |
| --- | --- | --- |
| **Post** | 5-7 | una idea, de una a tres líneas. El caballo de batalla. `/nc-x-post` |
| **Hilo** | 1-2 | las mejores ideas de la semana, con pasos. `/nc-x-thread` |
| **Cita** | 1-2 | tu mirada sobre la noticia de la semana en el nicho |
| **Encuesta** | 0-1 | solo cuando las respuestas son el post de la semana que viene |
| **Video / imagen** | 1 | una grabación de pantalla o un gráfico le gana a una foto de stock |
| **Respuestas** | 10-30 por día | en posts de otros. `/nc-x-comment`. Esto es el crecimiento |

Dos límites que conviene conocer: X limita a las cuentas no verificadas a 50
posts originales y 200 respuestas por día (a 2026, puede cambiar). Nadie
debería acercarse a ninguno de los dos.

Para cada lugar dá el tema, el ángulo concreto sacado de lo que pasó esta
semana, y el número de fórmula de `../nc-x-post/hooks.json`. No un tema: un
ángulo. "IA" no es un plan. "El presupuesto que perdí porque el borrador tenía
rayas largas por todos lados" es un post.

## Lo que X premia de verdad

Corré `python3 weights.py` y leele la salida al usuario en un párrafo. La forma
alrededor de la que se planifica: las respuestas, las citas y los compartidos
pesan mucho más que los likes, una respuesta entre dos cuentas que se siguen
mutuamente tiene un extra, y silenciar, "no me interesa" y denunciar pesan
muy en contra. Los propios comentarios del archivo dicen que se aplican a
probabilidades predichas, no a cantidades, así que no los conviertas en "una
respuesta = 10 likes".

Dos consecuencias prácticas:

- **Planificá para respuestas, no para likes.** Un post que pide una respuesta
  con honestidad (una pregunta concreta, una afirmación que la gente va a
  discutir) le gana a un post armado para el aplauso.
- **Los grupos de interacción no sirven.** Los comentarios del código de X dicen
  que la interacción solo cuenta para el ranking cuando el post se mostró en
  el timeline de quien interactúa; mandar gente al post desde un grupo de
  WhatsApp no tiene efecto en el ranking.

## Cuándo publicar

Cuando la audiencia del usuario está despierta y scrolleando, en el huso de la
audiencia: las mañanas de días hábiles y el mediodía son el punto de partida
para un público profesional. Si el usuario está en Buenos Aires y le habla a
México, son 2 o 3 horas menos; si le habla a España, 4 o 5 más. Y decilo
claro también: **la hora importa mucho menos que la primera línea.** Si el
usuario está ajustando horarios antes de que sus ganchos funcionen, está
puliendo lo equivocado.

La mejor palanca de horario es la hora después de publicar: estar ahí para
responder.

## Con quién interactuar

Una lista de 10 para la semana:

- **5 de alcance**: cuentas más grandes a cuyos posts el usuario puede aportar
  de verdad. Activar las notificaciones de sus posts y responder en los
  primeros 15 minutos.
- **3 colegas**: mismo tamaño, mismo nicho. Te responden de vuelta, y las
  respuestas entre mutuos son las que X potencia.
- **2 compradores**: gente que podría comprar. Responder sus posts durante
  semanas antes de cualquier DM, y nunca vender en una respuesta.

## Salida

```
SEMANA DEL 28 DE SEPTIEMBRE

LUN  9:00   HILO      #16 La promesa de hilo  - los 40 posts virales que leí, qué tenían en común
MAR  8:30   POST      #9  El ancla de tiempo  - presupuestos, de 5 horas a 20 minutos
MIÉ  12:00  ENCUESTA  -                       - "¿cuál pagás?" (las respuestas = el post del viernes)
JUE  9:00   HILO      #2  El número revelado  - 90 días publicando todos los días, qué movió los números
VIE  17:00  VIDEO     #15 El lanzamiento      - grabación de pantalla de 40 segundos de la herramienta nueva
SÁB  10:00  POST      #21 La frase sola       - (del resultado de la encuesta del miércoles)
DOM  19:00  CITA      -                       - la noticia más grande del nicho, tu mirada

TODOS LOS DÍAS  20 respuestas antes de publicar, no después. Lista abajo.

INTERACCIÓN  (5 alcance / 3 colegas / 2 compradores)
  ...

Decime "escribí el martes" y lo redacto.
```

Escribí el plan en `~/.claude/novacut/x-plan.md` para que las otras skills lo
lean. No se programa ni se publica nada en ningún lado. Es un plan, y lo
ejecuta el usuario.
