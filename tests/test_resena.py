from . import BaseTestClass
from bs4 import BeautifulSoup

class TestResena(BaseTestClass):
    def test_crear_resena(self):
        libro_id = 1  # Ajusta según tu aplicación
        usuario_id = 1 # Ajusta según tu aplicación
        puntuacion = 5
        comentario = "Excelente libro"

        # Iniciar sesión (si es necesario)
        self.login('james@gmail.com', '123456')

        # Simular una solicitud POST para escribir la reseña
        data = {
            'comentario': comentario,
            'puntuacion': 5
        }
        response = self.client.post(f'/escribir_resena/{libro_id}', data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)

        # Parsear la respuesta HTML con BeautifulSoup
        page = BeautifulSoup(response.data, 'html.parser')

        resena_guardada = self.db.select("SELECT comentario FROM Resena WHERE idLibro=? AND idUsuario=? AND puntuacion=?", (libro_id, usuario_id, puntuacion))
       # self.assertTrue(resena_guardada, "La reseña no se ha guardado en la base de datos.")
        self.assertEqual(resena_guardada[0][0], '')

       


