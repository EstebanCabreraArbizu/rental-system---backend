from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.db import mysql
import json

owner = Blueprint('owner', __name__, template_folder='app/templates')


@owner.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    if current_user.tipo_usuario != 'Propietario':
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('users.login'))

    try:
        cursor = mysql.connection.cursor()

        # Obtener estadísticas básicas
        stats = {
            'total_publicaciones': 0,
            'total_interesados': 0,
            'publicaciones_activas': 0,
            'publicaciones_inactivas': 0
        }

        # Contar publicaciones y estados
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as activas,
                SUM(CASE WHEN estado = 'Inactivo' THEN 1 ELSE 0 END) as inactivas
            FROM Publicacion
            WHERE Usuario_id_usuario = %s
        """, (current_user.id,))

        row = cursor.fetchone()
        if row:
            stats['total_publicaciones'] = row['total'] or 0
            stats['publicaciones_activas'] = row['activas'] or 0
            stats['publicaciones_inactivas'] = row['inactivas'] or 0

        # Contar total de interesados
        cursor.execute("""
            SELECT COUNT(DISTINCT cp.id_clientes) as total_interesados
            FROM Publicacion p
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = %s
        """, (current_user.id,))
        row = cursor.fetchone()
        if row:
            stats['total_interesados'] = row['total_interesados'] or 0
            
		# Consulta para obtener clientes potenciales
        cursor.execute("""
            SELECT 
                cp.Usuario_id_usuario AS cliente_id,
                u.nombre AS cliente_nombre,
                p.id_publicacion AS publicacion_id,
                p.titulo AS publicacion_titulo
            FROM Clientes_Potenciales cp
            JOIN Publicacion p ON cp.Publicacion_id_publicacion = p.id_publicacion
            JOIN Usuario u ON cp.Usuario_id_usuario = u.id_usuario
            WHERE p.Usuario_id_usuario = %s
        """, (current_user.id,))
            
        clientes = cursor.fetchall()
        # Consulta para obtener publicaciones activas
        cursor.execute("""
            SELECT
                p.id_publicacion,
                p.titulo,
                p.descripcion,
                p.precio_unitario,
                p.fecha_publicacion,
                p.estado,
                p.distrito,
                p.direccion,
                p.imagenes,
                CASE
                    WHEN p.Vivienda_id_vivienda IS NOT NULL THEN 'Vivienda'
                    WHEN p.Vehiculo_id_vehiculo IS NOT NULL THEN 'Vehículo'
                END as tipo_publicacion,
                COUNT(cp.id_clientes) as total_interesados,
                COALESCE(tv.nombre, tve.nombre) as tipo_especifico
            FROM Publicacion p
            LEFT JOIN Vivienda v ON p.Vivienda_id_vivienda = v.id_vivienda
            LEFT JOIN Vehiculo vh ON p.Vehiculo_id_vehiculo = vh.id_vehiculo
            LEFT JOIN Tipo_vivienda tv ON v.Tipo_vivienda_id = tv.id_tipo_v
            LEFT JOIN Tipo_vehiculo tve ON vh.Tipo_vechiculo_id = tve.id_tipo_ve
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = %s AND p.estado = 'Activo'
            GROUP BY
                p.id_publicacion, p.titulo, p.descripcion,
                p.precio_unitario, p.fecha_publicacion, p.estado,
                p.distrito, p.direccion, p.imagenes,
                p.Vivienda_id_vivienda, p.Vehiculo_id_vehiculo,
                tv.nombre, tve.nombre
            ORDER BY p.fecha_publicacion DESC
        """, (current_user.id,))
        publicaciones = []
        for row in cursor.fetchall():
            publicacion = {
                'id_publicacion': row['id_publicacion'],
                'titulo': row['titulo'],
                'descripcion': row['descripcion'],
                'precio_unitario': float(row['precio_unitario']),
                'fecha_publicacion': row['fecha_publicacion'].strftime('%Y-%m-%d %H:%M:%S'),
                'estado': row['estado'],
                'distrito': row['distrito'],
                'direccion': row['direccion'],
                'imagenes': row['imagenes'].split(',') if row['imagenes'] else [],
                'tipo_publicacion': row['tipo_publicacion'],
                'total_interesados': row['total_interesados'],
                'tipo_especifico': row['tipo_especifico']
            }
            publicaciones.append(publicacion)

        print(f"Publicaciones encontradas: {len(publicaciones)}")

        return render_template('owner/dashboard.html',
                               clientes = clientes,
                               publicaciones=publicaciones,
                               stats=stats,
                               current_user=current_user)

    except Exception as e:
        print(f"Error en dashboard: {str(e)}")
        flash('Error al cargar el dashboard', 'danger')
        return redirect(url_for('users.login'))

    finally:
        if cursor:
            cursor.close()


@owner.route('/publicacion/<int:id>')
def get_publication(id):
    try:
        cursor = mysql.connection.cursor()

        # Obtener datos básicos del usuario
        cursor.execute("""
            SELECT p.*, u.nombre as propietario
            FROM Publicacion p
            JOIN Usuario u ON p.Usuario_id_usuario = u.id_usuario
            WHERE p.id_publicacion = %s
        """, (id,))

        publicacion = cursor.fetchone()

        if not publicacion:
            return jsonify({'error': 'Publicación no encontrada'}), 404
        # Convertir a diccionario

        publicacion_dict = {
            'id_publicacion': publicacion['id_publicacion'],
            'titulo': publicacion['titulo'],
            'descripcion': publicacion['descripcion'],
            'precio_unitario': publicacion['precio_unitario'],
            'fecha_publicacion': publicacion['fecha_publicacion'],
            'distrito': publicacion['distrito'],
            'direccion': publicacion['direccion'],
            'latitud': publicacion['latitud'],
            'longitud': publicacion['longitud'],
            'imagenes': publicacion['imagenes'],
            'estado': publicacion['estado'],
            'propietario': publicacion['propietario'],
            'vivienda_registrada': publicacion['Vivienda_id_vivienda'],
            'vehículo_registrado': publicacion['Vehiculo_id_vehiculo']
        }

        return jsonify(publicacion_dict)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error al obtener datos de la publicación'}), 500

    finally:
        cursor.close()


# @owner.route('/update/<id>', methods=['POST'])
# def update_publication(id):
#     if request.method == 'POST':
#         titulo = request.form['titulo']
#         descripcion = request.form['descripcion']
#         precio_unitario = request.form['precio_unitario']
#         fecha_publicacion = request.form['fecha_publicacion']
#         distrito = request.form['distrito']
#         direccion = request.form['direccion']
#         latitud = request.form['latitud']
#         longitud = request.form['longitud']
#         imagenes = request.form['imagenes']
#         estado = request.form['estado']
#         Vivienda_id_vivienda = request.form['Vivienda_id_vivienda']
#         Vehiculo_id_vehiculo = request.form['Vehiculo_id_vehiculo']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#             UPDATE Publicacion
#             SET fecha_publicacion = %s,
#                 titulo = %s,
#                 descripcion = %s,
#                 precio_unitario = %s,
#                 distrito = %s,
#                 direccion = %s,
#                 latitud = %s,
#                 longitud = %s,
# 	            estado = %s,
#                 imagenes = %s,
#                 Usuario_id_usuario = %s,
#                 Vivienda_id_vivienda = %s,
#                 Vehiculo_id_vehiculo = %s
#             WHERE id_publicacion = %s
#         """, (fecha_publicacion, titulo, descripcion, precio_unitario, distrito, direccion, latitud, longitud, estado, imagenes, current_user.id, Vivienda_id_vivienda, Vehiculo_id_vehiculo, id))
#         flash('Product Updated Successfully')
#         mysql.connection.commit()
#         cur.close()
#         return redirect(url_for('owner.dashboard'))

