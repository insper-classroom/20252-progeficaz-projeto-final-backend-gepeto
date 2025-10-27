import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db_name = os.getenv('DB_NAME', 'db_concessionaria')

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
