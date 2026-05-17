# Motor de Otimização Preditiva de Estoque

Sistema web para previsão de demanda e gestão inteligente de estoque para pequenos e médios mercados de bairro.

## Serviços

| Serviço        | Tecnologia              | Porta |
|----------------|-------------------------|-------|
| Backend        | Kotlin / Spring Boot    | 8080  |
| AI/ML Service  | Python / FastAPI        | 8000  |
| Frontend       | HTML / CSS / JS (nginx) | 80    |
| Banco de Dados | MySQL 8.0               | 3306  |

## Pré-requisitos

- Docker e Docker Compose instalados
- Arquivo `.env` na raiz com as variáveis abaixo

## Variáveis de ambiente

```
DB_ROOT_PASSWORD=
DB_USERNAME=
DB_PASSWORD=
```

## Como executar

```bash
cp .env.example .env   # preencha as variáveis
docker-compose up --build
```

Acesse o frontend em `http://localhost`.
API disponível em `http://localhost:8080`.
AI/ML Service em `http://localhost:8000`.

## Estrutura

```
.
├── backend/      # API REST (Kotlin / Spring Boot)
├── ml-service/   # Motor preditivo (Python / FastAPI)
└── frontend/     # Interface web (HTML / CSS / JS)
```
