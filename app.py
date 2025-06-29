from flask import Flask, render_template
import csv

app = Flask(__name__)

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
    return render_template('index.html', categorias=categorias)

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

if __name__ == '__main__':
    app.run(debug=True)