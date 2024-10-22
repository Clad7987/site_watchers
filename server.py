from flask import Flask, send_from_directory, jsonify, request
import json
import os

app = Flask(__name__)

# Caminho para o arquivo JSON
DATA_FILE = "docs/data/fapdungeon.json"


# Rota para servir arquivos estáticos
@app.route("/")
def index():
    return send_from_directory("./docs", "index.html")


@app.route("/model")
def model():
    return send_from_directory("./docs", "model.html")


@app.route("/style.css")
def style():
    return send_from_directory("./docs/src", "style.css")


@app.route("/model.css")
def model_style():
    return send_from_directory("./docs/src", "model.css")


@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory("./docs/data", filename)


@app.route("/favorite", methods=["POST"])
def favorite_model():
    model_link = request.json.get("link")

    # Ler o arquivo JSON
    with open(DATA_FILE, "r") as file:
        models = json.load(file)

    # Atualizar o modelo com o link fornecido
    for model in models:
        if model["link"] == model_link:
            model["favorite"] = not model["favorite"]  # Define como favorito
            break

    # Salvar as alterações de volta no JSON
    with open(DATA_FILE, "w") as file:
        json.dump(models, file, indent=4)

    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
