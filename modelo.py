import datetime
import base64
from flask import render_template, redirect, url_for
import os
import matplotlib.pyplot as plt

def imagenesPermitidas(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ruta_inicio(mysql, session):
   return render_template('index.html')

def ruta_registro():
    return render_template('index.html')  

def ruta_login(mysql, session, request):
   if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
       
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password,))
        account = cur.fetchone()
      
        if account:
            session['logueado'] = True
            session['id'] = account['id']
            session['id_rol'] = account['id_rol']
            cur.execute("INSERT INTO actividad_usuarios (id_usuario, fecha_hora, tipo_movimiento) VALUES (%s, %s, %s)", (session['id'], datetime.datetime.now(), 'iniciar_sesion'))
            mysql.connection.commit()
            if session['id_rol']==1:
                return render_template("admin.html")
            elif session ['id_rol']==2:
                 return redirect(url_for('menu_principal'))
        else:
            return render_template('index.html',mensaje="Usuario o Contraseña Incorrectas")
    
def ruta_hacer_registro(mysql, session, request): 
    name=request.form['txtNombreUsuario']
    correo=request.form['txtCorreo']
    password=request.form['txtPassword']
    avatar =request.files['avatar']
    
    if avatar and imagenesPermitidas(avatar.filename):
        # Leer los datos de la imagen
        contenido_imagen = avatar.read()
        
    # Validar datos de entrada
    if not name or not correo or not password:
        return render_template("index.html", mensaje="LLena campos obligatorios")

    if len(password) < 8:
        return render_template("index.html", mensaje="La contraseña debe tener al menos 8 caracteres")

    if not imagenesPermitidas(avatar.filename):
        return render_template("index.html", mensaje="Formato de imagen no permitido")
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(" INSERT INTO usuarios (name, correo, password, id_rol, avatar) VALUES (%s, %s, %s, %s, %s)",(name,correo,password,2,contenido_imagen))
        mysql.connection.commit()
        
        # Obtener el ID del usuario recién registrado
        cur.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
        usuario_id = cur.fetchone()['id']
        
        # Establecer la sesión con el ID del usuario
        session['id'] = usuario_id
        
        # Registrar la acción en el log
        cur.execute("INSERT INTO actividad_usuarios (id_usuario, fecha_hora, tipo_movimiento) VALUES (%s, %s, %s)",
                    (usuario_id, datetime.datetime.now(), 'registrarse'))
        mysql.connection.commit()
        
        return render_template("index.html", mensaje2="Usuario Registrado Exitosamente")
    except Exception as e:
        error_message = f"Error al registrar usuario: {str(e)}"
        return render_template("index.html", mensaje=error_message)    
    
