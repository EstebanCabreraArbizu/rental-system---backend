from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from app.db import mysql

owner = Blueprint('owner', __name__, template_folder='app/templates')

@owner.route('/dashboard')
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
		# Total de publicaciones del usuario y sus clientes potenciales
        cur.execute("""
            SELECT 
            (SELECT COUNT(*) FROM Publicacion WHERE Usuario_id_usuario = %s) as total_publicaciones,
            (SELECT COUNT(*) FROM Clientes_potenciales WHERE Usuario_id_usuario = %s) as total_clientes
        """, (current_user.id, current_user.id))
        pub_stats = cur.fetchone()
        print(pub_stats)
        print('------------------')
        stats['total_publicaciones'] = pub_stats['total_publicaciones']
        stats['total_clientes'] = pub_stats['total_clientes']
        # Obtener lista de usuarios
        print('***************************')
        cur.execute("""
            SELECT 
                c.id_clientes,
                c.fecha_contacto,
                c.mensaje,
                c.Usuario_id_usuario as id_u,
                u.nombre,
                c.Publicacion_id_publicacion as id_p
            FROM Clientes_potenciales c
            JOIN Usuario u ON u.id_usuario = c.Usuario_id_usuario
            JOIN Publicacion p ON p.id_publicacion = c.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = %s
            ORDER BY c.fecha_contacto DESC
        """, (current_user.id,))
        clientes = cur.fetchall()
        
        cur.execute("""
			SELECT
              p.id_publicacion,
              p.titulo,
              p.precio_unitario,
              p.fecha_publicacion
            FROM Publicacion p
            WHERE p.Usuario_id_usuario = %s
	        ORDER BY fecha_publicacion DESC
            
              """, (current_user.id,))
        publicaciones = cur.fetchall()
        print('***************************')
        return render_template('owner/dashboard.html',
                           stats=stats,
                           clientes=clientes,
                           publicaciones = publicaciones,
                           current_user=current_user)

    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'danger')
        return render_template('owner/dashboard.html', stats={})
    finally:
        cur.close()
        

@owner.route('/publicacion/<int:id>')
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
