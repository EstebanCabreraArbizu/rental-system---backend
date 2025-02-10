from app import app
from products import products

app.register_blueprint(products)

# starting the app
if __name__ == "__main__":
    app.run(port=3000, debug=True)
