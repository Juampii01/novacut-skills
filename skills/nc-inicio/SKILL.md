---
name: nc-inicio
description: >-
  Menú y guía del pack NovaCut Skills: qué skill usar para cada tarea, por
  dónde empezar y cómo encadenarlas. Usala cuando el usuario diga "/nc-inicio",
  "qué puedo hacer con NovaCut", "qué skills tengo", "por dónde empiezo",
  "ayuda con el pack", "help", o no sepa qué skill usar.
---

# nc-inicio

Sos la puerta de entrada al pack. Tu trabajo: entender qué quiere hacer el usuario hoy y mandarlo a la skill justa, en el orden justo.

## Primero: ¿tiene su perfil de voz?

Revisá si existe `~/.claude/novacut/voz.md` (en claude.ai: si lo subió al proyecto o lo pegó en el chat). Si no existe, lo primero que le recomendás es `/nc-voz`: diez minutos ahí hacen que todo lo demás suene a él.

## Después: preguntá qué quiere hacer hoy

Una sola pregunta, con opciones:

1. **Editar un video que ya grabé** → bloque Edición.
2. **Saber qué publicar** → `/nc-viral` (o `/nc-yt-viral`, `/nc-x-viral`) y después `/nc-plan`.
3. **Escribir un guion** → `/nc-reel` (reel/TikTok/short) o `/nc-yt-script` (YouTube).
4. **Escribir un post o la descripción** → `/nc-caption`, `/nc-li-post`, `/nc-x-post`.
5. **Mejorar mi perfil** → `/nc-profile`, `/nc-li-profile`, `/nc-x-profile`.
6. **Responder comentarios y mensajes** → `/nc-reply`, `/nc-dm`.
7. **Ver qué funcionó y qué no** → `/nc-audit`, `/nc-yt-audit`, `/nc-li-audit`, `/nc-x-audit`.

## El menú completo

### Base
| Skill | Para qué |
|---|---|
| `/nc-inicio` | Este menú |
| `/nc-voz` | Arma tu perfil de voz. Hacelo primero |
| `/nc-human` | Le saca el "olor a IA" a cualquier texto y lo puntúa |

### Edición de video (necesita Claude Code en tu computadora)
| Skill | Para qué |
|---|---|
| `/nc-editar` | Video crudo → video listo: cortes, audio y subtítulos, con tu aprobación antes de renderizar |
| `/nc-cortar` | Saca silencios, muletillas y tomas repetidas |
| `/nc-subtitulos` | Subtítulos animados palabra por palabra, quemados en el video |
| `/nc-audio` | Limpia la voz, iguala el volumen y mete música por debajo |
| `/nc-brief-edicion` | El plan de edición segundo a segundo: texto en pantalla, animaciones, B-roll |
| `/nc-yt-edit` | Lista de cortes desde una transcripción (sin tocar el video) |

### Instagram, Reels y TikTok
| Skill | Para qué |
|---|---|
| `/nc-viral` | Qué está funcionando en tu nicho, ordenado por cuánto superó a su cuenta |
| `/nc-reel` | Guion de reel con 3 ganchos puntuados y tiempos por momento |
| `/nc-caption` | La descripción, revisada: lo que se ve antes del "más" |
| `/nc-carousel` | Carruseles: portada, texto de cada slide |
| `/nc-story` | La secuencia de historias del día |
| `/nc-plan` | La semana: qué publicar, cuándo y con quién interactuar |
| `/nc-profile` | Puntaje de tu perfil sobre 100 y cómo arreglarlo |
| `/nc-comment` | Comentarios en publicaciones de otros |
| `/nc-reply` | Respuestas a los comentarios de tus posts |
| `/nc-dm` | Mensajes directos y la palabra clave para comentarios |
| `/nc-repurpose` | Un video o podcast largo → una semana de contenido |
| `/nc-audit` | Qué funcionó de lo que ya publicaste |

### YouTube
| Skill | Para qué |
|---|---|
| `/nc-yt-viral` | Qué está funcionando en tu nicho |
| `/nc-yt-script` | Guion con gancho puntuado |
| `/nc-yt-package` | Título y miniatura, revisados como pareja |
| `/nc-yt-seo` | Descripción y búsqueda |
| `/nc-yt-chapters` | Capítulos desde la transcripción |
| `/nc-yt-shorts` | Los shorts que ya están escondidos en tu video largo |
| `/nc-yt-retention` | En qué segundo se va la gente y qué decías ahí |
| `/nc-yt-comment` | Respuestas a comentarios |
| `/nc-yt-plan` | La semana del canal |
| `/nc-yt-audit` | Auditoría del canal |

### LinkedIn
`/nc-li-post` · `/nc-li-carousel` · `/nc-li-comment` · `/nc-li-reply` · `/nc-li-dm` · `/nc-li-inbox` · `/nc-li-profile` · `/nc-li-plan` · `/nc-li-repurpose` · `/nc-li-audit` · `/nc-li-human`

### X (Twitter)
`/nc-x-post` · `/nc-x-thread` · `/nc-x-viral` · `/nc-x-comment` · `/nc-x-reply` · `/nc-x-dm` · `/nc-x-profile` · `/nc-x-plan` · `/nc-x-repurpose` · `/nc-x-audit` · `/nc-x-human`

## Recorridos recomendados

**Un reel de cero a publicado:**
`/nc-viral` (qué hacer) → `/nc-reel` (guion) → grabás → `/nc-editar` (cortes, audio, subtítulos) → `/nc-brief-edicion` (si querés animaciones) → `/nc-caption` (descripción) → publicás.

**Un video de YouTube:**
`/nc-yt-script` → grabás → `/nc-editar` → `/nc-yt-chapters` → `/nc-yt-package` → `/nc-yt-seo` → publicás → a la semana, `/nc-yt-retention`.

**Una semana de contenido con un solo video largo:**
`/nc-repurpose` → `/nc-yt-shorts` → `/nc-editar` en cada clip.

## Si algo no está disponible

Mirá qué skills tiene instaladas el usuario. Si recomendás una que no está, decile cuál zip subir (claude.ai) o que revise la carpeta `~/.claude/skills/` (Claude Code). Las skills de edición de video solo funcionan en Claude Code con ffmpeg instalado; si está en claude.ai, ofrecele `/nc-brief-edicion` y `/nc-yt-edit`, que no tocan el video.

## Reglas del pack

Ninguna skill publica nada, ninguna se loguea en tus cuentas y ninguna inventa números: si falta un dato, aparece `{{tu número}}`. Vos revisás y publicás.
