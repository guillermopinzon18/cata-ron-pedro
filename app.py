from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

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
DATA_FILE = "cata_data.json"

def cargar_datos():
    """Carga los datos del archivo JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    datos = cargar_datos()
    paso_actual = int(request.args.get('paso', 1))
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            return render_template("index.html", 
                                 puntajes=PUNTAJES, 
                                 rones=RONES, 
                                 paso_actual=paso_actual,
                                 error="Por favor ingresa tu nombre")
        
        # Crear estructura de usuario si no existe
        if nombre not in datos:
            datos[nombre] = {}
        
        # Obtener el ron actual basado en el paso
        ron_actual = RONES[paso_actual - 1]
        
        # Guardar las puntuaciones del ron actual
        datos[nombre][ron_actual] = {
            "pureza": int(request.form.get("pureza", 0)),
            "olfato_intensidad": int(request.form.get("olfato_intensidad", 0)),
            "olfato_complejidad": int(request.form.get("olfato_complejidad", 0)),
            "gusto_intensidad": int(request.form.get("gusto_intensidad", 0)),
            "gusto_complejidad": int(request.form.get("gusto_complejidad", 0)),
            "gusto_persistencia": int(request.form.get("gusto_persistencia", 0)),
            "armonia": int(request.form.get("armonia", 0)),
            "timestamp": datetime.now().isoformat()
        }
        
        # Calcular total
        datos[nombre][ron_actual]["total"] = sum([
            datos[nombre][ron_actual][k] for k in datos[nombre][ron_actual] 
            if k not in ["timestamp", "total"]
        ])
        
        # Guardar notas si es el último paso
        if paso_actual == len(RONES):
            datos[nombre]["notas"] = request.form.get("notas", "")
        
        guardar_datos(datos)
        
        # Determinar siguiente acción
        accion = request.form.get("accion")
        if accion == "siguiente" and paso_actual < len(RONES):
            return render_template("index.html", 
                                 puntajes=PUNTAJES, 
                                 rones=RONES, 
                                 paso_actual=paso_actual + 1,
                                 datos=datos,
                                 nombre=nombre,
                                 success=f"Ron {ron_actual} guardado correctamente")
        elif accion == "anterior" and paso_actual > 1:
            return render_template("index.html", 
                                 puntajes=PUNTAJES, 
                                 rones=RONES, 
                                 paso_actual=paso_actual - 1,
                                 datos=datos,
                                 nombre=nombre)
    
    return render_template("index.html", 
                         puntajes=PUNTAJES, 
                         rones=RONES, 
                         paso_actual=paso_actual,
                         datos=datos,
                         nombre=request.args.get('nombre', ''))

@app.route("/resultados")
def resultados():
    """Endpoint para obtener resultados actualizados vía AJAX"""
    datos = cargar_datos()
    return jsonify(datos)

@app.route("/reset")
def reset():
    """Endpoint para limpiar todos los datos (solo para desarrollo)"""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return "Datos limpiados"

if __name__ == "__main__":
    app.run(debug=True)

