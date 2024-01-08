from . import BaseTestClass
from bs4 import BeautifulSoup

class TestResena(BaseTestClass):
    ####### CREAR RESENA NUEVA #######
    def test_crear_resena(self):
        libro_id = 1  
        usuario_id = 1 

        self.login('james@gmail.com', '123456')
        self.db.delete("DELETE FROM Resena WHERE idUsuario = ?", (usuario_id,))
        num_resenas = len(self.db.select("SELECT * FROM Resena"))

        data = {
            'mensaje': 'Excelente libro',
            'puntuacion': 5
        }

        response = self.client.post(f'/escribir_resena/{libro_id}', data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        #soup = BeautifulSoup(response.data, features="html.parser")
        num_res_nuevo = len(self.db.select("SELECT * FROM Resena"))

        resena_guardada = self.db.select("SELECT * FROM Resena WHERE idLibro=? AND idUsuario=?", (libro_id, usuario_id,))
       # self.assertTrue(resena_guardada, "La reseña no se ha guardado en la base de datos.")
        if resena_guardada:
            self.assertEqual(resena_guardada[0][4], 'Excelente libro')
            self.assertEqual(resena_guardada[0][3], 5)
        self.assertEqual(num_resenas+1, num_res_nuevo)

    ###### EDITAR RESENA EXISTENTE ########
    
    def test_editar_resena(self):
        libro_id = 1  
        usuario_id = 1 

        #Escribimos una resena nueva desde 0 y comprobamos que se guarda
        self.login('james@gmail.com', '123456')
        self.db.delete("DELETE FROM Resena WHERE idUsuario = ?", (usuario_id,))
        num_resenas = len(self.db.select("SELECT * FROM Resena"))

        data = {
            'mensaje': 'Excelente libro',
            'puntuacion': 5
        }

        response = self.client.post(f'/escribir_resena/{libro_id}', data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        #soup = BeautifulSoup(response.data, features="html.parser")
        num_res_nuevo = len(self.db.select("SELECT * FROM Resena"))

        resena_guardada = self.db.select("SELECT * FROM Resena WHERE idLibro=? AND idUsuario=?", (libro_id, usuario_id,))
       # self.assertTrue(resena_guardada, "La reseña no se ha guardado en la base de datos.")
        if resena_guardada:
            self.assertEqual(resena_guardada[0][4], 'Excelente libro')
            self.assertEqual(resena_guardada[0][3], 5)
        self.assertEqual(num_resenas+1, num_res_nuevo)

        num_resenas_preedicion = len(self.db.select("SELECT * FROM Resena"))

        data2 = {
            'mensaje': 'Pues no me ha gustado tanto',
            'puntuacion': 2
        }
        response2 = self.client.post(f'/escribir_resena/{libro_id}', data=data2, follow_redirects=True)
        self.assertEqual(200, response2.status_code)
        resena_guardada2 = self.db.select("SELECT * FROM Resena WHERE idLibro=? AND idUsuario=?", (libro_id, usuario_id))
        num_resenas_postedicion = len(self.db.select("SELECT * FROM Resena"))
        if resena_guardada2:
            self.assertEqual(resena_guardada2[0][4], 'Pues no me ha gustado tanto')
            self.assertEqual(resena_guardada2[0][3], 2)
        self.assertEqual(num_resenas_preedicion, num_resenas_postedicion)

    ####### USUARIO ACCEDE A LIBRO

    def test_acceder_libro(self):
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res2 = self.client.get('/catalogue')
        self.assertEqual(200, res2.status_code)
        
        res3 = self.client.get('/ver_libro/4')
        self.assertEqual(200, res3.status_code)
        page = BeautifulSoup(res3.data, features="html.parser")

        titulo_esperado = "Manifiesto del surrealismo"

        titulo_actual = page.find('h2').get_text().strip()

        self.assertEqual(titulo_esperado, titulo_actual, f"El título esperado no coincide: {titulo_esperado} != {titulo_actual}")

    ####### USUARIO NO IDENTIFICADO ACCEDE A LIBRO (no puede)
    def test_noid_acceder_libro(self):

        res = self.client.get('/catalogue')
        self.assertEqual(200, res.status_code)
        
        res2 = self.client.get('/ver_libro/4')
        self.assertEqual(302, res2.status_code)
        self.assertEqual('/catalogue', res2.location)

    ####### USUARIO PULSA ESCRIBIR RESEÑA
    def test_escribir_resena(self):
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res2 = self.client.get('/ver_libro/4')
        self.assertEqual(200, res2.status_code)

        res3 = self.client.get('/escribir_resena/4')
        self.assertEqual(200, res3.status_code)
        self.assertNotEqual(302, res3.status_code)
        page = BeautifulSoup(res3.data, features="html.parser")

        titulo_esperado = "Escribe tu reseña"
        titulo_actual = page.find('h2').get_text().strip()
        self.assertEqual(titulo_esperado, titulo_actual, f"El título esperado no coincide: {titulo_esperado} != {titulo_actual}")
        self.assertNotEqual("Manifiesto del surrealismo", titulo_actual)

    ####### USUARIO COMENTA, NO PUNTUACION
    def test_no_comment(self):
        libro_id = 2 
        usuario_id = 8

        self.login('bibz@gmail.com', '3241')
        self.db.delete("DELETE FROM Resena WHERE idUsuario = ?", (usuario_id,))
        num_resenas = len(self.db.select("SELECT * FROM Resena"))

        data = {
            'mensaje': 'Bueeeeeno, no está mal, lalalalalalalalala',
        }

        response = self.client.post(f'/escribir_resena/{libro_id}', data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)
       
        num_res_nuevo = len(self.db.select("SELECT * FROM Resena"))

        resena_guardada = self.db.select("SELECT * FROM Resena WHERE idLibro=? AND idUsuario=?", (libro_id, usuario_id,))
       # self.assertTrue(resena_guardada, "La reseña no se ha guardado en la base de datos.")
        self.assertEqual(resena_guardada, [])
        self.assertEqual(num_resenas, num_res_nuevo)

    ####### USUARIO PUNTUA, NO COMENTA
    def test_no_puntuacion(self):
        libro_id = 2 
        usuario_id = 8

        self.login('bibz@gmail.com', '3241')
        self.db.delete("DELETE FROM Resena WHERE idUsuario = ?", (usuario_id,))
        num_resenas = len(self.db.select("SELECT * FROM Resena"))

        data = {
            'puntuacion': '3',
        }

        response = self.client.post(f'/escribir_resena/{libro_id}', data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)
       
        num_res_nuevo = len(self.db.select("SELECT * FROM Resena"))
        resena_guardada = self.db.select("SELECT * FROM Resena WHERE idLibro=? AND idUsuario=?", (libro_id, usuario_id,))
       # self.assertTrue(resena_guardada, "La reseña no se ha guardado en la base de datos.")
        self.assertEqual(resena_guardada, [])
        self.assertEqual(num_resenas, num_res_nuevo)


    ####### VISTA DE RESENAS DE UN LIBRO
    def test_escribir_resena(self):
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.insert("INSERT INTO Resena (idUsuario, idLibro, puntuacion, comentario) VALUES (?, ?, ?, ?)",(2, 4, 2, "No está mal"))
        self.db.insert("INSERT INTO Resena (idUsuario, idLibro, puntuacion, comentario) VALUES (?, ?, ?, ?)",(3, 4, 3, "Dammmmm boi"))
        self.db.insert("INSERT INTO Resena (idUsuario, idLibro, puntuacion, comentario) VALUES (?, ?, ?, ?)",(4, 4, 1, "Maaaaaaal"))

        res2 = self.client.get('/ver_libro/4')
        self.assertEqual(200, res2.status_code)

        page = BeautifulSoup(res2.data, features="html.parser")
        
        lista_resenas = page.find('ul', class_='resenas')
       # print("Lista de reseñas:", lista_resenas)  # Agrega este mensaje de depuración

        # Verificar si la lista de reseñas está presente
        self.assertIsNotNone(lista_resenas, "No se encontró la lista de reseñas en la página.")

        if lista_resenas:
            resenas_elementos = lista_resenas.find_all('li')
            autores_resenas = [elemento.find('p', {'class': 'usu'}).get_text(strip=True).replace('Usuario:', '') for elemento in resenas_elementos]
            self.assertNotEqual(autores_resenas, [], "No se encontraron autores de reseñas en la página.")
            nombres_esperados = [' Jhon', ' Juan', ' Patricia']

            for autor in autores_resenas:
                self.assertIn(autor, nombres_esperados)


                

        self.db.delete("DELETE FROM Resena WHERE idUsuario = ? AND idLibro = ?",(2, 4))
        self.db.delete("DELETE FROM Resena WHERE idUsuario = ? AND idLibro = ?",(3, 4))
        self.db.delete("DELETE FROM Resena WHERE idUsuario = ? AND idLibro = ?",(4, 4))





