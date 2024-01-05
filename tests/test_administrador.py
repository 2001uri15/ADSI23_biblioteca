from . import BaseTestClass
from bs4 import BeautifulSoup

class TestAdmin(BaseTestClass):
 
    
    ############################ ACCEDER A FUNCIONES DE ADMINISTRADOR ############################
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

    ############################ CREAR UN USUARIO ############################
    # P4    El usu no existe previamente
    def test_crear_usu_1(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        n_usu_antes = len(self.db.select("SELECT * FROM User"))
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
        n_usu_ahora = len(self.db.select("SELECT * FROM User"))
        self.assertEqual(n_usu_antes + 1, n_usu_ahora)

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

        n_usu_antes = len(self.db.select("SELECT * FROM User"))
        nuevo_usu = {
            'name': 'Nombre',
            'apellidos': 'Apellido',
            'birthdate': '2001-01-01',
            'email': 'p@gmail.com',   # este email ya está registrado
            'password': '123456'
        }

        res_add_user = self.client.post('/admin/add_user', data=nuevo_usu, follow_redirects=True)
        n_usu_ahora = len(self.db.select("SELECT * FROM User"))
        self.assertEqual(n_usu_antes, n_usu_ahora)
        
        # Comprobamos si el usuario se ha creado correctamente (no deberia)
        self.assertEqual(200, res_add_user.status_code)
        soup = BeautifulSoup(res_add_user.data, features="html.parser")
        error_message = soup.find('div', {'class': 'alert alert-danger'})
        self.assertIsNotNone(error_message, "Error message not found in the response")

        # Check the specific error message content
        expected_error_message = "Ya existe un usuario con el mismo correo electrónico."
        self.assertIn(expected_error_message, error_message.get_text())

    
    ############################ BORRAR UN USUARIO ############################
    # P5    Id proporcionado es de un usuario existente
    def test_borrar_usu_1(self):
        # Login como administrador
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        n_usu_antes = len(self.db.select("SELECT * FROM User"))
        #id_usu_a_borrar = 3 # Usuario de prueba ( 3 - Juan Ejemplo - ejemplo@gmail.com )
        id_usu_a_borrar = n_usu_antes - 1
        res_borrar_user = self.client.post('/admin/delete_user_confirm', data={'user_id': id_usu_a_borrar}, follow_redirects=True)

        # Comprobar que se ha eliminado correctamente
        self.assertEqual(200, res_borrar_user.status_code)
        soup = BeautifulSoup(res_borrar_user.data, features="html.parser")
        n_usu_ahora = len(self.db.select("SELECT * FROM User"))
        self.assertEqual(n_usu_antes, n_usu_ahora + 1)

        # Comprobar si el usuario con el ID que hemos borrado está presente en la lista
        deleted_user_info = soup.find('li', {'class': 'list-group-item'}, string=f'{id_usu_a_borrar}')
        self.assertIsNone(deleted_user_info, f"User with ID {id_usu_a_borrar} still found in the list")

        # Intentamos hacer login en el perfil que acabamos de crear (y no nos debería dejar)
        res3 = self.client.get('/logout')
        res = self.login('ejemplo@gmail.com', '123456') # Credenciales correctas del usuario que acabamos de borrar
        self.assertEqual(302, res.status_code) 

        
        
    # P5a   ID proporcionado es de un usuario no registrado
    def test_borrar_usu_2(self):
        # Login como administrador
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
        n_usu_antes = len(self.db.select("SELECT * FROM User"))

        id_usu_a_borrar = 999 # Usuario no registrado
        res_borrar_user = self.client.post('/admin/delete_user_confirm', data={'user_id': id_usu_a_borrar}, follow_redirects=True)

        # Comprobar que se ha eliminado correctamente
        self.assertEqual(200, res_borrar_user.status_code)
        soup = BeautifulSoup(res_borrar_user.data, features="html.parser")
        n_usu_ahora = len(self.db.select("SELECT * FROM User"))
        self.assertEqual(n_usu_antes, n_usu_ahora)

        # Buscar el mensaje que indica que el ID no existe
        error_message = soup.find('div', {'class': 'alert alert-danger'})
        self.assertIsNotNone(error_message, "Error message not found in the response")
        expected_error_message = "El usuario con el ID proporcionado no existe."
        self.assertIn(expected_error_message, error_message.get_text())

    
    ############################ CREAR UN LIBRO ############################
    # Autor no existe previamente
    def test_crear_libro_1(self):
        res = self.login('p@gmail.com', '1243')
        n_lib_antes = len(self.db.select("SELECT * FROM Book"))
        n_aut_antes = len(self.db.select("SELECT * FROM Author"))

        nuevo_lib = {
            'title': 'El libro de prueba 1',
            'author': 'Autor Inexistente',
            'cover': '',
            'description': '',
            'num_copies': '10'
        }

        res_add_book = self.client.post('/admin/add_book', data=nuevo_lib, follow_redirects=True)

        self.assertEqual(200, res_add_book.status_code)

        n_lib_ahora = len(self.db.select("SELECT * FROM Book"))
        n_aut_ahora = len(self.db.select("SELECT * FROM Author"))
        self.assertEqual(n_lib_antes + 1, n_lib_ahora)
        self.assertEqual(n_aut_antes + 1, n_aut_ahora)

    # Información(necesaria) incompleta
    def test_crear_libro_2(self):
        res = self.login('p@gmail.com', '1243')
        n_lib_antes = len(self.db.select("SELECT * FROM Book"))

        nuevo_lib = {
            'title': 'El libro de prueba 2',
            'author': 'Autor Inexistente',
            'cover': '',
            'description': '',
            'num_copies': ''
        }

        res_add_book = self.client.post('/admin/add_book', data=nuevo_lib, follow_redirects=True)

        self.assertEqual(200, res_add_book.status_code)

        n_lib_ahora = len(self.db.select("SELECT * FROM Book"))
        self.assertEqual(n_lib_antes, n_lib_ahora)
    
    # Libro no registrado
    def test_crear_libro_3(self):
        res = self.login('p@gmail.com', '1243')
        n_lib_antes = len(self.db.select("SELECT * FROM Book"))
        n_aut_antes = len(self.db.select("SELECT * FROM Author"))

        nuevo_lib = {
            'title': 'El libro de prueba 3',
            'author': 'Autor Inexistente',
            'cover': '',
            'description': '',
            'num_copies': '10'
        }

        res_add_book = self.client.post('/admin/add_book', data=nuevo_lib, follow_redirects=True)

        self.assertEqual(200, res_add_book.status_code)

        n_lib_ahora = len(self.db.select("SELECT * FROM Book"))
        n_aut_ahora = len(self.db.select("SELECT * FROM Author"))
        self.assertEqual(n_lib_antes + 1, n_lib_ahora)
        self.assertEqual(n_aut_antes, n_aut_ahora)

    ######################## EDITAR COPIAS UN LIBRO #########################
    # P7    Sumar copias
    def test_editar_copias_1(self):
        res = self.login('p@gmail.com', '1243')

    # P8     Restar copias
    def test_editar_copias_1(self):
        res = self.login('p@gmail.com', '1243')
    
    # P8a   Copias = 0
    def test_editar_copias_1(self):
        res = self.login('p@gmail.com', '1243')

    ############################ BORRAR UN LIBRO ############################
    def test_borrar_libro(self):
        res = self.login('p@gmail.com', '1243')
        n_lib_antes = len(self.db.select("SELECT * FROM Book"))

        id_lib_a_borrar = n_lib_antes - 1

        res_del_book = self.client.post(f'/admin/delete_book/{id_lib_a_borrar}', follow_redirects=True)
        self.assertEqual(200, res_del_book.status_code)

        n_lib_ahora = len(self.db.select("SELECT * FROM Book"))
        self.assertEqual(n_lib_antes, n_lib_ahora + 1)

