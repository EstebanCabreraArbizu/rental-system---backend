from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_required, current_user
from app.db import mysql

admin = Blueprint('admin', __name__, template_folder='app/templates')

@admin.route('/dashboard')
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
        return render_template('admin/dashboard.html',
                           stats=stats,
                           usuarios=usuarios,
                           publicaciones = publicaciones,
                           current_user=current_user)

    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'danger')
        return render_template('admin/dashboard.html', stats={})
    finally:
        cur.close()
        

@admin.route('/usuario/<int:id>')
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

@admin.route('/publicacion/<int:id>')
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
