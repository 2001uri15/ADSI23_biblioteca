from .Connection import Connection

db = Connection()

class Resena:
    def __init__(self, id, idUsuario, idLibro, puntuacion, comment):
        if id is not None and nombreLibro is not None and nomUsu is not None:
            self.id = id
            self.idUsuario = idUsuario
            self.idLibro = idLibro
            self.puntuacion = puntuacion
            self.comentario = comment
        else:
            self.id = None

    @property
    def nombre(self):
        return self._nombre
    
   # @nombre.setter
    #def nombre(self, value):
     #   self._nombre = value  
        
    #def getNombre(self):
     #   return f"{self.nombre}"