def obtenerDatosMenu(mysql, session):
    cur = mysql.connection.cursor()

    # Obtener las publicaciones y los datos del usuario actual
    cur.execute('''
        SELECT 
            p.id, 
            p.contenido, 
            p.fecha_publicacion, 
            p.imagen, 
            u.name AS usuario, 
            u.avatar,
            SUM(CASE WHEN r.tipo_reaccion = 'like' THEN 1 ELSE 0 END) AS num_likes,
            SUM(CASE WHEN r.tipo_reaccion = 'love' THEN 1 ELSE 0 END) AS num_loves,
            SUM(CASE WHEN r.tipo_reaccion = 'wow' THEN 1 ELSE 0 END) AS num_wows,
            SUM(CASE WHEN r.tipo_reaccion = 'sad' THEN 1 ELSE 0 END) AS num_sads,
            SUM(CASE WHEN r.tipo_reaccion = 'angry' THEN 1 ELSE 0 END) AS num_angrys,
            GROUP_CONCAT(c.id ORDER BY c.fecha_comentario DESC) AS comentario_ids
        FROM 
            publicaciones p 
        INNER JOIN 
            usuarios u ON p.usuario_id = u.id
        LEFT JOIN 
            reacciones r ON p.id = r.id_publicacion
        LEFT JOIN 
            comentarios c ON p.id = c.id_publicacion
        GROUP BY 
            p.id
        ORDER BY 
            p.fecha_publicacion DESC
    ''')
    publicaciones = cur.fetchall()

    usuario_actual = None
    if is_user_logged_in(session):
        cur.execute('SELECT name, avatar FROM usuarios WHERE id = %s', (session['id'],))
        usuario_actual = cur.fetchone()

        if usuario_actual and usuario_actual['avatar']:
            # Codificar el avatar del usuario en Base64 si existe
            avatar_blob = usuario_actual['avatar']
            encoded_avatar = base64.b64encode(avatar_blob).decode('utf-8')

    # Decodificar los avatares de todos los usuarios y las imágenes de las publicaciones
    for publicacion in publicaciones:
        # Decodificar el avatar si existe
        if publicacion['avatar']:
            try:
                encoded_avatar = base64.b64encode(publicacion['avatar']).decode('utf-8')
                publicacion['avatar'] = f'data:image/jpeg;base64,{encoded_avatar}'
            except Exception as e:
                publicacion['avatar'] = f'Error al cargar el avatar: {str(e)}'

        # Decodificar las imágenes de las publicaciones y convertirlas a Base64
        if publicacion['imagen']:
            try:
                encoded_image = base64.b64encode(publicacion['imagen']).decode('utf-8')
                publicacion['imagen'] = f'data:image/jpeg;base64,{encoded_image}'
            except Exception as e:
                publicacion['imagen'] = f'Error al cargar la imagen: {str(e)}'

        # Obtener los comentarios de la publicación
        if publicacion['comentario_ids']:
            comentario_ids = publicacion['comentario_ids'].split(',')
            comentarios = []
            for comentario_id in comentario_ids:
                cur.execute('''
                    SELECT 
                        c.*, 
                        u.name AS nombre_usuario,
                        u.avatar AS avatar_usuario,
                        c.fecha_comentario
                    FROM 
                        comentarios c 
                    INNER JOIN 
                        usuarios u ON c.id_usuario = u.id
                    WHERE 
                        c.id = %s
                ''', (comentario_id,))
                comentario = cur.fetchone()
                
                # Verificar si el comentario existe antes de agregarlo
                if comentario:
                    # Decodificar la imagen del avatar del usuario que hizo el comentario
                    if comentario['avatar_usuario']:
                        try:
                            encoded_avatar = base64.b64encode(comentario['avatar_usuario']).decode('utf-8')
                            comentario['avatar_usuario'] = f'data:image/jpeg;base64,{encoded_avatar}'
                        except Exception as e:
                            comentario['avatar_usuario'] = f'Error al cargar el avatar: {str(e)}'

                    # Decodificar la imagen del comentario
                    if comentario['imagen']:
                        try:
                            encoded_image = base64.b64encode(comentario['imagen']).decode('utf-8')
                            comentario['imagen'] = f'data:image/jpeg;base64,{encoded_image}'
                        except Exception as e:
                            comentario['imagen'] = f'Error al cargar la imagen: {str(e)}'
                    
                    comentarios.append(comentario)
            publicacion['comentarios'] = comentarios

    cur.close()
    return publicaciones, usuario_actual

def is_user_logged_in(session):
    return 'logueado' in session and session['logueado']

def ruta_cerrar_sesion(mysql, session):
    if 'id' in session:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO actividad_usuarios (id_usuario, fecha_hora, tipo_movimiento) VALUES (%s, %s, %s)",
                    (session['id'], datetime.datetime.now(), 'salida_sesion'))
        mysql.connection.commit()
        session.clear()

    else:
        session.clear()

    return redirect(url_for('inicio'))
    

def ruta_menu_principal(mysql, session):
    if not is_user_logged_in(session):
        return redirect(url_for('login'))
    
    publicaciones, usuario_actual = obtenerDatosMenu(mysql, session)
    return render_template('menu_principal.html', publicaciones=publicaciones, usuario_actual=usuario_actual)


# Función para obtener datos del la ventana mis publicaciones
def get_vmispub_data(mysql, session):
    if is_user_logged_in(session):
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM publicaciones WHERE usuario_id = %s ORDER BY fecha_publicacion DESC', (session['id'],))
        publicaciones = cur.fetchall()
        cur.close()
     # Decodificar las imágenes de las publicaciones y convertirlas a Base64
        for publicacion in publicaciones:
            if publicacion['imagen']:
                try:
                    encoded_image = base64.b64encode(publicacion['imagen']).decode('utf-8')
                    publicacion['imagen'] = f'data:image/jpeg;base64,{encoded_image}'
                except Exception as e:
                    publicacion['imagen'] = f'Error al cargar la imagen: {str(e)}'
        return publicaciones
    
