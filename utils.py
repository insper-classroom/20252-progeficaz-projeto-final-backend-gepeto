import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
import bcrypt
import jwt
from datetime import datetime, timedelta
from openai import OpenAI
import uuid


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



def verify_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Token ausente"}, 401
    token = auth_header.split(" ", 1)[1].strip()
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return {"valid": True, "payload": decoded}, 200
    except ExpiredSignatureError:
        return {"error": "Token expirado"}, 401
    except InvalidTokenError:
        return {"error": "Token inválido"}, 401



def criar_ou_buscar_conversa(session_id=None):
    """Cria uma nova conversa ou retorna uma existente"""
    try:
        db = connect_db()
        if db is None:
            print("Erro: Não foi possível conectar ao banco de dados")
            return None, None
        
        # Criar índice TTL para expiração automática (se não existir)
        try:
            # Verificar se a collection existe, se não, criar
            if "chats" not in db.list_collection_names():
                db.create_collection("chats")
            db.chats.create_index("data_expiracao", expireAfterSeconds=0)
        except Exception as e:
            # Erro ao criar índice não é crítico, pode continuar
            print(f"Erro ao criar índice TTL (pode ser normal se já existe): {e}")
            pass
        
        if session_id:
            try:
                conversa = db.chats.find_one({"session_id": session_id})
                if conversa:
                    conversa['_id'] = str(conversa['_id'])
                    return conversa, session_id
            except Exception as e:
                print(f"Erro ao buscar conversa: {e}")
                # Se falhar, criar nova conversa
        
        # Criar nova conversa
        nova_session_id = str(uuid.uuid4())
        agora = datetime.utcnow()
        expiracao = agora + timedelta(hours=24)  # Expira em 24 horas
        
        conversa = {
            "session_id": nova_session_id,
            "mensagens": [],
            "data_criacao": agora,
            "data_expiracao": expiracao
        }
        
        try:
            db.chats.insert_one(conversa)
            conversa['_id'] = str(conversa['_id'])
            return conversa, nova_session_id
        except Exception as e:
            print(f"Erro ao inserir conversa no banco: {e}")
            # Retornar conversa mesmo sem salvar no banco (modo degradado)
            conversa['_id'] = 'temp'
            return conversa, nova_session_id
            
    except Exception as e:
        print(f"Erro geral em criar_ou_buscar_conversa: {e}")
        # Em caso de erro total, criar conversa temporária sem banco
        nova_session_id = str(uuid.uuid4())
        conversa = {
            "session_id": nova_session_id,
            "mensagens": [],
            "data_criacao": datetime.utcnow(),
            "data_expiracao": datetime.utcnow() + timedelta(hours=24)
        }
        conversa['_id'] = 'temp'
        return conversa, nova_session_id


def salvar_mensagem(session_id, autor, texto):
    """Salva uma mensagem na conversa"""
    try:
        db = connect_db()
        if db is None:
            print("Aviso: Não foi possível conectar ao banco para salvar mensagem")
            return False
        
        mensagem = {
            "autor": autor,  # "user" ou "bot"
            "texto": texto,
            "timestamp": datetime.utcnow()
        }
        
        db.chats.update_one(
            {"session_id": session_id},
            {"$push": {"mensagens": mensagem}},
            upsert=True  # Cria o documento se não existir
        )
        return True
    except Exception as e:
        print(f"Erro ao salvar mensagem (não crítico): {e}")
        # Não crítico - a conversa pode continuar sem salvar no banco
        return False


def obter_historico_conversa(session_id, limite=20):
    """Obtém o histórico de mensagens da conversa"""
    try:
        db = connect_db()
        if db is None:
            return []
        
        conversa = db.chats.find_one({"session_id": session_id})
        if not conversa:
            return []
        
        mensagens = conversa.get("mensagens", [])
        # Retorna as últimas N mensagens
        return mensagens[-limite:] if len(mensagens) > limite else mensagens
    except Exception as e:
        print(f"Erro ao obter histórico (não crítico): {e}")
        # Se não conseguir buscar histórico, retorna vazio (conversa começa do zero)
        return []


def limpar_conversas_expiradas():
    """Remove conversas expiradas do banco"""
    try:
        db = connect_db()
        if db is None:
            return
        
        # Verificar se a collection existe
        if "chats" not in db.list_collection_names():
            return
        
        agora = datetime.utcnow()
        db.chats.delete_many({"data_expiracao": {"$lt": agora}})
    except Exception as e:
        print(f"Erro ao limpar conversas expiradas: {e}")
        pass  # Não crítico, pode falhar silenciosamente


