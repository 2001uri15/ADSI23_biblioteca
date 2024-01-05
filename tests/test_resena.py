from . import BaseTestClass
from bs4 import BeautifulSoup

class TestResena(BaseTestClass):
    def test_crear_resena(self):
        libro_id = 1  # Ajusta según tu aplicación
        #usuario_id = 2  # Ajusta según tu aplicación
        puntuacion = 5
        comentario = "Excelente libro"

        # Iniciar sesión (si es necesario)
        self.login('james@gmail.com', '123456')

        # Simular una solicitud POST para escribir la reseña
        data = {
            'mensaje': comentario,
            'puntuacion': 5
        }
        response = self.client.post(f'/escribir_resena/{libro_id}', data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)

        # Parsear la respuesta HTML con BeautifulSoup
        page = BeautifulSoup(response.data, 'html.parser')

        # Verificar que la reseña se ha publicado correctamente
        comentario_en_pagina = page.find('p', {'id': 'comentario'}).get_text()
        self.assertEqual(comentario, comentario_en_pagina)

       


