from flask import Flask, render_template, redirect, request, url_for
from flask_mysqldb import MySQL
from modelo import *
from flask import session

app = Flask(__name__,template_folder='template')
app.secret_key = "Holahshjendhbhgbdghxbs"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'brenda'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'login'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def inicio():
    return ruta_inicio(mysql, session)

@app.route('/registro')
def registro():
    return ruta_registro()

@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    return ruta_login(mysql, session, request)

@app.route('/crear-registro', methods=["POST"])
def hacer_registro(): 
    return ruta_hacer_registro(mysql, session, request)

@app.route('/nueva-publicacion', methods=['GET', 'POST'])
def nueva_publicacion():
    return vnuevapub_route(mysql, session, request)

@app.route('/logout')
def cerrar_sesion():
    return ruta_cerrar_sesion(mysql, session)

@app.route('/menu-principal')
def menu_principal():
    return ruta_menu_principal(mysql, session)

@app.route('/VMisPub')
def mis_publicaciones():
    return ruta_mis_publicaciones(mysql, session)

@app.route('/borrar-publicacion', methods=['POST'])
def borrar_publicacion():
    return ruta_borrar_publicacion(mysql, session, request)

@app.route('/editar_publicacion/<int:id_publicacion>', methods=["GET", "POST"])
def editar_publicacion(id_publicacion):
    return ruta_editar_publicacion(mysql, session, request, id_publicacion)

@app.route('/agrandar-publicacion', methods=["POST"])
def agrandar_publicacion():
    return ruta_agrandar_publicacion(mysql, session, request)

@app.route('/ruta-reaccionar', methods=['POST'])
def reaccionar():
    return ruta_reaccionar(mysql, session, request)

@app.route('/agregar-comentario', methods=['POST'])
def agregar_comentario():
    return ruta_agregar_comentario(mysql, session, request)

@app.route('/mostrar-perfil')
def mostrar_perfil():
    return ruta_mostrar_perfil(mysql, session)

@app.route('/editar-informacion-personal', methods=['POST'])
def editar_informacion_personal():
    return ruta_editar_informacion_personal(mysql, session, request)

@app.route('/mostrar-grafica')
def mostrar_grafica():
    return ruta_mostrar_grafica(mysql)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
