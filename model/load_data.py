import hashlib
import sqlite3
import json
import os

try:
	os.remove("datos.db")
except:
	pass

salt = "library"


con = sqlite3.connect("datos.db")
cur = con.cursor()


### Create tables
cur.execute("""
	CREATE TABLE Author(
		id integer primary key AUTOINCREMENT,
		name varchar(40)
	)
""")

cur.execute("""
	CREATE TABLE Book(
		id integer primary key AUTOINCREMENT,
		title varchar(50),
		author integer,
		cover varchar(50),
		description TEXT,
		numCopias integer,
		FOREIGN KEY(author) REFERENCES Author(id)
	)
""")

cur.execute("""
	CREATE TABLE User(
		id integer primary key AUTOINCREMENT,
		name varchar(20),
		apellidos varchar(100),
		creado integer,
		email varchar(30),
		password varchar(32),
		admin boolean,
		FOREIGN KEY(creado) REFERENCES User(id)
	)
""")

cur.execute("""
	CREATE TABLE Session(
		session_hash varchar(32) primary key,
		user_id integer,
		last_login float,
		FOREIGN KEY(user_id) REFERENCES User(id)
	)
""")

cur.execute("""
	CREATE TABLE Resena(
		id integer primary key AUTOINCREMENT,
		idUsuario integer,
		idLibro integer,
		puntuacion integer,
		comentario varchar(500),
		FOREIGN KEY(idUsuario) REFERENCES User(id),
		FOREIGN KEY(idLibro) REFERENCES Book(id)
	)
""")

cur.execute("""
	CREATE TABLE Reserva(
		id integer primary key AUTOINCREMENT,
		idUsuario integer,
		idLibro integer,
		fechaReserva data,
		fechaDevolucion date,
		FOREIGN KEY(idUsuario) REFERENCES User(id),
		FOREIGN KEY(idLibro) REFERENCES Book(id)
	)
""")

cur.execute("""
	CREATE TABLE Amigo(
		idUsuario integer,
		idAmigo integer,
		Primary key(idUsuario, idAmigo),
		FOREIGN KEY(idUsuario) REFERENCES User(id),
		FOREIGN KEY(idAmigo) REFERENCES user(id)
	)
""")

cur.execute("""
	CREATE TABLE PeticionAmigo(
		idUsuario integer,
		idAmigo integer,
		Primary key(idUsuario, idAmigo),
		FOREIGN KEY(idUsuario) REFERENCES User(id),
		FOREIGN KEY(idAmigo) REFERENCES user(id)
	)
""")

cur.execute("""
	CREATE TABLE Tema(
		id integer primary key AUTOINCREMENT,
		nombre varchar(100),
		creado integer,
		FOREIGN KEY(creado) REFERENCES User(id)
	)
""")

cur.execute("""
	CREATE TABLE Publicacion(
		id integer primary key AUTOINCREMENT,
		idTema integer,
		fecha datetime,
		idUsuario integer,
		texto varchar(500),
		FOREIGN KEY(idUsuario) REFERENCES User(id),
		FOREIGN KEY(idTema) REFERENCES Tema(id)
	)
""")

### Insert users

with open('usuarios.json', 'r') as f:
	usuarios = json.load(f)['usuarios']

for user in usuarios:
	dataBase_password = user['password'] + salt
	hashed = hashlib.md5(dataBase_password.encode())
	dataBase_password = hashed.hexdigest()
	cur.execute(f"""INSERT INTO User VALUES (NULL, '{user['nombres'].split(" ")[0]}', '{user['nombres'].split(" ")[1]}', null ,'{user['email']}', '{dataBase_password}', {user['admin']})""")
	con.commit()


#### Insert books
with open('libros.tsv', 'r') as f:
	libros = [x.split("\t") for x in f.readlines()]

count = 0
for author, title, cover, description in libros[:100]:
	res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	if res.rowcount == -1:
		cur.execute(f"""INSERT INTO Author VALUES (NULL, \"{author}\")""")
		con.commit()
		res = cur.execute(f"SELECT id FROM Author WHERE name=\"{author}\"")
	author_id = res.fetchone()[0]

	cur.execute("INSERT INTO Book VALUES (NULL, ?, ?, ?, ?, ?)",
		            (title, author_id, cover, description.strip(), (count%4)+1))

	con.commit()



