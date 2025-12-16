# Basurero IMAP
Un simple script que revisa el correo de un buzón IMAP y manda a la papelera los emails que cumplan unos criterios definidos por el usuario.
## ¿Por qué he hecho esto?
Me he hartado de borrar a mano los correos de `BUZONinfoUGR` que no me interesan y me he dado cuenta de que me puedo quitar mucho trabajo filtrando por palabras clave y remitentes.
## Configuración
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
El filtrado por remitente elimina todos los correos que vengan de las direcciones de correo especificadas.
```json
"remitentes": [
    "email1@ejemplo.com",
    "email2@ejemplo.com",
    "email3@ejemplo.com"
]
```

El filtrado por asunto es similar al filtrado por remitente, pero los elementos en la lista son objetos, no cadenas de texto. Estos objetos tendrán 2 propiedades:
- `filtro`: expresión regular de python que se busca en el asunto (puede ser una simple palabra clave, por ejemplo "sorteo").
- `ignorar-mayusculas-minusculas`: variable booleana que, como su nombre indica, sirve para configurar si la busqueda ignora la diferencia entre mayúsculas y minúsculas.
```json
"asuntos": [
    {"filtro": "sorteo", "ignorar-mayusculas-minusculas": true}
]
```
> Este filtro elimina todos los correos que tengan en su asunto `sorteo`, `SORTEO`, `SoRtEo`, etc.
