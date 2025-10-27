# 20252-progeficaz-projeto-final-backend-gepeto

Sistema backend para recomendação de veículos utilizando inteligência artificial (OpenAI).

## 📋 Sobre o Projeto

Este projeto é uma API Flask que permite aos clientes solicitar recomendações personalizadas de veículos baseadas em suas necessidades. Utilizando a API da OpenAI, o sistema analisa o pedido do cliente e recomenda os veículos mais adequados do estoque.

## 🚀 Como Executar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Configuração do Ambiente

Copie o arquivo `env.example` e crie um arquivo `.env`:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=db_concessionaria
OPENAI_API_KEY=sua_chave_openai_aqui
```

### 3. Executar o Servidor

```bash
python servidor.py
```

O servidor estará disponível em `http://localhost:5000`

## 📡 Endpoints da API

### GET `/api/veiculos`
Retorna a lista de todos os veículos disponíveis.

**Resposta:**
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano": 2023,
    "preco": 120000
  }
]
```

### GET `/api/veiculos/<id>`
Retorna um veículo específico pelo ID.

**Resposta:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "marca": "Toyota",
  "modelo": "Corolla",
  "ano": 2023,
  "preco": 120000
}
```

### POST `/api/recomendacao`
Gera uma recomendação de veículo baseada no pedido do cliente usando IA.

**Body:**
```json
{
  "pedido": "Preciso de um carro econômico para ir ao trabalho todos os dias, com bom consumo e até 50 mil reais"
}
```

**Resposta:**
```json
{
  "recomendacao": "Com base nas suas necessidades, recomendo...",
  "pedido": "Preciso de um carro econômico para ir ao trabalho todos os dias, com bom consumo e até 50 mil reais"
}
```

## 🗄️ Estrutura do Banco de Dados

A coleção `veiculos` no MongoDB deve seguir esta estrutura:

```json
{
  "_id": "ObjectId",
  "marca": "string",
  "modelo": "string",
  "ano": "number",
  "preco": "number",
  "categoria": "string (opcional)",
  "combustivel": "string (opcional)",
  "potencia": "string (opcional)"
}
```

## 🛠️ Tecnologias Utilizadas

- **Flask**: Framework web Python
- **MongoDB**: Banco de dados NoSQL
- **OpenAI API**: Geração de recomendações inteligentes
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **pymongo**: Driver Python para MongoDB

## 📝 Licença

Projeto acadêmico - Faculdade

