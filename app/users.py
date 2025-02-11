from flask import Blueprint, request, render_template, redirect, url_for, flash
from db import mysql

users = Blueprint('users', __name__, template_folder='app/templates')


@users.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuario')
    data = cur.fetchall()
    cur.close()
    return render_template('panel-admin.html', users=data)


@users.route('/login', methods=['GET', 'POST'])
def login():
    print("Método de la petición:", request.method)
    if request.method == 'POST':
        correo = request.form['correo']
        contrasenia = request.form['contrasenia']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM usuario WHERE correo = %s AND contrasenia = %s', (correo, contrasenia))
        data = cur.fetchone()
        cur.close()
        if data:
            return redirect(url_for('users.Index'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('users.login'))

    try:
        return render_template('login.html')
    except Exception as e:
        print("Error al renderizar:", str(e))  # Debug
        return str(e), 500


# @users.route('/add_product', methods=['POST'])
# def add_product():
#     if request.method == 'POST':
#         name = request.form['name']
#         description = request.form['description']
#         category = request.form['category']
#         unit_price = request.form['unit_price']
#         stock = request.form['stock']
#         try:
#             cur = mysql.connection.cursor()
#             cur.execute(
#                 "INSERT INTO users (name,description,category,unit_price,stock) VALUES (%s,%s,%s,%s,%s)",
#                 (name, description, category, unit_price, stock)
#             )
#             mysql.connection.commit()
#             cur.close()
#             flash('Product Added Successfully')
#             return redirect(url_for('users.Index'))
#         except Exception as e:
#             flash(e.args[1])
#             return redirect(url_for('users.Index'))


# @users.route('/edit/<id>', methods=['POST', 'GET'])
# def get_product(id):
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM users WHERE id_products = %s', (id))
#     data = cur.fetchall()
#     cur.close()
#     print(data[0])
#     return render_template('edit-product.html', product=data[0])


# @users.route('/update/<id>', methods=['POST'])
# def update_product(id):
#     if request.method == 'POST':
#         name = request.form['name']
#         description = request.form['description']
#         category = request.form['category']
#         unit_price = request.form['unit_price']
#         stock = request.form['stock']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#             UPDATE users
#             SET name = %s,
#                 description = %s,
#                 category = %s,
#                 unit_price = %s,
#                 stock = %s
#             WHERE id_products = %s
#         """, (name, description, category, unit_price, stock, id))
#         flash('Product Updated Successfully')
#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('users.Index'))


# @users.route('/delete/<string:id>', methods=['POST', 'GET'])
# def delete_product(id):
#     cur = mysql.connection.cursor()
#     print(id)
#     cur.execute('DELETE FROM users WHERE id_products = {0}'.format(id))
#     mysql.connection.commit()
#     cur.close()
#     flash('Product Removed Successfully')
#     return redirect(url_for('users.Index'))