# Ruta para obtener estadísticas de interesados por mes


@owner.route('/estadisticas/interesados', methods=['GET'])
@login_required
def get_estadisticas_interesados():
    try:
        cursor = mysql.connection.cursor()

        # Últimos 6 meses
        cursor.execute("""
            SELECT
                MONTH(cp.fecha_contacto) as mes,
                YEAR(cp.fecha_contacto) as anio,
                COUNT(*) as total
            FROM Clientes_Potenciales cp
            JOIN Publicacion p ON cp.Publicacion_id_publicacion = p.id_publicacion
            WHERE p.Usuario_id_usuario = %s
            AND cp.fecha_contacto >= DATEADD(month, -6, NOW())
            GROUP BY MONTH(cp.fecha_contacto), YEAR(cp.fecha_contacto)
            ORDER BY anio, mes
        """, (current_user.id,))

        resultados = cursor.fetchall()

        # Convertir a formato para el gráfico
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        datos = []
        for mes, anio, total in resultados:
            datos.append({
                'mes': meses[mes-1],
                'anio': anio,
                'total': total
            })

        return jsonify({'success': True, 'datos': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

# Ruta para obtener detalles de los interesados


@owner.route('/interesados', methods=['GET'])
@login_required
def get_interesados():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT
                cp.id_clientes,
                cp.fecha_contacto,
                cp.mensaje,
                u.nombre as nombre_interesado,
                u.correo as correo_interesado,
                p.titulo as titulo_publicacion,
                p.id_publicacion
            FROM Clientes_Potenciales cp
            JOIN Usuario u ON cp.Usuario_id_usuario = u.id_usuario
            JOIN Publicacion p ON cp.Publicacion_id_publicacion = p.id_publicacion
            WHERE p.Usuario_id_usuario = %s
            ORDER BY cp.fecha_contacto DESC
        """, (current_user.id,))

        interesados = [dict(zip([column[0] for column in cursor.description], row))
                       for row in cursor.fetchall()]

        return jsonify({'success': True, 'interesados': interesados})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

# Ruta para eliminar una publicación


@owner.route('/delete/<int:publication_id>', methods=['DELETE'])
@login_required
def delete_publication(publication_id):
    try:
        cursor = mysql.connection.cursor()

        # Primero eliminamos las referencias en Clientes_Potenciales
        cursor.execute("""
            DELETE FROM Clientes_Potenciales
            WHERE Publicacion_id_publicacion = %s
        """, (publication_id,))

        # Luego eliminamos la publicación
        cursor.execute("""
            DELETE FROM Publicacion
            WHERE id_publicacion = %s AND Usuario_id_usuario = %s
        """, (publication_id, current_user.id))
		# Obtener los IDs asociados antes de confirmar la eliminación 
        cursor.execute("SELECT Vivienda_id_vivienda, Vehiculo_id_vehiculo FROM Publicacion WHERE id_publicacion = %s", (publication_id,))
        registro = cursor.fetchone()
        if registro:
            if registro.get('Vivienda_id_vivienda'):
                cursor.execute("DELETE FROM Vivienda WHERE id_vivienda = %s", (registro['Vivienda_id_vivienda'],))
            if registro.get('Vehiculo_id_vehiculo'):
                cursor.execute("DELETE FROM Vehiculo WHERE id_vehiculo = %s", (registro['Vehiculo_id_vehiculo'],))
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Publicación eliminada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()


@owner.route('/add_publication', methods=['GET', 'POST'])
@login_required
def crear_publicacion():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT * FROM Tipo_vivienda")
            tipos_vivienda = cursor.fetchall()
            cursor.execute("SELECT * FROM Ambiente")
            ambientes = cursor.fetchall()
            cursor.execute("SELECT * FROM Servicio")
            servicios = cursor.fetchall()
            cursor.execute("SELECT * FROM Tipo_vehiculo")
            tipos_vehiculo = cursor.fetchall()
            cursor.execute("SELECT * FROM Equipamiento")
            equipamientos = cursor.fetchall()
        except Exception as e:
            print("Error al obtener datos para los formularios: ", str(e))
            tipos_vivienda = ambientes = servicios = tipos_vehiculo = equipamientos = []
        finally:
            cursor.close()

        return render_template('owner/crear_publicacion.html', tipos_vivienda=tipos_vivienda, ambientes=ambientes, servicios=servicios, tipos_vehiculo=tipos_vehiculo, equipamientos=equipamientos)

    try:
        print("=== Iniciando creación de publicación ===")
        print(f"Datos del formulario: {request.form}")
        print(f"Archivos recibidos: {request.files}")

        cursor = mysql.connection.cursor()

        # Obtener datos del formulario
        tipo_publicacion = request.form['tipo_publicacion']
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        distrito = request.form['distrito']
        direccion = request.form['direccion']
        latitud = int(request.form['latitud'])
        longitud = int(request.form['longitud'])
        print(f"""
        Datos recibidos:
        - Tipo: {tipo_publicacion}
        - Título: {titulo}
        - Descripción: {descripcion}
        - Precio: {precio}
        - Distrito: {distrito}
        - Dirección: {direccion}
        """)

        # Procesar imágenes
        imagenes = request.files.getlist('imagenes[]')
        imagen_urls = []
        for imagen in imagenes:
            filename = secure_filename(imagen.filename)
            imagen.save(f'app/static/img/{filename}')
            imagen_urls.append(f'/static/img/{filename}')
        print(f"Imágenes recibidas: {len(imagenes)}")

        # Check if images are valid and not empty
        if not imagenes or any(imagen.filename == '' for imagen in imagenes):
            flash('Por favor, sube imágenes válidas.', 'error')
            return redirect(url_for('owner.crear_publicacion'))

        if tipo_publicacion == 'vivienda':

            # Extraer campos de vivienda
            fecha_construccion = request.form['fecha_construccion']
            dimensiones = request.form['dimensiones']
            antiguedad = request.form['antiguedad']
            tipo_vivienda = request.form['tipo_vivienda']

            print(f"""
            Datos de vivienda:
            - Fecha_construcción: {fecha_construccion}
			- Dimensiones: {dimensiones}
            - Antiguedad: {antiguedad}
            - Tipo_vivienda: {tipo_vivienda}
            """)

            cursor.execute(
                   """
                    INSERT INTO Vivienda (fecha_construccion, dimensiones, antiguedad, Tipo_vivienda_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (fecha_construccion, dimensiones, antiguedad, tipo_vivienda))

            cursor.execute("SELECT LAST_INSERT_ID()")
            vivienda_id = cursor.fetchone()[
                    'LAST_INSERT_ID()'] if 'LAST_INSERT_ID()' in cursor.description[0][0] else cursor.fetchone()[0]
            print(f"Vivienda creada con ID: {vivienda_id}")
            ambientes_sel = request.form.getlist('ambientes[]')
            for ambiente_id in ambientes_sel:
                    cursor.execute("""
                        INSERT INTO Ambiente_Vivienda (Ambiente_id, Vivienda_id)
                        VALUES (%s, %s)
                    """, (ambiente_id, vivienda_id))
            for servicio_id in request.form.getlist('servicios[]'):
                    cursor.execute("""
                        INSERT INTO Servicio_Vivienda (Servicio_id, Vivienda_id)
                        VALUES (%s, %s)
                    """, (servicio_id, vivienda_id))

        else:
            tipo_vehiculo = request.form['tipo_vehiculo']
            marca = request.form['marca']
            modelo = request.form['modelo']
            anio_text = request.form['anio']
            anio = int(anio_text.split('-')[0])
            placa = request.form['placa']
            color = request.form['color']
            transmision = request.form['transmision']
            cant_combustible = request.form['cant_combustible']
            tipo_combustible = request.form['tipo_combustible']
            kilometraje = request.form['kilometraje']
            seguro = request.form['seguro']

            print(f"""
            Datos de vehículo:
            - Tipo vehículo: {tipo_vehiculo}
            - Marca: {marca}
            - Modelo: {modelo}
            """)

            cursor.execute(
                """
                INSERT INTO Vehiculo (
                Tipo_vechiculo_id, marca, modelo, anio, placa, color, transmision,
                cant_combustible, tipo_combustible, kilometraje, Seguro_id_seguro) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (tipo_vehiculo, marca, modelo, anio, placa, color, transmision,
                 cant_combustible, tipo_combustible, kilometraje, seguro))
            print("Se realizó inserción en Vehículo")
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            vehiculo_id = vehiculo_id = cursor.fetchone()['LAST_INSERT_ID()'] if 'LAST_INSERT_ID()' in cursor.description[0][0] else cursor.fetchone()[0]
            print(f"Vehículo creado con ID: {vehiculo_id}")
            equip_sel = request.form.getlist('equipamientos[]')
            for eq in equip_sel:
                cursor.execute(
                    """
                    INSERT INTO Equipamiento_Vehiculo (Vehiculo_id, Equipamiento_id)
                    VALUES (%s, %s)
                    """,
                    (vehiculo_id, eq))

        
        if tipo_publicacion == 'vivienda':
            cursor.execute("""
                    INSERT INTO Publicacion (
                        titulo, descripcion, precio_unitario, fecha_publicacion,
                        estado, latitud, longitud, distrito, direccion, imagenes, Usuario_id_usuario,
                        Vivienda_id_vivienda
                    ) VALUES (%s, %s, %s, NOW(), 'Activo',%s,%s, %s, %s, %s, %s, %s)
                """, (
                    titulo, descripcion, precio,latitud, longitud, distrito, direccion,
                    json.dumps(imagen_urls), current_user.id, vivienda_id
               ))
        else:
            cursor.execute("""
                    INSERT INTO Publicacion (
                        titulo, descripcion, precio_unitario, fecha_publicacion,
                        estado, latitud, longitud, distrito, direccion, imagenes, Usuario_id_usuario,
                        Vehiculo_id_vehiculo
                    ) VALUES (%s, %s, %s, NOW(), 'Activo',%s,%s, %s, %s, %s, %s, %s)
                """, (
                    titulo, descripcion, precio,latitud, longitud, distrito, direccion,
                    json.dumps(imagen_urls), current_user.id, vehiculo_id
                ))

        mysql.connection.commit()
        print("Publicación creada exitosamente")
        return jsonify({'success': True})

    except Exception as e:
        mysql.connection.rollback()
        print(f"Error general al crear publicación: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

    finally:
        if cursor:
            cursor.close()
@owner.route('/publicaciones', methods=['GET'])
@login_required
def get_publicaciones():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT
                p.id_publicacion,
                p.titulo,
                p.descripcion,
                p.precio_unitario,
                p.fecha_publicacion,
                p.estado,
                p.distrito,
                p.direccion,
                p.imagenes,
                CASE WHEN p.Vivienda_id_vivienda IS NOT NULL THEN 'Vivienda'
                     WHEN p.Vehiculo_id_vehiculo IS NOT NULL THEN 'Vehículo'
                END as tipo_publicacion,
                COUNT(cp.id_clientes) as total_interesados
            FROM Publicacion p
            LEFT JOIN Clientes_Potenciales cp ON p.id_publicacion = cp.Publicacion_id_publicacion
            WHERE p.Usuario_id_usuario = %s AND p.estado = 'Activo'
            GROUP BY p.id_publicacion, p.titulo, p.descripcion, p.precio_unitario,
                     p.fecha_publicacion, p.estado, p.distrito, p.direccion, p.imagenes,
                     p.Vivienda_id_vivienda, p.Vehiculo_id_vehiculo
            ORDER BY p.fecha_publicacion DESC
        """, (current_user.id,))
        publicaciones = []
        for row in cursor.fetchall():
            publicacion = {
                'id_publicacion': row['id_publicacion'],
                'titulo': row['titulo'],
                'descripcion': row['descripcion'],
                'precio_unitario': float(row['precio_unitario']),
                'fecha_publicacion': row['fecha_publicacion'].strftime('%Y-%m-%d %H:%M:%S'),
                'estado': row['estado'],
                'distrito': row['distrito'],
                'direccion': row['direccion'],
                'imagenes': json.loads(row['imagenes']) if row['imagenes'] else [],
                'tipo_publicacion': row['tipo_publicacion'],
                'total_interesados': row['total_interesados']
            }
            publicaciones.append(publicacion)

        return jsonify({'success': True, 'publicaciones': publicaciones})
    except Exception as e:
        print(f"Error en get_publicaciones: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()