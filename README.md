# 🧠 Projeto Final — Backend Flask (Concessionária Inteligente)

![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white&style=for-the-badge)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-4EA94B?logo=mongodb&logoColor=white&style=for-the-badge)
![Gunicorn](https://img.shields.io/badge/Gunicorn-Server-499848?logo=gunicorn&logoColor=white&style=for-the-badge)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazon-aws&logoColor=white&style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white&style=for-the-badge)

---

## 📋 Sobre o Projeto

O **Gepeto Backend** é uma API RESTful desenvolvida em **Flask**, que fornece:
- Recomendações de veículos baseadas em IA (OpenAI API),
- CRUD completo de veículos,
- Login e autenticação JWT,
- Integração com MongoDB Atlas,
- E deploy escalável via **Gunicorn + systemd** na **AWS EC2**.

---

## ⚙️ Tecnologias Utilizadas

| Categoria          | Tecnologia / Serviço          |
|--------------------|-------------------------------|
| Framework Web      | Flask                         |
| Servidor HTTP      | Gunicorn                      |
| Banco de Dados     | MongoDB Atlas                 |
| Autenticação       | JWT (PyJWT)                   |
| IA de Recomendação | OpenAI API                    |
| Configuração       | python-dotenv                 |
| Deploy             | AWS EC2 (Amazon Linux 2023)   |

---

## 🧩 Estrutura da API

| Endpoint | Método | Descrição |
|-----------|---------|-----------|
| `/api/veiculos` | GET | Lista todos os veículos |
| `/api/veiculos` | POST | Cadastra um novo veículo |
| `/api/veiculos/<id>` | GET | Retorna um veículo pelo ID |
| `/api/veiculos/<id>` | PUT | Atualiza um veículo |
| `/api/veiculos/<id>` | DELETE | Remove um veículo |
| `/api/recomendacao` | POST | Gera recomendações com IA |
| `/login` | POST | Retorna token JWT para acesso ao dashboard |

---

## 🧠 Estrutura do Banco (MongoDB)

```json
{
  "_id": "ObjectId",
  "marca": "Toyota",
  "modelo": "Yaris",
  "ano": 2025,
  "preco_estimado": 90000,
  "categoria": "hatch compacto",
  "motor": "1.5L Dual VVT-i Flex",
  "potencia": "110 cv (etanol)",
  "consumo": "12 km/l cidade",
  "tracao": "dianteira",
  "score": 0.92
}

🧰 Instalação Local
1️⃣ Clonar e acessar o projeto
git clone https://github.com/insper-classroom/20252-progeficaz-projeto-final-backend-gepeto.git
cd 20252-progeficaz-projeto-final-backend-gepeto

2️⃣ Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

3️⃣ Instalar dependências
pip install -r requirements.txt

4️⃣ Criar o arquivo .cred (⚠️ confidencial)

Nunca envie este arquivo para o GitHub.
Adicione-o ao .gitignore e mantenha apenas no ambiente de produção.

MONGO_URI=<sua conexão MongoDB Atlas>
DB_NAME=db_concessionaria

OPENAI_API_KEY=<sua chave da OpenAI>

FRONT_URL=http://<IP_PUBLICO>:5173
CORS_ORIGINS=http://<IP_PUBLICO>:5173

JWT_SECRET=<sua chave secreta JWT>

5️⃣ Rodar localmente
python servidor.py


Acesse:
👉 http://127.0.0.1:5000/api/veiculos

☁️ Deploy na AWS EC2
🔧 1️⃣ Acessar sua instância
ssh -i ~/.ssh/Projeto3-Gepeto.pem ec2-user@<IP_PUBLICO>

📦 2️⃣ Instalar dependências do sistema
sudo dnf update -y
sudo dnf install git python3-pip -y

🧱 3️⃣ Clonar e preparar o ambiente
git clone https://github.com/insper-classroom/20252-progeficaz-projeto-final-backend-gepeto.git
cd 20252-progeficaz-projeto-final-backend-gepeto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

⚙️ 4️⃣ Rodar com Gunicorn
nohup .venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 servidor:app > ~/nohup.out 2>&1 &


Verificar:

ps aux | grep gunicorn

🔄 Criar serviço systemd (rodar automaticamente)
sudo nano /etc/systemd/system/gepeto-backend.service


Conteúdo:

[Unit]
Description=Gepeto Backend Flask API (Gunicorn)
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/gepeto-backend/20252-progeficaz-projeto-final-backend-gepeto
Environment="PATH=/home/ec2-user/gepeto-backend/20252-progeficaz-projeto-final-backend-gepeto/.venv/bin"
ExecStart=/home/ec2-user/gepeto-backend/20252-progeficaz-projeto-final-backend-gepeto/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 servidor:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


Ativar e iniciar:

sudo systemctl daemon-reload
sudo systemctl enable gepeto-backend
sudo systemctl start gepeto-backend
sudo systemctl status gepeto-backend


Logs:

sudo journalctl -u gepeto-backend -f

🌐 Configurar Acesso Externo (AWS)

Abra as portas no Security Group:

Porta	Descrição	Protocolo	Origem
22	SSH	TCP	Seu IP
5000	Backend Flask	TCP	0.0.0.0/0
5173	Frontend React	TCP	0.0.0.0/0
💬 Frontend (Deploy e Integração)

URL base configurada no arquivo src/config.js do front:

export const API_BASE = "http://<IP_PUBLICO>:5000";


Frontend também pode rodar automaticamente:

sudo nano /etc/systemd/system/gepeto-frontend.service

[Unit]
Description=Gepeto Frontend (React + Vite)
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/20252-progeficaz-projeto-final-frontend-gepeto-frontend/frontend
ExecStart=/usr/bin/npm run dev -- --host 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


E ativar:

sudo systemctl daemon-reload
sudo systemctl enable gepeto-frontend
sudo systemctl start gepeto-frontend

👥 Equipe
🧠 Nader Taha	PO / Full Stack	@nadertaha06

💻 Ian Caodaglio	Backend / Flask	@iancaodaglio

⚙️ Davi Homem	Frontend / React	@davichmello

🔍 Prem Bueno	Integração / Testes	@prembueno
