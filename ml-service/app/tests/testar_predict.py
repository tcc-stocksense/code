from generate_synthetic_data import gerar_dataset
import json
import urllib.request

df, series = gerar_dataset()

pid = 1  # Arroz 5kg
serie = series[pid]
historico = [
    {"data": str(d.date()), "quantidade": int(q)}
    for d, q in serie.items() if q > 0
][-365:]

payload = {
    "produto_id": pid,
    "historico": historico,
    "lead_time_medio": 3,
    "variabilidade_lead_time": 1.0,
    "nivel_servico_alvo": 0.95,
    "estoque_atual": 40,
}

data = json.dumps(payload).encode()
req = urllib.request.Request(
    "http://localhost:8000/predict",
    data=data,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())

print(json.dumps(result, indent=2, ensure_ascii=False))
