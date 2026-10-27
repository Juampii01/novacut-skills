---
name: nc-li-post
description: >-
  Escribe un post de LinkedIn a partir de una idea suelta, con 21 fórmulas de
  gancho, en la voz del usuario y humanizado para que no suene a IA. Usala
  cuando el usuario quiera un post de LinkedIn, un gancho, un borrador para el
  feed, "escribime un post sobre X", "pasá esto a un post de LinkedIn",
  "haceme un post para LinkedIn", o pida opciones de gancho. También en
  inglés: "write a LinkedIn post", "turn this into a LinkedIn post". Devuelve
  tres ganchos, un borrador completo y un bloque listo para copiar que nunca
  se publica sin un sí explícito.
---

# nc-li-post

Convierte una idea en un post de LinkedIn que suena a la persona que lo
publica. Público típico: profesionales, consultores, dueños de pymes y
equipos comerciales de LATAM y España.

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario:
   cómo habla, qué no dice nunca, a quién le habla, si usa voseo, tuteo o
   usted. Si no existe, pedile **tres posts suyos** (de LinkedIn o de donde
   sea), inferí la voz y escribí el archivo, o mandalo a `/nc-voz`. No te
   saltees esto y no inventes una voz. Un post con la voz equivocada es peor
   que ningún post.
2. Leé `hooks.json` en esta carpeta. Las 21 fórmulas, con plantilla, ejemplo,
   para qué sirve cada una y cómo se suele arruinar.
3. Si la idea es flaca ("un post sobre IA"), no la rellenes. Hacé una sola
   pregunta, agrupada: qué pasó, a quién, y cuánto costó o rindió. Un post
   necesita una cosa concreta y cierta. Conseguila antes de escribir.

## La forma

LinkedIn premia el tiempo de lectura, los guardados y los comentarios. Así
que:

```
Línea 1     el gancho. Sola. Tiene que sobrevivir al corte de "ver más"
            (~140 caracteres en el celular, ~210 en computadora).
Línea 2     lo que paga la línea 1, no la preparación de la línea 3.
Cuerpo      párrafos cortos, de 1 a 3 líneas, con una línea en blanco entre
            cada uno. Nada de paredes de texto. El espacio en blanco es el formato.
El giro     una línea que reencuadra lo anterior.
Cierre      una pregunta concreta, o una instrucción. Nunca las dos.
```

Largo: entre 900 y 1.300 caracteres es el rango de trabajo para un post de
texto. Menos de 400 se lee como un pensamiento, no como un post. Más de 2.000
tiene que ganarse cada línea, y el toque en "ver más" lo tiene que pagar la
línea 2. (Los cortes de "ver más" son de 2026 y pueden cambiar.)

## El circuito

**1. Tres ganchos, no uno.** Pasá la idea por `hooks.json` y elegí las tres
fórmulas que de verdad le calzan. Fórmulas distintas, no tres variantes de la
misma. Mostralas como tres líneas numeradas y decí en una frase cuál
publicarías y por qué. Las fórmulas son una guía de escritura, no un
predictor: no prometas que una "funciona más".

**2. Escribí el post completo** con el gancho más fuerte.

**3. Humanizalo.** Pasá el borrador por `/nc-li-human` antes de mostrarlo.
Todo post de esta skill sale humanizado. No es un paso opcional: es lo que
hace que valga la pena leer el borrador.

**4. Imprimí el bloque.** Listo para copiar, en un bloque de código, tal cual
se tiene que pegar. Abajo:

```
POST LISTO
gancho:      #17 El ancla de tiempo
largo:       1.140 caracteres
humanizador: 6 marcas sacadas, puntaje humano 84 PASA
publicar:    martes 8:15 hora de tu audiencia (de tu plan)

Respondé "sí" para registrarlo, o decime qué cambiar.
```

**5. Nunca publiques.** Esta skill escribe texto. El usuario lo publica. Con
el "sí", agregá el post a `~/.claude/novacut/li-registro.md` con la fecha, la
fórmula usada y la primera línea, para que `/nc-li-audit` tenga historial.

## Reglas que hacen la diferencia

- **Una idea por post.** Si el borrador tiene dos, son dos posts. Decilo.
- **Números antes que adjetivos.** "USD 4.200" o "$3,5 millones" le gana a "un
  montón". Si el usuario no te dio un número, pedíselo en vez de escribir
  alrededor del hueco.
- **Nada de cebo de interacción.** "¿Qué opinan?" y "¿Están de acuerdo?" están
  muertos. La pregunta del cierre tiene que ser una que solo este post podría
  hacer.
- **Tres hashtags como máximo**, al final, y solo si son categorías reales que
  alguien sigue.
- **Nada de links en el cuerpo.** LinkedIn suele mostrar menos los posts con
  links externos. Poné el link en el primer comentario y decilo en el
  resumen. (Es el comportamiento observado a 2026; si `/nc-li-audit` muestra
  otra cosa para esta cuenta, manda el dato del usuario.)
- **Nunca inventes.** Ni métricas, ni clientes, ni facturación, ni resultados
  bajo el nombre del usuario, ni siquiera de relleno. Si hace falta un número
  y no lo tenés, dejá `{{tu número}}` en el borrador y avisalo.
- **Respetá el registro.** Si la audiencia es de España, nada de voseo; si el
  usuario trata de usted a sus clientes, el post también. Lo dice `voz.md`.

## Ejemplo

```
/nc-li-post armamos una herramienta interna que bajó el tiempo de armar un presupuesto de 5 horas a 20 minutos
```

```
GANCHOS
1. #17 El ancla de tiempo   Armar un presupuesto me llevaba 5 horas. Ahora me lleva 20 minutos.
2. #12 La comparación       Un redactor de propuestas de USD 1.500 vs un fin de semana y una plantilla. Ganó el fin de semana.
3. #3  La confesión         Durante dos años les cobré a mis clientes horas que perdía formateando Word.

Voy con el #17: la proporción se cree y el número es tuyo.
```
