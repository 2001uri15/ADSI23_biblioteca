from . import BaseTestClass
from flask import url_for
from bs4 import BeautifulSoup

class TestResena(BaseTestClass):
    def test_user_no_identificado(self):
        with self.app.app_context():
            # Configurar SERVER_NAME, APPLICATION_ROOT y PREFERRED_URL_SCHEME si es necesario
            self.app.config['SERVER_NAME'] = 'localhost:5000'  # Reemplaza con el nombre de tu servidor
            self.app.config['APPLICATION_ROOT'] = '/'
            self.app.config['PREFERRED_URL_SCHEME'] = 'http'

            # Realizar una solicitud GET al endpoint de ver libro sin usuario logueado
            response = self.client.get(url_for('ver_libro', book_id=1), follow_redirects=True)

            # Verificar que la respuesta sea un código de éxito (200) o la redirección correcta
            self.assertIn(response.status_code, [200, 302])

            # Si estás redirigiendo, verifica que la redirección sea al catálogo
            if response.status_code == 302:
                self.assertTrue(response.location.endswith(url_for('catalogue')))
