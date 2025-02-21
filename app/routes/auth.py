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

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return pyodbc.connect(Config.SQLSERVER_CONNECTION)

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.tipo_usuario_id == 2:  # Propietario
            return redirect(url_for('auth.dashboard_propietario'))
        elif current_user.tipo_usuario_id == 3:  # Administrador
            return redirect(url_for('auth.dashboard'))
        else:  # Cliente u otros
            return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            correo = data.get('correo')
            contrasenia = data.get('contrasenia')
        else:
            correo = request.form.get('correo')
            contrasenia = request.form.get('contrasenia')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT u.*, t.id_tipo_u, t.nombre as tipo_usuario 
                FROM Usuario u 
                JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u 
                WHERE u.correo = ?
            """, (correo,))
            
            user = cursor.fetchone()
            
            if user and check_password_hash(user.contrasenia, contrasenia):
                user_obj = User(
                    id_usuario=user.id_usuario,
                    nombre=user.nombre,
                    correo=user.correo,
                    tipo_usuario=user.tipo_usuario,
                    tipo_usuario_id=user.id_tipo_u,
                    imagen_url=getattr(user, 'imagen_url', None)
                )
                
                login_user(user_obj)

                if request.is_json:
                    if user.id_tipo_u == 2:  # Propietario
                        return jsonify({'success': True, 'redirect': url_for('auth.dashboard_propietario')})
                    elif user.id_tipo_u == 3:  # Administrador
                        return jsonify({'success': True, 'redirect': url_for('auth.dashboard')})
                    else:  # Cliente
                        return jsonify({'success': True, 'redirect': url_for('main.index')})
                else:
                    if user.id_tipo_u == 2:
                        return redirect(url_for('auth.dashboard_propietario'))
                    elif user.id_tipo_u == 3:
                        return redirect(url_for('auth.dashboard'))
                    else:
                        return redirect(url_for('main.index'))
            
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Correo o contraseña incorrectos'
                })
            else:
                flash('Correo o contraseña incorrectos', 'error')
                return redirect(url_for('auth.login'))

        except Exception as e:
            print(f"Error en login: {str(e)}")
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': f'Error al iniciar sesión: {str(e)}'
                })
            else:
                flash(f'Error al iniciar sesión: {str(e)}', 'error')
                return redirect(url_for('auth.login'))
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    return render_template('auth/login.html')

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
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.tipo_usuario_id != 2:  # 2 = Propietario
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener estadísticas básicas
        stats = {
            'total_publicaciones': 0,
            'total_interesados': 0,
            'publicaciones_activas': 0,
            'publicaciones_inactivas': 0
        }
        
        # Contar publicaciones y estados
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as activas,
                SUM(CASE WHEN estado = 'Inactivo' THEN 1 ELSE 0 END) as inactivas
            FROM Publicacion 
            WHERE Usuario_id_usuario = ?
        """, (current_user.id_usuario,))
        
        row = cursor.fetchone()
        if row:
            stats['total_publicaciones'] = row[0] or 0
            stats['publicaciones_activas'] = row[1] or 0
            stats['publicaciones_inactivas'] = row[2] or 0
        
        # Contar total de interesados
        cursor.execute("""
            SELECT COUNT(DISTINCT cp.id_clientes)
            FROM Publicacion p
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = ?
        """, (current_user.id_usuario,))
        
        stats['total_interesados'] = cursor.fetchone()[0] or 0
        
        # Consulta para obtener publicaciones activas
        cursor.execute("""
            SELECT 
                p.id_publicacion,
                p.titulo,
                p.descripcion,
                p.precio_unitario,
                p.fecha_publicacion,
                p.estado,
                p.distrito,
                p.direccion,
                p.imagenes,
                CASE 
                    WHEN p.Vivienda_id_vivienda IS NOT NULL THEN 'Vivienda'
                    WHEN p.Vehiculo_id_vehiculo IS NOT NULL THEN 'Vehículo'
                END as tipo_publicacion,
                COUNT(cp.id_clientes) as total_interesados,
                COALESCE(tv.nombre, tve.nombre) as tipo_especifico
            FROM Publicacion p
            LEFT JOIN Vivienda v ON p.Vivienda_id_vivienda = v.id_vivienda
            LEFT JOIN Vehiculo vh ON p.Vehiculo_id_vehiculo = vh.id_vehiculo
            LEFT JOIN Tipo_vivienda tv ON v.Tipo_vivienda_id = tv.id_tipo_v
            LEFT JOIN Tipo_vehiculo tve ON vh.Tipo_vechiculo_id = tve.id_tipo_ve
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = ? AND p.estado = 'Activo'
            GROUP BY 
                p.id_publicacion, p.titulo, p.descripcion, 
                p.precio_unitario, p.fecha_publicacion, p.estado,
                p.distrito, p.direccion, p.imagenes,
                p.Vivienda_id_vivienda, p.Vehiculo_id_vehiculo,
                tv.nombre, tve.nombre
            ORDER BY p.fecha_publicacion DESC
        """, (current_user.id_usuario,))
        
        publicaciones = []
        for row in cursor.fetchall():
            publicacion = {
                'id_publicacion': row.id_publicacion,
                'titulo': row.titulo,
                'descripcion': row.descripcion,
                'precio_unitario': float(row.precio_unitario),
                'fecha_publicacion': row.fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S'),
                'estado': row.estado,
                'distrito': row.distrito,
                'direccion': row.direccion,
                'imagenes': row.imagenes.split(',') if row.imagenes else [],
                'tipo_publicacion': row.tipo_publicacion,
                'total_interesados': row.total_interesados,
                'tipo_especifico': row.tipo_especifico
            }
            publicaciones.append(publicacion)
        
        print(f"Publicaciones encontradas: {len(publicaciones)}")
        
        return render_template('auth/dashboard_propietario.html',
                             publicaciones=publicaciones,
                             stats=stats,
                             current_user=current_user)
    
    except Exception as e:
        print(f"Error en dashboard_propietario: {str(e)}")
        flash('Error al cargar el dashboard', 'error')
        return redirect(url_for('auth.login'))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.tipo_usuario != 'Administrador':
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('auth.login'))  # Cambiado de 'main.index' a 'auth.login'
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener estadísticas para el dashboard
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usuarios,
                SUM(CASE WHEN t.nombre = 'Cliente' THEN 1 ELSE 0 END) as total_clientes,
                SUM(CASE WHEN t.nombre = 'Propietario' THEN 1 ELSE 0 END) as total_propietarios
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
        """)
        
        stats = cursor.fetchone()
        
        # Obtener lista de usuarios
        cursor.execute("""
            SELECT u.*, t.nombre as tipo_usuario
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
        """)
        
        usuarios = cursor.fetchall()
        
        return render_template('auth/dashboard.html', 
                             stats=stats,
                             usuarios=usuarios)
    
    except Exception as e:
        print(f"Error en dashboard: {str(e)}")
        flash('Error al cargar el dashboard', 'error')
        return redirect(url_for('auth.login'))  # Cambiado de 'main.index' a 'auth.login'
    
    finally:
        cursor.close()
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
        return render_template('auth/crear_publicacion.html')
    
    try:
        print("=== Iniciando creación de publicación ===")
        print(f"Datos del formulario: {request.form}")
        print(f"Archivos recibidos: {request.files}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener datos del formulario
        tipo_publicacion = request.form.get('tipo_publicacion')
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
        distrito = request.form.get('distrito')
        direccion = request.form.get('direccion')
        
        print(f"""
        Datos recibidos:
        - Tipo: {tipo_publicacion}
        - Título: {titulo}
        - Descripción: {descripcion}
        - Precio: {precio}
        - Distrito: {distrito}
        - Dirección: {direccion}
        """)
        
        # Procesar imágenes
        imagenes = request.files.getlist('imagenes[]')
        imagen_urls = []
        print(f"Imágenes recibidas: {len(imagenes)}")
        
        if tipo_publicacion == 'vivienda':
            tipo_vivienda = request.form.get('tipo_vivienda')
            habitaciones = request.form.get('habitaciones')
            banos = request.form.get('banos')
            
            print(f"""
            Datos de vivienda:
            - Tipo vivienda: {tipo_vivienda}
            - Habitaciones: {habitaciones}
            - Baños: {banos}
            """)
            
            try:
                cursor.execute("""
                    INSERT INTO Vivienda (Tipo_vivienda_id, habitaciones, banos)
                    VALUES (?, ?, ?)
                """, (tipo_vivienda, habitaciones, banos))
                conn.commit()
                
                cursor.execute("SELECT @@IDENTITY")
                vivienda_id = cursor.fetchone()[0]
                print(f"Vivienda creada con ID: {vivienda_id}")
                
            except Exception as e:
                print(f"Error al insertar vivienda: {str(e)}")
                raise
                
        else:
            tipo_vehiculo = request.form.get('tipo_vehiculo')
            marca = request.form.get('marca')
            modelo = request.form.get('modelo')
            
            print(f"""
            Datos de vehículo:
            - Tipo vehículo: {tipo_vehiculo}
            - Marca: {marca}
            - Modelo: {modelo}
            """)
            
            try:
                cursor.execute("""
                    INSERT INTO Vehiculo (Tipo_vechiculo_id, marca, modelo)
                    VALUES (?, ?, ?)
                """, (tipo_vehiculo, marca, modelo))
                conn.commit()
                
                cursor.execute("SELECT @@IDENTITY")
                vehiculo_id = cursor.fetchone()[0]
                print(f"Vehículo creado con ID: {vehiculo_id}")
                
            except Exception as e:
                print(f"Error al insertar vehículo: {str(e)}")
                raise
        
        # Insertar publicación
        try:
            if tipo_publicacion == 'vivienda':
                cursor.execute("""
                    INSERT INTO Publicacion (
                        titulo, descripcion, precio_unitario, fecha_publicacion,
                        estado, distrito, direccion, imagenes, Usuario_id_usuario,
                        Vivienda_id_vivienda
                    ) VALUES (?, ?, ?, GETDATE(), 'Activo', ?, ?, ?, ?, ?)
                """, (
                    titulo, descripcion, precio, distrito, direccion,
                    ','.join(imagen_urls), current_user.id_usuario, vivienda_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO Publicacion (
                        titulo, descripcion, precio_unitario, fecha_publicacion,
                        estado, distrito, direccion, imagenes, Usuario_id_usuario,
                        Vehiculo_id_vehiculo
                    ) VALUES (?, ?, ?, GETDATE(), 'Activo', ?, ?, ?, ?, ?)
                """, (
                    titulo, descripcion, precio, distrito, direccion,
                    ','.join(imagen_urls), current_user.id_usuario, vehiculo_id
                ))
            
            conn.commit()
            print("Publicación creada exitosamente")
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"Error al insertar publicación: {str(e)}")
            raise
        
    except Exception as e:
        conn.rollback()
        print(f"Error general al crear publicación: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
