from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from app.db import mysql

class User(UserMixin):
    def __init__(self, id_usuario, nombre, correo, tipo_usuario):
        self.id = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.tipo_usuario = tipo_usuario
        self._is_authenticated = True  # Agregar esta línea
    @property
    def is_authenticated(self):
        return self._is_authenticated
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT id_usuario, nombre, correo, Tipo_usuario_id_tipo_u 
                FROM Usuario WHERE id_usuario = %s
            """, (user_id,))
            user = cur.fetchone()
            if user:
                return User(
                    id_usuario=user['id_usuario'],
                    nombre=user['nombre'],
                    correo=user['correo'],
                    tipo_usuario=user['Tipo_usuario_id_tipo_u']
                )
            return None
        finally:
            cur.close()

    @staticmethod
    def get_by_email(email):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT u.id_usuario, u.nombre, u.correo, t.nombre as tipo_usuario 
                FROM Usuario u 
                JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u 
                WHERE u.correo = %s
            """, (email,))
            user = cur.fetchone()
            if user:
                return User(
                    id_usuario=user['id_usuario'],
                    nombre=user['nombre'],
                    correo=user['correo'],
                    tipo_usuario=user['tipo_usuario']
                )
            return None
        finally:
            cur.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
