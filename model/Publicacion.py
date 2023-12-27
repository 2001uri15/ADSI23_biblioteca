from .Connection import Connection

db = Connection()

class Publicacion:
    def __init__(self, id, idTema, fecha, idUsuario, texto):
        if id is not None and idTema is not None and fecha is not None and idUsuario is not None and texto is not None:
            self.id = id
            self.idTema = idTema
            self.fecha = fecha
            self.idUsuario = idUsuario
            self.texto = texto
        else:
            self.id = None
            self.idTema = None
            self.fecha = None
            self.idUsuario = None
            self.texto = None

    def getId(self):
        return f"{self.id}"
