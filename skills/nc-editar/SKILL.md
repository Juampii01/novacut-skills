---
name: nc-editar
description: >-
  Editor de video para videos hablados a cámara, en tu computadora y sin
  pagar API: transcribe, propone qué cortar (silencios, muletillas, retomas,
  arranques en falso), espera tu OK, corta con audio y video en sincronía,
  limpia y nivela el audio a -14 LUFS, suma música opcional y quema
  subtítulos animados. Entrega el MP4 final y el .srt, en 9:16 o 16:9. Usala
  cuando el usuario diga "editá este video", "editame el reel", "sacale los
  silencios", "cortá las muletillas", "ponele subtítulos", "dejalo listo para
  subir", "edit this video", "cut the silences", "add captions". Solo en
  Claude Code (necesita ffmpeg y Python en la compu).
---

# nc-editar

Hace la edición básica de un video hablado, la que haría un editor: limpia los cortes, deja el audio parejo y pone subtítulos. Vos (Claude) orquestás; los scripts de `nc-cortar`, `nc-audio` y `nc-subtitulos` hacen el trabajo con ffmpeg en la computadora del usuario. No se sube nada a internet (solo se descarga el modelo de transcripción la primera vez).

## Reglas que no se negocian

1. **Nunca sobrescribas el original.** Todo lo intermedio va a `RUTA/<nombre>_novacut/` y el resultado a `RUTA/<nombre>_editado.mp4` (+ `.srt`).
2. **Siempre pedí aprobación antes de renderizar los cortes.** Mostrás el plan (`--simular`), esperás un sí explícito, después renderizás.
3. El plan de cortes usa **IDs de palabra, nunca segundos.**
4. No inventes ni reescribas lo que dijo la persona: solo se saca.
5. No prometas lo que no hace: no hay animaciones, B-roll, zooms ni seguimiento de cara automáticos en esta versión. Para planificar animaciones y gráficos está `/nc-brief-edicion` (arma el brief para hacerlo en CapCut/Premiere o pasárselo a un editor); las animaciones automáticas llegan en una próxima versión del pack.

## Rutas