def vnuevapub_route(mysql, session, request):
    if request.method == 'POST':
        contenido = request.form['contenido']
        imagen = request.files['imagen']

       
        if imagen and imagenesPermitidas(imagen.filename):
            imagen_data = imagen.read()
        else:
            imagen_data = None
        
        fecha_publicacion = datetime.datetime.now()
        
        cur = mysql.connection.cursor()
        
        # Ejecutamos la inserción con o sin imagen
        if imagen_data:
            cur.execute(
                "INSERT INTO publicaciones (usuario_id, contenido, fecha_publicacion, imagen) VALUES (%s, %s, %s, %s)",
                (session['id'], contenido, fecha_publicacion, imagen_data)
            )
        else:
            cur.execute(
                "INSERT INTO publicaciones (usuario_id, contenido, fecha_publicacion) VALUES (%s, %s, %s)",
                (session['id'], contenido, fecha_publicacion)
            )

        mysql.connection.commit()
        
        cur.execute(
            "INSERT INTO actividad_usuarios (id_usuario, fecha_hora, tipo_movimiento) VALUES (%s, %s, %s)",
            (session['id'], fecha_publicacion, 'publicar')
        )
        mysql.connection.commit()
        
        if cur.rowcount > 0:
            cur.close()
            return redirect(url_for('menu_principal'))
        else:
            cur.close()
            return "Error: No se pudo insertar la publicación en la base de datos."

    return render_template('VPubNueva.html')

def ruta_mis_publicaciones(mysql, session):
    if not is_user_logged_in(session):
        return redirect(url_for('login'))
    
    publicaciones = get_vmispub_data(mysql, session)
    return render_template('VMisPub.html', publicaciones=publicaciones)

def ruta_borrar_publicacion(mysql, session, request):
    if not is_user_logged_in(session):
        return redirect(url_for('login'))

    publicacion_id = request.form['publicacion_id']

    cur = mysql.connection.cursor()

    # Eliminamos reacciones asociadas a la publicación
    cur.execute('DELETE FROM reacciones WHERE id_publicacion = %s', (publicacion_id,))
    mysql.connection.commit()

    # Eliminamos comentarios asociados a la publicación
    cur.execute('DELETE FROM comentarios WHERE id_publicacion = %s', (publicacion_id,))
    mysql.connection.commit()

    # Eliminamos la publicación
    cur.execute('DELETE FROM publicaciones WHERE id = %s', (publicacion_id,))
    mysql.connection.commit()

    # Eliminamos la actividad del usuario
    cur.execute("INSERT INTO actividad_usuarios (id_usuario, fecha_hora, tipo_movimiento) VALUES (%s, %s, %s)",
                (session['id'], datetime.datetime.now(), 'eliminar'))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('mis_publicaciones'))


def ruta_editar_publicacion(mysql, session, request, publish_id):
    if request.method == 'POST':
        nuevo_contenido = request.form['nuevo_contenido']
        nueva_imagen = request.files['nueva_imagen'] if 'nueva_imagen' in request.files else None
        nueva_fecha = datetime.datetime.now()

        cur = mysql.connection.cursor()
        if nueva_imagen and nueva_imagen.filename != '':
            if imagenesPermitidas(nueva_imagen.filename):
                imagen_data = nueva_imagen.read()
                cur.execute("UPDATE publicaciones SET contenido = %s, fecha_publicacion = %s, imagen = %s WHERE id = %s AND usuario_id = %s",
                            (nuevo_contenido, nueva_fecha, imagen_data, publish_id, session['id']))
                mysql.connection.commit()
            else:
                return "Error: La imagen no se ha cargado correctamente o tiene un formato no permitido."
        else:
            cur.execute("UPDATE publicaciones SET contenido = %s, fecha_publicacion = %s WHERE id = %s AND usuario_id = %s",
                        (nuevo_contenido, nueva_fecha, publish_id, session['id']))
            mysql.connection.commit()

        cur.execute("INSERT INTO actividad_usuarios (id_usuario, fecha_hora, tipo_movimiento) VALUES (%s, %s, %s)",
                    (session['id'], datetime.datetime.now(), 'editar'))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('menu_principal'))
    else:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM publicaciones WHERE id = %s AND usuario_id = %s', (publish_id, session['id'],))
        publicacion = cur.fetchone()
        if publicacion and publicacion['imagen']:
            encoded_image = base64.b64encode(publicacion['imagen']).decode('utf-8')
            publicacion['imagen_decodificada'] = encoded_image
        cur.close()
        return render_template('VPubEdit.html', publicacion=publicacion, id_publicacion=publish_id)

