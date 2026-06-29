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

## Como executar (completo via Docker)

```bash
docker compose up --build
```

Acesse o frontend em `http://localhost`.
API disponível em `http://localhost:8080`.
AI/ML Service em `http://localhost:8000`.

## Rodando localmente (desenvolvimento)

Ideal para desenvolver o backend sem rebuildar a imagem Docker a cada alteração.

### Pré-requisitos

- Docker Desktop instalado e rodando
- Java 17+

### Passo 1 — Configurar variáveis de ambiente

Crie o arquivo `.env` na raiz do projeto (já está no `.gitignore`):

```
DB_ROOT_PASSWORD=suasenharoot
DB_USERNAME=appuser
DB_PASSWORD=suasenha
```

> `DB_USERNAME` não pode ser `root` — o MySQL Docker reserva esse usuário internamente.

### Passo 2 — Subir o banco de dados

```bash
docker compose up db -d
```

Aguarde o container ficar `healthy`:

```bash
docker compose ps
```

### Passo 3 — Rodar o backend

Na pasta `backend/`, passe as credenciais como variáveis de ambiente:

```powershell
# PowerShell
$env:DB_USERNAME="appuser"; $env:DB_PASSWORD="suasenha"; .\gradlew.bat bootRun
```

```bash
# Bash / WSL
DB_USERNAME=appuser DB_PASSWORD=suasenha ./gradlew bootRun
```

O Flyway executa as migrations automaticamente na primeira inicialização.
O servidor sobe na porta **8080** — o processo fica travado em 85% no Gradle, isso é normal.

### Recriar o banco do zero

Se precisar recriar o banco (ex: trocar credenciais ou corrigir erros de inicialização):

```bash
docker compose down -v
docker compose up db -d
```

## Estrutura

```
.
├── backend/      # API REST (Kotlin / Spring Boot)
├── ml-service/   # Motor preditivo (Python / FastAPI)
└── frontend/     # Interface web (HTML / CSS / JS)
```
