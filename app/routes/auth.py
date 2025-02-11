from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import pyodbc
from ..config import Config
from ..models.user import User
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return pyodbc.connect(Config.SQLSERVER_CONNECTION)

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validación básica
        if not email or not password:
            flash('Por favor ingrese correo y contraseña', 'error')
            return render_template('auth/login.html')
            
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
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
                WHERE u.correo = ?
            """
            
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            
            if user_data:
                # Verificar contraseña
                if user_data.contrasenia == password:  # En producción usar hash
                    user = User(
                        id_usuario=user_data.id_usuario,
                        nombre=user_data.nombre,
                        correo=user_data.correo,
                        tipo_usuario=user_data.tipo_usuario
                    )
                    
                    # Recordar usuario por 7 días
                    login_user(user, remember=True, duration=timedelta(days=7))
                    
                    flash(f'¡Bienvenido {user.nombre}!', 'success')
                    
                    # Obtener la URL a la que el usuario intentaba acceder
                    next_page = request.args.get('next')
                    if not next_page or urlparse(next_page).netloc != '':
                        next_page = url_for('auth.dashboard')
                        
                    return redirect(next_page)
                else:
                    # Agregar pequeño delay para prevenir ataques de fuerza bruta
                    time.sleep(0.5)
                    flash('Contraseña incorrecta', 'error')
            else:
                # Agregar pequeño delay para prevenir enumeración de usuarios
                time.sleep(0.5)
                flash('Usuario no encontrado', 'error')
                
        except Exception as e:
            flash('Error al iniciar sesión. Por favor intente más tarde.', 'error')
            print(f"Error de login: {str(e)}")  # Log del error
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            data = {
                'nombre': request.form.get('nombre')[:10],  # Limitamos a 10 caracteres según la BD
                'correo': request.form.get('correo')[:10],
                'contrasenia': request.form.get('contrasenia')[:15],
                'doc_identidad': request.form.get('docIdentidad')[:10],
                'telefono': request.form.get('telefono')[:11],
                'direccion': request.form.get('direccion')[:30],
                'tipo_usuario': request.form.get('tipoUsuario'),
                'imagen_url': request.files.get('imagen').filename[:20] if request.files.get('imagen') else 'default.jpg'
            }
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Obtener el siguiente ID de usuario
            cursor.execute("SELECT MAX(id_usuario) FROM Usuario")
            max_id = cursor.fetchone()[0]
            next_id = 1 if max_id is None else max_id + 1
            
            # Insertar nuevo usuario
            cursor.execute("""
                INSERT INTO Usuario (
                    id_usuario, nombre, correo, contrasenia, doc_identidad, 
                    telefono, direccion, fecha_ingreso, preferencias, 
                    imagen_url, Tipo_usuario_id_tipo_u
                ) VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?)
            """, (
                next_id,
                data['nombre'],
                data['correo'],
                data['contrasenia'],
                data['doc_identidad'],
                data['telefono'],
                data['direccion'],
                'default',  # preferencias por defecto
                data['imagen_url'],
                int(data['tipo_usuario'])  # Convertir a entero para el tipo de usuario
            ))
            
            conn.commit()
            
            # Crear objeto usuario y hacer login
            user = User(next_id, data['nombre'], data['correo'], data['tipo_usuario'])
            login_user(user)
            
            flash('¡Cuenta creada exitosamente!', 'success')
            return redirect(url_for('auth.admin_dashboard'))
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
            
    return render_template('auth/create_account.html')

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener estadísticas generales
        stats = {}
        
        # Total de usuarios
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN Tipo_usuario_id_tipo_u = 1 THEN 1 ELSE 0 END) as clientes,
                SUM(CASE WHEN Tipo_usuario_id_tipo_u = 2 THEN 1 ELSE 0 END) as propietarios
            FROM Usuario
        """)
        user_stats = cursor.fetchone()
        stats['total_usuarios'] = user_stats[0]
        stats['total_clientes'] = user_stats[1]
        stats['total_propietarios'] = user_stats[2]

        # Obtener lista de clientes
        cursor.execute("""
            SELECT 
                u.id_usuario,
                u.nombre,
                u.correo,
                u.telefono,
                u.direccion,
                u.fecha_ingreso,
                t.nombre as tipo_usuario
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
            WHERE t.nombre = 'Cliente'
            ORDER BY u.fecha_ingreso DESC
        """)
        clientes = cursor.fetchall()

        # Obtener lista de propietarios
        cursor.execute("""
            SELECT 
                u.id_usuario,
                u.nombre,
                u.correo,
                u.telefono,
                u.direccion,
                u.fecha_ingreso,
                t.nombre as tipo_usuario
            FROM Usuario u
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
            WHERE t.nombre = 'Propietario'
            ORDER BY u.fecha_ingreso DESC
        """)
        propietarios = cursor.fetchall()

        return render_template('auth/Panel admin.html',
                           stats=stats,
                           clientes=clientes,
                           propietarios=propietarios,
                           current_user=current_user)

    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        return redirect(url_for('auth.login'))
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