def ruta_agrandar_publicacion(mysql, session, request):
    if 'publicacion_id' in request.form:
        publicacion_id = request.form['publicacion_id']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM publicaciones WHERE id = %s', (publicacion_id,))
        publicacion = cur.fetchone()
        cur.close()

        if publicacion and publicacion['imagen']:
            try:
                encoded_image = base64.b64encode(publicacion['imagen']).decode('utf-8')
                publicacion['imagen'] = f'data:image/jpeg;base64,{encoded_image}'
            except Exception as e:
                publicacion['imagen'] = f'Error al cargar la imagen: {str(e)}'

        return render_template('VPubDetalle.html', publicacion=publicacion)
    else:
        return "Error: No se proporcionó un ID de publicación."


def ruta_reaccionar(mysql, session, request):
    if request.method == 'POST' and is_user_logged_in(session):
        id_publicacion = request.form['id_publicacion']
        tipo_reaccion = request.form['tipo_reaccion']
        id_usuario = session['id']

        # Verificamo si el usuario ya ha reaccionado a esta publicación
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM reacciones WHERE id_publicacion = %s AND id_usuario = %s AND tipo_reaccion = %s", (id_publicacion, id_usuario, tipo_reaccion))
        existing_reaction = cur.fetchone()

        if existing_reaction:
            return redirect(url_for('menu_principal'))
        
        # Insertamos la nueva reacción en la base de datos
        cur.execute("INSERT INTO reacciones (id_publicacion, id_usuario, tipo_reaccion) VALUES (%s, %s, %s)", (id_publicacion, id_usuario, tipo_reaccion))
        
        # Incrementamos el contador de reacciones específico en la tabla publicaciones
        if tipo_reaccion == 'like':
            cur.execute("UPDATE publicaciones SET num_likes = num_likes + 1 WHERE id = %s", (id_publicacion,))
        elif tipo_reaccion == 'love':
            cur.execute("UPDATE publicaciones SET num_loves = num_loves + 1 WHERE id = %s", (id_publicacion,))
        elif tipo_reaccion == 'wow':
            cur.execute("UPDATE publicaciones SET num_wows = num_wows + 1 WHERE id = %s", (id_publicacion,))
        elif tipo_reaccion == 'sad':
            cur.execute("UPDATE publicaciones SET num_sads = num_sads + 1 WHERE id = %s", (id_publicacion,))
        elif tipo_reaccion == 'angry':
            cur.execute("UPDATE publicaciones SET num_angrys = num_angrys + 1 WHERE id = %s", (id_publicacion,))
    
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('menu_principal'))

    return "Error al procesar la solicitud."



def ruta_agregar_comentario(mysql, session, request):
    if request.method == 'POST':
        id_publicacion = request.form['id_publicacion']
        contenido = request.form['contenido']
        imagen = request.files['imagen'] if 'imagen' in request.files else None
        
        # Validamos si se proporcionó una imagen y si tiene el formato correcto
        if imagen:
            if imagenesPermitidas(imagen.filename):
                imagen_data = imagen.read()
            else:
                return "Error: La imagen no tiene un formato permitido."
        else:
            imagen_data = None  
        
        # Fecha y hora actual
        fecha_comentario = datetime.datetime.now()
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO comentarios (id_publicacion, id_usuario, contenido, imagen, fecha_comentario) VALUES (%s, %s, %s, %s, %s)",
                        (id_publicacion, session['id'], contenido, imagen_data, fecha_comentario))
            mysql.connection.commit()
            
            # Verificamos si se insertó correctamente el comentario
            if cur.rowcount > 0:
                cur.close()
                return redirect(url_for('menu_principal'))  
            else:
                cur.close()
                return "Error: No se pudo insertar el comentario en la base de datos."

        except Exception as e:
            return f"Error al agregar el comentario: {str(e)}"
    
    return render_template('VPubNueva.html')  


