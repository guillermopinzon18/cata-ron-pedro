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
        print("Iniciando carga de datos desde Supabase")
        datos = {}
        
        # Cargar datos de cada tabla de ron
        for ron in RONES:
            tabla = f'catas_{ron.lower()}'
            print(f"Cargando datos de tabla {tabla}")
            try:
                response = supabase.table(tabla).select('*').order('timestamp', desc=True).execute()
                print(f"Respuesta de {tabla}: {len(response.data)} registros")
                
                for cata in response.data:
                    nombre = cata['nombre']
                    if nombre not in datos:
                        datos[nombre] = {"nombre": nombre}
                    
                    # Solo actualizar si no existe una entrada más reciente para este nombre
                    if ron not in datos[nombre]:
                        datos[nombre][ron] = {
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
                        
                        # Solo guardar notas de la última tabla (Ron D)
                        if ron == RONES[-1] and cata.get('notas'):
                            datos[nombre]["notas"] = cata['notas']
            except Exception as e:
                print(f"Error cargando tabla {tabla}: {str(e)}")
                continue
        
        print(f"Carga de datos completada: {len(datos)} usuarios")
        return datos
    except Exception as e:
        print(f"Error general en cargar_datos(): {str(e)}")
        import traceback
        traceback.print_exc()
        return {}

def guardar_datos(datos):
    """Guarda los datos en Supabase"""
    max_intentos = 3
    intento = 0
    
    while intento < max_intentos:
        try:
            for nombre, datos_usuario in datos.items():
                # Verificar que tenemos datos para el ron actual
                ron_actual = None
                for ron in RONES:
                    if ron in datos_usuario and isinstance(datos_usuario[ron], dict):
                        ron_actual = ron
                        break
                
                if ron_actual is None:
                    print(f"No se encontró ron para guardar en los datos de {nombre}")
                    continue
                
                # Obtener las puntuaciones del ron actual
                puntuaciones = datos_usuario[ron_actual]
                if not puntuaciones:
                    print(f"No hay puntuaciones para {nombre}, ron {ron_actual}")
                    continue
                
                # Preparar datos para insertar
                cata_data = {
                    "nombre": nombre,
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
                
                # Agregar notas solo para el último ron
                if "notas" in datos_usuario and ron_actual == RONES[-1]:
                    cata_data["notas"] = datos_usuario["notas"]
                
                # Determinar la tabla correcta basada en el ron
                tabla = f'catas_{ron_actual.lower()}'
                print(f"Intentando guardar datos para {nombre} en tabla {tabla}: {cata_data}")
                
                try:
                    # Insertar nuevo registro en la tabla correspondiente
                    response = supabase.table(tabla).insert(cata_data).execute()
                    
                    if not response.data:
                        print(f"Respuesta de Supabase al guardar en {tabla}: {response}")
                        raise Exception(f"No se pudo guardar los datos para {nombre} en tabla {tabla}")
                    
                    print(f"Datos guardados exitosamente para {nombre} en tabla {tabla}")
                except Exception as e:
                    print(f"Error específico al guardar en tabla {tabla}: {e}")
                    raise
            
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
        print("Iniciando ruta index()")
        datos = cargar_datos()
        print(f"Datos cargados: {len(datos)} registros")
        
        # Obtener el paso actual de la URL o del formulario
        if request.method == "POST":
            print("Método POST detectado")
            # Si es POST, obtener el paso del formulario
            try:
                paso_actual = int(request.form.get('paso_actual', 1))
            except ValueError as e:
                print(f"Error al convertir paso_actual: {e}")
                paso_actual = 1
                
            accion = request.form.get("accion", "")
            nombre = request.form.get("nombre", "").strip()
            print(f"POST - Nombre: {nombre}, Acción: {accion}, Paso: {paso_actual}")
            
            # Si es pedroadmin y la acción es borrar
            if nombre and nombre.lower() == "pedroadmin" and accion.startswith("borrar"):
                print(f"Procesando acción de borrado: {accion}")
                try:
                    if accion == "borrar_todo":
                        print("Iniciando borrado de todos los datos")
                        # Eliminar todos los registros de todas las tablas
                        for ron in RONES:
                            tabla = f'catas_{ron.lower()}'
                            print(f"Borrando tabla {tabla}")
                            response = supabase.table(tabla).delete().neq('id', 0).execute()
                            print(f"Respuesta de borrado {tabla}: {response}")
                        mensaje = "Todos los datos han sido eliminados correctamente"
                    elif accion == "borrar_ron":
                        print("Iniciando borrado de ron específico")
                        # Eliminar registros de una tabla específica
                        ron_especifico = request.form.get("ron_especifico")
                        print(f"Ron específico a borrar: {ron_especifico}")
                        if ron_especifico in RONES:
                            tabla = f'catas_{ron_especifico.lower()}'
                            print(f"Borrando tabla {tabla}")
                            response = supabase.table(tabla).delete().neq('id', 0).execute()
                            print(f"Respuesta de borrado {tabla}: {response}")
                            mensaje = f"Datos de la Muestra {RONES.index(ron_especifico) + 1} eliminados correctamente"
                        else:
                            raise Exception(f"Muestra no válida: {ron_especifico}")
                    
                    # Recargar datos después de borrar
                    print("Recargando datos después del borrado")
                    datos = cargar_datos()
                    print(f"Datos recargados: {len(datos)} registros")
                    return render_template("index.html", 
                                         puntajes=PUNTAJES, 
                                         rones=RONES, 
                                         paso_actual=paso_actual,
                                         datos=datos,
                                         nombre=nombre,
                                         success=mensaje)
                except Exception as e:
                    print(f"Error durante el borrado: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return render_template("index.html", 
                                         puntajes=PUNTAJES, 
                                         rones=RONES, 
                                         paso_actual=paso_actual,
                                         datos=datos,
                                         nombre=nombre,
                                         error=f"Error al eliminar datos: {str(e)}")
            
            # Si es pedroadmin, no procesar el formulario normal
            if nombre and nombre.lower() == "pedroadmin":
                print("Usuario pedroadmin detectado, omitiendo procesamiento de formulario")
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     nombre=nombre)
            
            # Determinar el paso actual basado en la acción
            if accion == "siguiente":
                # No incrementamos aquí, lo haremos después de guardar
                pass
            elif accion == "anterior":
                paso_actual = max(1, paso_actual - 1)
                # Si es "anterior", permitir navegación sin validar campos
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     nombre=nombre)
        else:
            # Si es GET, obtener el paso de la URL
            paso_actual = int(request.args.get('paso', 1))
            nombre = request.args.get('nombre', '')
        
        # Validar que paso_actual esté en rango válido
        if paso_actual < 1:
            paso_actual = 1
        elif paso_actual > len(RONES):
            paso_actual = len(RONES)
    
        if request.method == "POST" and accion != "anterior":  # Solo validar campos si no es "anterior"
            if not nombre:
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     error="Por favor ingresa tu nombre")
            
            # Obtener el ron actual basado en el paso
            ron_actual = RONES[paso_actual - 1]
            print(f"Procesando datos para paso {paso_actual}, ron {ron_actual}")
            
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
                # Preparar datos para guardar solo el ron actual
                datos_a_guardar = {
                    nombre: {
                        "nombre": nombre,
                        ron_actual: puntuaciones
                    }
                }
                
                # Agregar notas solo si es el último paso
                if paso_actual == len(RONES):
                    datos_a_guardar[nombre]["notas"] = request.form.get("notas", "")
                
                print(f"Intentando guardar datos para paso {paso_actual}, ron {ron_actual}")
                guardar_datos(datos_a_guardar)
                print(f"Datos guardados exitosamente para {nombre}, ron {ron_actual}")
                
                # Determinar siguiente acción después de guardar exitosamente
                accion = request.form.get("accion", "")
                if accion == "siguiente" and paso_actual < len(RONES):
                    # Incrementar el paso solo después de guardar exitosamente
                    siguiente_paso = paso_actual + 1
                    return render_template("index.html", 
                                         puntajes=PUNTAJES, 
                                         rones=RONES, 
                                         paso_actual=siguiente_paso,
                                         datos=datos,
                                         nombre=nombre,
                                         success=f"Muestra {paso_actual} guardada correctamente")
                elif accion == "finalizar":
                    return render_template("index.html", 
                                         puntajes=PUNTAJES, 
                                         rones=RONES, 
                                         paso_actual=paso_actual,
                                         datos=datos,
                                         nombre=nombre,
                                         success="¡Cata completada exitosamente! Gracias por participar.")
                
            except Exception as e:
                print(f"Error real al guardar: {e}")
                return render_template("index.html", 
                                     puntajes=PUNTAJES, 
                                     rones=RONES, 
                                     paso_actual=paso_actual,
                                     datos=datos,
                                     nombre=nombre,
                                     error=f"Error al guardar: {e}")
        
        # GET request o POST sin redirección
        return render_template("index.html", 
                             puntajes=PUNTAJES, 
                             rones=RONES, 
                             paso_actual=paso_actual,
                             datos=datos,
                             nombre=nombre)
                             
    except Exception as e:
        print(f"Error general en index(): {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template("index.html", 
                             puntajes=PUNTAJES, 
                             rones=RONES, 
                             paso_actual=1,
                             datos={},
                             nombre="",
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
        # Eliminar todos los registros de todas las tablas
        for ron in RONES:
            tabla = f'catas_{ron.lower()}'
            response = supabase.table(tabla).delete().neq('id', 0).execute()
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

