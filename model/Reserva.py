from .Connection import Connection

db = Connection()

class Reserva:
    def __init__(self, id, idUsuario, idLibro, fechaReserva, fechaDevolucion):
        if id is not None and idLibro is not None and idUsuario is not None:
            self.id = id
            self.idUsuario = idUsuario
            self.idLibro = idLibro
            self.fechaReserva = fechaReserva
            self.fechaDevolucion = fechaDevolucion
        else:
            self.id = None