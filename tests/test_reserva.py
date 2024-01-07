from . import BaseTestClass
from bs4 import BeautifulSoup

class TestReserva(BaseTestClass):
    def test_crear_reserva(self):
        libro_id = 1 
        user_id = 1 

        self.login('james@gmail.com', '123456')

        response = self.client.post(f'/add_booking?book_id={ libro_id }&user_id={ user_id }', follow_redirects=True)
        self.assertEqual(200, response.status_code)

        page = BeautifulSoup(response.data, 'html.parser')

        reserva_guardada = self.db.select("SELECT * FROM Reserva WHERE idLibro=? AND idUsuario=?", (libro_id, user_id))
        #print(reserva_guardada)
        self.assertEqual(reserva_guardada[0][2], libro_id)