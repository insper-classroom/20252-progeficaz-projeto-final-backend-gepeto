from flask import Flask, request, jsonify
from utils import connect_db, get_all, get_by_id
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