Las skills están en `~/.claude/skills/` (Windows: `%USERPROFILE%\.claude\skills\`). Abajo:
- `$SK` = esa carpeta (`~/.claude/skills`).
- `$PY` = el Python a usar: si existe `~/.claude/novacut/venv/bin/python` (Windows: `%USERPROFILE%\.claude\novacut\venv\Scripts\python.exe`), usá ese (ahí se instaló faster-whisper); si no, `python3` en Mac/Linux o `py` en Windows.
- Poné las rutas entre comillas: los nombres de archivo suelen tener espacios.

## Paso 0 · Entender el pedido

Ubicá el video (si no dio la ruta, preguntala). Según lo que pide:
- "Editá este video" / "dejalo listo": todo el flujo (pasos 1 a 8).
- "Sacale los silencios / las muletillas": pasos 1 a 5 y entregá el cortado (ofrecé audio y subtítulos al final).
- "Ponele subtítulos" (sin cortar): pasos 1, 2 y 7 sobre el original, con el `palabras.json` del original.
- "Mejorá el audio": solo `/nc-audio`.

Antes de arrancar, hacé UNA sola pregunta con todo lo que no sea obvio, con valores por defecto para no frenar:
- Formato: vertical 9:16 (reel, TikTok, short) u horizontal 16:9 (YouTube). Por defecto, el del video. Si el video es horizontal y lo quiere para reel, se recorta al centro (se puede correr con `--encuadre-x`).
- Música de fondo: ¿tiene una pista con derechos? (por defecto, sin música).
- Subtítulos: `limpio` (frases de 2 líneas, default) o `impacto` (1-3 palabras grandes en mayúsculas). Colores de marca si los tiene (mirá `~/.claude/novacut/voz.md`).
- Ritmo: normal (pausas de hasta 0,5 s) o rápido tipo reel (0,3 s).

## Paso 1 · Verificar dependencias

```bash
$PY "$SK/nc-editar/verificar.py"
```

Si falta algo, mostrale al usuario los comandos exactos que imprime el script y la guía `nc-editar/instalar_dependencias.md` (Mac y Windows). No sigas hasta que esté todo.

## Paso 2 · Transcribir

```bash
$PY "$SK/nc-cortar/transcribir.py" "RUTA/video.mp4" --idioma es
```

Deja `RUTA/video_novacut/palabras.json`. La primera vez descarga el modelo "small" (~480 MB, una sola vez): avisá que tarda. Si el video no es en español, `--idioma auto`. Si la transcripción sale floja, ofrecé `--modelo medium`.

## Paso 3 · Candidatos y plan

```bash
$PY "$SK/nc-cortar/candidatos.py" "RUTA/video_novacut/palabras.json" --plan-base "RUTA/video_novacut/plan.json"
```

Leé la transcripción con IDs y los candidatos, y armá `plan.json` siguiendo `nc-cortar/SKILL.md` (sección "Armar el plan v2"): muletillas puras siempre, blandas solo si están sueltas, en retomas queda la última toma completa, arranques en falso fuera, ante la duda no cortes. Poné `format`, `pausa_max` (0,5 normal; 0,3 rápido) y 1-2 `captions.emphasis_words` por frase.

## Paso 4 · Mostrar y esperar el OK

```bash
$PY "$SK/nc-cortar/render.py" "RUTA/video.mp4" "RUTA/video_novacut/palabras.json" "RUTA/video_novacut/plan.json" --simular
```

Mostrale la duración antes y después y la lista de cortes con su texto. Preguntá: **"¿Lo corto así o cambiamos algo?"**. Si pide cambios, editá el plan, simulá de nuevo y volvé a preguntar. Sin un sí, no se renderiza.

## Paso 5 · Cortar

```bash
$PY "$SK/nc-cortar/render.py" "RUTA/video.mp4" "RUTA/video_novacut/palabras.json" "RUTA/video_novacut/plan.json"
```

Sale `video_novacut/cortado.mp4` y `video_novacut/cortado.palabras.json`. El script revisa duración y sincronía; si dice `REVISAR`, avisá con los números.

## Paso 6 · Audio

```bash
$PY "$SK/nc-audio/audio.py" "RUTA/video_novacut/cortado.mp4" --salida "RUTA/video_novacut/cortado_audio.mp4"
# con música:  ... --musica "RUTA/pista.mp3" --musica-db -22
```

Limpieza de voz + -14 LUFS / -1 dBTP en dos pasadas (+ música con ducking si la hay). Ver `nc-audio/SKILL.md`.

## Paso 7 · Subtítulos (y archivo final)

```bash
$PY "$SK/nc-subtitulos/subtitulos.py" "RUTA/video_novacut/cortado_audio.mp4" "RUTA/video_novacut/cortado.palabras.json" --salida "RUTA/video_editado.mp4"
```

Usá SIEMPRE el `cortado.palabras.json` (tiempos del video cortado), nunca el del original. Deja `RUTA/video_editado.mp4`, `RUTA/video_editado.srt` y `.ass`. Si el usuario no quiere subtítulos quemados, copiá `cortado_audio.mp4` como `video_editado.mp4` y generá solo el `.srt` con `--solo-srt`.

## Paso 8 · Entregar

Decile al usuario, corto:
- Dónde está el video final y el `.srt`.
- Duración antes → después y cuánto se sacó.
- Volumen final (LUFS) y formato.
- Que la carpeta `video_novacut/` tiene todo lo intermedio: si quiere cambiar algo (restaurar un corte, otro estilo de subtítulos, otra música), se rehace solo ese paso sin volver a transcribir. Cuando esté conforme, puede borrarla.
- Si quiere animaciones, textos en pantalla o B-roll: `/nc-brief-edicion` arma el plan segundo a segundo.

Si podés, mostrá un cuadro del resultado (`ffmpeg -v error -ss 3 -i "RUTA/video_editado.mp4" -frames:v 1 "RUTA/video_novacut/muestra.png"`) para que vea los subtítulos.

## Si algo falla

- **"No pude descargar el modelo"**: hace falta internet la primera vez (huggingface.co). Si hay firewall o VPN, que lo pruebe en otra red, o que use `--carpeta-modelo` con un modelo ya descargado.
- **ffmpeg sin libass** (no quema subtítulos): instalar el ffmpeg completo (ver la guía). Mientras tanto, entregá el `.srt`.
- **Va muy lento**: transcribir 10 min de video con "small" en una compu común lleva varios minutos; renderizar, más o menos lo que dura el video. Con `--preset fast` en `render.py` y `subtitulos.py` va más rápido con un poco más de peso de archivo.
- **El usuario pide algo que no está** (zoom a la cara, B-roll, transiciones, animaciones): decí claramente que esta versión no lo hace, ofrecé `/nc-brief-edicion` para planificarlo y seguí con lo que sí se puede.
