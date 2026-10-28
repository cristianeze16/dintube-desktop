# dintube-desktop

Empaqueta DinTube (`../dintube`, repo privado cristianeze16/dintube) como app de Windows. Ver README.md.
- `app_escritorio.py`: arranca servidor.py en un hilo, abre ventana pywebview, chequea Releases de este repo
  y se autoactualiza (instalador silencioso). Sin consola: no depender de stdout.
- `preparar.py`: copia el código de dintube a `build/` y parchea rutas (si dintube cambia esas líneas, ajustar acá).
- `construir.ps1 [-Origen ..\dintube] [-Version N]`: venv, deps, ffmpeg/deno, PyInstaller, Inno Setup.
- `instalador.iss`: instalación por usuario (sin admin), relanza la app tras actualización silenciosa.
- Las Releases las publica la Action de dintube: "DinTube 3.0.N", etiqueta `v3.0.N` (la `v4` fue el puente desde
  las viejas `v1`..`v3`, que la app compara como número). Este repo debe seguir público.
- Si cambiás algo acá, hay que hacer push acá y después un push (o "Run workflow") en dintube para publicar.
