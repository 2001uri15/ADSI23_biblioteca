from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect, flash, url_for
from datetime import datetime


app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')
app.secret_key = 'claveSecreta#ADSI2023'

library = LibraryController()


@app.before_request
def get_logged_user():
	if '/css' not in request.path and '/js' not in request.path:
		token = request.cookies.get('token')
		time = request.cookies.get('time')
		if token and time:
			request.user = library.get_user_cookies(token, float(time))
			if request.user:
				request.user.token = token


@app.after_request
def add_cookies(response):
	if 'user' in dir(request) and request.user and request.user.token:
		session = request.user.validate_session(request.user.token)
		response.set_cookie('token', session.hash)
		response.set_cookie('time', str(session.time))
	return response


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/catalogue')
def catalogue():
	userLogin = None
	title = request.values.get("title", "")
	author = request.values.get("author", "")
	page = int(request.values.get("page", 1))
	books, nb_books = library.search_books(title=title, author=author, page=page - 1)
	total_pages = (nb_books // 6) + 1

	# Verificar si el usuario es administrador
	is_admin = 'user' in dir(request) and request.user and request.user.admin

	# Conseguir el usuario logueado
	if 'user' in dir(request):
		userLogin = request.user

	# Obtener información adicional para el administrador
	total_copies_info = None
	if is_admin:
		total_copies_info = library.get_total_copies_info()
		return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
								total_pages=total_pages, max=max, min=min, is_admin=is_admin, total_copies_info=total_copies_info, userLogin=userLogin)
	else:
		return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
								total_pages=total_pages, max=max, min=min, userLogin=userLogin)

	"""
	if 'user' in dir(request) and request.user and request.user.token:
		return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
						   total_pages=total_pages, max=max, min=min, is_admin=request.user.admin)
	else:
		return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
						   total_pages=total_pages, max=max, min=min)
	"""

@app.route('/edit_copies/<int:book_id>', methods=['GET', 'POST'])
def edit_copies(book_id):
	# Verificar si el usuario es administrador
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")

	if request.method == 'POST':
		# Obtener el nuevo número de copias desde el formulario
		new_num_copies = int(request.form.get('new_num_copies', 0))

		# Actualizar el número de copias en la base de datos
		library.update_num_copies(book_id, new_num_copies)

		# Redirigir de vuelta al catálogo
		return redirect('/catalogue')

	# Obtener información del libro para mostrar en el formulario
	book_info = library.get_book_info(book_id)
	return render_template('edit_copies.html', book_info=book_info)

####EN PROCESO: ESCRIBIR RESENA #################################

@app.route('/escribir_resena/<int:book_id>', methods=['GET', 'POST'])
def escribir_resena(book_id):
	# Verificar si hay un usuario autenticado
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")

	# Obtener el usuario autenticado
	user = request.user.id
	existe = library.comprobar_resena(user, book_id)
	resena_existente = None
	if existe:
		resena_existente = library.obtener_resena(user, book_id)

	if request.method == 'POST':
		# Obtener el comentario y la puntuación del formulario
		comentario = request.form.get('mensaje', '')
		puntuacion = request.form.get('puntuacion', '')
		if not existe:
			library.anadir_resena(user,book_id,puntuacion,comentario)
		else:
			library.editar_resena(user, book_id, puntuacion, comentario)
		return redirect(url_for('ver_libro', book_id=book_id))
		# Aquí puedes agregar la lógica para guardar la reseña en la base de datos
		# o realizar cualquier otra acción con el comentario y la puntuación.

	return render_template('escribir_resena.html', book_id=book_id, resena_existente=resena_existente)


#####################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user' in dir(request) and request.user and request.user.token:
		return redirect('/')
	email = request.values.get("email", "")
	password = request.values.get("password", "")
	user = library.get_user(email, password)
	if user:
		session = user.new_session()
		resp = redirect("/")
		resp.set_cookie('token', session.hash)
		resp.set_cookie('time', str(session.time))
	else:
		if request.method == 'POST':
			return redirect('/login')
		else:
			resp = render_template('login.html')
	return resp


@app.route('/logout')
def logout():
	path = request.values.get("path", "/")
	resp = redirect(path)
	resp.delete_cookie('token')
	resp.delete_cookie('time')
	if 'user' in dir(request) and request.user and request.user.token:
		request.user.delete_session(request.user.token)
		request.user = None
	return resp


@app.route('/admin')
def admin():
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")
	return render_template('menu_admin.html')


