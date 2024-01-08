from . import BaseTestClass
from bs4 import BeautifulSoup

class TestRecomendacionesDelSistema(BaseTestClass):

    # CodPrueba: 1  -> El usuario no tiene libros reservados
    def test_usuario_sin_libros_reservados(self):
        # Iniciamos sesión
        res = self.login('james@gmail.com', '123456')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        # Accedemos al perfil del usuario
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que se espera una tabla vacía ya que el usuario no tiene libros reservados
        tabla_recomendaciones = page.find('a', {'href': '#recomendacionesSistema'})
        self.assertIsNotNone(tabla_recomendaciones)
        cantidad_filas_recomendaciones = len(tabla_recomendaciones.find_all('tr'))
        self.assertEqual(1, cantidad_filas_recomendaciones)  # 1 para la fila de encabezado


    # CodPrueba: 3  -> Usuario con libros reservados (1 o muchos)
    def test_usuario_con_libros_reservados_y_autores_sin_libros_no_reservados(self):
        # Iniciamos sesión
        res = self.login('lo.fig.andrea@gmail.com', '4321')
        self.assertEqual(302, res.status_code)
        self.assertEqual('/', res.location)

        # Simulamos que el usuario tiene un libro reservado
        self.anadir_reserva(usuario_id=2, libro_id=3)  # Usuario2 reserva el libro con id 3

        # Accedemos al perfil del usuario
        res_perfil = self.client.get('/perfil')
        self.assertEqual(200, res_perfil.status_code)
        page = BeautifulSoup(res_perfil.data, features="html.parser")

        # Verificar que se espera que haya recomendaciones de libros en la página
        tabla_recomendaciones = page.find('a', {'href' :'#recomendacionesSistema'})
        self.assertIsNotNone(tabla_recomendaciones)

        