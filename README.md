# Basurero IMAP
Un simple script que revisa el correo de un buzón IMAP y manda a la papelera los emails que cumplan unos criterios definidos por el usuario.
# ¿Por qué he hecho esto?
Me he hartado de borrar a mano los correos de `BUZONinfoUGR` que no me interesan y me he dado cuenta de que me puedo quitar mucho trabajo filtrando por palabras clave y remitentes.

# Instalación
### Python embebido (Windows)
Ve al [último lanzamiento](https://github.com/aceitunocode/basurero-imap/releases/latest) y descarga el zip llamado `basurero-imap_version.zip` y descomprímelo.

Para ejecutar el script, abre `basurero-imap.bat`.
> Esta instalación trae su propio python, por lo que no es necesario tenerlo instalado en el sistema.

### Git
La mayoría de las distribuciones de linux ofrecen en sus repositorios el paquete git `git`.

Puedes instalar la última versión estable con:
```bash
git clone https://github.com/aceitunocode/basurero-imap
cd basurero-imap
git checkout estable
```
Una vez hecho, se puede ejecutar con:
```bash
python3 main.py
```
Y para actualizar:
```bash
git pull --tags
git checkout estable
```
# Configuración
Toda la configuración del script va en el archivo `config.json`

Si quieres usar este script para filtrar basura de `BUZONinfoUGR`, rellena esta plantilla de configuración:
```json
{
    "conexion": {
        "servidor": "correo.ugr.es",
        "ssl": true,
        "usuario": "lo que va antes del @ en tu dirección de correo",
        "clave": "contraseña de tu correo",
        "carpeta_entrada": "INBOX.BUZONinfoUGR",
        "papelera": "INBOX.Trash"
    },
    "filtros":{
        "remitentes": [],
        "asuntos": []
    }
}
```
## Filtrado por remitente
El filtrado por remitente elimina todos los correos que vengan de las direcciones de correo especificadas.
```json
"remitentes": [
    "email1@ejemplo.com",
    "email2@ejemplo.com",
    "email3@ejemplo.com"
]
```
## Filtrado por asunto
En el filtrado por asunto los elementos en la lista son objetos, no cadenas de texto. Estos objetos tendrán 2 propiedades:
- `filtro`: expresión regular de python que se busca en el asunto (puede ser una simple palabra clave, por ejemplo "sorteo").
- `ignorar-mayusculas-minusculas`: variable booleana que, como su nombre indica, sirve para configurar si la busqueda ignora la diferencia entre mayúsculas y minúsculas.
```json
"asuntos": [
    {"filtro": "sorteo", "ignorar-mayusculas-minusculas": true}
]
```
> Este filtro elimina todos los correos que tengan en su asunto `sorteo`, `SORTEO`, `SoRtEo`, etc.
