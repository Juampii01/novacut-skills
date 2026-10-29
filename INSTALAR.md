# Cómo instalar NovaCut Skills

Hay dos formas. Elegí una según cómo usás Claude:

| | Camino A · claude.ai (web, escritorio o app) | Camino B · Claude Code |
|---|---|---|
| Plan de Claude | Cualquiera, incluido el gratis | Pro, Max, Team o Enterprise (el plan gratis no incluye Claude Code) |
| Dificultad | Fácil: subís archivos desde la configuración | Media: se usa la terminal una vez |
| Qué instalás | Las skills que elijas, una por una | Todas de una vez |
| Herramientas que corren (puntaje de ganchos, humanizador, tiempos) | Sí, en el entorno de Claude | Sí, en tu computadora |
| Edición de video (cortes, audio, subtítulos) | No | Sí |

Si nunca abriste una terminal, andá por el **Camino A**.

---

## Camino A · claude.ai

**1. Activá la ejecución de código.** Las skills la necesitan.
- Planes Free, Pro y Max: **Configuración → Capacidades** (*Settings → Capabilities*) y activá **"Ejecución de código y creación de archivos"** (*Code execution and file creation*; en la versión nueva, *Create and edit files*).
- Planes Team o Enterprise: lo activa quien administra la cuenta, en la configuración de la organización.

**2. Descomprimí el pack.** Adentro está la carpeta `claude-ai/` con un `.zip` por skill.

**3. Subí cada skill.**
1. En Claude, andá a **Personalizar → Skills** (*Customize → Skills*).
2. Tocá **"+"** y después **"+ Crear skill"** (*Create skill*).
3. Elegí **"Subir una skill"** (*Upload a skill*) y seleccioná el `.zip` (por ejemplo `nc-reel.zip`). **No lo descomprimas.**
4. Repetí con las que quieras. Cada skill se puede prender y apagar desde esa misma lista.

**¿Por cuáles empiezo?** No hace falta subir todas. Este es el kit de arranque:

| Skill | Para qué |
|---|---|
| `nc-inicio` | Te dice qué skill usar para cada cosa |
| `nc-voz` | Arma tu perfil de voz (hacelo primero) |
| `nc-viral` | Encuentra qué está funcionando en tu nicho |
| `nc-reel` | Guion de reel con ganchos puntuados |
| `nc-caption` | La descripción del post, revisada |
| `nc-human` | Le saca el "olor a IA" a cualquier texto |
| `nc-brief-edicion` | El plan de edición segundo a segundo |
| `nc-yt-script` | Guion de video para YouTube |

Después sumá las de la red que más uses (`nc-li-*` para LinkedIn, `nc-x-*` para X).

**4. Probala.** Abrí un chat nuevo y escribí: `armá mi perfil de voz`. Si Claude arranca con preguntas o te pide videos tuyos, está funcionando.

**Tu perfil de voz en claude.ai:** como Claude no puede guardar archivos en tu computadora desde la web, cuando `nc-voz` termine te va a dar el archivo `voz.md`. Lo más cómodo: creá un **Proyecto** en claude.ai, subí ahí `voz.md` como conocimiento del proyecto y hacé tu contenido dentro de ese proyecto.

---

## Camino B · Claude Code

**1. Instalá Claude Code** (si ya lo tenés, saltá al paso 2).

Mac (en la app Terminal):
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows (en PowerShell, sin permisos de administrador):
```powershell
irm https://claude.ai/install.ps1 | iex
```

Cerrá y volvé a abrir la terminal, y verificá con `claude --version`. Después escribí `claude` e iniciá sesión con tu cuenta (Pro o superior). Si preferís no usar la terminal, Claude Code también viene en la app de escritorio de Claude.

**2. Instalá las herramientas de video** (solo si vas a usar la edición: `nc-editar`, `nc-cortar`, `nc-subtitulos`, `nc-audio`).

El editor necesita **ffmpeg**, **Python 3.10 o más nuevo** y **faster-whisper** (la transcripción local, gratis). La primera vez descarga el modelo de voz (unos 480 MB) y después funciona sin internet. Los pasos exactos para Mac y Windows están en `skills/nc-editar/instalar_dependencias.md`.

Atajo: después del paso 3, abrí Claude Code y escribí *"instalame las dependencias del editor"*. Te guía y te pide permiso antes de cada comando.

Si solo vas a usar las skills de escritura, alcanza con tener Python 3 (`python3 --version`; en Windows puede ser `python`).

**3. Copiá las skills.** Descomprimí `NovaCut-Skills.zip`, abrí la terminal en la carpeta `NovaCut-Skills` y corré:

Mac:
```bash
mkdir -p ~/.claude/skills ~/.claude/novacut
cp -R skills/* ~/.claude/skills/
cp templates/voz.md ~/.claude/novacut/voz.md
```

Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills", "$env:USERPROFILE\.claude\novacut" | Out-Null
Copy-Item -Recurse -Force skills\* "$env:USERPROFILE\.claude\skills\"
Copy-Item templates\voz.md "$env:USERPROFILE\.claude\novacut\voz.md"
```

**Atajo:** también podés abrir Claude Code dentro de la carpeta del pack y escribir: *"Instalá todas las skills de la carpeta skills en mi carpeta personal de skills y copiá templates/voz.md a ~/.claude/novacut/voz.md."*

**4. Probala.** Abrí Claude Code (`claude`) y escribí `/nc-inicio`. Te muestra el menú del pack. Después corré `/nc-voz` para armar tu perfil. Para la edición, verificá todo con:
```bash
python3 ~/.claude/skills/nc-editar/verificar.py
```

---

## Problemas comunes

- **"La skill no aparece" (claude.ai):** verificá que subiste el `.zip` sin descomprimir y que la ejecución de código está activada.
- **"python3 no se reconoce" (Windows):** reinstalá Python marcando "Add Python to PATH", o usá `python` en lugar de `python3`.
- **"claude no se reconoce":** cerrá y abrí la terminal de nuevo. Si sigue, reinstalá con el comando del paso 1.
- **Los guiones no suenan a vos:** te falta el perfil de voz. Corré `/nc-voz`.

## Lo que el pack no hace

Las skills **escriben, planifican y revisan**. **No publican nada** en tus cuentas, no se loguean en Instagram, YouTube, LinkedIn ni X, y no inventan números ni resultados. Vos revisás y publicás.
