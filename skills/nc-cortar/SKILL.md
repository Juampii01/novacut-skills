---
name: nc-cortar
description: >-
  Corta un video crudo hablado a cámara en tu computadora, sin pagar API:
  transcribe palabra por palabra (faster-whisper local), detecta silencios,
  muletillas ("eh", "este", "o sea", "bueno, nada"), retomas y arranques en
  falso, arma un plan de cortes por IDs de palabra, te lo muestra para que lo
  apruebes y recién ahí renderiza con cortes exactos (audio y video en
  sincronía). Usala para "cortá este video", "sacale los silencios", "sacá
  las muletillas", "dejá la última toma", "limpiá la grabación", "cut the
  dead air", "remove the ums". Solo funciona en Claude Code (necesita
  ffmpeg y Python en la compu). Para el flujo completo (cortes + audio +
  subtítulos) usá /nc-editar.
---

# nc-cortar

Saca de un video hablado todo lo que sobra: silencios largos, muletillas, retomas y arranques en falso. Trabaja en la computadora del usuario con ffmpeg y Python. No sube nada a ningún lado.

**Regla de oro: el plan dice qué PALABRAS se sacan, nunca segundos.** Vos (Claude) elegís IDs de palabra; los tiempos salen de la transcripción y el script los ajusta a cuadros. Nunca escribas tiempos a mano en el plan.

## Archivos de esta skill

