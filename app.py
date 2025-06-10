from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
socketio = SocketIO(app, cors_allowed_origins="*")

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

# Almacenamiento temporal de datos de la sesión
session_data = {
    "current_step": 0,  # 0: inicio, 1-4: rones A-D, 5: resumen final
    "users": {},  # {user_id: {nombre, evaluaciones: {}, notas: ""}}
    "master_control": None  # ID del usuario que controla la navegación
}

@app.route("/")
def index():
    return render_template("index.html", 
                         puntajes=PUNTAJES, 
                         rones=RONES, 
                         current_step=session_data["current_step"],
                         users_data=session_data["users"])

@socketio.on('connect')
def on_connect():
    user_id = str(uuid.uuid4())
    session_data["users"][user_id] = {
        "nombre": "",
        "evaluaciones": {},
        "notas": "",
        "connected_at": datetime.now().isoformat()
    }
    
    # Si es el primer usuario, se convierte en master
    if session_data["master_control"] is None:
        session_data["master_control"] = user_id
        emit('master_status', {'is_master': True})
    else:
        emit('master_status', {'is_master': False})
    
    emit('user_id', {'user_id': user_id})
    emit('step_update', {'current_step': session_data["current_step"]})
    emit('users_update', {'users': session_data["users"]})

@socketio.on('disconnect')
def on_disconnect():
    # Limpiar usuario desconectado
    pass

@socketio.on('set_name')
def handle_set_name(data):
    user_id = data['user_id']
    nombre = data['nombre']
    
    if user_id in session_data["users"]:
        session_data["users"][user_id]["nombre"] = nombre
        socketio.emit('users_update', {'users': session_data["users"]})

@socketio.on('submit_evaluation')
def handle_evaluation(data):
    user_id = data['user_id']
    ron = data['ron']
    evaluacion = data['evaluacion']
    notas = data.get('notas', '')
    
    if user_id in session_data["users"]:
        if 'evaluaciones' not in session_data["users"][user_id]:
            session_data["users"][user_id]["evaluaciones"] = {}
        
        # Calcular total
        total = sum(evaluacion.values())
        evaluacion['total'] = total
        
        session_data["users"][user_id]["evaluaciones"][ron] = evaluacion
        session_data["users"][user_id]["notas"] = notas
        
        socketio.emit('users_update', {'users': session_data["users"]})

@socketio.on('next_step')
def handle_next_step(data):
    user_id = data['user_id']
    
    # Solo el master puede cambiar de paso
    if user_id == session_data["master_control"] and session_data["current_step"] < 5:
        session_data["current_step"] += 1
        socketio.emit('step_update', {'current_step': session_data["current_step"]})

@socketio.on('prev_step')
def handle_prev_step(data):
    user_id = data['user_id']
    
    # Solo el master puede cambiar de paso
    if user_id == session_data["master_control"] and session_data["current_step"] > 0:
        session_data["current_step"] -= 1
        socketio.emit('step_update', {'current_step': session_data["current_step"]})

@socketio.on('reset_session')
def handle_reset():
    session_data["current_step"] = 0
    session_data["users"] = {}
    session_data["master_control"] = None
    socketio.emit('session_reset')

if __name__ == '__main__':
    socketio.run(app, debug=True)

