from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login_manager
import pyodbc
from ..config import Config

class User(UserMixin):
    def __init__(self, id_usuario, nombre, correo, tipo_usuario):
        self.id = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.tipo_usuario = tipo_usuario

    @staticmethod
    def get_by_id(user_id):
        conn = pyodbc.connect(Config.SQLSERVER_CONNECTION)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id_usuario, nombre, correo, Tipo_usuario_id_tipo_u 
                FROM Usuario WHERE id_usuario = ?
            """, (user_id,))
            user = cursor.fetchone()
            if user:
                return User(user[0], user[1], user[2], user[3])
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_email(email):
        conn = pyodbc.connect(Config.SQLSERVER_CONNECTION)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.correo, t.nombre as tipo_usuario 
            FROM Usuario u 
            JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u 
            WHERE u.correo = ?
        """, email)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return User(user[0], user[1], user[2], user[3])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