def ruta_mostrar_perfil(mysql, session):
    if not is_user_logged_in(session):
        return redirect(url_for('login'))  # Redirigir al inicio de sesión si el usuario no está autenticado
    
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT u.*, i.estado, i.musica, i.edad, i.pasatiempos, i.direccion, i.trabajo 
        FROM usuarios u 
        LEFT JOIN informacion_personal i ON u.id = i.usuario_id 
        WHERE u.id = %s
    ''', (session['id'],))
    usuario = cur.fetchone()
    cur.close()

    if usuario:
        if usuario['avatar']:
            try:
                encoded_avatar = base64.b64encode(usuario['avatar']).decode('utf-8')
                usuario['avatar'] = f'data:image/jpeg;base64,{encoded_avatar}'
            except Exception as e:
                usuario['avatar'] = f'Error al cargar el avatar: {str(e)}'

        return render_template('perfil_usuario.html', usuario=usuario)
    else:
        return "Error: No se pudo encontrar la información del usuario."


def ruta_editar_informacion_personal(mysql, session, request):
    if not is_user_logged_in(session):
        return redirect(url_for('login'))

    usuario_id = session['id']
    estado = request.form.get('estado')
    musica = request.form.get('musica')
    edad = request.form.get('edad')
    pasatiempos = request.form.get('pasatiempos')
    direccion = request.form.get('direccion')
    trabajo = request.form.get('trabajo')
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM informacion_personal WHERE usuario_id = %s', (usuario_id,))
    info_personal = cur.fetchone()

    if info_personal:
        cur.execute('''
            UPDATE informacion_personal
            SET estado = %s, musica = %s, edad = %s, pasatiempos = %s, direccion = %s, trabajo = %s
            WHERE usuario_id = %s
        ''', (estado, musica, edad, pasatiempos, direccion, trabajo, usuario_id))
    else:
        cur.execute('''
            INSERT INTO informacion_personal (usuario_id, estado, musica, edad, pasatiempos, direccion, trabajo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (usuario_id, estado, musica, edad, pasatiempos, direccion, trabajo))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('mostrar_perfil'))


def obtener_conteo_publicaciones_por_usuario(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT usuario_id, COUNT(*) as conteo_publicaciones 
        FROM publicaciones 
        GROUP BY usuario_id
    """)
    resultados = cur.fetchall()
    cur.close()
    print("Resultados de conteo de publicaciones:", resultados)  
    return resultados

def obtener_conteo_comentarios_por_usuario(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id_usuario, COUNT(*) as conteo_comentarios 
        FROM comentarios 
        GROUP BY id_usuario
    """)
    resultados = cur.fetchall()
    cur.close()
    print("Resultados de conteo de comentarios:", resultados) 
    return resultados

def ruta_mostrar_grafica(mysql):
    # Obtenemos datos de conteo de publicaciones y comentarios
    conteo_publicaciones = obtener_conteo_publicaciones_por_usuario(mysql)
    conteo_comentarios = obtener_conteo_comentarios_por_usuario(mysql)

   
    usuarios = []
    publicaciones = []
    comentarios = []

    for row in conteo_publicaciones:
        usuario_id = row['usuario_id']
        usuarios.append(usuario_id)
        publicaciones.append(row['conteo_publicaciones'])

    for row in conteo_comentarios:
        usuario_id = row['id_usuario']
        # Verificamos si ya se ha contabilizado el usuario para publicaciones
        if usuario_id not in usuarios:
            usuarios.append(usuario_id)
            publicaciones.append(0)  
        comentarios.append(row['conteo_comentarios'])

    # Alineamos los datos de conteo de comentarios para que coincidan con los usuarios
    for usuario_id in usuarios:
        if usuario_id not in [row['id_usuario'] for row in conteo_comentarios]:
            comentarios.append(0)  

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.bar(usuarios, publicaciones, color='blue', label='Publicaciones')
    plt.bar(usuarios, comentarios, color='green', label='Comentarios')
    plt.xlabel('Usuario')
    plt.ylabel('Cantidad')
    plt.title('Conteo de Publicaciones y Comentarios por Usuario')
    plt.legend()
   
    static_dir = './Proyecto/static'
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Guardamos la gráfica como imagen
    try:
        plt.savefig(os.path.join(static_dir, 'grafica_actividad.png'))
        print("Gráfica guardada correctamente.")
    except Exception as e:
        print("Error al guardar la gráfica:", e)

    return render_template('mostrar_grafica.html')
