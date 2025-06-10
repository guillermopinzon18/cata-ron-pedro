from flask import Flask, render_template, request

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

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = {}
    notas = ""
    nombre = ""
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        ron_calculado = request.form.get("calcular_ron")
        
        if ron_calculado:
            resultados[ron_calculado] = {
                "pureza": int(request.form.get(f"pureza_{ron_calculado}", 0)),
                "olfato_intensidad": int(request.form.get(f"olfato_intensidad_{ron_calculado}", 0)),
                "olfato_complejidad": int(request.form.get(f"olfato_complejidad_{ron_calculado}", 0)),
                "gusto_intensidad": int(request.form.get(f"gusto_intensidad_{ron_calculado}", 0)),
                "gusto_complejidad": int(request.form.get(f"gusto_complejidad_{ron_calculado}", 0)),
                "gusto_persistencia": int(request.form.get(f"gusto_persistencia_{ron_calculado}", 0)),
                "armonia": int(request.form.get(f"armonia_{ron_calculado}", 0)),
            }
            resultados[ron_calculado]["total"] = sum(resultados[ron_calculado].values())
        
        notas = request.form.get("notas", "")
    
    return render_template("index.html", puntajes=PUNTAJES, rones=RONES, resultados=resultados, notas=notas, nombre=nombre)

if __name__ == "__main__":
    app.run(debug=True) 