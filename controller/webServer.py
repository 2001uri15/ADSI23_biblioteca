from .LibraryController import LibraryController
from flask import Flask, render_template, request, make_response, redirect
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='../view/static', template_folder='../view/')


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
	title = request.values.get("title", "")
	author = request.values.get("author", "")
	page = int(request.values.get("page", 1))
	books, nb_books = library.search_books(title=title, author=author, page=page - 1)
	total_pages = (nb_books // 6) + 1
	if 'user' in dir(request) and request.user and request.user.token:
		return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
	                       total_pages=total_pages, max=max, min=min, is_admin=request.user.admin)
	else:
		return render_template('catalogue.html', books=books, title=title, author=author, current_page=page,
	                       total_pages=total_pages, max=max, min=min)

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

        library.add_user(name, apellidos, birthdate, email, password, admin)
        return redirect('/admin')

    return render_template('add_user.html') 


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

        library.add_book(title, author_id, num_copies, cover, description)
        return redirect('/admin')

    return render_template('add_book.html')
	




@app.route('/perfil')
def perfil():
	_id = int (request.values.get("id", -1))
	esAmigo = False
	listas = None
	misAmigos = None
	if _id != -1:
		User = library.get_user_id(_id)
		UserLogin = request.user
		esAmigo = library.somosAmigos(UserLogin, User)
	else:
		if 'user' not in dir(request) or request.user is None:
			User = None
		else:
			User = request.user
			# Mi lista de amigos
			misAmigos = library.misAmigos(User)
			# Buscar las dos listas: Amigos de amigo y recomendaciones de usuarios por libros
			listaAmigos = library.recomendaciones_amigos(User)
			listaLibros = library.recomendaciones_amigos_libros(User)
			listas = set(listaAmigos + listaLibros)
	if User != None:
		return render_template('perfil.html', User=User, amigosRecom=listas, amigos=misAmigos, esAmigo=esAmigo) #Paso a la vita las dos litas
	else:
		return redirect("/")
	
@app.route('/foro')
def foro():
	temas = []
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	else:
		temas = library.mostrar_tema()

	return render_template('foro.html', temasF = temas)

@app.route('/anadir_foro')
def anadir_foro():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	return render_template('anadir_foro.html')

@app.route('/anadiramigo')
def anadiramigo():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	amigo_id = request.values.get("amigoid", "/")
	path = request.values.get("location", "/")
	# TODO
	return redirect(path)

@app.route('/gest_anadir_foro')
def gest_anadir_foro():
	if 'user' not in dir(request) or request.user is None:
		return redirect("/")
	else:
		User = request.user
		nombre = request.values.get("nombre_tema", "/")
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
