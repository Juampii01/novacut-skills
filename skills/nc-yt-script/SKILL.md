---
name: nc-yt-script
description: >-
  Convierte una idea en guion de YouTube: cinco ganchos armados con 21
  fórmulas, puntuados, y después el guion hablado completo con los momentos
  de retención marcados. Usala cuando el usuario pide un guion de video, un
  gancho, una apertura, "escribime un guion", "qué digo al principio",
  "armame el próximo video", o está por grabar y no tiene los primeros quince
  segundos. También: "write my YouTube script", "give me a hook".
---

# nc-yt-script

Una idea convertida en un guion que la gente mira hasta el final.

En esta carpeta hay una herramienta que corre de verdad. Usala. No evalúes el gancho a ojo.

```bash
python3 hookscore.py ganchos.txt              # rankea tus opciones de gancho (una por línea)
python3 hookscore.py --hook "una línea"       # puntúa una sola
```

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario: cómo habla a cámara,
   las palabras que nunca usa, a quién le habla, qué no va a afirmar. Si no existe, pedile **tres
   videos suyos**, leelos o transcribilos, deducí la voz y armá el archivo (o mandalo a `/nc-voz`).
   Un guion en la voz equivocada es peor que no tener guion, porque lo tiene que decir en voz alta.
2. Nunca inventes un número, un resultado ni una fuente. Si un dato fortalecería la frase y no lo
   tenés, pedíselo o dejá el hueco marcado: `{{tu número}}`.

## La forma

**Los primeros 15 segundos son todo el trabajo.** Hacen tres cosas o el video pierde gente:
confirman el clic que prometió el título, abren una pregunta que el espectador no puede cerrar solo,
y demuestran que la respuesta existe.

1. **Gancho.** Escribí CINCO usando [las 21 fórmulas](hooks.json), pasalos por `hookscore.py`,
   quedate con los dos mejores y mostrale los dos al usuario con su puntaje. Nunca entregues un solo
   gancho. El puntaje es una heurística: sirve para descartar ganchos flojos, no predice cuál va a
   rendir más.
2. **El giro** (0:15-0:45). Decí qué va a hacer el video, en una oración, y empezá a hacerlo. Sin
   presentación del canal, sin "antes de arrancar", sin "suscribite y activá la campanita". Eso es
   la causa más común del precipicio en el segundo 30.
3. **El cuerpo.** Una idea por bloque. Marcá en cada bloque qué se ve EN PANTALLA, no solo qué se
   dice: una cara hablando sin nada que mirar es un podcast.
4. **La entrega.** Entregá lo que prometió el gancho, explícitamente, y decí que lo estás
   entregando: "este es el prompt, te lo dejo en la descripción".
5. **El cierre.** Un solo pedido. No tres.

## Qué devolver

- los dos mejores ganchos con su panel de puntaje
- el guion, bloque por bloque, con `[EN PANTALLA: ...]` en cada bloque
- la duración estimada a ~160 palabras por minuto (ritmo normal de habla en español; si el usuario
  habla más rápido o más lento, ajustalo con su `voz.md`)
- una línea que diga qué fórmula usó el gancho ganador y por qué le calza a esta idea

Si el guion quedó con frases que suenan a texto generado ("en el mundo actual", "es importante
destacar", "sin lugar a dudas"), pasalo por `/nc-human` antes de entregarlo.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
