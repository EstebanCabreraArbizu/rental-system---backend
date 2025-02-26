from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login_manager
import pyodbc
from ..config import Config
from app.database import get_db_connection

class User(UserMixin):
    def __init__(self, id_usuario, nombre, correo, tipo_usuario, tipo_usuario_id, imagen_url=None):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.tipo_usuario = tipo_usuario
        self.tipo_usuario_id = tipo_usuario_id
        self.imagen_url = imagen_url

    def get_id(self):
        return str(self.id_usuario)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.tipo_usuario_id == 3

    @property
    def is_propietario(self):
        return self.tipo_usuario_id == 2

    @property
    def is_cliente(self):
        return self.tipo_usuario_id == 1

    @staticmethod
    def get_by_id(user_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Consulta actualizada para obtener todos los campos necesarios
            cursor.execute("""
                SELECT u.id_usuario, u.nombre, u.correo, t.nombre as tipo_usuario, 
                       t.id_tipo_u as tipo_usuario_id, u.imagen_url
                FROM Usuario u
                JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
                WHERE u.id_usuario = ?
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return User(
                    id_usuario=user.id_usuario,
                    nombre=user.nombre,
                    correo=user.correo,
                    tipo_usuario=user.tipo_usuario,
                    tipo_usuario_id=user.tipo_usuario_id,
                    imagen_url=user.imagen_url
                )
            return None

        except Exception as e:
            print(f"Error al cargar usuario: {str(e)}")
            return None
            
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_email(email):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_usuario, nombre, correo, contrasenia, Tipo_usuario_id_tipo_u 
                FROM Usuario 
                WHERE correo = ?
            """, (email,))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'nombre': user[1],
                    'correo': user[2],
                    'contrasenia': user[3],
                    'tipo_usuario': user[4]
                }
            return None
        except Exception as e:
            print(f"Error al obtener usuario por email: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def from_db(user_data):
        """Crea una instancia de User desde los datos de la base de datos"""
        return User(
            id_usuario=user_data.id_usuario,
            nombre=user_data.nombre,
            correo=user_data.correo,
            tipo_usuario=user_data.tipo_usuario,
            tipo_usuario_id=user_data.id_tipo_u,
            imagen_url=getattr(user_data, 'imagen_url', None)
        )

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
