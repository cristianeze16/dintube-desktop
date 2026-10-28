"""Copia DinTube (la carpeta hermana ../dintube) a build/src y parchea las rutas para el exe.

El proyecto original no se toca. Uso: python preparar.py [ruta-a-dintube]
"""
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "dintube"))
DESTINO = os.path.join(AQUI, "build", "src")

# Las 3 líneas de servidor.py que fijan dónde están los datos, la web y los audios.
# Con el parche siguen funcionando igual si las variables no están definidas.
REEMPLAZOS = {
    'CARPETA = os.path.dirname(os.path.abspath(__file__))':
        'CARPETA = os.environ.get("DINTUBE_DATOS") or os.path.dirname(os.path.abspath(__file__))',
    'WEB = os.path.join(CARPETA, "web")':
        'WEB = os.environ.get("DINTUBE_WEB") or os.path.join(CARPETA, "web")',
    'AUDIOS = os.path.join(CARPETA, "audios")':
        'AUDIOS = os.environ.get("DINTUBE_AUDIOS") or os.path.join(CARPETA, "audios")',
}


def main():
    if not os.path.isfile(os.path.join(ORIGEN, "servidor.py")):
        sys.exit(f"No encuentro servidor.py en {ORIGEN}")
    shutil.rmtree(DESTINO, ignore_errors=True)
    os.makedirs(DESTINO, exist_ok=True)
    for archivo in ("servidor.py", "descargar.py"):
        shutil.copy2(os.path.join(ORIGEN, archivo), DESTINO)
    shutil.copytree(os.path.join(ORIGEN, "web"), os.path.join(AQUI, "build", "web"), dirs_exist_ok=True)
    shutil.copy2(os.path.join(ORIGEN, "requirements.txt"), os.path.join(AQUI, "build", "requirements-dintube.txt"))

    ruta = os.path.join(DESTINO, "servidor.py")
    with open(ruta, encoding="utf-8") as f:
        codigo = f.read()
    for viejo, nuevo in REEMPLAZOS.items():
        if codigo.count(viejo) != 1:
            sys.exit(f"servidor.py cambió y no encuentro esta línea para parchear:\n  {viejo}")
        codigo = codigo.replace(viejo, nuevo)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(codigo)

    # En la app usamos solo el deno empaquetado: el node del sistema puede ser un enlace (nvm) que
    # Windows no deja seguir desde el exe ("WinError 448 ... punto de montaje no confiable")
    ruta = os.path.join(DESTINO, "descargar.py")
    with open(ruta, encoding="utf-8") as f:
        codigo = f.read()
    viejo = 'JS_RUNTIMES = {"deno": {}, "node": {}}'
    if codigo.count(viejo) != 1:
        sys.exit(f"descargar.py cambió y no encuentro esta línea para parchear:\n  {viejo}")
    codigo = codigo.replace(viejo, 'import os\n'
                            'JS_RUNTIMES = ({"deno": {"path": os.environ["DINTUBE_DENO"]}} if os.environ.get("DINTUBE_DENO")\n'
                            '               else {"deno": {}, "node": {}})')
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(codigo)

    # Número de versión (lo pone la Action de GitHub; en builds locales es 0)
    with open(os.path.join(AQUI, "build", "version.txt"), "w", encoding="utf-8") as f:
        f.write(os.environ.get("DINTUBE_VERSION", "0"))

    # Ícono .ico para el exe y el instalador, a partir del de la web
    from PIL import Image
    Image.open(os.path.join(ORIGEN, "web", "icono-512.png")).save(
        os.path.join(AQUI, "build", "dintube.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Listo: copiado desde {ORIGEN} y parcheado en build/")


if __name__ == "__main__":
    main()
