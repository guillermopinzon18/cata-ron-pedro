from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cata_ron_secret_key_2024'  # Necesario para sessions

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
DATA_FILE = "/tmp/cata_data.json"  # Usar directorio temporal en Vercel

# Variable global para almacenar datos en memoria como respaldo
DATOS_MEMORIA = {}

def cargar_datos():
    """Carga los datos del archivo JSON o de memoria"""
    global DATOS_MEMORIA
    
    # Intentar cargar desde archivo
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                DATOS_MEMORIA.update(data)  # Actualizar memoria
                return data
        except Exception as e:
            print(f"Error cargando archivo: {e}")
    
    # Si no se puede cargar desde archivo, usar memoria
    return DATOS_MEMORIA.copy()

def guardar_datos(datos):
    """Guarda los datos en archivo y memoria"""
    global DATOS_MEMORIA
    
    # Siempre guardar en memoria
    DATOS_MEMORIA.update(datos)
    
    # Intentar guardar en archivo (puede fallar en Vercel)
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: No se pudo guardar en archivo: {e}")
        # No importa si falla, los datos están en memoria

def validar_numero(valor, default=0):
    """Convierte un valor a entero de forma segura"""
    try:
        if valor is None or valor == "":
            return default
        return int(float(valor))
    except (ValueError, TypeError):
        return default

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        datos = cargar_datos()
        paso_actual = int(request.args.get('paso', 1))
        
        # Validar que paso_actual esté en rango válido
        if paso_actual < 1:
            paso_actual = 1
        elif paso_actual > len(RONES):
            paso_actual = len(RONES)
        
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            if not nombre:
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     error="Por favor ingresa tu nombre")
            
            # Crear estructura de usuario si no existe
            if nombre not in datos:
                datos[nombre] = {}
            
            # Obtener el ron actual basado en el paso
            ron_actual = RONES[paso_actual - 1]
            
            print(f"DEBUG: Guardando datos para {nombre} - Ron {ron_actual}")
            print(f"DEBUG: Datos actuales: {json.dumps(datos[nombre], indent=2)}")
            
            # Guardar las puntuaciones del ron actual con validación
            datos[nombre][ron_actual] = {
                "pureza": validar_numero(request.form.get("pureza")),
                "olfato_intensidad": validar_numero(request.form.get("olfato_intensidad")),
                "olfato_complejidad": validar_numero(request.form.get("olfato_complejidad")),
                "gusto_intensidad": validar_numero(request.form.get("gusto_intensidad")),
                "gusto_complejidad": validar_numero(request.form.get("gusto_complejidad")),
                "gusto_persistencia": validar_numero(request.form.get("gusto_persistencia")),
                "armonia": validar_numero(request.form.get("armonia")),
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
            
            # Guardar datos
            guardar_datos(datos)
            
            print(f"DEBUG: Datos después de guardar: {json.dumps(datos[nombre], indent=2)}")
            
            # Determinar siguiente acción
            accion = request.form.get("accion", "")
            if accion == "siguiente" and paso_actual < len(RONES):
                # Redirigir con nuevo paso
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual + 1,
                                     datos=datos,
                                     nombre=nombre,
                                     success=f"Muestra {paso_actual} guardada correctamente")
            elif accion == "anterior" and paso_actual > 1:
                # Redirigir con paso anterior
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual - 1,
                                     datos=datos,
                                     nombre=nombre)
            elif accion == "finalizar":
                # Cata completada
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     nombre=nombre,
                                     success="¡Cata completada exitosamente! Gracias por participar.")
        
        # GET request o POST sin redirección
        return render_template("index.html", 
                             puntajes=PUNTAJES, 
                             rones=RONES, 
                             paso_actual=paso_actual,
                             datos=datos,
                             nombre=request.args.get('nombre', ''))
                             
    except Exception as e:
        # Log del error para debugging
        print(f"Error en index(): {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Devolver página con error amigable
        return render_template("index.html", 
                             puntajes=PUNTAJES, 
                             rones=RONES, 
                             paso_actual=1,
                             datos={},
                             error=f"Error interno: {str(e)}")

@app.route("/resultados")
def resultados():
    """Endpoint para obtener resultados actualizados vía AJAX"""
    try:
        datos = cargar_datos()
        return jsonify(datos)
    except Exception as e:
        print(f"Error en resultados(): {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/reset")
def reset():
    """Endpoint para limpiar todos los datos (solo para desarrollo)"""
    global DATOS_MEMORIA
    try:
        # Limpiar memoria
        DATOS_MEMORIA = {}
        
        # Intentar eliminar archivo
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        
        return "Datos limpiados correctamente"
    except Exception as e:
        return f"Error al limpiar datos: {str(e)}"

@app.route("/debug")
def debug():
    """Endpoint para debugging"""
    try:
        datos = cargar_datos()
        return {
            "archivo_existe": os.path.exists(DATA_FILE),
            "datos_memoria": len(DATOS_MEMORIA),
            "datos_archivo": len(datos),
            "datos": datos
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)

