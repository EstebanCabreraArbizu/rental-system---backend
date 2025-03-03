import time
from datetime import timedelta
from urllib.parse import urlparse
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.db import mysql
from app.models.user import User

users = Blueprint('users', __name__, template_folder='app/templates')


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next_url = request.args.get('next')
        if not next_url or not urlparse(next_url).scheme or urlparse(next_url).netloc != request.host:
            user_type_urls = {
                'Admin': url_for('admin.dashboard'),
                'Cliente': url_for('users.add_user'),
                'Propietario': url_for('owner.dashboard')
            }
            print(current_user.tipo_usuario)
            next_url = user_type_urls.get(current_user.tipo_usuario)
            if not next_url or next_url == None:
                time.sleep(0.5)
                flash(
                    'Tipo de usuario no reconocido. Por favor, contacte al administrador.', 'danger')
                return redirect(url_for('users.login'))
        return redirect(next_url)
    if request.method == 'GET':
        return render_template('users/login.html')

    correo = request.form['correo']
    contrasenia = request.form['contrasenia']
    if not correo or not contrasenia:
        flash('Por favor ingrese correo y contraseña', 'warning')
        return redirect(url_for('users.login'))
    try:
        cur = mysql.connection.cursor()
        # Consulta optimizada usando índices
        query = """
            SELECT
                u.id_usuario,
                u.nombre,
                u.correo,
                u.contrasenia,
                t.nombre as tipo_usuario,
                u.imagen_url
            FROM Usuario u
            INNER JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
            WHERE u.correo = %s
            """

        cur.execute(query, (correo,))
        user_data = cur.fetchone()
        # Agregar print para debug
        print("Datos obtenidos:", user_data)
        print("Data type:", type(user_data), "Content:", user_data)
        cur.close()
        if user_data and str(user_data['contrasenia']) == str(contrasenia):
            user = User(
                id_usuario=int(user_data['id_usuario']),
                nombre=str(user_data['nombre']),
                correo=str(user_data['correo']),
                tipo_usuario=str(user_data['tipo_usuario']),
                imagen_url = str(user_data['imagen_url'])
            )
            # Recordar usuario por 7 día
            login_user(user, remember=True, duration=timedelta(days=7))

            flash(f'¡Bienvenido {user.nombre}!', 'success')

            # Obtener la URL a la que el usuario intentaba acceder
            next_url = request.args.get('next')
            if not next_url or not urlparse(next_url).scheme or urlparse(next_url).netloc != request.host:
                user_type_urls = {
                    'Admin': url_for('admin.dashboard'),
                    'Cliente': url_for('users.login'),
                    'Propietario': url_for('owner.dashboard')
                }
                next_url = user_type_urls.get(user.tipo_usuario)
                if not next_url:
                    time.sleep(0.5)
                    flash(
                        'Tipo de usuario no reconocido. Por favor, contacte al administrador.', 'danger')
                    return redirect(url_for('users.login'))
            return redirect(next_url)
        else:
            # Agregar pequeño delay para prevenir enumeración de usuarios
            time.sleep(0.5)
            flash('Usuario no encontrado o contrasenia incorrecta', 'danger')
            return redirect(url_for('users.login'))
    except Exception as e:
        flash('Error al iniciar sesión. Por favor intente más tarde.', 'danger')
        print(f"Error de login: {str(e)}")  # Log del er


