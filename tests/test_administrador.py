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
        # Login como administrador
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        nuevo_usu = {
            'name': 'Nombre',
            'apellidos': 'Apellido',
            'birthdate': '2001-01-01',
            'email': 'p@gmail.com',   # este email ya está registrado
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

    # P5    Id proporcionado es de un usuario existente
    def test_borrar_usu_1(self):
        # Login como administrador
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        id_usu_a_borrar = 3 # Usuario de prueba ( 3 - Juan Ejemplo - ejemplo@gmail.com )
        res_borrar_user = self.client.post('/admin/delete_user_confirm', data={'user_id': id_usu_a_borrar}, follow_redirects=True)

        # Comprobar que se ha eliminado correctamente
        self.assertEqual(200, res_borrar_user.status_code)
        soup = BeautifulSoup(res_borrar_user.data, features="html.parser")

        # Comprobar si el usuario con el ID que hemos borrado está presente en la lista
        deleted_user_info = soup.find('li', {'class': 'list-group-item'}, string=f'{id_usu_a_borrar}')
        self.assertIsNone(deleted_user_info, f"User with ID {id_usu_a_borrar} still found in the list")

        # Intentamos hacer login en el perfil que acabamos de crear (y no nos debería dejar)
        res3 = self.client.get('/logout')
        res = self.login('ejemplo@gmail.com', '123456') # Credenciales correctas del usuario que acabamos de borrar
        self.assertEqual(302, res.status_code) 
        self.assertEqual('/login', res.location)

        
        
    # P5a   ID proporcionado es de un usuario no registrado
    def test_borrar_usu_2(self):
        # Login como administrador
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        id_usu_a_borrar = 999 # Usuario no registrado
        res_borrar_user = self.client.post('/admin/delete_user_confirm', data={'user_id': id_usu_a_borrar}, follow_redirects=True)

        # Comprobar que se ha eliminado correctamente
        self.assertEqual(200, res_borrar_user.status_code)
        soup = BeautifulSoup(res_borrar_user.data, features="html.parser")

        # Buscar el mensaje que indica que el ID no existe
        error_message = soup.find('div', {'class': 'alert alert-danger'})
        self.assertIsNotNone(error_message, "Error message not found in the response")
        expected_error_message = "El usuario con el ID proporcionado no existe."
        self.assertIn(expected_error_message, error_message.get_text())

    # P5b   Borrar usuario desde lista de usuarios
    def test_borrar_usu_3(self):
        # Log in as an administrator
        res_login = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res_login.status_code)
        self.assertEqual('/', res_login.location)

        # Assume you are on the list_users page
        res_list_users = self.client.get('/admin/list_users')
        self.assertEqual(200, res_list_users.status_code)

        # Assume you are trying to delete a user with ID 1 (replace with an existing user ID)
        usuario_id_a_borrar = 7

        # Send a POST request to delete the user by clicking the delete button
        res_delete_user = self.client.post(f'/admin/delete_user/{usuario_id_a_borrar}', follow_redirects=True)

        # Check if the user is no longer in the list
        self.assertEqual(200, res_delete_user.status_code)
        soup = BeautifulSoup(res_delete_user.data, features="html.parser")

        # Check if the user with the specified ID is not present in the list anymore
        deleted_user_info = soup.find('li', {'class': 'list-group-item'}, string=f'{usuario_id_a_borrar}')
        self.assertIsNone(deleted_user_info, f"User with ID {usuario_id_a_borrar} still found in the list")
