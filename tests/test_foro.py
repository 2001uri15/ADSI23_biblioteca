from . import BaseTestClass
from bs4 import BeautifulSoup
import re


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

    ################### INSERTAR UN TEMA NO CREADO #################################################

    def test_crear_tema_nuevo(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        num_temas_antes = len(self.db.select("SELECT * FROM Tema"))
        nuevo_tema = {
            'nombre': 'Nuevo4' #Para que funcione este caso de prueba hay que cambiar el nombre del tema por un tema que no exista
        }

        res_add_tema = self.client.post('/gest_anadir_foro', data=nuevo_tema, follow_redirects=True) 
        num_temas_ahora = len(self.db.select("SELECT * FROM Tema"))
 
        self.assertEqual(num_temas_antes + 1, num_temas_ahora)
        
        self.assertEqual(200, res_add_tema.status_code)
        soup = BeautifulSoup(res_add_tema.data, features="html.parser")

    ################## EL MISMO USUARIO INSERTA OTRO TEMA NO CREADO ##################################

    def test_crear_otro_tema_nuevo(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        num_temas_antes = len(self.db.select("SELECT * FROM Tema"))
        nuevo_tema = {
            'nombre': 'SGI' #Para que funcione este caso de prueba hay que cambiar el nombre del tema por un tema que no exista
        }

        res_add_tema = self.client.post('/gest_anadir_foro', data=nuevo_tema, follow_redirects=True) 
        num_temas_ahora = len(self.db.select("SELECT * FROM Tema"))
 
        self.assertEqual(num_temas_antes + 1, num_temas_ahora)
        
        self.assertEqual(200, res_add_tema.status_code)
        soup = BeautifulSoup(res_add_tema.data, features="html.parser")

    ################## EL MISMO USUARIO INSERTA OTRO TEMA QUE YA EXISTE ##############################

    def test_crear_otro_tema_existente(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        num_temas_antes = len(self.db.select("SELECT * FROM Tema"))
        nuevo_tema = {
            'nombre': 'Nuevo2' #Para que funcione este caso de prueba hay que cambiar el nombre del tema por un tema que ya exista
        }

        res_add_tema = self.client.post('/gest_anadir_foro', data=nuevo_tema, follow_redirects=True) 
        num_temas_ahora = len(self.db.select("SELECT * FROM Tema"))
 
        self.assertEqual(num_temas_antes, num_temas_ahora)
        
        self.assertEqual(200, res_add_tema.status_code)
        soup = BeautifulSoup(res_add_tema.data, features="html.parser")

    ################## INSERTAR UN TEMA Y PULSAR SALIR ###############################################
    
    def test_crear_tema_salir(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        num_temas_antes = len(self.db.select("SELECT * FROM Tema"))
        nuevo_tema = {
            'nombre': 'Nuevo2' 
        }
        
        res2 = self.client.get('/foro')

        num_temas_ahora = len(self.db.select("SELECT * FROM Tema"))
 
        self.assertEqual(num_temas_antes, num_temas_ahora)
        self.assertEqual(200, res2.status_code)


    ################## VISUALIZAR UN TEMA EXISTENTE #################################################

    def test_ver_tema(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res2 = self.client.get('/foro')
        self.assertEqual(res2.status_code, 200)

        res3 = self.client.get('/tema/1')
        self.assertEqual(res3.status_code, 200)

        nombre_tema = res3.get_data(as_text=True)
        nombre_tema = re.search(r'<h1>(.*?)</h1>', nombre_tema).group(1)

        self.assertEqual(nombre_tema, 'Nuevo')

    #################### ENVIAR UN MENSAJE EN EL FORO ############################################

    def test_enviar_mensaje_en_tema(self):
        login_res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, login_res.status_code)
        self.assertEqual('/', login_res.location)

        num_mensajes_antes = len(self.db.select("SELECT * FROM Publicacion WHERE idTema = 1"))

        mensaje_data = {'mensaje': 'Este es un mensaje de prueba'}
        enviar_mensaje_res = self.client.post('/tema/1', data=mensaje_data, follow_redirects=True)

        self.assertEqual(200, enviar_mensaje_res.status_code)
        num_mensajes_ahora = len(self.db.select("SELECT * FROM Publicacion WHERE idTema = 1"))

        self.assertEqual(num_mensajes_antes + 1, num_mensajes_ahora)

    ################### ENVIAR UN MENSAJE QUE YA SE ENVIÓ PREVIAMENTE ##############################

    def test_enviar_mensaje_repetido(self):
        login_res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, login_res.status_code)
        self.assertEqual('/', login_res.location)

        num_mensajes_antes = len(self.db.select("SELECT * FROM Publicacion WHERE idTema = 1"))

        mensaje_data = {'mensaje': 'Este es otro mensaje de prueba'}
        enviar_mensaje_res = self.client.post('/tema/1', data=mensaje_data, follow_redirects=True)

        self.assertEqual(200, enviar_mensaje_res.status_code)
        num_mensajes_ahora = len(self.db.select("SELECT * FROM Publicacion WHERE idTema = 1"))

        self.assertEqual(num_mensajes_antes + 1, num_mensajes_ahora)

    ################## EL USUARIO SALE DEL FORO ANTES DE PULSAR ENVIAR ###############################

    def test_enviar_mensaje_salir(self):
        login_res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, login_res.status_code)
        self.assertEqual('/', login_res.location)

        num_mensajes_antes = len(self.db.select("SELECT * FROM Publicacion WHERE idTema = 1"))

        mensaje_data = {'mensaje': 'Este es otro mensaje de prueba'}
        res = self.client.get('/foro')

        num_mensajes_ahora = len(self.db.select("SELECT * FROM Publicacion WHERE idTema = 1"))

        self.assertEqual(num_mensajes_antes, num_mensajes_ahora)
        self.assertEqual(200, res.status_code)

    ################## EL USUARIO PINCHA EL ID DEL CREADOR DEL FORO ####################################

    def test_ver_perfil_creador(self):
        login_res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, login_res.status_code)
        self.assertEqual('/', login_res.location)

        res = self.client.get('/tema/1')
        self.assertEqual(res.status_code, 200)

        id_creador_lista = self.db.select("SELECT creado FROM TEMA WHERE id='1'")

        self.assertIsInstance(id_creador_lista, list)
        self.assertTrue(id_creador_lista)
        self.assertIsInstance(id_creador_lista[0], tuple)

        id_creador_valor = id_creador_lista[0][0]

        res_perfil = self.client.get(f'/perfil?id={id_creador_valor}')
        self.assertEqual(res_perfil.status_code, 200)

        page = BeautifulSoup(res_perfil.data, features="html.parser")
        self.assertEqual('Patricia Ortega', page.find('h5').get_text())

    ################## EL USUARIO PINCHA UN ID DE UN USUARIO QUE ENVIÓ UN MENSAJE ######################

    def test_ver_perfil_usuario(self):
        login_res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, login_res.status_code)
        self.assertEqual('/', login_res.location)

        res = self.client.get('/tema/1')
        self.assertEqual(res.status_code, 200)

        id_creador_lista = self.db.select("SELECT creado FROM TEMA WHERE id='1'")

        self.assertIsInstance(id_creador_lista, list)
        self.assertTrue(id_creador_lista)
        self.assertIsInstance(id_creador_lista[0], tuple)

        id_creador_valor = id_creador_lista[0][0]

        id_usuario_no_creador = self.db.select(f"SELECT idUsuario FROM PUBLICACION WHERE idTema='1' AND idUsuario != {id_creador_valor}")

        self.assertIsInstance(id_usuario_no_creador, list)
        self.assertTrue(id_usuario_no_creador)
        self.assertIsInstance(id_usuario_no_creador[0], tuple)

        id_no_creador_valor = id_usuario_no_creador[0][0]

        res_perfil = self.client.get(f'/perfil?id={id_no_creador_valor}')
        self.assertEqual(res_perfil.status_code, 200)

        page = BeautifulSoup(res_perfil.data, features="html.parser")
        self.assertEqual('Asier Larrazabal', page.find('h5').get_text())

    ################## EL USUARIO PULSA SALIR ESTANDO EN EL FORO #######################################

    def test_salir_tema_foro(self):
        login_res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, login_res.status_code)
        self.assertEqual('/', login_res.location)

        res = self.client.get('/tema/1')
        self.assertEqual(res.status_code, 200)

        res2 = self.client.get('/')
        self.assertEqual(res2.status_code, 200)


