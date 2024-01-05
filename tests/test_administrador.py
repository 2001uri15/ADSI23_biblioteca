from . import BaseTestClass
from bs4 import BeautifulSoup

class TestAdmin(BaseTestClass):

    # P1    Usuario: CORRECTO && Contraseña: CORRECTO
    def test_acceso_admin_1(self):
        # Hacemos login como administrador
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        # Comprobamos a ver si aparece el botón de menú administrador
        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertEqual('Menú Administrador', page.find('header').find('ul').find_all('li')[-3].get_text())
    
        # Comprobamos a ver si puede ir a la página de menú administrador (debería poder)
        res_admin = self.client.get('/admin')
        self.assertEqual(200, res_admin.status_code)


    # P2    Usuario: CORRECTO && Contraseña: INCORRECTO
    def test_acceso_admin_2(self):
        # Hacemos login como administrador
        res = self.login('p@gmail.com', '12435')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/login', res.location)

        # Comprobamos a ver si aparece el botón de menú administrador
        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertNotEqual('Menú Administrador', page.find('header').find('ul').find_all('li')[-3].get_text())

    # P2a   Usuario: INCORRECTO && Contraseña: CORRECTO
    def test_acceso_admin_3(self):
        # Hacemos login como administrador
        res = self.login('pog@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/login', res.location)

        # Comprobamos a ver si aparece el botón de menú administrador
        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertNotEqual('Menú Administrador', page.find('header').find('ul').find_all('li')[-3].get_text())

    # P2b   Usuario: INCORRECTO && Contraseña: INCORRECTO
    def test_acceso_admin_4(self):
        # Hacemos login como administrador
        res = self.login('pog@gmail.com', '12435')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/login', res.location)

        # Comprobamos a ver si aparece el botón de menú administrador
        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertNotEqual('Menú Administrador', page.find('header').find('ul').find_all('li')[-3].get_text())

    # PE    Credenciales correctas pero no es administrador
    def test_acceso_no_admin(self):
        # Hacemos login como administrador
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        # Comprobamos a ver si aparece el botón de menú administrador (no debería aparecer)
        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertNotEqual('Menú Administrador', page.find('header').find('ul').find_all('li')[-3].get_text())

        # Comprobamos a ver si puede ir a la página de menú administrador (no debería poder)
        res_admin = self.client.get('/admin')
        self.assertEqual(302, res_admin.status_code)
        self.assertEqual('/', res_admin.location)


    # P3    Cerrar Sesión como Administrador
    def test_cerrar_ses_admin(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
        res2 = self.client.get('/')
        self.assertIn('token', ''.join(res2.headers.values()))
        self.assertIn('time', ''.join(res2.headers.values()))
        res3 = self.client.get('/logout')
        self.assertEqual(302, res3.status_code)
        self.assertEqual('/', res3.location)
        res4 = self.client.get('/')
        self.assertNotIn('token', ''.join(res4.headers.values()))
        self.assertNotIn('time', ''.join(res4.headers.values()))

    # P4    El usu no existe previamente
    def test_crear_usu_1(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        nuevo_usu = {
            'name': 'Nombre',
            'apellidos': 'Apellido',
            'birthdate': '2001-01-01',
            'email': 'nuevousu@gmail.com',
            'password': '123456'
        }

        res_add_user = self.client.post('/admin/add_user', data=nuevo_usu, follow_redirects=True)
        
        # Comprobamos si el usuario se ha creado correctamente
        self.assertEqual(200, res_add_user.status_code)

        # Comprobamos si se puede hacer login con el nuevo usu
        res3 = self.client.get('/logout')

        res_log = self.login('nuevousu@gmail.com', '123456')
        self.assertEqual(302, res_log.status_code)
        self.assertEqual('/', res_log.location)

        res_log_2 = self.client.get('/')
        page = BeautifulSoup(res_log_2.data, features="html.parser")
        self.assertEqual('Nombre Apellido', page.find('header').find('ul').find_all('li')[-2].get_text())
    
    # P4a   El usu ya existe previamente
    def test_crear_usu_2(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        nuevo_usu = {
            'name': 'Nombre',
            'apellidos': 'Apellido',
            'birthdate': '2001-01-01',
            'email': 'ejemplo@gmail.com',   # este email ya está registrado
            'password': '123456'
        }

        res_add_user = self.client.post('/admin/add_user', data=nuevo_usu, follow_redirects=True)
        
        # Comprobamos si el usuario se ha creado correctamente
        self.assertEqual(200, res_add_user.status_code)
        soup = BeautifulSoup(res_add_user.data, features="html.parser")
        error_message = soup.find('div', {'class': 'alert alert-danger'})
        self.assertIsNotNone(error_message, "Error message not found in the response")

        # Check the specific error message content
        expected_error_message = "Ya existe un usuario con el mismo correo electrónico."
        self.assertIn(expected_error_message, error_message.get_text())


    #def borrar_usu(self):