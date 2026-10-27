---
name: nc-li-inbox
description: >-
  Ordena la bandeja de LinkedIn: separa invitaciones y mensajes en clientes
  posibles, reclutadores, colegas, pedidos y spam, y escribe solo las
  respuestas que vale la pena mandar. Usala cuando el usuario diga "tengo la
  bandeja hecha un lío", "ordená mis mensajes", "¿le respondo a esto?", pegue
  un montón de mensajes de LinkedIn, o esté tapado de invitaciones. También en
  inglés: "triage my DMs", "my inbox is a mess", "should I reply to this".
---

# nc-li-inbox

La mayoría de las bandejas de LinkedIn son 80% ruido, y el costo de ese ruido
es que el 20% que importa queda sin respuesta una semana. Esta skill los
separa y después escribe solo lo que vale la pena escribir.

## Qué pedir

El usuario pega los mensajes. Las capturas sirven. No te loguees en su cuenta
ni leas su bandeja con una herramienta de navegador.

## Cinco grupos

| grupo | señal | acción |
| --- | --- | --- |
| **CLIENTE POSIBLE** | describe un problema que el usuario resuelve, o pregunta por trabajar juntos | responder hoy, respuesta completa |
| **RECLUTADOR** | un puesto, una empresa, un rango de sueldo | responder si el puesto es real, una línea si no |
| **COLEGA** | alguien del mismo rubro con algo para decir | responder esta semana, en tono humano |
| **PEDIDO** | quiere un consejo, tiempo, una presentación, un favor | responder si es barato y concreto, declinar limpio si no |
| **SPAM** | agencia vendiendo, secuencia de generación de leads, cripto, "una consulta rápida" sin consulta | archivar, sin respuesta |

Mostrá los totales primero. Ver "3 clientes posibles, 2 reclutadores, 41 spam"
es la mitad del valor.

## Detectar una secuencia

La prospección automatizada tiene una forma: una invitación sin nada
concreto, un mensaje que llega a los minutos de aceptar, "una consulta
rápida", "vi que estás en el rubro {industria}", un link de agenda en el
primer mensaje, y después un "¿pudiste verlo?" exactamente cuatro días más
tarde. Cuando la veas, marcala SPAM y decí qué señal la delató. El usuario no
le debe una respuesta a un script.

## Respuestas

- **CLIENTE POSIBLE**: respondé la pregunta real del mensaje, completa, gratis.
  Si encaja, la oferta es una frase al final. Si no encaja, decilo y mandalo a
  algún lugar útil. Las dos salidas están bien.
- **RECLUTADOR**: si el puesto le interesa de verdad, preguntá las tres cosas
  que el mensaje no dijo: rango de sueldo (y en qué moneda), nivel, y si es
  presencial, remoto o híbrido. Si no le interesa, una línea: no estoy
  buscando, con gusto recomiendo a alguien, y que la recomendación sea en
  serio.
- **PEDIDO**: si cuesta menos de diez minutos y es concreto, hacelo. Si es
  "¿te puedo robar un café para hacerte unas preguntas?", declinalo en una
  frase cálida y dale la única respuesta que le habrías dado en el café. Esa
  es la versión amable y además la más útil.
- **DECLINAR**: corto, cálido y definitivo. Nada de "lo retomamos el próximo
  trimestre" si no hay próximo trimestre.

Leé `~/.claude/novacut/voz.md` si existe, para respetar el registro del
usuario. No inventes datos ni casos en las respuestas: si falta algo, dejá
`{{tu dato}}`.

## Salida

Agrupado, con los totales primero, borradores solo para los grupos que se
responden, cada uno pasado por `/nc-li-human`. Después el control: el
usuario los manda.

```
BANDEJA  ·  52 mensajes  ·  3 CLIENTE POSIBLE, 2 RECLUTADOR, 4 COLEGA, 2 PEDIDO, 41 SPAM

SPAM  (41) - archivar. 38 son la misma secuencia: invitación sin nada
concreto, "una consulta rápida" a los 4 minutos de aceptar, link de agenda en
el primer mensaje.
```
