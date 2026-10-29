---
name: nc-x-post
description: >-
  Escribe un post de X (Twitter) a partir de una idea suelta, con 21 fórmulas
  de gancho, en la voz del usuario, contado como cuenta X los caracteres y
  humanizado para que no suene a IA. Usala cuando el usuario quiera un tweet,
  un post de X, un gancho, "escribime un tweet sobre X", "pasá esto a un
  tweet", "haceme un post para X", un post largo de Premium, o pida opciones
  de gancho. También en inglés: "write a tweet", "turn this into a tweet",
  "X post". Devuelve tres ganchos puntuados, un borrador y un bloque listo
  para copiar que nunca se publica sin un sí explícito.
---

# nc-x-post

Convierte una idea en un post que suena a la persona que lo publica.

En esta carpeta hay tres archivos que hacen trabajo real:

```bash
python3 hookscore.py --hook "una línea"      # panel de cinco propiedades + nombre de la fórmula
python3 hookscore.py ganchos.txt             # ordena varias opciones
python3 count.py post.txt                    # cuenta ponderada de X + seis revisiones
python3 count.py post.txt --premium          # post largo: muestra dónde corta "Mostrar más"
```

`hooks.json` tiene las 21 fórmulas: plantilla, ejemplo, para qué sirve cada
una, cómo se suele arruinar y la regex que la nombra (pensada para español,
con voseo y tuteo, con y sin tilde).

## Antes de escribir

1. Leé `~/.claude/novacut/voz.md` si existe. Es el perfil de voz del usuario.
   Si no existe, pedile **cinco posts suyos recientes**, inferí la voz y
   escribí el archivo (o mandalo a `/nc-voz`). No inventes una voz. Un post
   con la voz equivocada es peor que ningún post.
2. Leé `hooks.json`. Las 21.
3. Leé `~/.claude/novacut/x-swipe.md` si `/nc-x-viral` ya corrió. Si una
   fórmula está rindiendo en el nicho del usuario ahora, preferila cuando
   calce.
4. Si la idea es flaca ("un post sobre IA"), no la rellenes. Hacé una sola
   pregunta agrupada: qué pasó, a quién, y cuánto costó o rindió. Un post
   necesita una cosa concreta y cierta.

## La forma de un post en X

En X la primera línea no es el comienzo del post. Es casi todo el post.

```
Línea 1   el gancho. Completo por sí solo. Menos de ~110 caracteres, para que
          se lea de un vistazo en el celular.
Línea 2   lo que paga la línea 1, o su prueba. No la preparación de la línea 3.
Resto     solo si se gana el lugar. Líneas cortas. Una línea en blanco entre ideas.
Final     la última frase cierta, o una pregunta concreta. Nunca las dos.
```

- **Cuenta normal: 280 caracteres ponderados.** `count.py` cuenta como X: cada
  link vale 23, cada emoji vale 2, "…" vale 2. Las tildes, la ñ, ¿ y ¡ valen 1.
- **Los posts largos de Premium** llegan a 25.000, pero el timeline muestra
  más o menos los primeros 280 y esconde el resto detrás de "Mostrar más".
  Todo lo que importa va arriba de ese corte. `count.py --premium` lo dibuja.
- **La mayoría de los posts que viajan tienen de una a tres líneas.** Usá el
  largo cuando la idea lo necesita, no porque está disponible.
- El español usa más palabras que el inglés para decir lo mismo. Si no entra,
  cortá ideas, no artículos: un post sin "el" y "la" se lee a telegrama.

(Límites de X a 2026; pueden cambiar.)

## Lo que premia el ranking de X

X publica sus pesos de ranking actuales. Corré `python3 ../nc-x-plan/weights.py`
para ver los de hoy. La forma se mantuvo aunque los valores se muevan: las
respuestas, las citas y los compartidos (por DM o copiando el link) pesan
mucho más que los likes, y "no me interesa", silenciar, bloquear y denunciar
pesan muy en contra. El propio comentario de X en ese archivo avisa que se
aplican a probabilidades predichas, no a cantidades, así que no le digas al
usuario "una respuesta vale diez likes". Decile qué significa para el borrador:

