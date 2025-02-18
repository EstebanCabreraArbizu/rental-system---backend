import time
from datetime import timedelta
from urllib.parse import urlparse
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.db import mysql
from app.models.user import User

users = Blueprint('users', __name__, template_folder='app/templates')


@users.route('/')
@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))
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
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('users.dashboard')
            
            return redirect(next_page)
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

@users.route('/dashboard')
@login_required
def dashboard():
    try:
        cur = mysql.connection.cursor()
        
        # Verificar si el usuario aún existe en la base de datos
        cur.execute("""
            SELECT id_usuario 
            FROM Usuario 
            WHERE id_usuario = %s AND correo = %s
        """, (current_user.id, current_user.correo))
        
        user_exists = cur.fetchone()
        
        if not user_exists:
            logout_user()
            flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'error')
            return redirect(url_for('users.login'))
        
		# Obtener estadísticas generales
        
        stats = {}
        print(stats)
        # Total de usuarios
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN Tipo_usuario_id_tipo_u = 1 THEN 1 ELSE 0 END) as clientes,
                SUM(CASE WHEN Tipo_usuario_id_tipo_u = 2 THEN 1 ELSE 0 END) as propietarios
            FROM Usuario
        """)
        user_stats = cur.fetchone()
        print(user_stats)
        print('------------------')
        stats['total_usuarios'] = user_stats['total']
        stats['total_clientes'] = user_stats['clientes']
        stats['total_propietarios'] = user_stats['propietarios']
        # Obtener lista de usuarios
        print('***************************')
        cur.execute("""
            SELECT 
                u.id_usuario,
                u.nombre,
                u.correo,
                u.telefono,
                u.fecha_ingreso,
                t.nombre as tipo_usuario
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
            ORDER BY u.fecha_ingreso DESC
        """)
        usuarios = cur.fetchall()
        
        cur.execute("""
			SELECT
              p.id_publicacion,
              p.titulo,
              p.precio_unitario,
              p.fecha_publicacion,
              u.nombre as propietario
            FROM Publicacion p
            JOIN Usuario u ON p.Usuario_id_usuario = u.id_usuario
	        ORDER BY fecha_publicacion DESC
            
              """)
        publicaciones = cur.fetchall()
        print('***************************')
        return render_template('users/dashboard.html',
                           stats=stats,
                           usuarios=usuarios,
                           publicaciones = publicaciones,
                           current_user=current_user)

    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'danger')
        return render_template('users/dashboard.html', stats={})
    finally:
        cur.close()
        

@users.route('/usuario/<int:id>')
def get_usuario(id):
    try:
        cursor = mysql.connection.cursor()
        
        # Obtener datos básicos del usuario
        cursor.execute("""
            SELECT u.*, t.nombre as tipo_usuario 
            FROM Usuario u 
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u 
            WHERE u.id_usuario = %s
        """, (id,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Convertir a diccionario
        usuario_dict = {
            'id_usuario': usuario['id_usuario'],
			'nombre': usuario['nombre'],
			'correo': usuario['correo'],
			'doc_identidad': usuario['doc_identidad'],
			'telefono': usuario['telefono'],
			'direccion': usuario['direccion'],
			'fecha_ingreso': usuario['fecha_ingreso'],
			'preferencias': usuario['preferencias'],
			'imagen_url': usuario['imagen_url'],
			'tipo_usuario': usuario['Tipo_usuario_id_tipo_u']
        }

        # Obtener estadísticas adicionales según el tipo de usuario
        if usuario['tipo_usuario'] == 'Propietario':
            # Contar propiedades y vehículos
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT v.id_vivienda) as propiedades_count,
                    COUNT(DISTINCT vh.id_vehiculo) as vehiculos_count
                FROM Usuario u
                LEFT JOIN Publicacion p ON u.id_usuario = p.Usuario_id_usuario
                LEFT JOIN Vivienda v ON p.Vivienda_id_vivienda = v.id_vivienda
                LEFT JOIN Vehiculo vh ON p.Vehiculo_id_vehiculo = vh.id_vehiculo
                WHERE u.id_usuario = %s
            """, (id,))
            stats = cursor.fetchone()
            usuario_dict.update({
                'propiedades_count': stats['propiedades_count'],
                'vehiculos_count': stats['vehiculos_count']
            })
        else:
            # Contar reservas para clientes
            cursor.execute("""
                SELECT COUNT(*) as reservas_count
                FROM Clientes_Potenciales
                WHERE Usuario_id_usuario = %s
            """, (id,))
            stats = cursor.fetchone()
            usuario_dict['reservas_count'] = stats['reservas_count']

        return jsonify(usuario_dict)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error al obtener datos del usuario'}), 500
    
    finally:
        cursor.close()

