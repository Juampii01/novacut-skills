---
name: nc-brief-edicion
description: >-
  Convierte un guion (o un video grabado con su transcripción) en un brief de
  edición listo para ejecutar: cortes, texto en pantalla, animaciones y gráficos
  por momento, subtítulos, música y efectos, con tiempos. Sirve para editar vos
  mismo en CapCut o Premiere, para pasárselo a un editor, o para cargarlo en el
  editor NovaCut. Usala cuando el usuario diga "armame el brief de edición",
  "cómo edito esto", "qué animaciones pongo", "pasale esto a mi editor", "edit
  brief", o después de /nc-reel o /nc-yt-script cuando ya grabó.
---

# nc-brief-edicion

El guion dice qué se dice. El brief dice qué se **ve** en cada segundo. Sin brief, la edición se improvisa y el video queda con planos muertos justo donde la gente se va.

## Qué necesitás

1. **El guion** (idealmente con el beat sheet de `/nc-reel` o la estructura de `/nc-yt-script`).
2. **Si ya grabó:** la transcripción con tiempos (.srt, .vtt o el JSON de whisper). Si la tiene, corré antes `/nc-yt-edit` para sacar silencios, rellenos y retomas, y armá el brief sobre los tiempos ya limpios.
3. **El formato:** vertical 9:16 (reel, short, TikTok) u horizontal 16:9 (YouTube).
4. **Lo que tiene a mano:** solo su cara, grabaciones de pantalla, fotos de producto, B-roll propio. No le pidas material que no tiene.
5. Leé `~/.claude/novacut/voz.md` si existe: ahí está si muestra la cara y su estilo.

Si falta el guion o el formato, preguntá las dos cosas juntas, una sola vez.

## Reglas de edición que aplicás

- **El plano cambia en cada momento.** Más de 4 segundos con el mismo plano fijo es donde la gente se va. Cambiá algo: zoom, texto, animación, B-roll, corte de ángulo.
- **El gancho visual está en el frame 1.** Movimiento y texto desde el segundo 0, nunca una cara quieta esperando.
- **Texto en pantalla: 6 palabras o menos por tarjeta,** y dentro de la zona segura. En 1080×1920: nada por encima de y=230 ni por debajo de y=1440, y dejá libres los 230 px de la derecha (ahí van los botones y la descripción).
- **Subtítulos quemados** en todo el cuerpo. La mayoría mira sin sonido primero.
- **Animación cuando hay un número, un proceso o una comparación.** Un número dicho se olvida; un número que crece en pantalla se recuerda.
- **Gráfico solo si hay datos reales.** Nunca inventes cifras para llenar un gráfico: si falta el dato, `{{tu número}}`.
- **Música por debajo de la voz** (−18 a −24 dB respecto de la voz). Si la voz se tapa, no hay música que salve el video.
- **El cierre repite algo del gancho** (palabra o imagen) para que la repetición enganche.

## La salida

Una tabla por momento, en el orden del video:

```
BRIEF DE EDICIÓN · reel 9:16 · ~32 s · 8 momentos

| Tiempo      | Momento   | Se dice (resumen)              | Plano / visual                         | Texto en pantalla   | Animación / gráfico                    | Sonido            |
|-------------|-----------|--------------------------------|----------------------------------------|---------------------|----------------------------------------|-------------------|
| 0:00–0:02.5 | GANCHO    | "Cinco horas a veinte minutos" | Cara, zoom in lento                    | 5 HORAS → 20 MIN    | El 5 se tacha y aparece 20 MIN         | Whoosh en el 20   |
| 0:02.5–0:07 | EL PORQUÉ | ...                            | Grabación de pantalla, recorte cerrado | —                   | Flecha señalando el botón              | Música entra −20dB|
| ...         | ...       | ...                            | ...                                    | ...                 | ...                                    | ...               |
```

Después de la tabla:

```
SUBTÍTULOS:   palabra por palabra, 2 líneas máx, resaltá en color las palabras clave: {lista}
MÚSICA:       {tipo y energía, sin nombrar temas con derechos que no pueda usar}
B-ROLL QUE FALTA:  {lista de tomas cortas para grabar, o "ninguno"}
ALERTAS:      {planos de más de 4 s, gráficos sin dato real, gancho sin movimiento}
```

## Para el editor NovaCut

Si el usuario usa NovaCut, sumá al final un bloque de pedidos listo para pegar en el asistente, uno por momento, en lenguaje natural:

```
PEDIDOS PARA NOVACUT
1. Recortá silencios y errores en todo el video.
2. Entre 0:00 y 0:02.5: animación pantalla completa, el número 5 HORAS se tacha y aparece 20 MIN, estilo limpio.
3. Entre 0:02.5 y 0:07: mitad y mitad, arriba una flecha animada señalando...
...
N. Subtítulos animados en todo el video, resaltando: {palabras}.
```

Pedidos concretos: tiempo de inicio y fin, qué aparece, cómo entra y cómo sale. "Poné algo lindo" no se puede ejecutar.

## Lo que esta skill no hace

No edita el video ni toca archivos de media: escribe el plan. Vos (o tu editor, o NovaCut) lo ejecutás. Termina siempre con la pregunta: **¿lo dejamos así o cambiamos algo?**
