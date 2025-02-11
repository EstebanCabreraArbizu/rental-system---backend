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
        try:
            correo = request.form.get('email')
            contrasenia = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            print(f"\n=== INICIO PROCESO DE LOGIN ===")
            print(f"Email ingresado: {correo}")
            
            # Usar el método del modelo
            user_data = User.get_by_email(correo)
            
            if user_data:
                print("Usuario encontrado:", user_data)
                print("Contraseña almacenada:", user_data['contrasenia'])
                print("Contraseña ingresada:", contrasenia)
                
                # Verificar si la contraseña está hasheada
                if user_data['contrasenia'].startswith('pbkdf2:sha256:'):
                    is_valid = check_password_hash(user_data['contrasenia'], contrasenia)
                else:
                    # Si la contraseña no está hasheada, comparar directamente
                    is_valid = user_data['contrasenia'] == contrasenia
                
                print("¿Contraseña válida?:", is_valid)
                
                if is_valid:
                    user_obj = User(
                        id_usuario=user_data['id'],
                        nombre=user_data['nombre'],
                        correo=user_data['correo'],
                        tipo_usuario=user_data['tipo_usuario']
                    )
                    
                    login_user(user_obj, remember=remember)
                    print("Login exitoso")
                    
                    return jsonify({
                        'success': True,
                        'message': '¡Inicio de sesión exitoso!',
                        'redirect': url_for('auth.dashboard')
                    })
                else:
                    print("Contraseña incorrecta")
                    return jsonify({
                        'success': False,
                        'message': 'Contraseña incorrecta'
                    }), 401
            else:
                print("Usuario no encontrado")
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 404
                
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
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
    if not current_user.is_authenticated:
        flash('Por favor inicia sesión para acceder al dashboard.', 'error')
        return redirect(url_for('auth.login'))
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el usuario aún existe en la base de datos
        cursor.execute("""
            SELECT id_usuario 
            FROM Usuario 
            WHERE id_usuario = ? AND correo = ?
        """, (current_user.id, current_user.correo))
        
        user_exists = cursor.fetchone()
        
        if not user_exists:
            logout_user()
            flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'error')
            return redirect(url_for('auth.login'))
        
        # Obtener estadísticas
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN Tipo_usuario_id_tipo_u = 1 THEN 1 ELSE 0 END) as clientes,
                SUM(CASE WHEN Tipo_usuario_id_tipo_u = 2 THEN 1 ELSE 0 END) as propietarios
            FROM Usuario
        """)
        user_stats = cursor.fetchone()
        
        stats = {
            'total_usuarios': user_stats[0] if user_stats[0] else 0,
            'total_clientes': user_stats[1] if user_stats[1] else 0,
            'total_propietarios': user_stats[2] if user_stats[2] else 0
        }

        # Obtener lista de usuarios
        cursor.execute("""
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
        usuarios = cursor.fetchall()

        return render_template('auth/dashboard.html',
                           stats=stats,
                           usuarios=usuarios,
                           current_user=current_user)

    except Exception as e:
        print(f"Error en dashboard: {str(e)}")  # Debug
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        return redirect(url_for('auth.login'))
    finally:
        if cursor:
            cursor.close()
        if conn:
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
