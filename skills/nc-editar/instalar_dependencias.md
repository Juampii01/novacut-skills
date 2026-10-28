# Instalar lo que necesita el editor de video NovaCut

El editor corre en tu computadora. Necesita tres cosas (una sola vez):

1. **ffmpeg** (con libass, para los subtítulos): el programa que corta y codifica el video.
2. **Python 3.10 o más nuevo** (recomendado: 3.12).
3. **faster-whisper**: la transcripción por voz, local y gratis. La primera vez descarga el modelo de voz (~480 MB el "small"); después funciona sin internet.

Cuando termines, verificá con:
- Mac: `python3 ~/.claude/skills/nc-editar/verificar.py` (o con el Python del entorno, ver abajo)
- Windows: `py %USERPROFILE%\.claude\skills\nc-editar\verificar.py`

Si en vez de seguir esto le decís a Claude Code "instalame las dependencias del editor", también te puede guiar paso a paso (te va a pedir permiso antes de cada comando).

---

## Mac

**1. Homebrew** (si ya lo tenés, saltá). Abrí la Terminal y pegá el comando que aparece en https://brew.sh. Al final te muestra 2 o 3 líneas para agregar brew al PATH: copialas y pegalas también.

**2. ffmpeg y Python**
```bash
brew install ffmpeg python@3.12
```
El ffmpeg de Homebrew trae libass (subtítulos) y x264.

**3. faster-whisper, en un entorno propio de NovaCut**

El Python de Homebrew no deja instalar paquetes "sueltos" (da el error `externally-managed-environment`), así que se crea un entorno para NovaCut:
```bash
mkdir -p ~/.claude/novacut
python3.12 -m venv ~/.claude/novacut/venv
~/.claude/novacut/venv/bin/python -m pip install --upgrade pip
~/.claude/novacut/venv/bin/python -m pip install faster-whisper
```
Claude usa ese Python automáticamente si existe. Para verificar:
```bash
~/.claude/novacut/venv/bin/python ~/.claude/skills/nc-editar/verificar.py
```
Funciona en Mac con Apple Silicon (M1/M2/M3/M4) y con Intel.

---

## Windows

Usá **PowerShell** (botón Inicio → escribí "PowerShell").

**1. ffmpeg** (build completo de Gyan, trae libass y zscale)
```powershell
winget install --id Gyan.FFmpeg -e
```
**Cerrá y abrí de nuevo PowerShell** (si no, no encuentra `ffmpeg`). Probá con `ffmpeg -version`.

**2. Python 3.12**
```powershell
winget install --id Python.Python.3.12 -e
```
Cerrá y abrí PowerShell de nuevo. Probá con `py --version`.

**3. faster-whisper**
```powershell
py -m pip install faster-whisper
```
(Opcional, para tenerlo separado del resto: `py -m venv $env:USERPROFILE\.claude\novacut\venv` y después `& "$env:USERPROFILE\.claude\novacut\venv\Scripts\python.exe" -m pip install faster-whisper`. Claude usa ese Python si existe.)

**4. Verificar**
```powershell
py $env:USERPROFILE\.claude\skills\nc-editar\verificar.py
```

---

## Lo que no está 100 % verificado (avisanos si te pasa)

- **Windows sin winget** (Windows 10 viejo): instalá "App Installer" desde Microsoft Store, o bajá ffmpeg de https://www.gyan.dev/ffmpeg/builds/ (el "full build"), descomprimilo y agregá su carpeta `bin` al PATH.
- **Windows y el runtime de Visual C++**: si `import faster_whisper` falla con un error de DLL, instalá el "Microsoft Visual C++ Redistributable" (x64) desde la web de Microsoft. No debería hacer falta en la mayoría de las PCs.
- **Python 3.13 / 3.14**: faster-whisper funciona en 3.13 (probado); con versiones más nuevas puede que su dependencia `ctranslate2` todavía no tenga instalador. Si `pip install` falla, usá Python 3.12.
- **zscale en el ffmpeg de Homebrew**: sirve solo para videos HDR del iPhone. Si `verificar.py` dice que falta, el resto funciona igual; para evitar el HDR, en el iPhone: Configuración → Cámara → Formatos → desactivá "Video HDR".
- **Firewall o VPN de empresa**: la descarga del modelo sale de huggingface.co. Si está bloqueado, el script lo dice; probá desde otra red solo esa primera vez.
