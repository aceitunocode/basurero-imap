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

    # Conexión
    def conectar(self):
        if self.use_ssl:
            self.mail = imaplib.IMAP4_SSL(self.servidor)
        else:
            self.mail = imaplib.IMAP4(self.servidor)

        self.mail.login(self.usuario, self.clave)

        status, _ = self.mail.select(self.carpeta)
        if status != "OK":
            raise RuntimeError(f"No se pudo seleccionar la carpeta {self.carpeta}")

    def cerrar(self):
        if self.mail:
            self.mail.expunge()
            self.mail.close()
            self.mail.logout()
            self.mail = None

    # Utilidades
    @staticmethod
    def _decodificar_asunto(mensaje):
        subject = decode_header(mensaje.get("Subject", ""))
        return "".join(
            part.decode(charset or "utf-8") if isinstance(part, bytes) else part
            for part, charset in subject
        )

    def _obtener_mensaje(self, msg_id):
        status, msg_data = self.mail.fetch(msg_id, "(BODY.PEEK[])")
        if status != "OK":
            return None

        raw_email = msg_data[0][1]
        return email.message_from_bytes(raw_email)

    def _mover_a_papelera(self, msg_id, asunto=None):
        if not asunto:
            asunto = self._decodificar_asunto(self._obtener_mensaje(msg_id))

        print(f"Moviendo a la papelera: {asunto}")
        self.mail.copy(msg_id, self.papelera)
        self.mail.store(msg_id, "+FLAGS", "\\Deleted")

    # Funciones públicas
    def borrar_por_asuntos(self, patrones: list[re.Pattern]):
        status, data = self.mail.search(None, "ALL")
        if status != "OK":
            print("No se pudo buscar correos")
            return

        for msg_id in data[0].split():
            mensaje = self._obtener_mensaje(msg_id)
            if not mensaje:
                continue

            asunto = self._decodificar_asunto(mensaje)

            for patron in patrones:
                if patron.search(asunto):
                    self._mover_a_papelera(msg_id, asunto)
                    break

    def borrar_por_remitente(self, remitente: str):
        status, data = self.mail.search(None, "FROM", f'"{remitente}"')
        if status != "OK":
            print("No se pudo buscar correos")
            return

        for msg_id in data[0].split():
            mensaje = self._obtener_mensaje(msg_id)
            asunto = self._decodificar_asunto(mensaje) if mensaje else None
            self._mover_a_papelera(msg_id, asunto)


if __name__ == "__main__":
    import json

    with open("config.json") as f:
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
