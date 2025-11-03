from flask import Flask, request, jsonify,Response
from utils import connect_db, get_all, get_by_id, insert_veiculo, remove_veiculo, update_veiculo, authenticate,recomendacao_veiculo, verify_token
from flask_cors import CORS
from dotenv import load_dotenv
import os
from bson import json_util
import json 
app = Flask(__name__)
load_dotenv(".cred")

origins_list = [os.getenv('CORS_ORIGINS')]

front_url = os.getenv('FRONT_URL')
if front_url:
    origins_list.append(front_url)

CORS(
    app,
    origins=origins_list,
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)


@app.before_request
def require_auth_for_api():
    if request.path in ["/login", "/api/recomendacao"]:
        return None
    if request.method == "OPTIONS":
        return None
    if request.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization", "")
        msg, code = verify_token(auth_header)
        if code != 200:
            return jsonify(msg), code
    return None

@app.route("/api/veiculos", methods=["GET"])
def get_veiculos():
    veiculos = get_all()
    return Response(
        json_util.dumps(veiculos),
        mimetype='application/json'
    )


@app.route("/api/veiculos/<id>", methods=["GET"])
def get_veiculos_by_id(id):
    veiculo = get_by_id(id)
    if veiculo:
        return Response(
            json_util.dumps(veiculo),
            mimetype='application/json'
        )
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

# @app.route("/verify", methods=["GET"])
# def jwt_verify():
#     auth_header = request.headers.get("Authorization", "")
#     msg, code = verify_token(auth_header)
#     return jsonify(msg), code


@app.route("/api/recomendacao", methods=["POST"])
def gerar_recomendacao():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum dado enviado"}), 400

        recomendacao, status = recomendacao_veiculo(data)

        return jsonify(recomendacao), status

    except Exception as e:
        return jsonify({"error": f"Erro ao processar solicitação: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