@users.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            correo = request.form['correo']
            contrasenia = request.form['contrasenia']
            doc_identidad = request.form['docIdentidad']
            telefono = request.form['telefono']
            direccion = request.form['direccion']
            fecha_ingreso = time.strftime('%Y-%m-%d %H:%M:%S')
            preferencias = ' '
            imagen_file = request.files.get('imagen')
            if imagen_file:
                filename = secure_filename(imagen_file.filename)
                imagen_file.save(f'app/static/img/{filename}')
                imagen_url = f'/static/img/{filename}'
            else:
                imagen_url = '/static/img/default.png'
            
            tipo_usuario = request.form['tipoUsuario']
            tipo_usuario_id = 2 if tipo_usuario == 'Cliente' else 3
            print(imagen_url)
            cur = mysql.connection.cursor()
            # Verificar si el correo ya existe
            cur.execute(
                'SELECT correo FROM Usuario WHERE correo = %s', (correo,))
            if cur.fetchone():
                flash('El correo ya está registrado', 'danger')
                return redirect(url_for('users.add_user'))
            print('*************************')
            cur.execute(
                "INSERT INTO Usuario (nombre,correo,contrasenia,doc_identidad, telefono, direccion, fecha_ingreso, preferencias, imagen_url, Tipo_usuario_id_tipo_u) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (nombre, correo, contrasenia, doc_identidad, telefono, direccion,
                 fecha_ingreso, preferencias, imagen_url, tipo_usuario_id)
            )
            mysql.connection.commit()
            new_user_id = cur.lastrowid
            cur.close()
            print('======================')
            # Crear objeto usuario y hacer login
            user = User(new_user_id, nombre, correo, tipo_usuario, imagen_url)
            login_user(user)

            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('users.login'))
        except Exception as e:
            mysql.connection.rollback()
            # Agrega este print para debug
            print(f"Error al registrar usuario: {str(e)}")
            flash(f'Error al registrar usuario: {str(e)}', 'danger')
            return redirect(url_for('users.add_user'))
        finally:
            if 'cur' in locals():
                cur.close()
    return render_template('users/create_account.html')

@users.route('/profile/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
def config_account(id_usuario):
    cursor = mysql.connection.cursor()
    query = """
    SELECT u.*, t.nombre as tipo_usuario
    FROM Usuario u
    INNER JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
    WHERE u.id_usuario = %s
	"""
    cursor.execute(query, (id_usuario,))
    user = cursor.fetchone()
    cursor.close()
    if request.method == 'GET':
        return render_template('users/config-account.html', user=user)
    else:
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        doc_identidad = request.form['doc_identidad']
        direccion = request.form['direccion']
        imagen_file = request.files.get('imagen')
        if imagen_file:
            filename = secure_filename(imagen_file.filename)
            imagen_file.save(f'app/static/img/{filename}')
            imagen_url = f'/static/img/{filename}'
        else:
            imagen_url = user['imagen_url']
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE Usuario SET 
                    nombre = %s,
                    telefono = %s,
                    doc_identidad = %s,
                    direccion = %s,
                    imagen_url = %s
                WHERE id_usuario = %s
            """, (nombre, telefono, doc_identidad, direccion, imagen_url, id_usuario))
            mysql.connection.commit()
            cursor.close()
            current_user.set_nombre(nombre)
            current_user.set_imagen_url(imagen_url)
            flash('Datos actualizados exitosamente', 'success')
            return redirect(url_for('users.config_account',  id_usuario = id_usuario))
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar datos: {str(e)}")
            flash(f'Error al actualizar datos: {str(e)}', 'danger')
@users.route('/edit_password/<int:id_usuario>', methods = ['POST'])
@login_required
def change_password(id_usuario):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT contrasenia FROM Usuario WHERE id_usuario = %s', (id_usuario,))
        user = cursor.fetchone()
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        if current_password == new_password:
            flash('La nueva contraseña no puede ser igual a la actual', 'warning')
            return redirect(url_for('users.config_account', id_usuario = id_usuario))
        else:
            cursor.execute(
                """
				UPDATE Usuario SET contrasenia = %s WHERE id_usuario = %s
				"""
                , (new_password, id_usuario)
				
			)
            cursor.connection.commit()
            cursor.close()
            flash('Contraseña actualizada exitosamente', 'success')
            return redirect(url_for('users.config_account', id_usuario = id_usuario))
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al actualizar contraseña: {str(e)}")
        flash(f'Error al actualizar contraseña: {str(e)}', 'danger')
        return redirect(url_for('users.config_account', id_usuario = id_usuario))

@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('users.login'))
