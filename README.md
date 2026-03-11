# 🏈 SGE Sports Store — Sistema de Gestão de Estoque

> API REST profissional para gestão de estoque de uma loja de roupas esportivas (NFL, NBA, MLB, NHL), construída com FastAPI, PostgreSQL e integração com IA via LangChain.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![LangChain](https://img.shields.io/badge/LangChain-0.3-purple)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)

---

## ✨ Features

- 🛍️ **Gestão de Produtos** — CRUD completo com filtro por liga, time, tamanho e categoria
- 📦 **Controle de Estoque** — Movimentações (entrada, saída, ajuste) com histórico completo
- 🧾 **Pedidos & Vendas** — Criação de pedidos com dedução automática de estoque
- 👥 **Clientes** — Cadastro e histórico de compras
- 🤖 **IA com LangChain** — Chatbot assistente + análise inteligente de alertas de reposição
- 🔐 **Autenticação JWT** — Login seguro com OAuth2
- 🐳 **Docker Ready** — Sobe tudo com um comando
- 🗃️ **Migrations** — Alembic configurado com suporte async
- ✅ **Testes** — Pytest com AsyncClient

---

## 🚀 Rodando o projeto

### Pré-requisitos
- Docker & Docker Compose
- Python 3.12+ (para rodar localmente)

### Com Docker (recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sge-sports.git
cd sge-sports

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com sua OPENAI_API_KEY e SECRET_KEY

# Suba os containers
docker-compose up --build
```

API disponível em: **http://localhost:8000**
Documentação: **http://localhost:8000/docs**

### Localmente

```bash
# Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o .env
cp .env.example .env

# Rode as migrations
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload
```

---

## 📁 Estrutura do Projeto

```
sge-sports/
├── app/
│   ├── api/v1/
│   │   ├── routes/          # Endpoints FastAPI
│   │   └── deps.py          # Dependências (auth)
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # Engine async + sessão
│   │   └── security.py      # JWT + bcrypt
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Regras de negócio
│   ├── repositories/        # Repository Pattern (acesso ao BD)
│   ├── ai/
│   │   └── chatbot.py       # LangChain — Chatbot + Análise de estoque
│   └── main.py
├── alembic/                 # Migrations
├── tests/                   # Pytest
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## 📋 Endpoints

### Auth
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Cadastrar usuário |
| POST | `/api/v1/auth/login` | Login (retorna JWT) |

### Produtos
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/products/` | Listar com filtros |
| POST | `/api/v1/products/` | Criar produto |
| GET | `/api/v1/products/{id}` | Detalhar produto |
| PATCH | `/api/v1/products/{id}` | Atualizar produto |
| DELETE | `/api/v1/products/{id}` | Desativar produto |
| GET | `/api/v1/products/low-stock` | Produtos abaixo do mínimo |

### Estoque
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/stock/movements` | Registrar movimentação |
| GET | `/api/v1/stock/movements/{product_id}` | Histórico do produto |

### Pedidos
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/orders/` | Criar pedido |
| GET | `/api/v1/orders/` | Listar pedidos |
| GET | `/api/v1/orders/{id}` | Detalhar pedido |
| PATCH | `/api/v1/orders/{id}/status` | Atualizar status |

### Clientes
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/clients/` | Cadastrar cliente |
| GET | `/api/v1/clients/` | Listar clientes |
| GET | `/api/v1/clients/{id}` | Detalhar cliente |
| GET | `/api/v1/clients/{id}/orders` | Histórico de compras |
| PATCH | `/api/v1/clients/{id}` | Atualizar cliente |

### 🤖 IA
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/ai/chat` | Chat com assistente |
| GET | `/api/v1/ai/alerts/stock` | Análise IA de estoque baixo |

---

## 🧪 Testes

```bash
# Instale aiosqlite para os testes
pip install aiosqlite

# Rode os testes
pytest -v
```

---

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas bem definidas:

```
Request → Router → Service → Repository → Database
                ↓
            Schemas (Pydantic validation)
```

- **Routers** — Apenas definem os endpoints e delegam para services
- **Services** — Toda a lógica de negócio (validações, regras)
- **Repositories** — Toda a comunicação com o banco de dados
- **Models** — Representação das tabelas (SQLAlchemy)
- **Schemas** — Validação de entrada/saída (Pydantic)

---

## 🤖 Integração com IA

A IA usa **LangChain + OpenAI GPT-4o-mini** para dois recursos:

1. **Chatbot Assistente** (`/ai/chat`) — Responde perguntas sobre produtos, times e estoque
2. **Análise de Reposição** (`/ai/alerts/stock`) — Analisa produtos com estoque baixo e gera relatório priorizado com sugestões de reposição

---

## 👨‍💻 Desenvolvedor

**Guilherme Donato**
- Backend Developer | Python | FastAPI | Django
- [GitHub](https://github.com/guilhermedonato) • [LinkedIn](https://linkedin.com/in/guilhermedonato)
