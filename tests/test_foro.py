from . import BaseTestClass
from bs4 import BeautifulSoup

class TestForo(BaseTestClass):

    #################### ACCEDER A FUNCIONES DE FORO SIN ESTAR REGISTRADO #######################

    def test_acceso_foros_incorrecto(self):
        # Los dos incorrectos
        res = self.login('a@gmail.com', '2136')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/login', res.location)

        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertNotEqual('Menú Administrador', page.find('header').find('ul').find_all('li')[-2].get_text())

        # Contraseña incorrecta
        res3 = self.login('andergorocica@gmail.com', '2136')
        self.assertEqual(302, res3.status_code)
        self.assertEqual('/login', res3.location)

        res4 = self.client.get('/')
        page2 = BeautifulSoup(res4.data, features="html.parser")
        self.assertNotEqual('Foro', page2.find('header').find('ul').find_all('li')[2].get_text())

        # Email incorrecto
        res5 = self.login('a@gmail.com', '2134')
        self.assertEqual(302, res5.status_code)
        self.assertEqual('/login', res5.location)

        res6 = self.client.get('/')
        page3 = BeautifulSoup(res6.data, features="html.parser")
        self.assertNotEqual('Foro', page3.find('header').find('ul').find_all('li')[2].get_text())

        #Sin intentar registrarse
        res7 = self.client.get('/')
        page4 = BeautifulSoup(res6.data, features="html.parser")
        self.assertNotEqual('Foro', page4.find('header').find('ul').find_all('li')[2].get_text())

    #################### ACCEDER A FUNCIONES DE FORO ESTANDO REGISTRADO ############################

    def test_acceso_foros_correcto(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        self.assertEqual('Foro', page.find('header').find('ul').find_all('li')[2].get_text())

        res3 = self.client.get('/admin')
        self.assertEqual(200, res3.status_code)

    ################### INSERTAR UN TEMA YA CREADO #################################################

    def test_crear_tema_existente(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        num_temas_antes = len(self.db.select("SELECT * FROM Tema"))
        nuevo_tema = {
            'nombre': 'Nuevo' #Para que funcione este caso de prueba hay que cambiar el nombre del tema por un tema que exista
        }

        res_add_tema = self.client.post('/anadir_foro', data=nuevo_tema, follow_redirects=True)
        self.assertEqual(200, res_add_tema.status_code)  # Verificar código de estado después de la solicitud POST

        num_temas_ahora = len(self.db.select("SELECT * FROM Tema"))
        self.assertEqual(num_temas_antes, num_temas_ahora)

        # soup = BeautifulSoup(res_add_tema.data, features="html.parser")
        # mensaje_error = soup.find('div', {'class': 'alert alert-danger'})
        # print("Contenido HTML:", soup.prettify())
        # self.assertIsNotNone(mensaje_error, "No se encontró el elemento de mensaje de error")
        # mensaje_error = mensaje_error_element.get_text(strip=True)

        # self.assertEqual("El tema ya existe", mensaje_error)


    ################### INSERTAR UN TEMA NO CREADO #################################################

    def test_crear_tema_nuevo(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        num_temas_antes = len(self.db.select("SELECT * FROM Tema"))
        nuevo_tema = {
            'nombre': 'Nuevo2' #Para que funcione este caso de prueba hay que cambiar el nombre del tema por un tema que no exista
        }

        res_add_tema = self.client.post('/gest_anadir_foro', data=nuevo_tema, follow_redirects=True) 
        num_temas_ahora = len(self.db.select("SELECT * FROM Tema"))
 
        self.assertEqual(num_temas_antes + 1, num_temas_ahora)
        
        self.assertEqual(200, res_add_tema.status_code)
        soup = BeautifulSoup(res_add_tema.data, features="html.parser")
