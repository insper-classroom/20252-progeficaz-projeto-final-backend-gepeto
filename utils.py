import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
import bcrypt
import jwt
from datetime import datetime, timedelta
from openai import OpenAI


load_dotenv(".cred")

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('DB_NAME', 'db_concessionaria')
JWT_SECRET = os.getenv("JWT_SECRET", "chave_super_secreta")
JWT_ALG = "HS256"
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key) if openai_api_key else None
def connect_db():
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        print("Conexão com MongoDB bem-sucedida.")
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        return None
    
    
def get_all():
    db = connect_db()
    if db is not None:
        veiculos_collection = list(db.veiculos.find())
        for veiculo in veiculos_collection:
            veiculo['_id'] = str(veiculo['_id'])
        return veiculos_collection
    return []


def get_by_id(veiculo_id):
    db = connect_db()
    if db is not None:
        try:
            object_id = ObjectId(veiculo_id)
        except:
            return None
        veiculo = db.veiculos.find_one({'_id': object_id})
        if veiculo:
            veiculo['_id'] = str(veiculo['_id'])
            return veiculo
    return None



def insert_veiculo(data):
    db = connect_db()
    if db is None:
        return {"error": "Erro ao conectar ao banco de dados"}, 500
    if data is None:
        return {"error": "Dados inválidos"}, 400
    required_fields = ['marca', 'modelo', 'ano', 'km', 'categoria', 'motor', 'potencia', 'torque', 'transmissao', 'tracao', 'combustivel', 'consumo', 'preco_estimado', 'descricao','estoque']
    for field in required_fields:
        if field not in data:
            return {"error": f"Campo '{field}' é obrigatório."}, 400
    db.veiculos.insert_one(data)
    return {"message": "Veículo inserido com sucesso."}, 201


def remove_veiculo(id):
    db = connect_db()
    if db is None:
        return {"error": "Erro ao conectar ao banco de dados"}, 500
    try:
        object_id = ObjectId(id)
    except:
        return {"error": "ID inválido"}, 400
    result = db.veiculos.delete_one({'_id': object_id})
    if result.deleted_count == 1:
        return {"message": "Veículo removido com sucesso."}, 200
    else:
        return {"error": "Veículo não encontrado."}, 404
    
    
def update_veiculo(id, data):
    db = connect_db()
    if db is None:
        return {"error": "Erro ao conectar ao banco de dados"}, 500
    try:
        object_id = ObjectId(id)
    except:
        return {"error": "ID inválido"}, 400
    if "_id" in data:
        data.pop("_id")

    result = db.veiculos.update_one({'_id': object_id}, {'$set': data})

    if result.matched_count == 0:
        return {"error": "Veículo não encontrado"}, 404

    return {"message": "Veículo atualizado com sucesso"}, 200
    
    
def authenticate(data):
    db = connect_db()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return {"error": "Usuário e senha são obrigatórios"}, 400

    user = db.usuarios.find_one({"credenciais.username": username})
    if not user:
        return {"error": "Usuário não encontrado"}, 401
    
    
    pw_hash = user["credenciais"]["password_hash"]
    
    if isinstance(pw_hash, str):
        pw_hash = pw_hash.encode()

    if not bcrypt.checkpw(password.encode(), pw_hash):
        return {"error": "Senha incorreta"}, 401

    payload = {
        "concessionaria_id": str(user["_id"]),
        "role": user.get("role", "dealer"),
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

    return {
        "token": token,
        "role": payload["role"],
        "expira_em": payload["exp"].isoformat() + "Z"
    }, 200
    
from jwt import ExpiredSignatureError, InvalidTokenError



# def verify_token(data):
    
#     if not data.startswith("Bearer "):
#         return {"error": "Token ausente"}, 401

#     token = data.split(" ")[1]
#     try:
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
#         return {"valid": True, "role": decoded.get("role")}, 200
#     except ExpiredSignatureError:
#         return {"error": "Token expirado"}, 401
#     except InvalidTokenError:
#         return {"error": "Token inválido"}, 401



def recomendacao_veiculo(data):
    if not client:
        return {"error": "API da OpenAI não configurada. Verifique a variável OPENAI_API_KEY."}, 500

    pedido_cliente = data.get("texto")
    if not pedido_cliente:
        return {"error": "O campo 'pedido_cliente' é obrigatório."}, 400

    veiculos = get_all()
    if not veiculos:
        return {"error": "Nenhum veículo encontrado no banco de dados."}, 404

    lista_veiculos = "\n".join([
        (
            f"- {v.get('marca', '')} {v.get('modelo', '')} ({v.get('ano', '')})\n"
            f"  Categoria: {v.get('categoria', '')}\n"
            f"  Motor: {v.get('motor', '')}\n"
            f"  Potência: {v.get('potencia', '')} | Torque: {v.get('torque', '')}\n"
            f"  Transmissão: {v.get('transmissao', '')} | Tração: {v.get('tracao', '')}\n"
            f"  Combustível: {v.get('combustivel', '')}\n"
            f"  Consumo cidade: {v.get('consumo', {}).get('cidade_km_l', '')} km/l | estrada: {v.get('consumo', {}).get('estrada_km_l', '')} km/l\n"
            f"  Preço: R$ {v.get('preco_estimado', '')}\n"
            f"  Descrição: {v.get('descricao', '')}\n"
        )
        for v in veiculos
    ])

    prompt = f"""
Você é um consultor técnico de vendas especializado em veículos.

Estoque disponível:
{lista_veiculos}

Pedido do cliente: {pedido_cliente}

Analise tecnicamente as opções disponíveis e recomende o veículo mais adequado.
Baseie-se em consumo, conforto, categoria e uso indicado. Seja direto, objetivo e técnico.
"""

    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sou um vendedor técnico e objetivo. Minhas respostas são curtas, técnicas e vão direto ao ponto."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=250
    )

        recomendacao = response.choices[0].message.content.strip()

        return {
            "recomendacao": recomendacao,
            "pedido": pedido_cliente
        }, 200

    except Exception as e:
        return {"error": f"Erro ao comunicar com a API da OpenAI: {str(e)}"}, 500
        