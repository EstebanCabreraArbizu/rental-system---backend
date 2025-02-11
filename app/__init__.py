from flask import Flask
from flask_login import LoginManager
from .config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    login_manager.init_app(app)
    
    # Importar el modelo User después de crear login_manager
    from .models.user import User
    
    # Registrar blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app
