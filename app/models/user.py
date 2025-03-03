from flask_login import UserMixin
from app import login_manager
from app.db import mysql

class User(UserMixin):
    def __init__(self, id_usuario, nombre, correo, tipo_usuario, imagen_url):
        self.id = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.tipo_usuario = tipo_usuario
        self.imagen_url = imagen_url
        self._is_authenticated = True  # Agregar esta línea
    @property
    def is_authenticated(self):
        return self._is_authenticated
    def get_id(self):
        return str(self.id)
    def set_nombre(self, nombre):
        self.nombre = nombre
    def set_imagen_url(self, image_url):
        self.imagen_url = image_url
    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
            SELECT
                u.id_usuario,
                u.nombre,
                u.correo,
                u.contrasenia,
                t.nombre as tipo_usuario,
                u.imagen_url
            FROM Usuario u
            INNER JOIN Tipo_usuario t ON u.Tipo_usuario_id_tipo_u = t.id_tipo_u
            WHERE u.id_usuario = %s
            """, (user_id,))
            user = cur.fetchone()
            if user:
                return User(
                    id_usuario=user['id_usuario'],
                    nombre=user['nombre'],
                    correo=user['correo'],
                    tipo_usuario=user['tipo_usuario'],
                    imagen_url=user['imagen_url']
                )
            return None
        finally:
            cur.close()

    @staticmethod
    def get_by_email(email):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT u.id_usuario, u.nombre, u.correo, t.nombre as tipo_usuario, u.imagen_url 
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
                    tipo_usuario=user['tipo_usuario'],
                    imagen_url=user['imagen_url']
                )
            return None
        finally:
            cur.close()

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
