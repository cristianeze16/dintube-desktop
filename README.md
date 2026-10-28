# DinTube de escritorio

Empaqueta [DinTube](../dintube) como app de Windows: ventana propia (sin navegador), con Python,
ffmpeg y deno adentro, e instalador con acceso directo. El proyecto `dintube` no se modifica:
`preparar.py` copia `servidor.py`, `descargar.py` y `web/` a `build/` y parchea 3 rutas.

## Armar

1. (Opcional, para el instalador) Instalar [Inno Setup 6](https://jrsoftware.org/isdl.php).
2. Doble click en `construir.bat`. La primera vez tarda: crea `.venv`, instala dependencias y baja ffmpeg y deno.

Sale:
- `dist\DinTube\DinTube.exe`: la app lista para usar (podés copiar la carpeta entera a otra PC).
- `instalador\DinTube-Setup.exe`: el instalador, si está Inno Setup.

Cada vez que cambies algo en `dintube`, volvé a correr `construir.bat`.
Para actualizar yt-dlp alcanza con volver a construir (pip lo actualiza); para ffmpeg/deno, borrá `build\bin`.

## Cómo funciona instalado

- Abre una ventana con DinTube (WebView2 de Windows). Cerrarla apaga DinTube.
- El celu, la tablet y la tele siguen entrando por `http://IP-de-la-PC:8000` mientras esté abierta.
  El instalador ofrece abrirlo al iniciar Windows.
- Datos (historial, listas, Kids, `clave.txt`): `%LOCALAPPDATA%\DinTube`. Para pasar los que ya tenés,
  copiá los `.json`, `.secreto` y `clave.txt` de `dintube` ahí.
- MP3: `Música\DinTube`.
- Si ya está corriendo `DinTube Web.bat`, la ventana usa ese servidor en vez de levantar otro.
- Variables que siguen andando: `DINTUBE_PUERTO`, `DINTUBE_LAT`, `DINTUBE_LON`, `DINTUBE_LUGAR`.

## Archivos

- `app_escritorio.py`: arranca el servidor y abre la ventana.
- `preparar.py`: copia y parchea el código de `dintube`.
- `construir.ps1` / `construir.bat`: arma todo.
- `instalador.iss`: script de Inno Setup.

## Actualizaciones automáticas

- La Action `.github/workflows/escritorio.yml` del repo `dintube` (privado) arma el instalador en cada push a `main`
  (y los lunes si salió un yt-dlp nuevo) y lo publica como Release acá, en `cristianeze16/dintube-desktop` (público).
- Al abrir, DinTube compara su `version.txt` con la última Release. Si hay una más nueva pregunta,
  la baja, se instala en silencio y se vuelve a abrir.
- Builds locales con `construir.bat` salen como versión 0 (siempre van a ofrecer actualizar a la publicada).
- Se instala por usuario (`%LOCALAPPDATA%\Programs\DinTube`), sin pedir admin.