Los scripts están en la carpeta de esta skill (en Claude Code suele ser `~/.claude/skills/nc-cortar/`; en Windows `%USERPROFILE%\.claude\skills\nc-cortar\`). Abajo, `$SKILL` es esa carpeta. En Windows usá `py` en lugar de `python3`.

| Script | Qué hace |
|---|---|
| `transcribir.py` | Video → `palabras.json` (cada palabra con `id`, `texto`, `inicio`, `fin`). faster-whisper local, bordes ajustados a la energía del audio. |
| `candidatos.py` | Detecta sin IA retomas, arranques en falso, muletillas y silencios. Imprime la transcripción con IDs. |
| `render.py` | Valida el plan v2 y lo aplica. `--simular` muestra qué se corta sin renderizar. |

**Qué Python usar:** si existe `~/.claude/novacut/venv/bin/python` (Windows: `%USERPROFILE%\.claude\novacut\venv\Scripts\python.exe`), usá ese en lugar de `python3` (ahí está instalado faster-whisper). Si no, `python3` en Mac/Linux o `py` en Windows.

Dependencias: ffmpeg + Python 3.10+ + `pip install faster-whisper`. Si falta algo, corré `python3 $SKILL/../nc-editar/verificar.py` y seguí `nc-editar/instalar_dependencias.md`.

## Pasos

### 1. Transcribir

```bash
python3 "$SKILL/transcribir.py" "RUTA/video.mp4"            # --modelo small (default) | medium | large-v3 · --idioma es | auto
```

Deja `RUTA/video_novacut/palabras.json`. La primera vez descarga el modelo (una sola vez; "small" pesa ~480 MB): avisale al usuario que puede tardar. Si el video es largo (más de 10 min) avisá que transcribir lleva varios minutos en CPU. Si el usuario habla con mucho acento o jerga y la transcripción sale floja, ofrecé `--modelo medium` (más lento, más preciso).

### 2. Detectar candidatos

```bash
python3 "$SKILL/candidatos.py" "RUTA/video_novacut/palabras.json" --plan-base "RUTA/video_novacut/plan.json"
```

Imprime la transcripción con IDs (`[12]palabra<C3>` = la palabra 12 está en el candidato C3) y la lista de candidatos con motivo y confianza. `--plan-base` escribe un borrador con los candidatos de confianza alta (≥ 0,75). Si el usuario tiene el guion, sumá `--guion guion.txt` (refuerza las retomas).

### 3. Armar el plan v2 (esto lo hacés vos)

Leé la transcripción con IDs y los candidatos, y escribí `plan.json`:

```json
{
  "version": 2,
  "format": "9:16",
  "removals": [
    {"from_word": 1, "to_word": 1, "reason": "filler", "confidence": 0.9, "nota": "eh"},
    {"from_word": 7, "to_word": 10, "reason": "retake", "confidence": 0.85, "nota": "primera toma de «tres errores que cometen»"}
  ],
  "pausa_max": 0.5,
  "captions": {"emphasis_words": [11, 24, 44]},
  "summary": "Saqué 6 muletillas y una retoma; quedan 18 s."
}
```

- `reason`: `filler` (muletilla), `retake` (retoma), `false_start` (arranque en falso), `silence`, `off_topic` (se fue de tema), `other`.
- `from_word`/`to_word` son IDs inclusivos. Los cortes no se pueden superponer (si dos se tocan, unilos en uno).
- No hace falta cortar silencios: `render.py` acorta solo cualquier pausa de más de `pausa_max` segundos (default 0,5; usá 0,3 para un ritmo de reel rápido, 0,7-0,8 para algo más pausado o educativo).
- `format`: `"9:16"` (reel, short, TikTok) o `"16:9"` (YouTube). Si no lo ponés, sale según la orientación del video.
- `hook` (opcional): `{"from_word": 40, "to_word": 52}` mueve ese tramo al principio. Proponelo solo si hay una frase claramente más fuerte que la apertura y preguntá antes.
- `captions.emphasis_words`: 1 o 2 palabras clave por frase (números, el resultado, la palabra que carga la idea) para resaltarlas en los subtítulos.

Criterio para decidir:
- **Muletillas puras** ("eh", "mmm"): cortalas siempre.
- **Muletillas blandas** ("este", "bueno", "o sea", "nada", "tipo"): solo si están sueltas entre pausas. Si son parte de la frase ("bueno, eso es todo" como cierre natural), dejalas.
- **Retomas**: se queda la ÚLTIMA toma completa. Verificá leyendo que la toma que queda esté entera; si la última se cortó a la mitad, quedate con la anterior.
- **Arranques en falso** y palabras cortadas: cortalos.
- **Fuera de tema**: solo si el usuario lo pidió ("dejalo en 60 segundos", "sacá lo que no suma"). Nunca cortes contenido por gusto propio sin decirlo.
- Ante la duda, NO cortes y mencionalo.

### 4. Mostrar el plan y esperar el OK (obligatorio)

```bash
python3 "$SKILL/render.py" "RUTA/video.mp4" "RUTA/video_novacut/palabras.json" "RUTA/video_novacut/plan.json" --simular
```

Mostrale al usuario la salida tal cual (duración antes/después y la lista de cortes con el texto que se va) y preguntá: "¿Lo renderizo así o querés cambiar algo?". **No renderices sin un sí explícito.** Si pide cambios ("dejá el 'bueno' del final", "sacá también la parte de X"), editá el plan, volvé a simular y volvé a mostrar.

### 5. Renderizar

```bash
python3 "$SKILL/render.py" "RUTA/video.mp4" "RUTA/video_novacut/palabras.json" "RUTA/video_novacut/plan.json"
```

Sale `RUTA/video_novacut/cortado.mp4` (H.264 + AAC, 30 cuadros fijos, 1080x1920 o 1920x1080) y `cortado.palabras.json` con los tiempos re-mapeados al video cortado (lo usa `/nc-subtitulos`). Opciones: `--formato 9:16|16:9`, `--encuadre-x -1..1` (al pasar un video horizontal a vertical: -1 izquierda, 0 centro, 1 derecha), `--fps 24|25|30|60`, `--preset fast` si la compu es lenta.

El script controla solo la duración y la sincronía. Si dice `REVISAR`, avisale al usuario con el número exacto que dio.

## Lo que garantiza el render

- Mismo corte en audio y video: cada tramo son N cuadros y exactamente N × 1600 muestras (a 30 fps). Sin desfase, aunque haya 100 cortes.
- Fundido de audio de 10 ms en cada corte: no hay clics.
- 80 ms de aire antes y 140 ms después de cada tramo: no se comen sílabas.
- Video del celular con cuadros variables (VFR) o 29,97: se normaliza antes de cortar. HDR del iPhone: se pasa a SDR (si el ffmpeg tiene zscale).
- **Nunca sobrescribe el original.** Todo va a la carpeta `video_novacut/`.

## Lo que no hace

- No reencuadra siguiendo la cara (el recorte de horizontal a vertical es fijo; se ajusta con `--encuadre-x`).
- No agrega B-roll, zooms ni animaciones. Para planificarlos está `/nc-brief-edicion`; las animaciones automáticas llegan en una próxima versión del pack.
- No inventa contenido ni cambia lo que dijo la persona: solo saca.
