from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
from dotenv import load_dotenv
import time
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'cata_ron_secret_key_2024'

# Supabase configuration
SUPABASE_URL = "https://jpdizuizmhqmellbhniz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpwZGl6dWl6bWhxbWVsbGJobml6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwMzQ1ODYsImV4cCI6MjA2NTYxMDU4Nn0.theNyi8_x76eyC5cAu7uQAbsS_cGGZmghVLCzRy6_hI"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def cargar_datos():
    """Carga los datos desde Supabase"""
    try:
        # Obtener todas las catas, ordenadas por timestamp descendente
        response = supabase.table('catas').select('*').order('timestamp', desc=True).execute()
        
        # Convertir a diccionario, tomando solo la entrada más reciente para cada combinación nombre-ron
        datos = {}
        for cata in response.data:
            if cata['nombre'] not in datos:
                datos[cata['nombre']] = {"nombre": cata['nombre']}
            
            # Solo actualizar si no existe una entrada más reciente para este nombre-ron
            if cata['ron'] not in datos[cata['nombre']]:
                datos[cata['nombre']][cata['ron']] = {
                    "pureza": cata['pureza'],
                    "olfato_intensidad": cata['olfato_intensidad'],
                    "olfato_complejidad": cata['olfato_complejidad'],
                    "gusto_intensidad": cata['gusto_intensidad'],
                    "gusto_complejidad": cata['gusto_complejidad'],
                    "gusto_persistencia": cata['gusto_persistencia'],
                    "armonia": cata['armonia'],
                    "total": cata['total'],
                    "timestamp": cata['timestamp']
                }
                
                if cata.get('notas'):
                    datos[cata['nombre']]["notas"] = cata['notas']
        
        return datos
    except Exception as e:
        print(f"Error cargando datos de Supabase: {e}")
        return {}

def guardar_datos(datos):
    """Guarda los datos en Supabase"""
    max_intentos = 3
    intento = 0
    
    while intento < max_intentos:
        try:
            for nombre, datos_usuario in datos.items():
                # Obtener el ron actual basado en los datos del usuario
                ron_actual = None
                for ron in RONES:
                    if ron in datos_usuario and isinstance(datos_usuario[ron], dict):
                        ron_actual = ron
                        break
                
                if ron_actual is None:
                    print(f"No se encontró ron para guardar en los datos de {nombre}")
                    continue
                
                puntuaciones = datos_usuario[ron_actual]
                
                # Preparar datos para insertar
                cata_data = {
                    "nombre": nombre,
                    "ron": ron_actual,
                    "pureza": puntuaciones.get("pureza", 0),
                    "olfato_intensidad": puntuaciones.get("olfato_intensidad", 0),
                    "olfato_complejidad": puntuaciones.get("olfato_complejidad", 0),
                    "gusto_intensidad": puntuaciones.get("gusto_intensidad", 0),
                    "gusto_complejidad": puntuaciones.get("gusto_complejidad", 0),
                    "gusto_persistencia": puntuaciones.get("gusto_persistencia", 0),
                    "armonia": puntuaciones.get("armonia", 0),
                    "total": puntuaciones.get("total", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if "notas" in datos_usuario and ron_actual == RONES[-1]:
                    cata_data["notas"] = datos_usuario["notas"]
                
                print(f"Intentando guardar datos para {nombre}, ron {ron_actual}: {cata_data}")
                
                # Insertar nuevo registro
                response = supabase.table('catas').insert(cata_data).execute()
                
                if not response.data:
                    print(f"Respuesta de Supabase al guardar: {response}")
                    raise Exception(f"No se pudo guardar los datos para {nombre}, ron {ron_actual}")
                
                print(f"Datos guardados exitosamente para {nombre}, ron {ron_actual}")
            
            return  # Éxito, salir del bucle
                
        except Exception as e:
            intento += 1
            print(f"Error guardando datos en Supabase (intento {intento}): {e}")
            if intento == max_intentos:
                raise
            print(f"Intento {intento} fallido, reintentando...")
            time.sleep(0.1 * intento)  # Esperar un poco más entre intentos

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
            
            # Obtener el ron actual basado en el paso
            ron_actual = RONES[paso_actual - 1]
            
            # Crear o actualizar el documento del usuario
            puntuaciones = {
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
            puntuaciones["total"] = sum([
                puntuaciones[k] for k in puntuaciones 
                if k not in ["timestamp", "total"]
            ])
            
            # Actualizar datos en memoria
            if nombre not in datos:
                datos[nombre] = {"nombre": nombre}
            
            # Guardar solo los datos del ron actual
            datos[nombre][ron_actual] = puntuaciones
            
            # Guardar notas si es el último paso
            if paso_actual == len(RONES):
                datos[nombre]["notas"] = request.form.get("notas", "")
            
            try:
                # Guardar solo los datos del ron actual
                datos_a_guardar = {
                    nombre: {
                        "nombre": nombre,
                        ron_actual: puntuaciones
                    }
                }
                if paso_actual == len(RONES):
                    datos_a_guardar[nombre]["notas"] = request.form.get("notas", "")
                
                guardar_datos(datos_a_guardar)
                print(f"Datos guardados exitosamente para {nombre}, ron {ron_actual}")
            except Exception as e:
                print(f"Error real al guardar: {e}")
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     nombre=nombre,
                                     error=f"Error al guardar: {e}")
            
            # Determinar siguiente acción
            accion = request.form.get("accion", "")
            if accion == "siguiente" and paso_actual < len(RONES):
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual + 1,
                                     datos=datos,
                                     nombre=nombre,
                                     success=f"Muestra {paso_actual} guardada correctamente")
            elif accion == "anterior" and paso_actual > 1:
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual - 1,
                                     datos=datos,
                                     nombre=nombre)
            elif accion == "finalizar":
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
        print(f"Error en index(): {str(e)}")
        import traceback
        traceback.print_exc()
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
    try:
        # Eliminar todos los registros de la tabla catas
        response = supabase.table('catas').delete().neq('id', 0).execute()
        return "Datos limpiados correctamente"
    except Exception as e:
        return f"Error al limpiar datos: {str(e)}"

@app.route("/debug")
def debug():
    """Endpoint para debugging"""
    try:
        datos = cargar_datos()
        return {
            "total_catas": len(datos),
            "datos": datos
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)

