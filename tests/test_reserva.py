from . import BaseTestClass
from bs4 import BeautifulSoup

class TestReserva(BaseTestClass):
    def test_crear_reserva(self):
        libro_id = 1 
        user_id = 1 

        self.login('james@gmail.com', '123456')

        # Guardamos los datos del libro para comparar las copias antes y despues de crear la reserva
        libro1 = self.db.select("SELECT * FROM Book WHERE id=?", (libro_id,))

        response = self.client.post(f'/add_booking?book_id={ libro_id }&user_id={ user_id }', follow_redirects=True)
        self.assertEqual(200, response.status_code)

        # El numero de copias ha disminuido después de crear la reserva
        libro2 = self.db.select("SELECT * FROM Book WHERE id=?", (libro_id,))
        self.assertEqual(libro1[0][5], libro2[0][5]+1)

        page = BeautifulSoup(response.data, 'html.parser')

        reserva_guardada = self.db.select("SELECT * FROM Reserva WHERE idLibro=? AND idUsuario=?", (libro_id, user_id))
        self.assertEqual(reserva_guardada[0][2], libro_id)
