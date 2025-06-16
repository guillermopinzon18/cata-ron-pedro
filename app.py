from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
import urllib.parse

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'cata_ron_secret_key_2024'

# PostgreSQL configuration with Supabase
# Parse the connection URL to add SSL requirements
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:BRevIdsERoclrtgf@db.jpdizuizmhqmellbhniz.supabase.co:5432/postgres')
parsed = urllib.parse.urlparse(DATABASE_URL)
# Add SSL mode and other required parameters
DATABASE_URL = urllib.parse.urlunparse(parsed._replace(
    query=urllib.parse.urlencode({
        'sslmode': 'require',
        'connect_timeout': '10',
        'application_name': 'cata_ron_app'
    })
))

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 1,  # Vercel works better with a small pool
    'max_overflow': 2,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'pool_pre_ping': True,  # Verify connections before using them
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
}

db = SQLAlchemy(app)

# Configurar SQLite para mejor concurrencia
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance entre seguridad y rendimiento
        cursor.execute("PRAGMA busy_timeout=5000")  # Esperar hasta 5 segundos si la BD está bloqueada
        cursor.close()

# Modelo para las catas
class Cata(db.Model):
    __tablename__ = 'catas'  # Explicitly name the table
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)  # Índice para búsquedas más rápidas
    ron = db.Column(db.String(1), nullable=False, index=True)
    pureza = db.Column(db.Integer, default=0)
    olfato_intensidad = db.Column(db.Integer, default=0)
    olfato_complejidad = db.Column(db.Integer, default=0)
    gusto_intensidad = db.Column(db.Integer, default=0)
    gusto_complejidad = db.Column(db.Integer, default=0)
    gusto_persistencia = db.Column(db.Integer, default=0)
    armonia = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    notas = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.UniqueConstraint('nombre', 'ron', name='unique_cata_ron'),
        db.Index('idx_nombre_ron', 'nombre', 'ron'),  # Índice compuesto para búsquedas más eficientes
    )

# Crear las tablas solo si no existen
def init_db():
    try:
        with app.app_context():
            # Verificar si la tabla existe
            inspector = db.inspect(db.engine)
            if 'catas' not in inspector.get_table_names():
                db.create_all()
                print("Tablas creadas exitosamente")
            else:
                print("Las tablas ya existen")
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")
        raise

# Inicializar la base de datos
init_db()

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
    """Carga los datos desde PostgreSQL"""
    try:
        with db.session.begin():
            # Obtener todas las catas con ordenamiento
            catas = Cata.query.order_by(Cata.nombre, Cata.ron).all()
            
            # Convertir a diccionario
            datos = {}
            for cata in catas:
                if cata.nombre not in datos:
                    datos[cata.nombre] = {"nombre": cata.nombre}
                
                datos[cata.nombre][cata.ron] = {
                    "pureza": cata.pureza,
                    "olfato_intensidad": cata.olfato_intensidad,
                    "olfato_complejidad": cata.olfato_complejidad,
                    "gusto_intensidad": cata.gusto_intensidad,
                    "gusto_complejidad": cata.gusto_complejidad,
                    "gusto_persistencia": cata.gusto_persistencia,
                    "armonia": cata.armonia,
                    "total": cata.total,
                    "timestamp": cata.timestamp.isoformat()
                }
                
                if cata.notas:
                    datos[cata.nombre]["notas"] = cata.notas
            
            return datos
    except Exception as e:
        db.session.rollback()
        print(f"Error cargando datos de PostgreSQL: {e}")
        return {}

def guardar_datos(datos):
    """Guarda los datos en PostgreSQL"""
    max_intentos = 3
    intento = 0
    
    while intento < max_intentos:
        try:
            with db.session.begin():
                for nombre, datos_usuario in datos.items():
                    for ron in RONES:
                        if ron in datos_usuario:
                            puntuaciones = datos_usuario[ron]
                            
                            # Buscar o crear registro
                            cata = Cata.query.filter_by(nombre=nombre, ron=ron).first()
                            if not cata:
                                cata = Cata(nombre=nombre, ron=ron)
                            
                            # Actualizar puntuaciones
                            cata.pureza = puntuaciones.get("pureza", 0)
                            cata.olfato_intensidad = puntuaciones.get("olfato_intensidad", 0)
                            cata.olfato_complejidad = puntuaciones.get("olfato_complejidad", 0)
                            cata.gusto_intensidad = puntuaciones.get("gusto_intensidad", 0)
                            cata.gusto_complejidad = puntuaciones.get("gusto_complejidad", 0)
                            cata.gusto_persistencia = puntuaciones.get("gusto_persistencia", 0)
                            cata.armonia = puntuaciones.get("armonia", 0)
                            cata.total = puntuaciones.get("total", 0)
                            
                            if "notas" in datos_usuario and ron == RONES[-1]:
                                cata.notas = datos_usuario["notas"]
                            
                            db.session.add(cata)
                
                db.session.commit()
                return  # Éxito, salir del bucle
                
        except Exception as e:
            db.session.rollback()
            intento += 1
            if intento == max_intentos:
                print(f"Error guardando datos en PostgreSQL después de {max_intentos} intentos: {e}")
                raise
            print(f"Intento {intento} fallido, reintentando...")
            import time
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
            
            datos[nombre][ron_actual] = puntuaciones
            
            # Guardar notas si es el último paso
            if paso_actual == len(RONES):
                datos[nombre]["notas"] = request.form.get("notas", "")
            
            # Guardar en PostgreSQL
            guardar_datos(datos)
            
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
        with app.app_context():
            db.drop_all()
            db.create_all()
        return "Datos limpiados correctamente"
    except Exception as e:
        return f"Error al limpiar datos: {str(e)}"

@app.route("/debug")
def debug():
    """Endpoint para debugging"""
    try:
        datos = cargar_datos()
        return {
            "total_catas": Cata.query.count(),
            "datos": datos
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)

