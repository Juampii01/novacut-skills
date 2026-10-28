---
name: nc-yt-audit
description: >-
  Audita un canal de YouTube de punta a punta (empaquetado, constancia, los
  primeros quince segundos) y termina en qué arreglar primero. Usala para
  "auditá mi canal", "por qué mi canal no crece", "revisá mis videos",
  "qué estoy haciendo mal en YouTube", o cuando el usuario pega la URL de un
  canal. También: "audit my channel", "review my YouTube".
---

# nc-yt-audit

Una auditoría que lista veinte problemas es una forma de esquivar el que importa. Esta termina en UN
arreglo.

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario: cómo habla a cámara,
   las palabras que nunca usa, a quién le habla, qué no va a afirmar. Si no existe, pedile **tres
   videos suyos**, leelos o transcribilos, deducí la voz y armá el archivo (o mandalo a `/nc-voz`).
2. Nunca inventes un número, un resultado ni una fuente. Si te falta un dato (vistas, retención,
   CTR), pedíselo; no lo estimes ni lo completes de memoria.
3. Leés lo que es público, a velocidad humana. Nunca te logueás en la cuenta del usuario ni le pedís
   la contraseña: si hace falta algo de Studio, que lo exporte o lo pegue él.

## Qué mirar, en este orden

1. **Los últimos diez títulos, como conjunto.** Leelos como lista, como los muestra la página del
   canal. ¿Prometen cosas distintas? Pasalos por `../nc-yt-package/title.py`. Un canal donde todos
   los títulos tienen la misma forma tiene un problema de formato, no de títulos.
2. **Las miniaturas, a tamaño de feed.** Achicalas. ¿Qué sobrevive? Si tres no se leen a ese tamaño,
   ese es el arreglo y nada más importa todavía.
3. **Los primeros quince segundos de los tres más recientes.** Transcribilos y puntualos con
   `../nc-yt-script/hookscore.py`. Ahí es donde pierde la mayoría de los canales.
4. **El ritmo de subida.** No la frecuencia: la CONSTANCIA. Seis videos en una semana y después nada
   por un mes es peor que uno cada quince días para siempre.
5. **La forma de la retención**, si la pueden exportar. `/nc-yt-retention`.

## Qué devolver

- El arreglo más grande, con nombre, y qué hacer con él esta semana.
- Tres cosas que ya funcionan, para que no las rompa. Concretas: "tenés buena energía" no es una
  observación.
- Qué NO hacer todavía, y por qué.

Nunca abras una auditoría con elogios que no sentís, y nunca la cierres con una lista de veinte
cosas.

## La compuerta

Nada de esto se publica solo. Esta skill escribe y vos publicás. Cada salida termina en un bloque
para copiar, y la última línea de cada corrida es la pregunta: **¿lo publicás así o lo cambiamos?**
