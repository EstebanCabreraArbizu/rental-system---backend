from flask import Flask
from flask_login import LoginManager
from .config import Config
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    login_manager.init_app(app)
    
    # Registrar blueprints
    from .routes import auth
    app.register_blueprint(auth.auth_bp, url_prefix='/')
    
    # Crear carpetas necesarias
    for folder in ['static', 'templates']:
        os.makedirs(os.path.join(app.root_path, folder), exist_ok=True)
    
    return app

# Importar el modelo User y la función load_user después de crear login_manager
from .models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
