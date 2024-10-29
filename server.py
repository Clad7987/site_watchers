from flask import Flask, send_from_directory, jsonify, request
import json
import os

app = Flask(__name__)

# Caminho para o arquivo JSON
DATA_FILES = ["docs/data/fapdungeon.json", 'docs/data/waifubitches.json']


# Rota para servir arquivos estáticos
@app.route("/")
def index():
    return send_from_directory("./docs", "index.html")


@app.route("/model")
def model():
    return send_from_directory("./docs", "model.html")


@app.route("/src/style.css")
def style():
    return send_from_directory("./docs/src", "style.css")


@app.route("/src/model.css")
def model_style():
    return send_from_directory("./docs/src", "model.css")


@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory("./docs/data", filename)


@app.route("/like", methods=["POST"])
def favorite_model():
    model_link = request.json.get("name")

    for data in DATA_FILES:
        with open(data, 'r') as file:
            models = json.load(file)

        # Atualizar o modelo com o link fornecido
        for model in models:
            if model["name"] == model_link:
                model["like"] += 1 # Define como favorito
                break

        # Salvar as alterações de volta no JSON
        with open(data, "w") as file:
            json.dump(models, file)

    return jsonify({"success": True}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
