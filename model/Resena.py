from .Connection import Connection

db = Connection()

class Tema:
    def __init__(self, id, nombreLibro, editorial, autor, nomUsu, puntuacion, comment):
        if id is not None and nombreLibro is not None and nomUsu is not None:
            self.id = id
            self.nombreLib = nombreLibro
            self.editorial = editorial
            self.author = autor
            self.nombreUsuario = nomUsu
            self.puntuacion = puntuacion
            self.comentario = comment
        else:
            self.id = None
            self._nombre = None
            self.creado = None

    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, value):
        self._nombre = value  
        
    def getNombre(self):
        return f"{self.nombre}"