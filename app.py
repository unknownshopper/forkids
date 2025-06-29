import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import unicodedata

def slugify(text):
    # Quita acentos y convierte a minúsculas, reemplaza espacios por guion bajo
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text.lower().replace(' ', '_')
    

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pago_info TEXT,
            delivery_info TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def normalizar_categoria(tipo):
    tipo = tipo.strip().lower()
    if tipo in ["evento", "eventos", "salón de eventos", "salones de eventos"]:
        return "Eventos"
    elif tipo in ["guardería", "guarderias"]:
        return "Guardería"
    elif tipo in ["salud y bienestar"]:
        return "Salud y bienestar"
    elif tipo in ["educación", "educacion"]:
        return "Educación"
    else:
        return tipo.capitalize()


def leer_empresas():
    empresas = []
    with open('empresas.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['tipo'] = normalizar_categoria(row['tipo'])
            empresas.append(row)
    return empresas

@app.route('/')
def index():
    empresas = leer_empresas()
    # Obtener categorías únicas (tipo)
    categorias = sorted(set(e['tipo'] for e in empresas))
    categorias_info = [{"nombre": cat, "slug": slugify(cat)} for cat in categorias]
    return render_template('index.html', categorias=categorias_info)    

@app.route('/categoria/<tipo>')
def categoria(tipo):
    empresas = leer_empresas()
    # Filtrar empresas por tipo
    empresas_categoria = [e for e in empresas if e['tipo'] == tipo]
    return render_template('categoria.html', tipo=tipo, empresas=empresas_categoria)

@app.route('/empresa/<id>')
def detalle(id):
    empresas = leer_empresas()
    empresa = next((e for e in empresas if e['id'] == id), None)
    return render_template('detalle.html', empresa=empresa)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        pago_info = request.form.get('pago_info', '')
        delivery_info = request.form.get('delivery_info', '')
        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO usuarios (email, password, pago_info, delivery_info) VALUES (?, ?, ?, ?)',
                (email, password, pago_info, delivery_info)
            )
            conn.commit()
            conn.close()
            flash('Usuario registrado. Inicia sesión.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El email ya está registrado.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Aquí va tu lógica de login (puedes usar el ejemplo anterior)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)