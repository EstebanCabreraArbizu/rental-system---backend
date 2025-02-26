from flask import Flask, render_template
from flask_login import LoginManager
from .config import Config
import os
import logging
from logging.handlers import RotatingFileHandler

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
    login_manager.init_app(app)
    
    # Registrar blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Crear carpetas necesarias
    for folder in ['static', 'templates']:
        os.makedirs(os.path.join(app.root_path, folder), exist_ok=True)
    
    # Manejador de errores global
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/rentall.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('RentAll startup')

    return app

# Importar el modelo User y la función load_user después de crear login_manager
from .models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
