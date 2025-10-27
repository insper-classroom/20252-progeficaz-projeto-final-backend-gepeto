import os
from dotenv import load_dotenv
from openai import OpenAI
from utils import get_all

load_dotenv(".cred")

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key) if openai_api_key else None


def get_recomendacao_veiculo(pedido_cliente):
    """
    Recebe o pedido do cliente e gera uma recomendação usando OpenAI
    
    Args:
        pedido_cliente (str): Descrição das necessidades do cliente
        
    Returns:
        str: Recomendação de veículo baseada nas necessidades
    """
    if not client:
        return None, "API da OpenAI não configurada. Verifique a variável OPENAI_API_KEY."
    
    # Busca todos os veículos disponíveis no banco
    veiculos = get_all()
    
    if not veiculos:
        return None, "Nenhum veículo encontrado no banco de dados."
    
    # Monta uma string com os veículos disponíveis
    lista_veiculos = "\n".join([
        f"- {veiculo.get('marca', 'Marca')} {veiculo.get('modelo', 'Modelo')} "
        f"({veiculo.get('ano', 'Ano')}) - R$ {veiculo.get('preco', 'Preço')}"
        for veiculo in veiculos
    ])
    
    # Prompt para a API da OpenAI
    prompt = f"""Você é um especialista em venda de veículos de uma concessionária.
    
Veículos disponíveis no nosso estoque:
{lista_veiculos}

Pedido do cliente: {pedido_cliente}

Analise as necessidades do cliente e recomende um ou mais veículos que melhor se adequem às suas necessidades.
Forneça uma resposta detalhada explicando por que esses veículos são ideais para o cliente.

Resposta:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um vendedor experiente de veículos que ajuda clientes a encontrar o carro ideal."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        recomendacao = response.choices[0].message.content
        return recomendacao, None
        
    except Exception as e:
        return None, f"Erro ao comunicar com a API da OpenAI: {str(e)}"

