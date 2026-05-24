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

### Gerar o CSV de vendas

```powershell
python app/tests/generate_synthetic_data.py
```

Gera `app/tests/fixtures/5_vendas_sintetico.csv` com 365 dias de histórico para 10 produtos simulando um mercadinho de bairro.

### Chamar o endpoint `/predict`

Com o servidor rodando, execute em outro terminal (venv ativo):

```powershell
python -c "
from app.tests.generate_synthetic_data import gerar_dataset
import json, urllib.request

df, series = gerar_dataset()

pid = 1  # Arroz 5kg — demanda estável
serie = series[pid]
historico = [
    {'data': str(d.date()), 'quantidade': int(q)}
    for d, q in serie.items() if q > 0
][-365:]

payload = {
    'produto_id': pid,
    'historico': historico,
    'lead_time_medio': 3,
    'variabilidade_lead_time': 1.0,
    'nivel_servico_alvo': 0.95,
    'estoque_atual': 40
}

data = json.dumps(payload).encode()
req = urllib.request.Request('http://localhost:8000/predict', data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())

print('Modelo selecionado:', result['modelo_selecionado'])
print('Ponto de reposição:', result['ponto_reposicao'])
print('Estoque de segurança:', result['estoque_seguranca'])
print('Dias até ruptura:', result['dias_ate_ruptura'])
print('Classe ABC:', result['classe_abc'])
print('Métricas HW:', result['metricas'].get('holt_winters'))
print('Métricas Prophet:', result['metricas'].get('prophet'))
"
```

Ou use o Swagger em `http://localhost:8000/docs` → `POST /predict` → **Try it out**.

---

## Rodando os testes unitários

```powershell
pytest app/tests/ -v --tb=short
```

Valida as fórmulas de estoque de segurança, classificação ABC, Holt-Winters e Prophet antes de chamar o endpoint.
