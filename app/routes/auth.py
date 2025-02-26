from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pyodbc
from ..config import Config
from ..models.user import User
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app
from ..database import Database
from werkzeug.exceptions import BadRequest, Unauthorized

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return pyodbc.connect(Config.SQLSERVER_CONNECTION)

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.tipo_usuario_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            correo = data.get('correo')
            contrasenia = data.get('contrasenia')
            
            if not correo or not contrasenia:
                return jsonify({
                    'success': False,
                    'message': 'Correo y contraseña son requeridos'
                })
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Modificar la consulta para obtener todos los campos necesarios
            cursor.execute("""
                SELECT 
                    u.id_usuario,
                    u.nombre,
                    u.correo,
                    u.contrasenia,
                    u.imagen_url,
                    t.id_tipo_u,
                    t.nombre as tipo_usuario
                FROM Usuario u
                JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
                WHERE u.correo = ?
            """, (correo,))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                })

            # Verificar la contraseña
            if not check_password_hash(user.contrasenia, contrasenia):
                return jsonify({
                    'success': False,
                    'message': 'Contraseña incorrecta'
                })
            
            # Crear objeto de usuario y hacer login
            user_obj = User(
                id_usuario=user.id_usuario,
                nombre=user.nombre,
                correo=user.correo,
                tipo_usuario=user.tipo_usuario,
                tipo_usuario_id=user.id_tipo_u,
                imagen_url=user.imagen_url
            )
            
            login_user(user_obj)
            
            # Determinar la redirección basada en el tipo de usuario
            redirect_url = url_for('auth.dashboard_propietario' if user.id_tipo_u == 2 
                                 else 'auth.dashboard' if user.id_tipo_u == 3 
                                 else 'main.index')
            
            return jsonify({
                'success': True,
                'redirect': redirect_url
            })
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al procesar el login'
            })
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    # Si es GET, mostrar el formulario de login
    return render_template('auth/login.html')

