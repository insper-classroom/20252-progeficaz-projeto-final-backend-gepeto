import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
import bcrypt
import jwt
from datetime import datetime, timedelta


load_dotenv()

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('DB_NAME', 'db_concessionaria')
JWT_SECRET = os.getenv("JWT_SECRET", "chave_super_secreta")
JWT_ALG = "HS256"

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
        object_id = ObjectId(veiculo_id)
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


        