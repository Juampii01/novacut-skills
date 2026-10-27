---
name: nc-audio
description: >-
  Mejora el audio de un video hablado en tu computadora con ffmpeg: saca
  rumor y ruido de fondo, empareja la voz, la normaliza a -14 LUFS / -1 dBTP
  (el volumen que esperan Instagram, TikTok y YouTube) en dos pasadas y,
  si querés, suma música de fondo que baja sola cuando hablás. Usala para
  "mejorá el audio", "se escucha bajo", "sacale el ruido", "ponele música de
  fondo", "nivelá el volumen", "fix the audio", "add background music".
  Solo en Claude Code (necesita ffmpeg).
---

# nc-audio

Limpieza y volumen de la voz, sin IA ni servicios pagos: filtros de ffmpeg. El video no se recodifica (se copia tal cual), así que es rápido.

Script: `audio.py` en la carpeta de esta skill (`$SKILL`, normalmente `~/.claude/skills/nc-audio/`). En Windows usá `py` en vez de `python3`.

**Qué Python usar:** si existe `~/.claude/novacut/venv/bin/python` (Windows: `%USERPROFILE%\.claude\novacut\venv\Scripts\python.exe`), usá ese en lugar de `python3` (ahí está instalado faster-whisper). Si no, `python3` en Mac/Linux o `py` en Windows.

## Uso

```bash
python3 "$SKILL/audio.py" "RUTA/cortado.mp4"                                  # -> cortado_audio.mp4
python3 "$SKILL/audio.py" "RUTA/cortado.mp4" --musica "RUTA/pista.mp3"         # con música de fondo
python3 "$SKILL/audio.py" "RUTA/video.mp4" --medir                             # solo mide LUFS y pico
```

Opciones:
- `--limpieza normal` (default) · `suave` (micrófono bueno, sala silenciosa) · `fuerte` (ruido de ventilador, aire acondicionado, calle) · `ninguna` (solo volumen).
- `--musica pista.mp3 --musica-db -22`: la música queda ~22 dB por debajo de la voz mientras hablás y sube ~10 dB en las pausas largas. Si es más corta que el video, se repite; entra y sale con fundido (`--fundido 0.8 1.5`).
- `--objetivo -14 --pico -1`: los valores de las redes. No los cambies salvo que el usuario lo pida (por ejemplo, -16 para podcasts).

## Qué hace, en orden

1. Pasa altos a 80 Hz (rumor, golpes en la mesa), reducción de ruido (`afftdn`), +2 dB de presencia en 4 kHz, de-esser y compresor suave 3:1.
2. Mide el retraso que agrega la reducción de ruido (~25 ms) y lo compensa: la voz no se corre del video.
3. `loudnorm` en dos pasadas: la primera mide, la segunda aplica en modo lineal (solo ganancia, sin "bombeo"). Antes deja la voz cerca del objetivo con un limitador para que el modo lineal entre siempre.
4. Si hay música: la mide, la ajusta, la baja con `sidechaincompress` cuando hablás y pone un limitador final a -1 dBFS.
5. Mide el resultado con `ebur128` y lo informa (LUFS, pico verdadero, modo de la segunda pasada).

## Música: avisá esto al usuario

- Usá solo música con derechos para redes (propia, comprada con licencia, o de bibliotecas que permitan uso comercial). Una canción comercial puede hacer que silencien o bajen el video.
- En Instagram y TikTok muchas veces conviene subir el video **sin** música y agregar el audio en tendencia dentro de la app. Ofrecé las dos opciones.

## Reglas

- Nunca sobrescribe el archivo de entrada.
- Si el resultado queda a más de 1 LU del objetivo o el pico pasa el techo, el script avisa: decíselo al usuario con los números.
- No es un estudio de grabación: limpia ruido constante (ventilador, aire), no rescata un audio con mucho eco o saturado. Si el audio original es malo, decilo y recomendá regrabar con el micrófono más cerca.
