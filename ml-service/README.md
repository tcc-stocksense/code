# ml-service — Motor Preditivo StockSense

Serviço Python/FastAPI responsável pela previsão de demanda e cálculo de KPIs de estoque.

---

## Rodando com Docker (recomendado)

Na raiz do projeto (`tcc-stocksense/code`), suba apenas o ml-service:

```bash
docker-compose up ml-service
```

O serviço ficará disponível em `http://localhost:8000`.

---

## Rodando localmente (desenvolvimento)

Use esse modo quando quiser testar mudanças rapidamente sem rebuildar a imagem Docker.

### Pré-requisitos

- Python 3.10+
- PowerShell (Windows)

### 1. Ativar o ambiente virtual

Dentro da pasta `ml-service/`:

```powershell
.\venv\Scripts\Activate.ps1
```

O prompt deve exibir `(venv)` confirmando que está ativo.

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

> Prophet pode demorar na primeira instalação — ele instala `pystan` internamente.

### 3. Subir o servidor

```powershell
uvicorn main:app --reload --port 8000
```

Acesse `http://localhost:8000/docs` para a interface Swagger interativa.

### 4. Verificar que está respondendo

Em outro terminal (com venv ativo):

```powershell
curl http://localhost:8000/health
```

---

## Testando com dados sintéticos

O projeto inclui um gerador de dados sintéticos que simula 365 dias de vendas de um mercadinho de bairro com 10 produtos (Arroz, Feijão, Leite, etc.), com sazonalidade semanal e variabilidade realista.

Há dois scripts de teste em `app/tests/`, ambos devem ser executados com o servidor já rodando e em outro terminal com o venv ativo.

---

### Opção 1 — `testar_predict.py` (resultado direto no terminal)

Gera os dados sintéticos, chama o `POST /predict` e imprime o resultado JSON no terminal.

```powershell
py .\app\tests\testar_predict.py
```

Use quando quiser ver o retorno do motor rapidamente sem sair do terminal.

---

### Opção 2 — `gerar_payload_postman.py` (testar pelo Postman)

Gera o payload de entrada e salva em `app/tests/fixtures/payload_predict_produto1.json`.

```powershell
py .\app\tests\gerar_payload_postman.py
```

Depois, no Postman:

- Método: `POST`
- URL: `http://localhost:8000/predict`
- Body → **raw** → **JSON** → cole o conteúdo do arquivo gerado

Para testar outro produto, altere a variável `pid` no script (valores de 1 a 10).

---

### Opção 3 — Swagger interativo

Acesse `http://localhost:8000/docs` → `POST /predict` → **Try it out** e cole o payload gerado pelo `gerar_payload_postman.py`.

---

### Gerar apenas o CSV de vendas

Para exportar o histórico sintético no formato da planilha `5_vendas`:

```powershell
python app/tests/generate_synthetic_data.py
```

Gera `app/tests/fixtures/5_vendas_sintetico.csv` com 365 dias para os 10 produtos.

---

## Rodando os testes unitários

```powershell
pytest app/tests/ -v --tb=short
```

Valida as fórmulas de estoque de segurança, classificação ABC, Holt-Winters e Prophet antes de chamar o endpoint.
