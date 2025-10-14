import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('.cred')

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
    
