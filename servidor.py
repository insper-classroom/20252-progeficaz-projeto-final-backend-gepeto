from flask import Flask, request, jsonify
from utils import connect_db, get_all, get_by_id

app = Flask(__name__)



@app.route("/api/veiculos", methods=["GET"])
def get_veiculos():
    veiculos = get_all()
    return jsonify(veiculos), 200


@app.route("/api/veiculos/<id>", methods=["GET"])
def get_veiculos_by_id(id):
    veiculo = get_by_id(id)
    if veiculo:
        return jsonify(veiculo), 200
    else:
        return jsonify({"error": "Veículo não encontrado"}), 404
    



if __name__ == '__main__':
    app.run(debug=True)
