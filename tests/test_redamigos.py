from . import BaseTestClass
from bs4 import BeautifulSoup
import re


class TestRedAmigos(BaseTestClass):
    #################### PERFIL PROPIO ####################
        
    def test_acceder_a_perfil_propio(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res2 = self.client.get('/')
        page = BeautifulSoup(res2.data, features="html.parser")
        # ver si hay pestaña de perfil
        self.assertEqual('/perfil', page.find('header').find('ul').find_all('li')[3].a.get('href'))
        # ver si se nuestra el nombre del que ha iniciado sesion en la cabecera
        self.assertEqual('Andreea Vasilica', page.find('header').find('ul').find_all('li')[3].get_text())

        res3 = self.client.get('/perfil')
        page = BeautifulSoup(res3.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())

    def test_acceder_a_perfil_propio_sin_amigos(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver si no hay elementos en la tabla de amigos
        self.assertEqual(0, len(page.find('body').find_all('tbody')[0].find_all('th')))


    def test_acceder_a_perfil_propio_con_amigos(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,1)")
        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,2)")
        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,3)")

        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver si hay elementos en la tabla de amigos
        self.assertEqual(3, len(page.find('body').find_all('tbody')[0].find_all('th')))

        self.db.select("DELETE FROM Amigo where idAmigo=1 and idUsuario=10")
        self.db.select("DELETE FROM Amigo where idAmigo=2 and idUsuario=10")
        self.db.select("DELETE FROM Amigo where idAmigo=3 and idUsuario=10")

    def test_acceder_a_perfil_propio_con_solicitudes(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(1,10)")
        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(2,10)")
        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(3,10)")

        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver si hay elementos en el apartado solicitudes
        self.assertEqual(3, len(page.find('body').find_all('tbody')[1].find_all('tr')))
        #ver nombres de las solicitudes
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[1].find_all('tr')[0].find('a').get_text())
        self.assertEqual("Jhon Doe", page.find('body').find_all('tbody')[1].find_all('tr')[1].find('a').get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[1].find_all('tr')[2].find('a').get_text())
        
        self.db.select("DELETE FROM PeticionAmigo where idUsuario=1 and idAmigo=10")
        self.db.select("DELETE FROM PeticionAmigo where idUsuario=2 and idAmigo=10")
        self.db.select("DELETE FROM PeticionAmigo where idUsuario=3 and idAmigo=10")

    def test_acceder_a_perfil_propio_aceptar_solicitud(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(1,10)")
        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(2,10)")
        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(3,10)")

        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver si hay elementos en el apartado solicitudes
        self.assertEqual(3, len(page.find('body').find_all('tbody')[1].find_all('tr')))
        #ver nombres de las solicitudes
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[1].find_all('tr')[0].find('a').get_text())
        self.assertEqual("Jhon Doe", page.find('body').find_all('tbody')[1].find_all('tr')[1].find('a').get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[1].find_all('tr')[2].find('a').get_text())

        self.client.get('/anadiramigo?amigoid=2&id=10&location=/perfil')
        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver que Jhon Doe ya no está entre las solicitudes
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[1].find_all('tr')[0].find('a').get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[1].find_all('tr')[1].find('a').get_text())
        # ver si hay elemento en la tabla de amigos
        self.assertEqual(1, len(page.find('body').find_all('tbody')[0].find_all('th')))
        # ver si el elemento es Jhon Doe
        self.assertEqual("Jhon Doe", page.find('body').find_all('tbody')[0].find_all('td')[0].get_text())

        self.db.select("DELETE FROM PeticionAmigo where idUsuario=1 and idAmigo=10")
        self.db.select("DELETE FROM Amigo where idUsuario=10 and idAmigo=2")
        self.db.select("DELETE FROM PeticionAmigo where idUsuario=3 and idAmigo=10")

    def test_acceder_a_perfil_propio_denegar_solicitud(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(1,10)")
        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(2,10)")
        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(3,10)")

        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver si hay elementos en el apartado solicitudes
        self.assertEqual(3, len(page.find('body').find_all('tbody')[1].find_all('tr')))
        #ver nombres de las solicitudes
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[1].find_all('tr')[0].find('a').get_text())
        self.assertEqual("Jhon Doe", page.find('body').find_all('tbody')[1].find_all('tr')[1].find('a').get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[1].find_all('tr')[2].find('a').get_text())

        self.client.get('/eliminarpeticion?amigoid=2&id=10&location=/perfil')
        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver que Jhon Doe ya no está entre las solicitudes
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[1].find_all('tr')[0].find('a').get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[1].find_all('tr')[1].find('a').get_text())
        # ver si hay elemento en la tabla de amigos
        self.assertEqual(0, len(page.find('body').find_all('tbody')[0].find_all('th')))

        self.db.select("DELETE FROM PeticionAmigo where idUsuario=1 and idAmigo=10")
        self.db.select("DELETE FROM PeticionAmigo where idUsuario=3 and idAmigo=10")

    def test_acceder_a_perfil_propio_eliminar_amigo(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,1)")
        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,2)")
        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,3)")

        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si el nombre del que ha iniciado sesión coincide con el de perfil
        self.assertEqual('Andreea Vasilica', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver si hay elementos en la tabla de amigos
        self.assertEqual(3, len(page.find('body').find_all('tbody')[0].find_all('th')))
        # ver que amigos hay
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[0].find_all('td')[0].get_text())
        self.assertEqual("Jhon Doe", page.find('body').find_all('tbody')[0].find_all('td')[2].get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[0].find_all('td')[4].get_text())

        self.client.get('/eliminaramigo?amigoid=2&id=10&location=/perfil?id={{User.id}}')
        res = self.client.get('/perfil')
        page = BeautifulSoup(res.data, features="html.parser")
        # ver si hay elementos en la tabla de amigos
        self.assertEqual(2, len(page.find('body').find_all('tbody')[0].find_all('th')))
        # ver que amigos hay
        self.assertEqual("James Gomez", page.find('body').find_all('tbody')[0].find_all('td')[0].get_text())
        self.assertEqual("Juan Ejemplo", page.find('body').find_all('tbody')[0].find_all('td')[2].get_text())
        

        self.db.select("DELETE FROM Amigo where idAmigo=1 and idUsuario=10")
        self.db.select("DELETE FROM Amigo where idAmigo=2 and idUsuario=10")
        self.db.select("DELETE FROM Amigo where idAmigo=3 and idUsuario=10")
        

    #################### PERFIL AJENO ####################
        
    def test_acceder_a_perfil_ajeno_no_amigo(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que no es amigo
        self.assertEqual("Añadir amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

    def test_acceder_a_perfil_ajeno_amigo(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,1)")        

        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que es amigo
        self.assertEqual("Dejar amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

        self.db.select("DELETE FROM Amigo where idAmigo=1 and idUsuario=10")

    def test_acceder_a_perfil_ajeno_mandar_solicitud_y_cancelarla(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)
       
        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que no amigo
        self.assertEqual("Añadir amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

        self.client.get('/anadirpeticion?amigoid=1&id=10&location=/perfil?id=1')
        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver que se ha mandado la solicitud
        self.assertEqual("Cancelar solicitud", page.find('body').find_all('div')[5].find('button').find('a').get_text())

        self.client.get('/cancelarpeticion?amigoid=1&id=10&location=/perfil?id=1')
        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver que se ha cancelado la solicitud
        self.assertEqual("Añadir amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

    def test_acceder_a_perfil_ajeno_eliminar_amigo(self):
        res = self.login('andreea@gmail.com', '1234')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO Amigo(idUsuario, idAmigo) values(10,1)")        

        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que es amigo
        self.assertEqual("Dejar amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

        self.client.get('/eliminaramigo?amigoid=1&id=10&location=/perfil?id=1')
        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que es no amigo
        self.assertEqual("Añadir amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

    
    def test_acceder_a_perfil_ajeno_responder_solicitud_aceptar(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(1,4)")        

        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que le he mandado solicitud
        self.assertEqual("Responder solicitud", page.find('body').find_all('div')[5].find('button').find('a').get_text())
    
        self.client.get('/anadiramigo?amigoid=1&id=4&location=/perfil')
        res = self.client.get('/perfil?id=1')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('James Gomez', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que es amigo
        self.assertEqual("Dejar amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

        self.db.select("DELETE FROM Amigo where idAmigo=1 and idUsuario=4")

    def test_acceder_a_perfil_ajeno_responder_solicitud_denegar(self):
        res = self.login('p@gmail.com', '1243')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        self.db.select("INSERT INTO PeticionAmigo(idUsuario, idAmigo) values(2,4)")        

        res = self.client.get('/perfil?id=2')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('Jhon Doe', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que le he mandado solicitud
        self.assertEqual("Responder solicitud", page.find('body').find_all('div')[5].find('button').find('a').get_text())
    
        self.client.get('/eliminarpeticion?amigoid=2&id=4&location=/perfil')
        res = self.client.get('/perfil?id=2')
        self.assertEqual(200, res.status_code)
        page = BeautifulSoup(res.data, features="html.parser")
        # ver de quien es el perfil
        self.assertEqual('Jhon Doe', page.find('body').find_all('div')[6].find('h5').get_text())
        # ver que no es amigo
        self.assertEqual("Añadir amig@", page.find('body').find_all('div')[5].find('button').find('a').get_text())

        self.db.select("DELETE FROM Amigo where idAmigo=2 and idUsuario=4")



