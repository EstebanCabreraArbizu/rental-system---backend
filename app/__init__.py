from flask import Flask
from flask_login import LoginManager
from datetime import timedelta
app = Flask(__name__)
app.secret_key = "mysecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'  # Updated to use blueprint route
login_manager.login_message = 'You need to login to access this page.'
login_manager.login_message_category = 'info'

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['SESSION_PROTECTION'] = 'strong'
# Import routes after app initialization to avoid circular imports
from app.routes.users import users
from app.routes.admin import admin
from app.routes.owner import owner
app.register_blueprint(users)
app.register_blueprint(admin, url_prefix = '/admin')
app.register_blueprint(owner, url_prefix = '/owner')