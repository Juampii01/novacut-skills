---
name: nc-subtitulos
description: >-
  Pone subtítulos animados palabra por palabra a un video (la palabra que
  decís se ilumina, las palabras clave en otro color, máximo 2 líneas, dentro
  de la zona segura de Reels/TikTok/Shorts) y los quema con ffmpeg en tu
  computadora. También entrega el .srt. Usala para "ponele subtítulos",
  "subtitulá este video", "quiero los subtítulos tipo reel", "pasame el srt",
  "add captions", "burn subtitles". Solo en Claude Code (necesita ffmpeg y
  Python). Si el video todavía no está cortado, usá /nc-editar.
---

# nc-subtitulos

Subtítulos animados al estilo reel, quemados en el video, más el `.srt` para subirlo aparte (YouTube, LinkedIn) o para editar.

Script: `subtitulos.py` en la carpeta de esta skill (`$SKILL`, normalmente `~/.claude/skills/nc-subtitulos/`). Fuente incluida: Montserrat, licencia SIL OFL 1.1 (`fuentes/OFL-Montserrat.txt`). En Windows usá `py` en vez de `python3`.

**Qué Python usar:** si existe `~/.claude/novacut/venv/bin/python` (Windows: `%USERPROFILE%\.claude\novacut\venv\Scripts\python.exe`), usá ese en lugar de `python3` (ahí está instalado faster-whisper). Si no, `python3` en Mac/Linux o `py` en Windows.

## Qué necesita

1. **El video** (ya cortado, idealmente con el audio procesado por `/nc-audio`).
2. **Las palabras con tiempos DEL VIDEO QUE SE VA A SUBTITULAR.**
   - Si el video salió de `/nc-cortar`: usá `cortado.palabras.json` (ya re-mapeado a los tiempos del video cortado). **No uses el `palabras.json` del original sobre un video cortado**: los subtítulos quedarían corridos.
   - Si el video no se cortó: el `palabras.json` de `nc-cortar/transcribir.py` sirve directo.
   - Si no hay transcripción: corré primero `python3 "$SKILL/../nc-cortar/transcribir.py" video.mp4`.

## Uso

```bash
python3 "$SKILL/subtitulos.py" "RUTA/cortado_audio.mp4" "RUTA/cortado.palabras.json" --salida "RUTA/video_editado.mp4"
```

Opciones:
- `--estilo limpio` (default): frases de hasta 2 líneas, Montserrat ExtraBold. Para la mayoría de los videos de coaches, inmobiliarias, gastronomía, educativos.
- `--estilo impacto`: 1 a 3 palabras grandes en mayúsculas, Montserrat Black. Para reels de ritmo rápido.
- `--color-activo "#FFD84D"` (palabra que se está diciendo) y `--color-clave "#3DDC84"` (palabras clave). Si el usuario tiene colores de marca, usalos (leé `~/.claude/novacut/voz.md` si existe).
- `--claves 12,40`: IDs originales de palabras clave extra. Las del plan (`captions.emphasis_words`) ya vienen marcadas; si no hay ninguna, se resaltan los números solos (`--sin-claves-auto` para apagarlo).
- `--solo-srt`: no quema nada, solo deja el `.srt` y el `.ass`.

Sale el MP4 con los subtítulos quemados (el audio se copia sin tocar) y, al lado, `.srt` y `.ass` con el mismo nombre. El formato (9:16 o 16:9) se detecta del video.

## Reglas que aplica

- Máximo 2 líneas por bloque; corta en fin de frase y en pausas de más de 0,45 s.
- 9:16: el texto queda por encima del 30 % inferior (ahí están la descripción y los botones de la app) y con más margen a la derecha. 16:9: cerca del borde inferior.
- La palabra activa entra con un pequeño "pop" y cambia de color. Las claves quedan coloreadas todo el bloque.
- Saca comas y puntos de los bordes (en pantalla molestan); deja ¿? y ¡!.

## Después

Mostrale al usuario un cuadro del video para que vea cómo quedó, si podés:
```bash
ffmpeg -v error -ss 3 -i "RUTA/video_editado.mp4" -frames:v 1 "RUTA/muestra.png"
```
Si hay errores de transcripción en los subtítulos (nombres propios, marcas), corregí el `texto` en el `.palabras.json` y volvé a correr el script: es rápido.

Si el script avisa que tu ffmpeg no tiene libass, explicale al usuario cómo instalar un ffmpeg completo (`nc-editar/instalar_dependencias.md`) y entregale igual el `.srt`.
