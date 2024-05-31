from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import spacy
import math
import re

app = Flask(__name__)
socketio = SocketIO(app)

# Cargar el modelo de spaCy en español
try:
    nlp = spacy.load("es_core_news_sm")
except IOError:
    print("No se pudo cargar el modelo 'es_core_news_sm'. Asegúrate de que está instalado correctamente.")
    exit(1)

# Constante de gravedad
G = 9.81

def solve_parabolic_motion(query):
    print(f"Query received: {query}")

    # Extraer el texto dentro de los signos de interrogación
    match = re.search(r'¿(.*?)\?', query)
    if match:
        question = match.group(1).strip()
        print(f"Extracted question: {question}")
    else:
        return {"error": "No se encontró una pregunta válida."}

    data = {
        "altura": None,
        "velocidad": None,
        "angulo": None,
        "tiempo": None,
        "distancia": None,
        "tipo": None,
        "resultado": None
    }

    # Expresiones regulares para extraer los valores numéricos y sus unidades
    patterns = {
        "velocidad": re.compile(r'(\d+\.?\d*)\s*m/s'),
        "angulo": re.compile(r'(\d+\.?\d*)\s*grados'),
        "tiempo": re.compile(r'(\d+\.?\d*)\s*segundos'),
        "altura": re.compile(r'(\d+\.?\d*)\s*metros'),
        "distancia": re.compile(r'(\d+\.?\d*)\s*metros')
    }

    # Buscar y asignar valores en el texto de la pregunta
    for key, pattern in patterns.items():
        matches = pattern.findall(question)
        if matches:
            value = float(matches[-1])
            if key == "altura":
                if "altura" in question.lower() and "alcanzar una distancia horizontal" not in question.lower():
                    data[key] = value
            elif key == "distancia":
                if "distancia" in question.lower():
                    data[key] = value
            elif key != "altura" and key != "distancia":
                data[key] = value
            print(f"{key.capitalize()} detectada: {data[key]}")

    # Determinar el tipo de cálculo basado en la pregunta
    if "alcance horizontal" in question.lower():
        data["tipo"] = "alcance"
    elif "velocidad inicial" in question.lower() and "alcance" in question.lower():
        data["tipo"] = "velocidad_requerida"
    elif "altura máxima" in question.lower():
        data["tipo"] = "max_altura"
    elif "tiempo de vuelo" in question.lower():
        data["tipo"] = "tiempo_vuelo"
    elif "desplazamiento" in question.lower() and "después de" in question.lower():
        data["tipo"] = "desplazamiento"
    elif "altura" in question.lower() and "después de" in question.lower():
        data["tipo"] = "altura_a"

    print(f"Tipo de cálculo detectado: {data['tipo']}")
    print(f"Datos extraídos: {data}")

    try:
        if data["tipo"] == "max_altura" and data["altura"] is not None and data["velocidad"] is not None and data["angulo"] is not None:
            result = max_altura(data["altura"], data["velocidad"], data["angulo"])
        elif data["tipo"] == "tiempo_vuelo" and data["altura"] is not None and data["velocidad"] is not None and data["angulo"] is not None:
            result = tiempo_vuelo(data["altura"], data["velocidad"], data["angulo"])
        elif data["tipo"] == "alcance" and data["altura"] is not None and data["velocidad"] is not None and data["angulo"] is not None:
            result = alcance(data["altura"], data["velocidad"], data["angulo"])
        elif data["tipo"] == "desplazamiento" and data["altura"] is not None and data["velocidad"] is not None and data["angulo"] is not None and data["tiempo"] is not None:
            result = desplazamiento(data["altura"], data["velocidad"], data["angulo"], data["tiempo"])
        elif data["tipo"] == "altura_a" and data["altura"] is not None and data["velocidad"] is not None and data["angulo"] is not None and data["tiempo"] is not None:
            result = altura_a(data["altura"], data["velocidad"], data["angulo"], data["tiempo"])
        elif data["tipo"] == "velocidad_requerida" and data["altura"] is not None and data["angulo"] is not None and data["distancia"] is not None:
            result = velocidad_requerida(data["altura"], data["angulo"], data["distancia"])
        else:
            return {"error": "Faltan datos para realizar el cálculo."}
    except TypeError as e:
        return {"error": "Error en los datos ingresados: {}".format(e)}

    data["resultado"] = f"{result}"
    return data

def max_altura(h0, v0, angulo):
    v0y = v0 * math.sin(math.radians(angulo))
    h_max = h0 + (v0y**2) / (2 * G)
    return f"la altura máxima es de {round(h_max, 2)} metros"

def tiempo_vuelo(h0, v0, angulo):
    v0y = v0 * math.sin(math.radians(angulo))
    t_total = (v0y + math.sqrt(v0y**2 + 2 * G * h0)) / G
    return f"el tiempo de vuelo es de {round(t_total, 2)} segundos"

def alcance(h0, v0, angulo):
    v0x = v0 * math.cos(math.radians(angulo))
    t_total = (v0 * math.sin(math.radians(angulo)) + math.sqrt((v0 * math.sin(math.radians(angulo)))**2 + 2 * G * h0)) / G
    d_total = v0x * t_total
    return f"el alcance es de {round(d_total, 2)} metros"

def desplazamiento(h0, v0, angulo, t):
    v0x = v0 * math.cos(math.radians(angulo))
    x = v0x * t
    return f"el desplazamiento después de {t} segundos es de {round(x, 2)} metros"

def altura_a(h0, v0, angulo, t):
    v0y = v0 * math.sin(math.radians(angulo))
    y = h0 + (v0y * t) - (0.5 * G * t * t)
    return f"la altura después de {t} segundos es de {round(y, 2)} metros"

def velocidad_requerida(h0, angulo, d):
    angulo_rad = math.radians(angulo)
    # Calculamos la velocidad inicial requerida para alcanzar la distancia horizontal dada desde la altura inicial
    v0_squared = (G * d**2) / (2 * (d * math.tan(angulo_rad) + h0) * (math.cos(angulo_rad)**2))
    if v0_squared < 0:
        return "no es posible alcanzar la distancia dada con estos parámetros"
    v0 = math.sqrt(v0_squared)
    return f"la velocidad requerida para alcanzar {d} metros es de {round(v0, 2)} m/s"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('calculate')
def calculate(data):
    query = data['query']
    result = solve_parabolic_motion(query)
    emit('result', result)

if __name__ == '__main__':
    socketio.run(app)
