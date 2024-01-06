from . import BaseTestClass
from bs4 import BeautifulSoup

class TestRecomendacionesDeAmigo(BaseTestClass):

    # CodPrueba: 1  -> El usuario no está identificado en el sistema
    def test_acceso_recomendaciones_usuario_no_identificado(self):
        # Cerrar sesión para asegurarse de que el usuario no esté identificado
        res_logout = self.client.get('/logout')
        self.assertEqual(302, res_logout.status_code)
        self.assertEqual('/', res_logout.location)

        # Intentar acceder a la página de recomendaciones
        res_recomendaciones = self.client.get('/perfil') 
        self.assertEqual(302, res_recomendaciones.status_code)
        self.assertEqual('/login', res_recomendaciones.location)


        res_login = self.client.get('/login')
        self.assertEqual(200, res_login.status_code)
        page = BeautifulSoup(res_login.data, features="html.parser")

    # CodPrueba: 2  -> Sin amigos
    def test_sin_amigos_mensaje(self):
        # Iniciamos sesión
        res = self.login('2001uri15@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        #Borrar los amigos y los libros leidos
        self.db.select("DELETE FROM Amigo")
        self.db.select("DELETE FROM Reserva")

        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que el mensaje de "Sin amigos" esté presente en la página
        mensaje_sin_amigos = page.find('p', {'class': 'mensaje-sin-amigos'})
        self.assertIsNotNone(mensaje_sin_amigos)
        self.assertEqual('No tienes ninguna recomendación de amigos', mensaje_sin_amigos.get_text())

    # CodPrueba: 3  -> No tengo ningun amigo de mi amigo añadido
    def test_sin_amigos_de_amigos(self):
        # Iniciamos sesión
        res = self.login('2001uri15@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        #Borrar los amigos y los libros leidos
        self.db.select("DELETE FROM Amigo")
        self.db.select("DELETE FROM Reserva")

        #Metemos que tenemos un amigo y que ese amigo tiene dos amigos
        self.db.select("INSERT INTO Amigo VALUES (5, 1)")
        self.db.select("INSERT INTO Amigo VALUES (1, 4)")
        self.db.select("INSERT INTO Amigo VALUES (1, 3)")

        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que la tabla de amigos de amigos está presente en la página
        tabla_amigos_de_amigos = page.find('table', {'class': 'tabla-amigos-de-amigos'})
        self.assertIsNotNone(tabla_amigos_de_amigos)

        # Obtener la cantidad de filas en la tabla de amigos de amigos
        cantidad_filas_amigos_de_amigos = len(tabla_amigos_de_amigos.find_all('tr'))

        # Verificar que se espera una tabla vacía ya que el usuario no tiene amigos de amigos
        self.assertEqual(1, cantidad_filas_amigos_de_amigos)  # 1 para la fila de encabezado