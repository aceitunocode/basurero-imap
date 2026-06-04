import imaplib
import email
import re
from email.header import decode_header


class Limpiador:
    def __init__(
        self,
        servidor,
        usuario,
        clave,
        carpeta,
        papelera,
        use_ssl=True,
    ):
        self.servidor = servidor
        self.usuario = usuario
        self.clave = clave
        self.carpeta = carpeta
        self.papelera = papelera
        self.use_ssl = use_ssl
        self.mail = None
        #self.cache = {}

    # Conexión
    def conectar(self):
        """Crea la conexión con el servidor de correo"""
        try:
            if self.use_ssl:
                self.mail = imaplib.IMAP4_SSL(self.servidor)
            else:
                self.mail = imaplib.IMAP4(self.servidor)

            self.mail.login(self.usuario, self.clave)
        except Exception as e:
            raise RuntimeError(f"No se pudo conectar al servidor. Motivo: {e}")

        status, _ = self.mail.select(self.carpeta)
        if status != "OK":
            raise RuntimeError(f"No se pudo seleccionar la carpeta {self.carpeta}")

    def cerrar(self):
        """Manda las órdenes de eliminación de correo y cierra sesión.

        AVISO: Si la conexión se cierra sin usar esta función, el inicio de sesión por IMAP quedará bloqueado hasta que el servidor cierre la sesión por inactividad"""
        if self.mail:
            self.mail.expunge()
            self.mail.close()
            self.mail.logout()
            self.mail = None

    # Utilidades
    def _mover_a_papelera(self, msg_id, asunto=None):
        if not asunto:
            asunto = self._decodificar_asunto(self._obtener_mensaje(msg_id, "HEADER"))

        print(f"Moviendo a la papelera: {asunto}")

        #if msg_id in self.cache.keys():
        #    del self.cache[msg_id]

        self.mail.copy(msg_id, self.papelera)
        self.mail.store(msg_id, "+FLAGS", "\\Deleted")

    def _obtener_mensaje(self, msg_id, parte = ""):
        #if msg_id in self.cache.keys():
        #    msg_data = self.cache[msg_id]
        #else:

        status, msg_data = self.mail.fetch(msg_id, f"(BODY.PEEK[{parte}])")
        # Se usa parte = "TEXT" para el cuerpo y parte = "HEADER" para el remitente y el asunto.
        # Esto evita la descarga de archivos adjuntos que no se analizan.
        if status != "OK":
            return None

        #    self.cache[msg_id] = msg_data

        raw_email = msg_data[0][1]
        return email.message_from_bytes(raw_email)

    ## Decodificadores
    @staticmethod
    def _decodificar_asunto(mensaje):
        subject = decode_header(mensaje.get("Subject", ""))

        partes = []

        for part, charset in subject:
            if isinstance(part, bytes):

                # Algunos correos usan este charset inválido
                if not charset or charset.lower() == "unknown-8bit":
                    charset = "utf-8"

                try:
                    partes.append(part.decode(charset, errors="replace"))
                except LookupError:
                    # Charset realmente desconocido
                    partes.append(part.decode("utf-8", errors="replace"))
            else:
                partes.append(part)

        return "".join(partes)

    @staticmethod
    def _decodificar_contenido(mensaje):
        if mensaje.is_multipart():
            fragmentos = []
            for parte in mensaje.walk():
                content_disposition = str(parte.get("Content-Disposition"))

                # Ignorar adjuntos
                if "attachment" in content_disposition:
                    continue

                charset = parte.get_content_charset() or "utf-8"
                try:
                    fragmentos.append(parte.get_payload(decode=True).decode(
                        charset, errors="replace"
                    ))
                except:
                    continue
            contenido = "\n".join(fragmentos)
        else:
            charset = mensaje.get_content_charset() or "utf-8"
            contenido = mensaje.get_payload(decode=True).decode(
                charset, errors="replace"
            )

        return contenido

    # Funciones públicas
    def borrar_por_asuntos(self, patrones: list[re.Pattern]):
        """Elimina todos los correos que cumplan al menos una de las expresiones regulares en la lista"""
        status, data = self.mail.search(None, "UNDELETED")
        # Como normalmente se ejecuta el borrado por asuntos después del borrado por remitente, se usa
        # "UNDELETED" en vez de "ALL" para no volver a pasar por correos que ya hayan sido marcados para eliminar
        if status != "OK":
            print("No se pudo buscar correos")
            return

        for msg_id in data[0].split():
            mensaje = self._obtener_mensaje(msg_id, "HEADER")
            if not mensaje:
                continue

            asunto = self._decodificar_asunto(mensaje)

            for patron in patrones:
                if patron.search(asunto):
                    self._mover_a_papelera(msg_id, asunto)
                    break

    def borrar_por_remitente(self, remitente: str):
        status, data = self.mail.search(None, "FROM", f'"{remitente}"')
        # Debido a como funciona IMAP, solo se buscan correos que existan dentro de la carpeta seleccionada (self.carpeta)
        if status != "OK":
            print("No se pudo buscar correos")
            return

        for msg_id in data[0].split():
            mensaje = self._obtener_mensaje(msg_id, "HEADER")
            asunto = self._decodificar_asunto(mensaje) if mensaje else None
            self._mover_a_papelera(msg_id, asunto)


if __name__ == "__main__":
    import json

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    limpiador = Limpiador(
        servidor=config["conexion"]["servidor"],
        use_ssl=config["conexion"]["ssl"],
        usuario=config["conexion"]["usuario"],
        clave=config["conexion"]["clave"],
        carpeta=config["conexion"]["carpeta_entrada"],
        papelera=config["conexion"]["papelera"]
    )

    try:
        limpiador.conectar()
    except Exception as e:
        print(e)
    else:
        try:

            print("Borrando por remitente")
            for remitente in config["filtros"]["remitentes"]:
                limpiador.borrar_por_remitente(remitente)

            print("Borrando por asunto")
            asuntos = [] # Optimización disponible: prealocación
            for asunto in config["filtros"]["asuntos"]:
                if asunto["ignorar-mayusculas-minusculas"]:
                    asuntos.append(
                        re.compile(asunto["filtro"], re.IGNORECASE)
                    )
                else:
                    asuntos.append(
                        re.compile(asunto["filtro"])
                    )
            limpiador.borrar_por_asuntos(asuntos)

        finally:
            limpiador.cerrar()
