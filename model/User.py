import datetime
from .Connection import Connection
from .tools import hash_password

db = Connection()

class Session:
	def __init__(self, hash, time):
		self.hash = hash
		self.time = time

	def __str__(self):
		return f"{self.hash} ({self.time})"

class User:
	def __init__(self, id, username, apellidos, creado, email, admin):
		self.id = id
		self.name = username
		self.apellidos = apellidos
		self.email = email
		self.admin = admin
		self.creado = creado

	def __str__(self):
		return f"{self.name} {self.apellidos} ({self.email})"

	def __hash__(self):
		return hash(self.id)

	def __eq__(self, x):
		if type(x) == User:
			return self.id == x.id
		else:
			return False
		
	def __ne__(self, x):
		if type(x) == User:
			return self.id != x.id
		else:
			return True

	def new_session(self):
		now = float(datetime.datetime.now().time().strftime("%Y%m%d%H%M%S.%f"))
		session_hash = hash_password(str(self.id)+str(now))
		db.insert("INSERT INTO Session VALUES (?, ?, ?)", (session_hash, self.id, now))
		return Session(session_hash, now)

	def validate_session(self, session_hash):
		s = db.select("SELECT * from Session WHERE user_id = ? AND session_hash = ?", (self.id, session_hash))
		if len(s) > 0:
			now = float(datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
			session_hash_new = hash_password(str(self.id) + str(now))
			db.update("UPDATE Session SET session_hash = ?, last_login=? WHERE session_hash = ? and user_id = ?", (session_hash_new, now, session_hash, self.id))
			return Session(session_hash_new, now)
		else:
			return None

	def delete_session(self, session_hash):
		db.delete("DELETE FROM Session WHERE session_hash = ? AND user_id = ?", (session_hash, self.id))
	
	@property
	def creado(self):
		if type(self._creado) == int:
			em = db.select("SELECT * from User WHERE id=?", (self._creado,))
			if len(em)==0:
				self._creado=None
			else:
				em=em[0]
				self._creado = User(em[0], em[1], em[2], em[3], em[4], em[6])
		return self._creado

	@creado.setter
	def creado(self, value):
		self._creado = value