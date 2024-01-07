from . import BaseTestClass
from bs4 import BeautifulSoup

class TestResena(BaseTestClass):

    ####### CREAR RESENA NUEVA #######
    def test_crear_resena(self):
        libro_id = 1  
        usuario_id = 1 
        puntuacion = 5

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
        



       


