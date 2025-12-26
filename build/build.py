import shutil
import zipfile
import urllib.request
from pathlib import Path
import os

# Configuración

VERSION_PYTHON = "3.12.2"
PYTHON_URL = (
    f"https://www.python.org/ftp/python/{VERSION_PYTHON}/"
    f"python-{VERSION_PYTHON}-embed-amd64.zip"
)

VERSION = os.getenv("VERSION")
if VERSION:
    NOMBRE_ZIP = f"basurero-imap_{VERSION}.zip"
else:
    NOMBRE_ZIP = "basurero-imap.zip"


# Rutas

RAIZ = Path(__file__).resolve().parent.parent

CARPETA_APP = RAIZ
CARPETA_DIST = RAIZ / "dist"
CARPETA_BUILD = RAIZ / ".build"

# Limpiar carpetas
shutil.rmtree(CARPETA_BUILD, ignore_errors=True)
shutil.rmtree(CARPETA_DIST, ignore_errors=True)
CARPETA_BUILD.mkdir()
CARPETA_DIST.mkdir()

# Descargar python embebido
zip_python = CARPETA_BUILD / "python.zip"
print("Descargando Python embebido...")
urllib.request.urlretrieve(PYTHON_URL, zip_python)

python_dir = CARPETA_BUILD / "python"
python_dir.mkdir()

with zipfile.ZipFile(zip_python) as z:
    z.extractall(python_dir)
os.remove(CARPETA_BUILD / "python.zip")

# Configurar python embebido
pth_files = list(python_dir.glob("python*._pth"))
if not pth_files:
    raise RuntimeError("No se encontró archivo ._pth")

pth = pth_files[0]
texto = pth.read_text(encoding="utf-8")

if "import site" not in texto:
    texto += "\nimport site\n"
else:
    texto = texto.replace("#import site", "import site")

pth.write_text(texto, encoding="utf-8")

# Copiar archivos a build/
shutil.copy(CARPETA_APP / "main.py", CARPETA_BUILD / "main.py")
shutil.copy(CARPETA_APP / "build" / "basurero-imap.bat", CARPETA_BUILD / "basurero-imap.bat")

# Comprimir los archivos en build/
zip_final = CARPETA_DIST / NOMBRE_ZIP
print("Creando ZIP final...")

with zipfile.ZipFile(zip_final, "w", zipfile.ZIP_DEFLATED) as z:
    for archivo in CARPETA_BUILD.rglob("*"):
        z.write(archivo, archivo.relative_to(CARPETA_BUILD))

print("Build completado:", zip_final)
