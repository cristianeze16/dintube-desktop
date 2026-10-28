"""DinTube de escritorio: levanta servidor.py y lo muestra en una ventana propia (pywebview).

El celu y la tablet siguen entrando por http://IP-de-la-PC:8000 mientras la ventana esté abierta.
Cerrar la ventana apaga DinTube (igual que el botón "Apagar DinTube").
"""
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time

# Sin consola (exe con --noconsole) stdout/stderr son None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# Dentro del exe los archivos empaquetados están en sys._MEIPASS; en desarrollo, junto a este archivo
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

# Archivos Program Files no se pueden escribir: los datos van a %LOCALAPPDATA%\DinTube
# y los MP3 a Música\DinTube. servidor.py (parcheado por preparar.py) lee estas variables.
DATOS = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "DinTube")
AUDIOS = os.path.join(os.path.expanduser("~"), "Music", "DinTube")
os.makedirs(DATOS, exist_ok=True)
os.makedirs(AUDIOS, exist_ok=True)
os.environ.setdefault("DINTUBE_DATOS", DATOS)
os.environ.setdefault("DINTUBE_AUDIOS", AUDIOS)
os.environ.setdefault("DINTUBE_WEB", os.path.join(BASE, "web"))

# ffmpeg, ffprobe y deno van empaquetados en bin/: yt-dlp los busca en el PATH.
# Se sacan del PATH las carpetas que son enlaces (p. ej. C:\Program Files\nodejs de nvm):
# Windows no deja que el exe las recorra y yt-dlp falla con "WinError 448".
def carpeta_segura(ruta):
    try:
        return bool(ruta) and not os.path.islink(ruta) and not getattr(os.path, "isjunction", lambda _: False)(ruta)
    except OSError:
        return False


BIN = os.path.join(BASE, "bin")
os.environ["PATH"] = os.pathsep.join([BIN] + [r for r in os.environ.get("PATH", "").split(os.pathsep) if carpeta_segura(r)])
os.environ.setdefault("DINTUBE_DENO", os.path.join(BIN, "deno.exe"))

PUERTO = int(os.environ.get("DINTUBE_PUERTO", 8000))
URL = f"http://127.0.0.1:{PUERTO}"  # 127.0.0.1 (no localhost) para que "Apagar DinTube" funcione


def puerto_abierto():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", PUERTO)) == 0


def levantar_servidor():
    sys.path.insert(0, os.path.join(BASE, "src"))
    import servidor  # noqa: E402  (después de configurar las variables)

    threading.Thread(target=servidor.revisar_iptv, daemon=True).start()
    servidor.app.run(host="0.0.0.0", port=PUERTO, threaded=True, use_reloader=False)


# --- Actualizaciones: la Action de GitHub publica cada versión en este repo (público) ---
REPO_RELEASES = "cristianeze16/dintube-desktop"


def como_tupla(version):
    # "v3.0.2" -> (3, 0, 2), para comparar bien: 3.0.10 es más nueva que 3.0.9
    return tuple(int(n) for n in version.strip().lstrip("v").split("."))


def version_local():
    try:
        with open(os.path.join(BASE, "version.txt"), encoding="utf-8") as f:
            return como_tupla(f.read())
    except (OSError, ValueError):
        return (0,)


def buscar_actualizacion(ventana):
    if not getattr(sys, "frozen", False):
        return  # corriendo desde el código fuente: nada que actualizar
    time.sleep(3)  # que primero cargue la app
    import requests
    try:
        r = requests.get(f"https://api.github.com/repos/{REPO_RELEASES}/releases/latest", timeout=10)
        r.raise_for_status()
        release = r.json()
        etiqueta = release["tag_name"]
        # Las etiquetas viejas eran un número solo (v1, v2, y v4 fue el puente a 3.0.0): esas no se comparan
        if "." not in etiqueta:
            return
        nueva = etiqueta.lstrip("v")
        instalador = next(a for a in release["assets"] if a["name"].lower().endswith(".exe"))
        if como_tupla(nueva) <= version_local():
            return
    except Exception:
        return  # sin internet, sin releases, etc.: se prueba la próxima vez
    if not ventana.create_confirmation_dialog(
            "Actualización de DinTube",
            f"Hay una versión nueva de DinTube (versión {nueva}).\n\n"
            "¿Instalarla ahora? DinTube se cierra un momento y vuelve a abrirse solo."):
        return

    destino = os.path.join(tempfile.gettempdir(), f"DinTube-Setup-{nueva}.exe")
    try:
        with requests.get(instalador["browser_download_url"], stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length") or instalador.get("size") or 0)
            bajado = 0
            with open(destino + ".part", "wb") as f:
                for parte in r.iter_content(1 << 20):
                    f.write(parte)
                    bajado += len(parte)
                    if total:
                        ventana.set_title(f"DinTube — bajando actualización {bajado * 100 // total}%")
        os.replace(destino + ".part", destino)
    except Exception as e:
        ventana.set_title("DinTube")
        ventana.create_confirmation_dialog("DinTube", f"No se pudo bajar la actualización:\n{e}")
        return

    # El instalador (silencioso, con barra de progreso) reemplaza la app y la vuelve a abrir
    subprocess.Popen([destino, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"],
                     creationflags=getattr(subprocess, "DETACHED_PROCESS", 0), close_fds=True)
    os._exit(0)


def main():
    import webview

    ya_habia_uno = puerto_abierto()  # otra ventana de DinTube (o DinTube Web.bat) ya está sirviendo
    if not ya_habia_uno:
        threading.Thread(target=levantar_servidor, daemon=True).start()
        for _ in range(150):  # hasta 15 s
            if puerto_abierto():
                break
            time.sleep(0.1)

    ventana = webview.create_window("DinTube", URL, width=1280, height=800, min_size=(400, 500),
                          background_color="#0f0f0f", text_select=True)
    webview.start(buscar_actualizacion, (ventana,), private_mode=False, storage_path=os.path.join(DATOS, "webview"))
    # Se cerró la ventana: si el servidor es nuestro, se apaga con ella
    os._exit(0)


if __name__ == "__main__":
    main()
