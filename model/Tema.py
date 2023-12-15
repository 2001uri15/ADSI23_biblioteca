from .Connection import Connection

db = Connection()

class Tema:
    def __init__(self, id, nombre, creado):
        self.id = id
        self._nombre = nombre  
        self.creado = creado
    
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, value):
        self._nombre = value  
        
    def __str__(self):
        return f"{self.nombre}"