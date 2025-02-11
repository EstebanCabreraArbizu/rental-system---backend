from app import app
from products import products
from users import users
# app.register_blueprint(products)
app.register_blueprint(users)
# starting the app
if __name__ == "__main__":
    app.run(port=3000, debug=True)
