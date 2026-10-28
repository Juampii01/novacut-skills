---
name: nc-voz
description: >-
  Arma o actualiza el perfil de voz del usuario (~/.claude/novacut/voz.md), que
  leen todas las skills de NovaCut. Usala cuando el usuario arranca con el pack,
  dice "armá mi voz", "configurá mi perfil", "los guiones no suenan a mí",
  "write my voice profile", o cuando otra skill necesita voz.md y no existe.
---

# nc-voz

Todo el pack escribe en la voz del usuario. Si `~/.claude/novacut/voz.md` no existe o está vacío, los guiones salen genéricos, y un guion genérico no se graba: se reescribe. Esta skill arma ese archivo.

## Paso 1: ¿qué ya existe?

1. Si `~/.claude/novacut/voz.md` existe, leelo y preguntá qué quiere cambiar. No lo pises entero.
2. Si no existe, usá como molde la plantilla `templates/voz.md` del pack (si no la encontrás, usá las secciones de abajo).

## Paso 2: conseguir material real

La mejor fuente son sus propias palabras, no sus respuestas sobre cómo habla. Pedí **una** de estas, en este orden de preferencia:

1. **Tres videos o reels suyos** (transcripción, link que se pueda leer, o texto pegado). Si te pasa links de Instagram o TikTok que no podés abrir, pedile que pegue el texto o suba el archivo.
2. **Tres descripciones o posts suyos** que sienta que "suenan a él".
3. Si no tiene nada publicado: una nota de voz o un párrafo escrito como le hablaría a un cliente.

## Paso 3: preguntas, en un solo bloque

Lo que el material no te diga, preguntalo junto, una sola vez (no de a una):

- A quién le habla, con el máximo detalle (rubro, nivel, país).
- Qué vende y a dónde quiere llevar a la gente (DM, link, llamada).
- País y forma de hablar: voseo, tuteo o vosotros.
- Si muestra la cara, si usa malas palabras, si usa emojis.
- Tres cosas que cree y que parte de su público no.
- Temas, clientes o números que no se pueden decir.
- Resultados reales que puede usar como prueba.
- Su palabra clave para comentarios, si tiene.

## Paso 4: escribir el archivo

Completá todas las secciones: Quién soy, Cómo sueno, Lo que pienso, Lo que no se toca, Pruebas que puedo usar, El llamado a la acción.

Reglas:
- **Copiá sus frases reales** en "Palabras que uso de verdad". Nada de adjetivos como "cercano y auténtico": eso no le sirve a ninguna skill.
- **"Palabras que nunca diría"** sale de comparar su material con texto típico de IA. Si nunca dice "potenciar" ni "sumergite", anotalo.
- **Nunca inventes pruebas.** Si no te dio números, la sección queda con `{{tu número}}`.
- Estimá la velocidad si tenés un audio con duración: palabras ÷ minutos. Si no, poné 160 (español promedio) y aclaralo.

## Paso 5: confirmar

Mostrale el archivo completo en un bloque y preguntá: **¿lo guardo así o cambiamos algo?** Recién con un "sí", guardalo en `~/.claude/novacut/voz.md` (creá la carpeta si no existe).

Si estás en claude.ai y no podés escribir en su computadora, entregale el archivo para que lo descargue y decile que lo suba al proyecto o lo pegue al inicio de la conversación cuando use las otras skills.