# Función auxiliar para redirigir según el rol
def redirect_by_role(tipo_usuario_id):
    if tipo_usuario_id == 2:  # Propietario
        return redirect(url_for('auth.dashboard_propietario'))
    elif tipo_usuario_id == 3:  # Administrador
        return redirect(url_for('auth.dashboard'))
    else:  # Cliente
        return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            correo = request.form.get('correo')
            contrasenia = request.form.get('contrasenia')
            doc_identidad = request.form.get('docIdentidad')
            telefono = request.form.get('telefono')
            direccion = request.form.get('direccion')
            tipo_usuario = request.form.get('tipoUsuario')
            imagen_url = request.form.get('imagen_url', 'https://i.pravatar.cc/150')

            # Hash de la contraseña usando el método específico
            hashed_password = generate_password_hash(contrasenia, method='pbkdf2:sha256')
            print(f"Contraseña original: {contrasenia}")  # Debug
            print(f"Contraseña hasheada: {hashed_password}")  # Debug

            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                # Insertar usuario con la contraseña hasheada
                cursor.execute("""
                    INSERT INTO Usuario (
                        nombre, correo, contrasenia, doc_identidad, 
                        telefono, direccion, imagen_url, Tipo_usuario_id_tipo_u
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nombre, correo, hashed_password, doc_identidad, 
                    telefono, direccion, imagen_url, tipo_usuario
                ))
                
                conn.commit()
                print("Usuario registrado exitosamente")

                return jsonify({
                    'success': True,
                    'message': '¡Registro exitoso!',
                    'redirect': url_for('auth.login')
                })

            except Exception as e:
                conn.rollback()
                print(f"Error en registro: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Error al registrar: {str(e)}'
                }), 500

            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            print(f"Error general: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en el servidor: {str(e)}'
            }), 500

    return render_template('auth/create_account.html')

@auth_bp.route('/dashboard_propietario')
@login_required
def dashboard_propietario():
    if not current_user.is_propietario:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('auth.login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener estadísticas
        cursor.execute("""
            SELECT 
                COUNT(id_publicacion) as total_publicaciones,
                SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as publicaciones_activas,
                SUM(CASE WHEN estado = 'Inactivo' THEN 1 ELSE 0 END) as publicaciones_inactivas
            FROM Publicacion 
            WHERE Usuario_id_usuario = ?
        """, (current_user.id_usuario,))
        
        stats = cursor.fetchone()
        
        # Obtener publicaciones recientes
        cursor.execute("""
            SELECT TOP 5 * FROM Publicacion 
            WHERE Usuario_id_usuario = ? 
            ORDER BY fecha_publicacion DESC
        """, (current_user.id_usuario,))
        
        publicaciones_recientes = cursor.fetchall()
        
        return render_template('auth/dashboard_propietario.html',
                             stats=stats,
                             publicaciones_recientes=publicaciones_recientes)
                             
    except Exception as e:
        print(f"Error en dashboard_propietario: {str(e)}")
        flash('Error al cargar el dashboard', 'error')
        return redirect(url_for('auth.login'))
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('auth.login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usuarios,
                SUM(CASE WHEN t.nombre = 'Cliente' THEN 1 ELSE 0 END) as total_clientes,
                SUM(CASE WHEN t.nombre = 'Propietario' THEN 1 ELSE 0 END) as total_propietarios,
                SUM(CASE WHEN t.nombre = 'Administrador' THEN 1 ELSE 0 END) as total_admins
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
        """)
        
        stats = cursor.fetchone()
        
        # Obtener usuarios con más detalles
        cursor.execute("""
            SELECT 
                u.*, 
                t.nombre as tipo_usuario,
                (SELECT COUNT(*) FROM Publicacion p WHERE p.Usuario_id_usuario = u.id_usuario) as total_publicaciones
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
            ORDER BY u.fecha_ingreso DESC
        """)
        
        usuarios = cursor.fetchall()
        
        return render_template('auth/dashboard.html',
                             stats=stats,
                             usuarios=usuarios)
                             
    except Exception as e:
        print(f"Error en dashboard admin: {str(e)}")
        flash('Error al cargar el dashboard', 'error')
        return redirect(url_for('auth.login'))
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Rutas para gestión de usuarios
@auth_bp.route('/usuario/editar/<int:id>', methods=['POST'])
@login_required
def editar_usuario(id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Usuario 
            SET nombre = ?, correo = ?, telefono = ?, direccion = ?
            WHERE id_usuario = ?
        """, (data['nombre'], data['correo'], data['telefono'], data['direccion'], id))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/usuario/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM Usuario WHERE id_usuario = ?", (id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/usuario/<int:id>')
def get_usuario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener datos básicos del usuario
        cursor.execute("""
            SELECT u.*, t.nombre as tipo_usuario 
            FROM Usuario u 
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u 
            WHERE u.id_usuario = ?
        """, (id,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Convertir a diccionario
        usuario_dict = {
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'doc_identidad': usuario.doc_identidad,
            'telefono': usuario.telefono,
            'direccion': usuario.direccion,
            'fecha_ingreso': usuario.fecha_ingreso,
            'preferencias': usuario.preferencias,
            'imagen_url': usuario.imagen_url,
            'tipo_usuario': usuario.tipo_usuario
        }

        # Obtener estadísticas adicionales según el tipo de usuario
        if usuario.tipo_usuario == 'Propietario':
            # Contar propiedades y vehículos
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT v.id_vivienda) as propiedades_count,
                    COUNT(DISTINCT vh.id_vehiculo) as vehiculos_count
                FROM Usuario u
                LEFT JOIN Publicacion p ON u.id_usuario = p.Usuario_id_usuario
                LEFT JOIN Vivienda v ON p.Vivienda_id_vivienda = v.id_vivienda
                LEFT JOIN Vehiculo vh ON p.Vehiculo_id_vehiculo = vh.id_vehiculo
                WHERE u.id_usuario = ?
            """, (id,))
            stats = cursor.fetchone()
            usuario_dict.update({
                'propiedades_count': stats.propiedades_count,
                'vehiculos_count': stats.vehiculos_count
            })
        else:
            # Contar reservas para clientes
            cursor.execute("""
                SELECT COUNT(*) as reservas_count
                FROM Clientes_Potenciales
                WHERE Usuario_id_usuario = ?
            """, (id,))
            stats = cursor.fetchone()
            usuario_dict['reservas_count'] = stats.reservas_count

        return jsonify(usuario_dict)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error al obtener datos del usuario'}), 500
    
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/get_publicaciones', methods=['GET'])
@login_required
def get_publicaciones():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.*, 
                CASE 
                    WHEN p.Vivienda_id_vivienda IS NOT NULL THEN 'Vivienda'
                    WHEN p.Vehiculo_id_vehiculo IS NOT NULL THEN 'Vehículo'
                END as tipo_publicacion,
                COUNT(cp.id_clientes) as total_interesados
            FROM Publicacion p
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = ?
            GROUP BY p.id_publicacion, p.titulo, p.descripcion, p.precio_unitario,
                     p.fecha_publicacion, p.estado, p.distrito, p.direccion,
                     p.latitud, p.longitud, p.imagenes, p.Usuario_id_usuario,
                     p.Vivienda_id_vivienda, p.Vehiculo_id_vehiculo
            ORDER BY p.fecha_publicacion DESC
        """, (current_user.id_usuario,))
        
        publicaciones = [dict(zip([column[0] for column in cursor.description], row)) 
                        for row in cursor.fetchall()]
        
        return jsonify({'success': True, 'publicaciones': publicaciones})
    except Exception as e:
        print(f"Error al obtener publicaciones: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Ruta para actualizar el estado de una publicación
@auth_bp.route('/api/publicacion/<int:id>/estado', methods=['PUT'])
@login_required
def actualizar_estado_publicacion(id):
    try:
        estado = request.json.get('estado')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Publicacion 
            SET estado = ? 
            WHERE id_publicacion = ? AND Usuario_id_usuario = ?
        """, (estado, id, current_user.id_usuario))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Estado actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# Ruta para obtener estadísticas de interesados por mes
