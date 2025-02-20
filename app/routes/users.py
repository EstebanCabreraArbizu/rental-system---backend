import time
from datetime import timedelta
from urllib.parse import urlparse
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
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
		        'Cliente': url_for('users.login'),
		        'Propietario': url_for('owner.dashboard')
		    }
            print(current_user.tipo_usuario)
            next_url = user_type_urls.get(current_user.tipo_usuario)
            print('***', next_url, '***')
            if not next_url or next_url == None:
                time.sleep(0.5)
                flash('Tipo de usuario no reconocido. Por favor, contacte al administrador.', 'danger')
                return redirect(url_for('users.login'))
        print('------', next_url)
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
                t.nombre as tipo_usuario
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
                tipo_usuario=str(user_data['tipo_usuario'])
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
                print('***',next_url, '***')
                if not next_url:
                    time.sleep(0.5)
                    flash('Tipo de usuario no reconocido. Por favor, contacte al administrador.', 'danger')
                    return redirect(url_for('users.login'))
            print('------', next_url)
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
            imagen_url = 'imagen_url'
            tipo_usuario = request.form['tipoUsuario']
            
            cur = mysql.connection.cursor()
            # Verificar si el correo ya existe
            cur.execute('SELECT correo FROM Usuario WHERE correo = %s', (correo,))
            if cur.fetchone():
                flash('El correo ya está registrado', 'danger')
                return redirect(url_for('users.create_account'))
			
            # Obtener el siguiente ID de usuario
            cur.execute('SELECT MAX(id_usuario) FROM Usuario')
            result = cur.fetchone()
            max_id = result[0] if result and result[0] is not None else 0
            next_id = max_id + 1
            
            cur.execute(
                "INSERT INTO usuario (nombre,correo,contrasenia,doc_identidad, telefono, direccion, fecha_ingreso, preferencias, imagen_url, Tipo_usuario_id_tipo_u) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (nombre, correo, contrasenia, doc_identidad, telefono, direccion,
                 fecha_ingreso, preferencias, imagen_url, tipo_usuario)
            )
            mysql.connection.commit()
            cur.close()
            # Crear objeto usuario y hacer login
            user = User(next_id,nombre, correo, tipo_usuario)
            login_user(user)
            
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('users.login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al registrar usuario: {str(e)}', 'danger')
            return redirect(url_for('users.add_user'))
        finally:
            if 'cur' in locals():
                cur.close()
    return render_template('users/create_account.html')

@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('users.login'))