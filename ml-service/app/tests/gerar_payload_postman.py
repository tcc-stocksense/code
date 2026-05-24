"""
Gera o payload JSON para testar o POST /predict no Postman.

Uso:
    py app/tests/gerar_payload_postman.py

Saída:
    app/tests/fixtures/payload_predict_produto{pid}.json
"""
from generate_synthetic_data import gerar_dataset
from pathlib import Path
import json

df, series = gerar_dataset()

pid = 1  # Arroz 5kg — altere aqui para testar outro produto (1-10)
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

destino = Path(__file__).parent / "fixtures" / f"payload_predict_produto{pid}.json"
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"Payload gerado: {destino.resolve()}")
print(f"Produto: {pid} | Registros no historico: {len(historico)}")
