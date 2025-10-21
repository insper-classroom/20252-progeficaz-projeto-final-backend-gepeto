from flask import Flask, request, jsonify
from utils import connect_db, get_all, get_by_id, insert_veiculo, remove_veiculo, update_veiculo

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
    
    
    
@app.route("/api/veiculos", methods=["POST"])
def new_item():
    data = request.get_json()
    resp, status = insert_veiculo(data)
    return jsonify(resp), status
    

@app.route("/api/veiculos/<id>", methods=["DELETE"])
def remove_item(id):
    resp, status = remove_veiculo(id)
    return jsonify(resp), status

@app.route("/api/veiculos/<id>", methods=["PUT"])
def update_item(id):
    data = request.get_json()
    resp,status = update_veiculo(id,data)
    return jsonify(resp), status

if __name__ == '__main__':
    app.run(debug=True)