@auth_bp.route('/api/estadisticas/interesados', methods=['GET'])
@login_required
def get_estadisticas_interesados():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Últimos 6 meses
        cursor.execute("""
            SELECT 
                MONTH(cp.fecha_contacto) as mes,
                YEAR(cp.fecha_contacto) as anio,
                COUNT(*) as total
            FROM Clientes_Potenciales cp
            JOIN Publicacion p ON cp.Publicacion_id_publicacion = p.id_publicacion
            WHERE p.Usuario_id_usuario = ?
            AND cp.fecha_contacto >= DATEADD(month, -6, GETDATE())
            GROUP BY MONTH(cp.fecha_contacto), YEAR(cp.fecha_contacto)
            ORDER BY anio, mes
        """, (current_user.id_usuario,))
        
        resultados = cursor.fetchall()
        
        # Convertir a formato para el gráfico
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        datos = []
        for mes, anio, total in resultados:
            datos.append({
                'mes': meses[mes-1],
                'anio': anio,
                'total': total
            })
            
        return jsonify({'success': True, 'datos': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# Ruta para obtener detalles de los interesados
@auth_bp.route('/api/interesados', methods=['GET'])
@login_required
def get_interesados():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                cp.id_clientes,
                cp.fecha_contacto,
                cp.mensaje,
                u.nombre as nombre_interesado,
                u.correo as correo_interesado,
                p.titulo as titulo_publicacion,
                p.id_publicacion
            FROM Clientes_Potenciales cp
            JOIN Usuario u ON cp.Usuario_id_usuario = u.id_usuario
            JOIN Publicacion p ON cp.Publicacion_id_publicacion = p.id_publicacion
            WHERE p.Usuario_id_usuario = ?
            ORDER BY cp.fecha_contacto DESC
        """, (current_user.id_usuario,))
        
        interesados = [dict(zip([column[0] for column in cursor.description], row)) 
                      for row in cursor.fetchall()]
        
        return jsonify({'success': True, 'interesados': interesados})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# Ruta para eliminar una publicación
@auth_bp.route('/api/publicacion/<int:id>', methods=['DELETE'])
@login_required
def eliminar_publicacion(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primero eliminamos las referencias en Clientes_Potenciales
        cursor.execute("""
            DELETE FROM Clientes_Potenciales 
            WHERE Publicacion_id_publicacion = ?
        """, (id,))
        
        # Luego eliminamos la publicación
        cursor.execute("""
            DELETE FROM Publicacion 
            WHERE id_publicacion = ? AND Usuario_id_usuario = ?
        """, (id, current_user.id_usuario))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Publicación eliminada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/crear_publicacion', methods=['GET', 'POST'])
@login_required
def crear_publicacion():
    if request.method == 'GET':
        # Obtener tipos de vivienda para el formulario
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_tipo_v, nombre, capacidad, pisos FROM Tipo_vivienda")
        tipos_vivienda = cursor.fetchall()
        
        cursor.execute("SELECT id_ambiente, nombre FROM Ambiente")
        ambientes = cursor.fetchall()
        
        cursor.execute("SELECT id_servicio, nombre FROM Servicio")
        servicios = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('auth/crear_publicacion.html',
                             tipos_vivienda=tipos_vivienda,
                             ambientes=ambientes,
                             servicios=servicios,
                             datetime=datetime)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validar y obtener datos básicos del formulario
        tipo_publicacion = request.form.get('tipo_publicacion')
        titulo = request.form.get('titulo')
        if not titulo:
            return jsonify({'success': False, 'error': 'El título es requerido'})
            
        descripcion = request.form.get('descripcion')
        if not descripcion:
            return jsonify({'success': False, 'error': 'La descripción es requerida'})
            
        precio = request.form.get('precio')
        if not precio:
            return jsonify({'success': False, 'error': 'El precio es requerido'})
            
        distrito = request.form.get('distrito')
        if not distrito:
            return jsonify({'success': False, 'error': 'El distrito es requerido'})
            
        direccion = request.form.get('direccion')
        if not direccion:
            return jsonify({'success': False, 'error': 'La dirección es requerida'})
            
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        if not latitud or not longitud:
            return jsonify({'success': False, 'error': 'La ubicación es requerida'})

        # Procesar imágenes
        imagenes = request.files.getlist('imagenes[]')
        imagen_urls = []
        for imagen in imagenes:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                imagen.save(filepath)
                imagen_urls.append(filepath)

        if tipo_publicacion == 'vivienda':
            try:
                # Validar datos específicos de vivienda
                tipo_vivienda = request.form.get('tipo_vivienda')
                if not tipo_vivienda:
                    return jsonify({'success': False, 'error': 'El tipo de vivienda es requerido'})

                fecha_construccion = request.form.get('fecha_construccion')
                if not fecha_construccion:
                    return jsonify({'success': False, 'error': 'La fecha de construcción es requerida'})

                antiguedad = request.form.get('antiguedad')
                if not antiguedad:
                    return jsonify({'success': False, 'error': 'La antigüedad es requerida'})

                dimensiones = request.form.get('dimensiones')
                if not dimensiones:
                    return jsonify({'success': False, 'error': 'Las dimensiones son requeridas'})

                # Insertar vivienda con formato de fecha corregido
                cursor.execute("""
                    INSERT INTO Vivienda (
                        fecha_construccion, 
                        dimensiones, 
                        antiguedad, 
                        Tipo_vivienda_id
                    ) VALUES (?, ?, ?, ?)
                """, (
                    datetime.strptime(fecha_construccion, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    dimensiones,
                    datetime.strptime(antiguedad, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    int(tipo_vivienda)
                ))
                conn.commit()
                
                # Obtener el ID de la vivienda recién creada
                cursor.execute("SELECT SCOPE_IDENTITY()")
                vivienda_id = int(cursor.fetchone()[0])  # Asegurarnos que sea un entero
                
                # Insertar ambientes seleccionados
                ambientes = request.form.getlist('ambientes[]')
                if ambientes:  # Solo si hay ambientes seleccionados
                    for ambiente_id in ambientes:
                        cursor.execute("""
                            INSERT INTO Ambiente_Vivienda (Ambiente_id, Vivienda_id)
                            VALUES (?, ?)
                        """, (int(ambiente_id), vivienda_id))
                        conn.commit()  # Commit después de cada inserción
                
                # Insertar servicios seleccionados
                servicios = request.form.getlist('servicios[]')
                if servicios:  # Solo si hay servicios seleccionados
                    for servicio_id in servicios:
                        cursor.execute("""
                            INSERT INTO Servicio_Vivienda (Servicio_id, Vivienda_id)
                            VALUES (?, ?)
                        """, (int(servicio_id), vivienda_id))
                        conn.commit()  # Commit después de cada inserción
                
                # Insertar publicación con vivienda
                cursor.execute("""
                    INSERT INTO Publicacion (
                        titulo, descripcion, precio_unitario, distrito, direccion,
                        latitud, longitud, estado, imagenes, Usuario_id_usuario,
                        Vivienda_id_vivienda, fecha_publicacion, Vehiculo_id_vehiculo
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, 'Activo', ?, ?,
                        ?, GETDATE(), NULL
                    )
                """, (
                    titulo, descripcion, float(precio), distrito, direccion,
                    float(latitud), float(longitud), ','.join(imagen_urls), current_user.id_usuario,
                    vivienda_id
                ))
                conn.commit()
                
                return jsonify({'success': True})
                
            except Exception as e:
                print(f"Error al crear publicación: {str(e)}")
                conn.rollback()
                return jsonify({'success': False, 'error': str(e)})
        
        else:  # Tipo vehículo
            # Insertar vehículo
            cursor.execute("""
                INSERT INTO Vehiculo (
                    marca, modelo, anio, placa, color, transmision,
                    cant_combustible, tipo_combustible, kilometraje,
                    Tipo_vechiculo_id, Seguro_id_seguro
                ) VALUES (?, ?, CONVERT(DATE, ?), ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form.get('marca'),
                request.form.get('modelo'),
                request.form.get('anio'),
                request.form.get('placa'),
                request.form.get('color'),
                request.form.get('transmision'),
                request.form.get('cantCombustible'),
                request.form.get('tipoCombustible'),
                request.form.get('kilometraje'),
                int(request.form.get('tipo_vehiculo')),
                int(request.form.get('seguro'))
            ))
            conn.commit()
            
            # Obtener el ID del vehículo recién creado
            cursor.execute("SELECT SCOPE_IDENTITY()")
            vehiculo_id = cursor.fetchone()[0]
            
            # Insertar publicación con vehículo
            cursor.execute("""
                INSERT INTO Publicacion (
                    titulo, descripcion, precio_unitario, distrito, direccion,
                    latitud, longitud, estado, imagenes, Usuario_id_usuario,
                    Vehiculo_id_vehiculo, fecha_publicacion, Vivienda_id_vivienda
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, 'Activo', ?, ?,
                    ?, GETDATE(), NULL
                )
            """, (
                titulo, descripcion, float(precio), distrito, direccion,
                float(latitud), float(longitud), ','.join(imagen_urls), current_user.id_usuario,
                vehiculo_id
            ))
            
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error al crear publicación: {str(e)}")
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/mis_publicaciones')
@login_required
def mis_publicaciones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener todas las publicaciones del usuario actual
        cursor.execute("""
            SELECT 
                p.id_publicacion,
                p.titulo,
                p.descripcion,
                p.precio_unitario,
                p.distrito,
                p.direccion,
                p.estado,
                p.imagenes,
                p.fecha_publicacion,
                CASE 
                    WHEN v.id_vivienda IS NOT NULL THEN 'Vivienda'
                    ELSE 'Vehículo'
                END as tipo_publicacion,
                v.dimensiones,
                tv.nombre as tipo_vivienda,
                COUNT(cp.id_clientes) as total_interesados
            FROM Publicacion p
            LEFT JOIN Vivienda v ON p.Vivienda_id_vivienda = v.id_vivienda
            LEFT JOIN Tipo_vivienda tv ON v.Tipo_vivienda_id = tv.id_tipo_v
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = ?
            GROUP BY 
                p.id_publicacion, p.titulo, p.descripcion, p.precio_unitario,
                p.distrito, p.direccion, p.estado, p.imagenes, p.fecha_publicacion,
                v.id_vivienda, v.dimensiones, tv.nombre
            ORDER BY p.fecha_publicacion DESC
        """, (current_user.id_usuario,))
        
        publicaciones = []
        for row in cursor.fetchall():
            publicacion = {
                'id': row.id_publicacion,
                'titulo': row.titulo,
                'descripcion': row.descripcion,
                'precio': float(row.precio_unitario),
                'distrito': row.distrito,
                'direccion': row.direccion,
                'estado': row.estado,
                'imagenes': row.imagenes.split(',') if row.imagenes else [],
                'fecha': row.fecha_publicacion.strftime('%d/%m/%Y'),
                'tipo': row.tipo_publicacion,
                'dimensiones': row.dimensiones,
                'tipo_vivienda': row.tipo_vivienda,
                'total_interesados': row.total_interesados
            }
            publicaciones.append(publicacion)
            
        return jsonify({
            'success': True,
            'publicaciones': publicaciones
        })
        
    except Exception as e:
        print(f"Error al obtener publicaciones: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })
        
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/config-account', methods=['GET', 'POST'])
@login_required
def config_account():
    print("Accediendo a config-account")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener datos del usuario actual
        cursor.execute("""
            SELECT 
                u.id_usuario,
                u.nombre,
                u.correo,
                u.telefono,
                u.doc_identidad,
                u.direccion,
                u.imagen_url,
                tu.nombre as tipo_usuario
            FROM Usuario u
            JOIN Tipo_usuario tu ON u.Tipo_usuario_id = tu.id_tipo_usuario
            WHERE u.id_usuario = ?
        """, (current_user.id_usuario,))
        
        user_data = cursor.fetchone()
        
        if request.method == 'POST':
            # Lógica para actualizar datos
            nombre = request.form.get('nombre')
            telefono = request.form.get('telefono')
            direccion = request.form.get('direccion')
            doc_identidad = request.form.get('doc_identidad')
            
            # Actualizar datos
            cursor.execute("""
                UPDATE Usuario 
                SET nombre = ?, telefono = ?, direccion = ?, doc_identidad = ?
                WHERE id_usuario = ?
            """, (nombre, telefono, direccion, doc_identidad, current_user.id_usuario))
            
            conn.commit()
            flash('Datos actualizados correctamente', 'success')
            return redirect(url_for('auth.config_account'))
            
        return render_template('auth/config-account.html', user=user_data)
        
    except Exception as e:
        print(f"Error en config_account: {str(e)}")
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('auth.dashboard_propietario'))
        
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('auth.config_account'))
            
        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden', 'error')
            return redirect(url_for('auth.config_account'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar contraseña actual
        cursor.execute("SELECT contrasenia FROM Usuario WHERE id_usuario = ?", 
                      (current_user.id_usuario,))
        stored_password = cursor.fetchone().contrasenia
        
        if not check_password_hash(stored_password, current_password):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('auth.config_account'))
            
        # Actualizar contraseña
        hashed_password = generate_password_hash(new_password)
        cursor.execute("""
            UPDATE Usuario 
            SET contrasenia = ?
            WHERE id_usuario = ?
        """, (hashed_password, current_user.id_usuario))
        
        conn.commit()
        flash('Contraseña actualizada correctamente', 'success')
        
    except Exception as e:
        print(f"Error al cambiar contraseña: {str(e)}")
        flash('Error al cambiar la contraseña', 'error')
        
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('auth.config_account'))
