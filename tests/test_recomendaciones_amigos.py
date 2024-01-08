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

        #Comprobar si se redirige a el login
        res_login = self.client.get('/login')
        self.assertEqual(200, res_login.status_code)
        page = BeautifulSoup(res_login.data, features="html.parser")

    # CodPrueba: 2  -> Sin amigos y sin ningun libro leido, por lo que no tengo recomendaciones
    def test_sin_amigos_mensaje(self):
        # Iniciamos sesión
        res = self.login('2001uri15@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
        
        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que el mensaje de "Sin recomendaciones" esté presente en la página
        mensaje_sin_amigos = page.find('p', {'class': 'mensaje-sin-amigos'})
        self.assertIsNotNone(mensaje_sin_amigos)
        self.assertEqual('No tienes ninguna recomendación de amigos', mensaje_sin_amigos.get_text())

    # CodPrueba: 3  -> Tengo un amigo y mi amigo tiene 2 amigos que no son mis amigos
    def test_un_amigo_sin_sus_amigos(self):
        # Iniciamos sesión
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        #Preparo la base de datos
        self.db.delete("DELETE from Amigo")
        self.db.insert("Insert into Amigo VALUES (1, 2), (2, 4), (2, 7)")

        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que la tabla de amigos de amigos está presente en la página
        tabla_amigos_de_amigos = page.find('table', {'class': 'tabla-amigos-de-amigos'})
        self.assertIsNotNone(tabla_amigos_de_amigos)

        # Cuantas filas de recomendaciones hay 
        cantidad_filas_amigos_de_amigos = len(tabla_amigos_de_amigos.find_all('tr'))

        # Verificar que hay 2 recomendaciones
        self.assertEqual(3, cantidad_filas_amigos_de_amigos)  # Se suma 1 por la cabezera de la tabla

    # CodPrueba: 4  -> No tengo dos amigos y uno de ellos tiene dos amigos y yo soy amigo de uno de ellos
    def test_dos_amigos_un_amigo_de_amigo(self):
        # Iniciamos sesión
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.delete("DELETE from Amigo")
        self.db.insert("Insert into Amigo VALUES (1, 2), (2, 4), (2, 7), (1, 4)")

        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que la tabla de amigos de amigos está presente en la página
        tabla_amigos_de_amigos = page.find('table', {'class': 'tabla-amigos-de-amigos'})
        self.assertIsNotNone(tabla_amigos_de_amigos)

        # Cuantas filas de recomendaciones hay 
        cantidad_filas_amigos_de_amigos = len(tabla_amigos_de_amigos.find_all('tr'))

        # Verificar que hay 1 recomendaciones
        self.assertEqual(2, cantidad_filas_amigos_de_amigos)  # Se suma 1 por la cabezera de la tabla
    
    # CodPrueba: 5  -> No tengo amigos y he leido un libro. Ese libro no lo ha leido nadie más
    def test_ningun_amigo_leido_un_libro_que_nadie_lee(self):
        # Iniciamos sesión
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.delete("DELETE from Amigo")
        self.db.delete("DELETE from Reserva")
        self.db.insert("INSERT into Reserva (idUsuario, idLibro, fechaReserva, fechaDevolucion) VALUES (1, 1, '2024-01-08 21:14:39', '2024-03-08 21:14:39')")


        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que el mensaje de "Sin amigos" esté presente en la página
        mensaje_sin_amigos = page.find('p', {'class': 'mensaje-sin-amigos'})
        self.assertIsNotNone(mensaje_sin_amigos)
        self.assertEqual('No tienes ninguna recomendación de amigos', mensaje_sin_amigos.get_text())

    # CodPrueba: 6  -> No tengo amigos y he leido un libro que otra persona ha leido
    def test_ningun_amigo_leido_un_libro(self):
        # Iniciamos sesión
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.delete("DELETE from Amigo")
        self.db.delete("DELETE from Reserva")
        self.db.insert("INSERT into Reserva (idUsuario, idLibro, fechaReserva, fechaDevolucion) VALUES (1, 1, '2024-01-08 21:14:39', '2024-03-08 21:14:39'), (1, 3, '2024-01-09 21:14:39', '2024-03-09 21:14:39')")


        # Acceder al perfil del usuario y obtener la respuesta
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que la tabla de amigos de amigos está presente en la página
        tabla_amigos_de_amigos = page.find('table', {'class': 'tabla-amigos-de-amigos'})
        self.assertIsNotNone(tabla_amigos_de_amigos)

        # Cuantas filas de recomendaciones hay 
        cantidad_filas_amigos_de_amigos = len(tabla_amigos_de_amigos.find_all('tr'))

        # Verificar que hay 1 recomendaciones
        self.assertEqual(2, cantidad_filas_amigos_de_amigos)  # Se suma 1 por la cabezera de la tabla

    