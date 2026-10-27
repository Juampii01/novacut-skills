# Guiones de los tutoriales (interno, no viaja en el pack)

Para lanzar alcanzan los 3 primeros. Grabá pantalla + voz (o tu voz clonada). Ritmo: corto, sin intro, cada paso en pantalla mientras lo decís.

---

## Tutorial 1 · Instalar en claude.ai (4–5 min)

**Objetivo:** que alguien que nunca usó skills las tenga andando.

1. **(0:00) Qué vas a lograr.** "En cinco minutos vas a tener tus primeras skills de NovaCut andando en Claude. No necesitás terminal ni saber programar."
2. **(0:20) Activar la ejecución de código.** Pantalla: Configuración → Capacidades → "Crear y editar archivos" (o "Ejecución de código y creación de archivos"). "Sin esto, las skills no corren."
3. **(0:50) Descomprimir el pack.** Mostrá la carpeta `claude-ai/` con un zip por skill. "No descomprimas estos zips: se suben así."
4. **(1:20) Subir la primera skill.** Personalizar → Skills → "+" → Crear skill → Subir una skill → `nc-voz.zip`. Mostrá que aparece en la lista y se puede prender y apagar.
5. **(2:00) El kit de arranque.** Subí rápido: `nc-inicio`, `nc-viral`, `nc-reel`, `nc-caption`, `nc-human`, `nc-brief-edicion`, `nc-yt-script`. "Con estas ya hacés el 80%."
6. **(3:00) Crear un Proyecto para tu voz.** "Las skills necesitan conocer cómo hablás. Creá un proyecto llamado 'Mi contenido'."
7. **(3:30) Probar.** En el proyecto: "armá mi perfil de voz". Mostrá cómo Claude pregunta. Cuando da `voz.md`, subilo al conocimiento del proyecto.
8. **(4:30) Cierre.** "Desde ahora, todo lo hacés dentro de este proyecto. En el próximo video: tu primer reel de punta a punta."

**Errores a mostrar:** zip descomprimido por error; ejecución de código apagada.

---

## Tutorial 2 · Instalar en Claude Code, con edición de video (7–8 min)

**Objetivo:** dejar andando también las skills que editan video.

1. **(0:00) Por qué Claude Code.** "Las skills que editan tu video trabajan con el archivo en tu computadora. Para eso está Claude Code. Necesitás plan Pro o superior."
2. **(0:30) Instalar Claude Code.** Mac: Terminal + comando. Windows: PowerShell + comando. Cerrar y abrir, `claude --version`, `claude` e iniciar sesión.
3. **(2:00) Instalar las herramientas de video.** ffmpeg y Python + faster-whisper (los comandos exactos están en INSTALAR.md). Mostrá `ffmpeg -version` y `python3 --version`.
4. **(3:30) Copiar las skills.** Descomprimir `NovaCut-Skills.zip`, abrir la terminal en la carpeta y pegar los comandos. Atajo: abrir `claude` en la carpeta y pedirle que las instale.
5. **(4:30) Probar `/nc-inicio`.** Mostrá el menú.
6. **(5:00) Primera edición.** `/nc-editar` con un video corto. La primera vez descarga el modelo de transcripción (avisá que tarda unos minutos y es una sola vez).
7. **(6:30) Aprobar el plan de cortes.** Mostrá cómo te muestra lo que va a cortar y cómo pedís cambios ("dejá la parte del ejemplo").
8. **(7:30) Cierre.** El video final y el `.srt` en la carpeta. "Nunca toca tu original."

---

## Tutorial 3 · Un reel de punta a punta (6–8 min)

**Objetivo:** que vean el valor completo en un caso real. Este también sirve como video de venta.

1. **(0:00) Gancho.** Mostrá el resultado final 5 segundos. "Esto lo hice sin abrir un editor. Te muestro cómo."
2. **(0:15) `/nc-viral`.** Qué está funcionando en tu nicho (usá un swipe ya armado para no esperar).
3. **(1:15) `/nc-reel`.** Tres ganchos con puntaje, elegís el mejor, guion con tiempos.
4. **(2:30) Grabás.** Cortá: mostrá el crudo con errores y silencios.
5. **(3:00) `/nc-editar`.** Plan de cortes, aprobás, render. Antes y después lado a lado.
6. **(4:30) `/nc-brief-edicion`.** Plan de animaciones para los momentos clave.
7. **(5:30) `/nc-caption`.** La descripción con la palabra clave.
8. **(6:30) Cierre.** "Un editor te cobra USD 10 a 100 por esto. Acá lo hiciste vos, con tu plan de Claude."

---

## Videos cortos por bloque (después del lanzamiento)

Uno por skill estrella, 60–90 s cada uno: `nc-human` (antes/después de un texto con olor a IA), `nc-yt-package` (título y miniatura), `nc-yt-retention` (dónde se va la gente), `nc-profile` (puntaje del perfil), `nc-plan` (la semana armada).
