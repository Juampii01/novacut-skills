---
name: nc-li-dm
description: >-
  Escribe notas de invitación y mensajes de seguimiento en LinkedIn que
  consiguen respuesta: la nota de 200 caracteres, el primer mensaje y los dos
  seguimientos. Usala cuando el usuario diga "escribime una invitación",
  "mandale un mensaje a esta persona", "mensaje de prospección", "¿cómo hago el
  seguimiento?", "quiero contactar a este dueño de pyme", o esté por
  escribirle a alguien concreto en LinkedIn. También en inglés: "write a
  connection request", "DM this person", "outreach message".
---

# nc-li-dm

La nota de invitación tiene 200 caracteres. El primer mensaje decide si hay
un segundo. Ninguno de los dos es una venta.

## Antes de escribir, conseguí lo concreto

Pedí, en una sola pregunta agrupada:

1. **Quién**: nombre, cargo, empresa.
2. **El motivo**: la razón real para escribirle ahora. Un post suyo, algo que
   lanzó su empresa, un contacto en común, una charla que dio. No "encaja con
   mi cliente ideal".
3. **Qué quiere el usuario**: una charla, una recomendación, un trabajo, una
   venta. Sé honesto puertas adentro, aunque el mensaje no arranque por ahí.

Si no hay una razón concreta para escribirle a esta persona hoy, decilo. Un
mensaje sin motivo es lo que manda todo el mundo, y por eso responde el 2%.

Leé `~/.claude/novacut/voz.md` si existe. Ojo con el registro: en muchos
países de LATAM a un dueño de empresa que no conocés se le escribe de usted,
y en España se tutea más. Si no está claro, preguntá.

## La nota de invitación (200 caracteres)

```
{una referencia concreta a la persona} + {una línea de quién sos} + {sin pedido}
```

La nota no pide nada. Existe para que aceptar sea obvio. Menos de 200
caracteres con espacios: contalos y mostrá la cuenta. (200 es el límite de la
nota en cuentas gratuitas a 2026, y LinkedIn limita cuántas notas
personalizadas por mes se pueden mandar sin Premium; puede cambiar.)

```
Vi tu post sobre dejar de hacer llamadas de diagnóstico. Lo probamos en marzo
y funcionó. Llevo operaciones en un estudio de 12 personas. Me gustaría seguirte.
                                                                    [159/200]
```

## El primer mensaje, después de que acepta

Esperá un día. Después:

- **De dos a cuatro frases.** Una pantalla de texto se borra.
- **Retomá lo concreto** de la nota. La continuidad es la razón por la que la
  nota fue concreta.
- **Dá algo antes de pedir.** Un número, una plantilla, un nombre, una
  respuesta.
- **Un solo pedido, y chico.** "¿Te sirve una llamada de 15 minutos?" le gana a
  "te quiero mostrar nuestra plataforma".
- **Nada de link de agenda en el primer mensaje.** Se lee como embudo, porque
  lo es.

## Seguimientos

Dos. Ese es el número.

- **+4 días**: sumá algo nuevo. Nunca "te escribo para retomar" ni "¿pudiste ver
  mi mensaje?". Si no tenés nada nuevo, no tenés seguimiento.
- **+10 días**: el mensaje de cierre. Decí que no vas a insistir más, y
  cumplilo. Este se lleva una parte sorprendente de las respuestas, porque
  saca la presión.

Después, parar. Un tercer seguimiento no convierte a nadie y quema la
relación.

## Nunca

- Nunca mandes una secuencia automatizada de invitaciones o mensajes. Las
  herramientas de prospección automática violan el Acuerdo de Usuario de
  LinkedIn y hacen que restrinjan la cuenta.
- Nunca inventes un contacto en común, una universidad compartida, ni haber
  leído algo que el usuario no leyó.
- Nunca escribas el mensaje que arranca con "Espero que te encuentres muy
  bien" o "Espero que este mensaje te encuentre bien".
- Nunca más de 20 invitaciones por día. Más que eso y LinkedIn frena la
  cuenta, y una cuenta frenada está muerta.

## Salida

La nota con su cuenta de caracteres, el primer mensaje y los dos seguimientos
con el día en que sale cada uno. Todo pasado por `/nc-li-human`. El usuario
manda cada uno a mano.
