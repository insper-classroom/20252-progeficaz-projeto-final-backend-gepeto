# 🧠 Projeto Final — Backend Flask (Concessionária Inteligente)

![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white&style=for-the-badge)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-4EA94B?logo=mongodb&logoColor=white&style=for-the-badge)
![Gunicorn](https://img.shields.io/badge/Gunicorn-Server-499848?logo=gunicorn&logoColor=white&style=for-the-badge)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazon-aws&logoColor=white&style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white&style=for-the-badge)

---

## 🌐 Deploy da API

A API está atualmente hospedada e acessível publicamente no link abaixo:

👉 **[http://56.124.79.244:5000/api/veiculos](http://56.124.79.244:5000/api/veiculos)**



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
