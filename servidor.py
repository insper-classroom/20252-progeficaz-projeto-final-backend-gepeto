from flask import Flask, request, jsonify
from utils import connect_db, get_all, get_by_id, insert_veiculo, remove_veiculo, update_veiculo, authenticate

from openai_service import get_recomendacao_veiculo

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

## Login 

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    response, status = authenticate(data)
    return jsonify(response), status


@app.route("/api/recomendacao", methods=["POST"])
def gerar_recomendacao():
    """
    Recebe um pedido do cliente e retorna uma recomendação de veículo
    usando a API da OpenAI
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Nenhum dado enviado"}), 400
        
        pedido = data.get("pedido")
        
        if not pedido:
            return jsonify({"error": "Campo 'pedido' é obrigatório"}), 400
        
        recomendacao, erro = get_recomendacao_veiculo(pedido)
        
        if erro:
            return jsonify({"error": erro}), 500
        
        return jsonify({
            "recomendacao": recomendacao,
            "pedido": pedido
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao processar solicitação: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