- Escribí el post que alguien responde, cita o le manda a un amigo.
- No escribas el post que te hace silenciar: cebo, bronca, o algo fuera del
  tema por el que te siguen.

## El circuito

**1. Tres ganchos, de tres fórmulas distintas.** Pasá la idea por
`hooks.json`, elegí las tres que de verdad calzan, escribí una línea por cada
una y puntualas juntas:

```bash
printf '%s\n' "gancho uno" "gancho dos" "gancho tres" | python3 hookscore.py -
```

Mostrá el ranking. Decí en una frase cuál publicarías y por qué. Si el
primero está debajo de 50, ninguno de estos es el gancho: escribí tres más.
El puntaje es un control de calidad, no un predictor: atrapa etiquetas,
saludos y ganchos sin nada concreto, pero no te dice cuál de dos ganchos
decentes va a viajar más. Eso lo dicen los datos del usuario (`/nc-x-audit`).

**2. Escribí el post completo** con el gancho más fuerte.

**3. Contalo.** `python3 count.py borrador.txt`. Arreglá cada FALLA. Leele al
usuario cada OJO y qué hiciste al respecto.

**4. Humanizalo.** Pasá el borrador por `/nc-x-human`. Todo post de esta skill
sale humanizado.

**5. Imprimí el bloque.** Listo para copiar, en un bloque de código, tal cual
se pega. Abajo:

```
POST LISTO
gancho:      #9 El ancla de tiempo  (puntaje 78 FUERTE)
largo:       187 / 280
humanizador: 3 marcas sacadas, puntaje humano 91 PASA
publicar:    martes 9:00 hora de tu audiencia (de tu plan)

Respondé "sí" para registrarlo, o decime qué cambiar.
```

**6. Nunca publiques.** Esta skill escribe texto. El usuario lo publica. Con
el "sí", agregá el post a `~/.claude/novacut/x-registro.md` con la fecha, la
fórmula y la primera línea, para que `/nc-x-audit` tenga historial.

## Reglas que hacen la diferencia

- **Una idea por post.** Dos ideas son dos posts. Decilo.
- **Números antes que adjetivos.** "USD 4.200" le gana a "un montón". Si el
  usuario no te dio un número, preguntá. Nunca escribas alrededor del hueco.
- **Nada de etiqueta como gancho.** "Opinión impopular:", "Hilo:", "Rapidito"
  son envoltorio.
- **Nada de cebo reflejo.** "¿Qué opinan?", "¿Están de acuerdo?", "Dale RT
  si..." están muertos. Una pregunta de cierre tiene que ser una que solo este
  post podría hacer.
- **Hashtags: uno, o ninguno.** Elon Musk, diciembre de 2024: el sistema ya no
  los necesita. Un hashtag es un link para irse de tu propio post.
- **Links.** X dice que dejó de castigar los posts con links hace más de un
  año (julio de 2026). Un análisis independiente de enero de 2026 todavía les
  midió menos vistas. Por defecto: el link en una respuesta debajo del post, y
  decile al usuario que es una decisión, no una regla. `/nc-x-audit` muestra
  cuál es verdad para su cuenta.
- **Las menciones** después del carácter 280 de un post largo no le llegan a la
  persona mencionada.
- **Nunca inventes.** Ni métricas, ni clientes, ni facturación, ni resultados
  bajo el nombre del usuario, ni de relleno. Si hace falta un número y no lo
  tenés, dejá `{{tu número}}` en el borrador y avisalo.

## Ejemplo

```
/nc-x-post rehice mi proceso de presupuestos con Claude, de 5 horas a 20 minutos
```

```
RANKING DE GANCHOS
->  81.4 FUERTE  Perdí dos años formateando presupuestos a mano que podría...
        #17 El arrepentimiento  ·  más floja: TENSIÓN (70)
    77.8 FUERTE  Un presupuesto me llevaba 5 horas. Ahora me lleva 20 minu...
        #9 El ancla de tiempo  ·  más floja: TENSIÓN (70)
    59.4 OK      Un redactor de presupuestos de USD 1.500 vs un fin de sem...
        #18 La comparación  ·  más floja: DESTINATARIO (35)

Voy con el #9 antes que el #17. La diferencia es chica, que es ruido, y los
números del #9 son del usuario. El puntaje es un control, no un juez.
```