@users.route('/publicacion/<int:id>')
def get_publicacion(id):
    try:
        cursor = mysql.connection.cursor()
        
        # Obtener datos básicos del usuario
        cursor.execute("""
            SELECT p.*, u.nombre as propietario 
            FROM Publicacion p 
            JOIN Usuario u ON p.Usuario_id_usuario = u.id_usuario 
            WHERE p.id_publicacion = %s
        """, (id,))
        
        publicacion = cursor.fetchone()
        
        if not publicacion:
            return jsonify({'error': 'Publicación no encontrada'}), 404
        # Convertir a diccionario
        
        publicacion_dict = {
            'id_publicacion': publicacion['id_publicacion'],
            'titulo': publicacion['titulo'],
            'descripcion': publicacion['descripcion'],
            'precio_unitario': publicacion['precio_unitario'],
            'fecha_publicacion': publicacion['fecha_publicacion'],
            'distrito': publicacion['distrito'],
            'direccion': publicacion['direccion'],
            'latitud': publicacion['latitud'],
            'longitud':publicacion['longitud'],
            'imagenes': publicacion['imagenes'],
            'estado': publicacion['estado'],
            'propietario': publicacion['propietario'],
            'vivienda_registrada': publicacion['Vivienda_id_vivienda'],
            'vehículo_registrado': publicacion['Vehiculo_id_vehiculo']
        }

        return jsonify(publicacion_dict)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error al obtener datos de la publicación'}), 500
    
    finally:
        cursor.close()

@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('users.login'))

# @users.route('/add_product', methods=['POST'])
# def add_product():
#     if request.method == 'POST':
#         name = request.form['name']
#         description = request.form['description']
#         category = request.form['category']
#         unit_price = request.form['unit_price']
#         stock = request.form['stock']
#         try:
#             cur = mysql.connection.cursor()
#             cur.execute(
#                 "INSERT INTO users (name,description,category,unit_price,stock) VALUES (%s,%s,%s,%s,%s)",
#                 (name, description, category, unit_price, stock)
#             )
#             mysql.connection.commit()
#             cur.close()
#             flash('Product Added Successfully')
#             return redirect(url_for('users.Index'))
#         except Exception as e:
#             flash(e.args[1])
#             return redirect(url_for('users.Index'))


# @users.route('/edit/<id>', methods=['POST', 'GET'])
# def get_product(id):
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM users WHERE id_products = %s', (id))
#     data = cur.fetchall()
#     cur.close()
#     print(data[0])
#     return render_template('edit-product.html', product=data[0])


# @users.route('/update/<id>', methods=['POST'])
# def update_product(id):
#     if request.method == 'POST':
#         name = request.form['name']
#         description = request.form['description']
#         category = request.form['category']
#         unit_price = request.form['unit_price']
#         stock = request.form['stock']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#             UPDATE users
#             SET name = %s,
#                 description = %s,
#                 category = %s,
#                 unit_price = %s,
#                 stock = %s
#             WHERE id_products = %s
#         """, (name, description, category, unit_price, stock, id))
#         flash('Product Updated Successfully')
#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('users.Index'))


# @users.route('/delete/<string:id>', methods=['POST', 'GET'])
# def delete_product(id):
#     cur = mysql.connection.cursor()
#     print(id)
#     cur.execute('DELETE FROM users WHERE id_products = {0}'.format(id))
#     mysql.connection.commit()
#     cur.close()
#     flash('Product Removed Successfully')
#     return redirect(url_for('users.Index'))
