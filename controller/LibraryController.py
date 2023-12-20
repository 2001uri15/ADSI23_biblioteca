from model import Connection, Book, User, Tema
from model.tools import hash_password

db = Connection()

class LibraryController:
	__instance = None

	def __new__(cls):
		if cls.__instance is None:
			cls.__instance = super(LibraryController, cls).__new__(cls)
			cls.__instance.__initialized = False
		return cls.__instance


	def search_books(self, title="", author="", limit=6, page=0):
		count = db.select("""
				SELECT count() 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
		""", (f"%{title}%", f"%{author}%"))[0][0]
		res = db.select("""
				SELECT b.* 
				FROM Book b, Author a 
				WHERE b.author=a.id 
					AND b.title LIKE ? 
					AND a.name LIKE ? 
				LIMIT ? OFFSET ?
		""", (f"%{title}%", f"%{author}%", limit, limit*page))
		books = [
			Book(b[0],b[1],b[2],b[3],b[4], b[5])
			for b in res
		]
		return books, count

	def search_tema(self, nombre=""):
		res = db.select("SELECT * FROM Tema WHERE nombre LIKE ?", ('%' + nombre + '%'))
		temas = [Tema(t[0], t[1], t[2]) for t in res]
		return temas
	
	def comprobar_tema(self, nombre=""):
		tema_existente = db.select("SELECT 1 FROM Tema WHERE nombre = ? LIMIT 1", (nombre,))
		return bool(tema_existente)
	
	# def anadir_tema(self, nombre="", creado=""):


	def get_user(self, email, password):
		user = db.select("SELECT * from User WHERE email = ? AND password = ?", (email, hash_password(password)))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2], user[0][3], user[0][4], user[0][6])
		else:
			return None
	
	def get_user_id(self, id):
		user = db.select("SELECT * from User WHERE id = ? ", (id, ))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2], user[0][3], user[0][4], user[0][6])
		else:
			return None

	def get_user_cookies(self, token, time):
		user = db.select("SELECT u.* from User u, Session s WHERE u.id = s.user_id AND s.last_login = ? AND s.session_hash = ?", (time, token))
		if len(user) > 0:
			return User(user[0][0], user[0][1], user[0][2], user[0][3], user[0][4], user[0][6])
		else:
			return None

	def recomendaciones_amigos(self, user):
		user = db.select("SELECT * from Amigo WHERE idUsuario = ?", (user.id,))
		amigoRecom = []
		if len(user) > 0:
			for amigo in user:
				# Amigos de mis amigos
				amigos_de_amigo = db.select("SELECT * FROM Amigo WHERE idUsuario = ?", (amigo[1],))

				for amigo_de_amigo in amigos_de_amigo:
					# Información del amigo de mi amigo
					amigo_info = db.select("SELECT * FROM User WHERE id = ?", (amigo_de_amigo[1],))
					amigo_obj = User(amigo_info[0][0], amigo_info[0][1], amigo_info[0][2], amigo_info[0][3], amigo_info[0][4], amigo_info[0][6])
					amigoRecom.append(amigo_obj)

			return amigoRecom
		else:
			return amigoRecom
	
	def misAmigos(self, user):
		user = db.select("SELECT * from Amigo WHERE idUsuario = ?", (user.id,))
		misAmigos = []
		if len(user) > 0:
			for amigo in user:
				# Información de mi amigo
				user1 = db.select("SELECT * from User WHERE id = ? ", (amigo[1], ))
				amigo_obj = User(user1[0][0], user1[0][1], user1[0][2], user1[0][3], user1[0][4], user1[0][6])
				misAmigos.append(amigo_obj)
				print(amigo_obj)

			return misAmigos
		else:
			return misAmigos

	def somosAmigos(self, user, amigo):
		somosAmigos = db.select("SELECT 1 FROM Amigo WHERE idUsuario = ? AND idAmigo = ? LIMIT 1", (user.id, amigo.id, ))
		return bool(somosAmigos)
