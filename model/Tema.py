from .Connection import Connection

db = Connection()

class Tema:
    def __init__(self, id, nombre, creado):
        if id is not None and nombre is not None and creado is not None:
            self.id = id
            self._nombre = nombre
            self.creado = creado
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