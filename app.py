from flask import Flask, render_template, request, jsonify, session
import uuid
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Puntuaciones fijas por criterio
PUNTAJES = {
    "pureza": [10, 8, 6, 4, 2],
    "olfato_intensidad": [10, 8, 6, 4, 2],
    "olfato_complejidad": [25, 20, 16, 10, 5],
    "gusto_intensidad": [20, 18, 16, 8, 4],
    "gusto_complejidad": [10, 8, 6, 4, 2],
    "gusto_persistencia": [15, 12, 10, 6, 3],
    "armonia": [10, 8, 6, 4, 2]
}

RONES = ["A", "B", "C", "D"]

# Almacenamiento temporal de datos (en producción usarías una base de datos)
# Por ahora usamos archivos temporales
DATA_FILE = '/tmp/cata_data.json'

def load_session_data():
    """Cargar datos de la sesión desde archivo temporal"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "current_step": 0,
        "users": {},
        "master_control": None
    }

def save_session_data(data):
    """Guardar datos de la sesión en archivo temporal"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

@app.route("/")
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    session_data = load_session_data()
    
    # Si es el primer usuario, se convierte en master
    if not session_data["master_control"]:
        session_data["master_control"] = session['user_id']
        save_session_data(session_data)
    
    is_master = session['user_id'] == session_data["master_control"]
    
    return render_template("index.html", 
                         puntajes=PUNTAJES, 
                         rones=RONES, 
                         current_step=session_data["current_step"],
                         users_data=session_data["users"],
                         user_id=session['user_id'],
                         is_master=is_master)

@app.route("/api/set_name", methods=["POST"])
def set_name():
    data = request.get_json()
    user_id = session.get('user_id')
    nombre = data.get('nombre')
    
    if user_id and nombre:
        session_data = load_session_data()
        
        if user_id not in session_data["users"]:
            session_data["users"][user_id] = {
                "nombre": "",
                "evaluaciones": {},
                "notas": "",
                "connected_at": datetime.now().isoformat()
            }
        
        session_data["users"][user_id]["nombre"] = nombre
        save_session_data(session_data)
        
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error"}), 400

@app.route("/api/submit_evaluation", methods=["POST"])
def submit_evaluation():
    data = request.get_json()
    user_id = session.get('user_id')
    ron = data.get('ron')
    evaluacion = data.get('evaluacion')
    notas = data.get('notas', '')
    
    if user_id and ron and evaluacion:
        session_data = load_session_data()
        
        if user_id not in session_data["users"]:
            session_data["users"][user_id] = {
                "nombre": "",
                "evaluaciones": {},
                "notas": "",
                "connected_at": datetime.now().isoformat()
            }
        
        # Calcular total
        total = sum(evaluacion.values())
        evaluacion['total'] = total
        
        session_data["users"][user_id]["evaluaciones"][ron] = evaluacion
        session_data["users"][user_id]["notas"] = notas
        save_session_data(session_data)
        
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error"}), 400

@app.route("/api/next_step", methods=["POST"])
def next_step():
    user_id = session.get('user_id')
    session_data = load_session_data()
    
    # Solo el master puede cambiar de paso
    if user_id == session_data["master_control"] and session_data["current_step"] < 5:
        session_data["current_step"] += 1
        save_session_data(session_data)
        return jsonify({"status": "success", "current_step": session_data["current_step"]})
    
    return jsonify({"status": "error"}), 403

@app.route("/api/prev_step", methods=["POST"])
def prev_step():
    user_id = session.get('user_id')
    session_data = load_session_data()
    
    # Solo el master puede cambiar de paso
    if user_id == session_data["master_control"] and session_data["current_step"] > 0:
        session_data["current_step"] -= 1
        save_session_data(session_data)
        return jsonify({"status": "success", "current_step": session_data["current_step"]})
    
    return jsonify({"status": "error"}), 403

@app.route("/api/reset_session", methods=["POST"])
def reset_session():
    user_id = session.get('user_id')
    session_data = load_session_data()
    
    # Solo el master puede resetear
    if user_id == session_data["master_control"]:
        new_data = {
            "current_step": 0,
            "users": {},
            "master_control": user_id
        }
        save_session_data(new_data)
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error"}), 403

@app.route("/api/get_data")
def get_data():
    session_data = load_session_data()
    user_id = session.get('user_id')
    is_master = user_id == session_data["master_control"]
    
    return jsonify({
        "current_step": session_data["current_step"],
        "users": session_data["users"],
        "is_master": is_master
    })

if __name__ == '__main__':
    app.run(debug=True)