def recomendacao_veiculo(data):
    try:
        if not client:
            return {"error": "API da OpenAI não configurada. Verifique a variável OPENAI_API_KEY."}, 500

        pedido_cliente = data.get("texto")
        if not pedido_cliente:
            return {"error": "O campo 'texto' é obrigatório."}, 400

        session_id = data.get("session_id")
        conversa, session_id_atual = criar_ou_buscar_conversa(session_id)
        
        if not conversa or not session_id_atual:
            return {"error": "Erro ao criar/recuperar conversa."}, 500

        # Salvar mensagem do usuário
        salvar_mensagem(session_id_atual, "user", pedido_cliente)

        # Obter histórico da conversa
        historico = obter_historico_conversa(session_id_atual)
        
        # Limpar conversas expiradas periodicamente (não crítico se falhar)
        try:
            limpar_conversas_expiradas()
        except Exception:
            pass

        veiculos = get_all()
        if not veiculos:
            return {"error": "Nenhum veículo encontrado no banco de dados."}, 404

        # Filtrar apenas veículos em estoque
        veiculos_disponiveis = [v for v in veiculos if v.get('estoque', 0) > 0]
        
        if not veiculos_disponiveis:
            return {"error": "Nenhum veículo disponível em estoque."}, 404

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
            for v in veiculos_disponiveis
        ])

        # Prompt aprimorado com contexto e melhor entendimento
        system_prompt = """Você é um assistente virtual amigável e profissional da concessionária Toyota. 

IMPORTANTE - Como responder:
1. SAUDAÇÕES (oi, olá, tudo bem, bom dia, etc): 
   - Responda de forma calorosa e natural, como um vendedor amigável
   - Exemplos: "Oi! Tudo bem sim, obrigado! 😊 Como posso te ajudar hoje?" ou "Olá! Tudo ótimo! Estou aqui para te ajudar a encontrar o veículo perfeito! 🚗"
   - NUNCA responda com "Certo! Anotei sua resposta" ou respostas genéricas para saudações
   - Após responder a saudação, pergunte naturalmente como pode ajudar com veículos

2. SOBRE VEÍCULOS:
   - Analise cuidadosamente as preferências do cliente
   - Se pedir "carro esportivo/potente", NÃO sugira modelos econômicos como Yaris
   - Se pedir SUV, NÃO sugira hatchback
   - Se pedir luxo, NÃO sugira básico
   - Seja específico e mencione os modelos que REALMENTE atendem ao pedido

3. INTERESSE EM COMPRAR:
   - Identifique quando o cliente quer comprar
   - Ajude no processo de forma proativa

4. CONVERSA CASUAL:
   - Seja natural e conversacional
   - Mantenha o foco em veículos, mas não seja robótico
   - Se o cliente fizer perguntas gerais, responda de forma amigável e direcione para veículos quando apropriado

Seja sempre natural, amigável e inteligente. Evite respostas genéricas ou robóticas."""

        # Construir mensagens para a API com histórico
        messages = [{"role": "system", "content": system_prompt}]
        
        # Adicionar histórico como mensagens anteriores (todas exceto a última que é a mensagem atual)
        historico_anterior = historico[:-1] if len(historico) > 1 else []
        for msg in historico_anterior:
            role = "user" if msg.get("autor") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("texto", "")})
        
        # Construir prompt com contexto e mensagem atual
        contexto_texto = ""
        if historico_anterior:
            contexto_texto = "\n\n⚠️ ATENÇÃO: CONTEXTO DA CONVERSA ANTERIOR (USE ESTAS INFORMAÇÕES!):\n"
            for msg in historico_anterior[-10:]:  # Últimas 10 mensagens do histórico
                autor_nome = "Cliente" if msg.get("autor") == "user" else "Você (Assistente)"
                texto_msg = msg.get('texto', '')
                # Limpar HTML se houver
                texto_msg = texto_msg.replace('<br />', '\n').replace('<b>', '').replace('</b>', '')
                contexto_texto += f"{autor_nome}: {texto_msg}\n"
            contexto_texto += "\n⚠️ IMPORTANTE: O cliente já forneceu informações acima. Use esse contexto para dar uma resposta relevante e específica. NÃO repita perguntas genéricas!"
        
        # Detectar se é uma saudação simples (mais robusto)
        saudacoes = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem", "td bem", "e aí", "eai", "hey", "hi", "hello", "eae", "e aê"]
        pedido_lower = pedido_cliente.lower().strip()
        # Remove pontuação para melhor detecção
        pedido_limpo = ''.join(c for c in pedido_lower if c.isalnum() or c.isspace())
        palavras = pedido_limpo.split()
        is_saudacao = len(palavras) <= 3 and any(saudacao in pedido_limpo for saudacao in saudacoes)
        
        if is_saudacao:
            # É uma saudação - resposta mais simples e natural
            user_prompt = f"""O cliente enviou uma saudação: "{pedido_cliente}"

IMPORTANTE: Você DEVE responder de forma calorosa e natural, como um vendedor amigável da Toyota.

Exemplos CORRETOS de resposta:
- "Oi! Tudo bem sim, obrigado! 😊 Como posso te ajudar hoje?"
- "Olá! Tudo ótimo! Estou aqui para te ajudar a encontrar o veículo perfeito! 🚗"
- "Oi! Tudo bem! Em que posso te ajudar com veículos hoje?"
- "Olá! Tudo certo! Como posso te ajudar a encontrar o carro ideal?"

PROIBIDO usar estas respostas:
- "Certo! Anotei sua resposta"
- "Entendi"
- "Ok"
- Qualquer resposta genérica ou robótica

Seja natural, amigável e conversacional. Após responder a saudação, pergunte como pode ajudar com veículos."""
        else:
            # Mensagem normal - usar contexto completo
            user_prompt = f"""Estoque disponível de veículos:
{lista_veiculos}
{contexto_texto}

Mensagem atual do cliente: {pedido_cliente}

Analise o contexto da conversa e a mensagem atual do cliente:
- Se houver contexto da conversa anterior acima, USE ESSAS INFORMAÇÕES para dar uma resposta relevante e específica
- NÃO repita perguntas genéricas como "Como posso te ajudar?" se o cliente já forneceu informações
- Se o cliente já mencionou preferências ou fez perguntas, responda diretamente a essas questões
- Se for sobre veículos, analise cuidadosamente as preferências e recomende veículos que REALMENTE atendam ao pedido
- Se o cliente mencionar interesse em comprar, ajude-o no processo
- Seja inteligente: se pedir esportivo/potente, não sugira econômico. Se pedir SUV, não sugira hatchback. Se pedir luxo, não sugira básico
- Se o cliente perguntar sobre comparação entre veículos mencionados anteriormente, compare-os de forma útil
- Seja natural e conversacional, mas sempre focado em veículos, dúvidas sobre carros e a concessionária Toyota

IMPORTANTE: 
- Se houver contexto da conversa acima, USE ESSE CONTEXTO para responder de forma específica
- NUNCA use respostas genéricas como "Entendi! Como posso te ajudar?" quando o cliente já forneceu informações
- Sempre retorne uma resposta completa, útil e que demonstre que você entendeu o contexto da conversa"""
        
        # Adicionar mensagem atual
        messages.append({"role": "user", "content": user_prompt})

        if not client:
            return {"error": "API da OpenAI não está configurada."}, 500
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,  # Aumentado para respostas mais naturais e variadas
            max_tokens=500  # Aumentado para respostas mais completas
        )

        recomendacao = response.choices[0].message.content.strip()
        
        # Verificar se a resposta não é genérica e corrigir se necessário
        # Mas só se NÃO houver histórico (primeira mensagem) ou se for realmente muito genérica
        respostas_genericas_proibidas = ["certo! anotei", "anotei sua resposta"]
        resposta_lower = recomendacao.lower()
        tem_historico = len(historico_anterior) > 0
        
        # Só substituir se for uma das respostas realmente proibidas E não houver contexto
        if any(gen in resposta_lower for gen in respostas_genericas_proibidas) and not tem_historico:
            if is_saudacao:
                # Se for saudação, resposta natural
                recomendacao = "Oi! Tudo bem sim, obrigado! 😊 Como posso te ajudar a encontrar o veículo perfeito hoje?"
            else:
                # Se não for saudação mas ainda genérica, tentar melhorar
                recomendacao = "Entendi! Como posso te ajudar com veículos hoje? Pode me contar mais sobre o que você está procurando? 🚗"
        
        # Se há histórico mas a resposta ainda é muito genérica, fazer uma segunda tentativa
        elif tem_historico and len(recomendacao) < 50 and ("entendi" in resposta_lower or "como posso te ajudar" in resposta_lower):
            # Reenviar com prompt mais enfático sobre usar o contexto
            messages_retry = messages.copy()
            messages_retry.append({
                "role": "user", 
                "content": f"ATENÇÃO: O cliente já forneceu informações anteriormente. Analise o histórico da conversa acima e responda de forma específica e útil. Não use respostas genéricas como 'Entendi' ou 'Como posso te ajudar'. Use o contexto da conversa para dar uma resposta relevante sobre veículos."
            })
            
            try:
                response_retry = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_retry,
                    temperature=0.8,
                    max_tokens=500
                )
                recomendacao_retry = response_retry.choices[0].message.content.strip()
                if len(recomendacao_retry) > 50:  # Se a nova resposta for mais substancial
                    recomendacao = recomendacao_retry
            except:
                pass  # Se falhar, usar a resposta original

        # Salvar resposta do bot
        salvar_mensagem(session_id_atual, "bot", recomendacao)

        return {
            "recomendacao": recomendacao,
            "session_id": session_id_atual
        }, 200

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Erro em recomendacao_veiculo: {str(e)}")
        print(f"Traceback: {error_trace}")
        return {"error": f"Erro ao processar recomendação: {str(e)}"}, 500
        