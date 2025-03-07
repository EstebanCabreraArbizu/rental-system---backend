from flask import Blueprint, render_template
from app.db import mysql
from app.models.user import User
import json

client = Blueprint('client', __name__, template_folder='app/templates')
@client.route('/', methods=['GET'])
def publications():
	cursor = mysql.connection.cursor()
	cursor.execute('''
		SELECT p.*, v.*, h.*, u.nombre as nombre_publicante 
		FROM Publicacion p 
		LEFT JOIN Vivienda h ON p.Vivienda_id_vivienda = h.id_vivienda 
		LEFT JOIN Vehiculo v ON p.Vehiculo_id_vehiculo = v.id_vehiculo
		LEFT JOIN Usuario u ON p.Usuario_id_usuario = u.id_usuario
	''')
	pubs = cursor.fetchall()
	for pub in pubs:
		pub['imagenes'] = json.loads(pub['imagenes']) if pub['imagenes'] else []
	cursor.close()
	
	return render_template('clients/index.html', pubs = pubs)