@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")

	if request.method == 'POST':
		name = request.form['name']
		apellidos = request.form['apellidos']
		birthdate = request.form['birthdate']
		email = request.form['email']
		password = request.form['password']
		admin = 'admin' in request.form

		# Verificar si ya existe un usuario con el mismo correo electrónico
		existing_user = library.get_user_by_email(email)
		if existing_user:
			flash('Ya existe un usuario con el mismo correo electrónico.', 'error')
			return redirect(request.url)


		library.add_user(name, apellidos, birthdate, email, password, admin)
		return redirect('/admin')

	return render_template('add_user.html') 


@app.route('/admin/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")
	
	if request.method == 'POST':
		idInt = int(book_id)
		library.delete_book(idInt)
		return redirect('/catalogue')


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")
	
	if request.method == 'POST':
		idInt = int(user_id)
		library.delete_user(idInt)
		return redirect('/admin/list_users')

@app.route('/admin/delete_user_confirm', methods=['GET', 'POST'])
def delete_user_confirm():
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")

	if request.method == 'POST':
		user_id = int(request.form.get("user_id", ""))

		# Verificar si el usuario existe antes de intentar eliminarlo
		existing_user = library.get_user_id(user_id)
		if existing_user:
			library.delete_user(user_id)
			return redirect('/admin/list_users')
		else:
			error_message = "El usuario con el ID proporcionado no existe."
			return render_template('delete_user_confirm.html', error_message=error_message)

	return render_template('delete_user_confirm.html')


@app.route('/admin/list_users')
def list_users():
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")
	users = library.get_all_users()
	return render_template('list_users.html', users=users) 

@app.route('/admin/add_author', methods=['GET', 'POST'])
def add_author():
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")

	if request.method == 'POST':
		name = request.form['name']
		library.add_author(name)
		return redirect('/admin')

	return render_template('add_author.html')

@app.route('/admin/add_book', methods=['GET', 'POST'])
def add_book():
	if 'user' not in dir(request) or request.user is None or not request.user.admin:
		return redirect("/")

	if request.method == 'POST':
		title = request.form['title']
		author_name = request.form['author']
		cover = request.form.get('cover', None)
		description = request.form.get('description', None)
		num_copies = request.form['num_copies']

		# Obtén el ID del autor existente o añádelo si no existe
		author = library.get_author_by_name(author_name)
		if not author:
			author_id = library.add_author(author_name)
		else:
			author_id = author.id


		# Validar que num_copies sea un número positivo o cero
		num_copies = request.form['num_copies']
		try:
			num_copies = int(num_copies)
			if num_copies < 0:
				flash('Please enter a non-negative integer for the number of copies.', 'error')
				return redirect(request.url)
		except ValueError:
			flash('Please enter a valid integer for the number of copies.', 'error')
			return redirect(request.url)

		library.add_book(title, author_id, num_copies, cover, description)
		return redirect('/admin')

		

	return render_template('add_book.html')
	




@app.route('/perfil')
def perfil():
	_id = int (request.values.get("id", -1))
	esAmigo = False
	listas = None
	amigos = None
	listaPeticiones = None
	soyYo = None
	UserLogin= None
	solicitudYo=False
	solicitudUsuario=False
	solicitudEl=False
	librosre_comendados = None
	
	if _id != -1:
		#PERFIL AJENO
		User = library.get_user_id(_id)
		UserLogin = request.user
		esAmigo = library.somosAmigos(UserLogin, User)
		soyYo = User.id == UserLogin.id
		#lista de amigos
		amigos = library.misAmigos(User,UserLogin)
		solicitudYo=library.solicitudMandadaYo(UserLogin.id,User.id)
		solicitudEl=library.solicitudMandadaEl(UserLogin.id,User.id)
	
	else:
		if 'user' not in dir(request) or request.user is None:
			User = None
		else:
			#MI PERFIL
			soyYo=True
			User = request.user
			# Mi lista de amigos
			amigos = library.misAmigos(User,User)
			# Buscar las dos listas: Amigos de amigo y recomendaciones de usuarios por libros
			listaAmigos = library.recomendaciones_amigos(User)
			listaLibros = library.recomendaciones_amigos_libros(User)
			listas = set(listaAmigos + listaLibros)
			listaPeticiones = library.obtenerListaPeticiones(User)
			libros_recomendados = library.recomendacion_libros_sistema(User.id)
	if User != None:
		return render_template('perfil.html', User=User, id=_id, soyYo=soyYo, UserLogin=UserLogin, amigosRecom=listas, solicitudYo=solicitudYo, solicitudEl=solicitudEl, amigos=amigos, esAmigo=esAmigo, peticiones=listaPeticiones, libros_recomendados=libros_recomendados) #Paso a la vista las dos litas
	else:
		return redirect("/login")
	
@app.route('/foro')
def foro():
	temas = []
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	else:
		temas = library.mostrar_tema()

	return render_template('foro.html', temasF = temas)

@app.route('/anadir_foro',  methods=['GET', 'POST'])
def anadir_foro():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	return render_template('anadir_foro.html')

@app.route('/anadiramigo')
def anadiramigo():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	amigo_id = request.values.get("amigoid", "/")
	mi_id = request.values.get("id", "/")
	path = request.values.get("location", "/")
	
	library.aceptarAmistad(mi_id, amigo_id)

	return redirect(path)

@app.route('/eliminaramigo')
def eliminaramigo():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	amigo_id = request.values.get("amigoid", "/")
	mi_id = request.values.get("id", "/")
	path = request.values.get("location", "/")
	
	library.eliminarAmigo(mi_id, amigo_id)

	return redirect(path)

@app.route('/anadirpeticion')
def anadirpeticion():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	amigo_id = request.values.get("amigoid", "/")
	mi_id = request.values.get("id", "/")
	path = request.values.get("location", "/")
	
	library.anadirPeticionAmistad(mi_id, amigo_id)

	return redirect(path)

@app.route('/cancelarpeticion')
def cancelarpeticion():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	amigo_id = request.values.get("amigoid", "/")
	mi_id = request.values.get("id", "/")
	path = request.values.get("location", "/")
	
	library.eliminarPeticion(amigo_id, mi_id)

	return redirect(path)

@app.route('/eliminarpeticion')
def eliminarpeticion():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	amigo_id = request.values.get("amigoid", "/")
	mi_id = request.values.get("id", "/")
	path = request.values.get("location", "/")
	
	library.eliminarPeticion(mi_id, amigo_id)

	return redirect(path)

@app.route('/gest_anadir_foro', methods=['GET', 'POST'])
def gest_anadir_foro():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	else:
		User = request.user
		nombre = request.form.get('nombre')
		comprobar = library.comprobar_tema(nombre)
		path = request.values.get("location", "/")
		if not comprobar:
			library.anadir_tema(nombre, User.id)
			return redirect(path)
		else:
			return render_template('anadir_foro.html', mensaje="El tema ya existe")
	return render_template('foro.html')

@app.route('/tema/<int:tema_id>', methods=['GET', 'POST'])
def ver_tema(tema_id):
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	else:
		if request.method == 'POST':
			User = request.user
			mensaje = request.form.get("mensaje", "")
			if mensaje:
				library.enviar_mensaje(tema_id, datetime.now(), User.id, mensaje)
		nombre_tema = library.obtener_nombre_tema(tema_id)
		mensajes = library.mostrar_mensaje(tema_id)
		return render_template('tema.html', nombre_tema=nombre_tema, mensajes=mensajes, tema_id=tema_id)

@app.route('/ver_libro/<int:book_id>', methods=['GET'])
def ver_libro(book_id):
	if 'user' not in dir(request) or request.user is None:
		return redirect("/catalogue")

	autores_resenas = []
	user = request.user.id
	existe_resena = library.comprobar_resena(user, book_id)
	book_info = library.get_book_info(book_id)
	resenas = library.buscar_resenas_por_libro(book_id)
	autores_resenas = [library.obtener_autor_resena(resena.idUsuario) if resena else None for resena in resenas]

	
	return render_template('ver_libro.html', book_info=book_info, resenas=resenas, existe_resena=existe_resena, autores_resenas=autores_resenas)

# Reservas

@app.route('/add_booking', methods=['POST'])
def add_booking():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/catalogue")

	user_id = request.args.get('user_id', type=int)
	book_id = request.args.get('book_id', type=int)

	print(user_id)

	library.anadir_reserva(user_id, book_id)
	
	return redirect("/catalogue")

@app.route('/historial_reservas', methods=['GET'])
def historial_reservas():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/perfil")
	
	user_id = request.args.get('user_id', type=int)

	reservas = library.mostrar_reservas(user_id)
	return render_template('historial_reservas.html', reservas=reservas) 
