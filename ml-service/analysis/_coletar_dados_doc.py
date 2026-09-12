"""
Coleta os números reais usados no documento docs/relatorio-modelos-preditivos.pdf.

Roda o mesmo código de produção do notebook e despeja tudo em JSON, para que o
gerador do PDF nunca precise digitar um número à mão.

Uso (a partir de ml-service/):
    venv/Scripts/python.exe analysis/_coletar_dados_doc.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "analysis"))

from app.services import holt_winters_service as hw  # noqa: E402
from app.services import stock_service  # noqa: E402
from app.tests.generate_synthetic_data import gerar_dataset, PRODUTOS_META  # noqa: E402

import analysis_utils as au  # noqa: E402

SEED = 42
np.random.seed(SEED)

PROPHET_OK = au.prophet_disponivel()
if PROPHET_OK:
    from app.services import prophet_service as pr

ID_ESTAVEL, ID_VOLATIL = 1, 5

_, series = gerar_dataset(random_state=SEED)
nomes = {p["produto_id"]: p["nome"] for p in PRODUTOS_META}
meta = {p["produto_id"]: p for p in PRODUTOS_META}

dados: dict = {"prophet_ok": PROPHET_OK, "seed": SEED}

# ── 1. Tabela descritiva ─────────────────────────────────────────────────────
desc = []
for pid, s in series.items():
    ativos = s[s > 0]
    desc.append({
        "produto_id": pid,
        "nome": nomes[pid],
        "variabilidade": meta[pid]["variabilidade"],
        "media_diaria": round(float(ativos.mean()), 2),
        "desvio": round(float(s.std()), 2),
        "cv": round(float(s.std() / s.mean()), 2),
        "pct_zeros": round(float((s == 0).mean()) * 100, 1),
        "n_dias": int(len(s)),
    })
dados["descritiva"] = desc

# ── 2. Parâmetros ajustados pelo otimizador (prova de que ele BUSCA) ─────────
params = []
for pid in (ID_ESTAVEL, ID_VOLATIL):
    treino, _ = au.split_temporal(series[pid])
    ajustado = hw._ajustar_modelo(treino, True)
    p = ajustado.params
    params.append({
        "produto_id": pid,
        "nome": nomes[pid],
        "alpha": round(float(p["smoothing_level"]), 4),
        "beta": round(float(p["smoothing_trend"]), 4),
        "gamma": round(float(p["smoothing_seasonal"]), 4),
        "nivel_inicial": round(float(p["initial_level"]), 3),
        "tendencia_inicial": round(float(p["initial_trend"]), 5),
        "sazonais_iniciais": [round(float(v), 3) for v in p["initial_seasons"]],
    })
dados["params_hw"] = params

# ── 2b. Os mesmos parâmetros para TODOS os produtos (seção 13 do relatório) ──
alphas = []
for pid, s in series.items():
    treino, _ = au.split_temporal(s)
    p = hw._ajustar_modelo(treino, True).params
    alphas.append({
        "pid": pid,
        "nome": nomes[pid],
        "a": round(float(p["smoothing_level"]), 5),
        "b": round(float(p["smoothing_trend"]), 5),
        "g": round(float(p["smoothing_seasonal"]), 5),
    })
(RAIZ / "analysis" / "results" / "_alphas.json").write_text(
    json.dumps(alphas, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ── 3. Métricas walk-forward dos dois produtos-vitrine ──────────────────────
resultados = {}
for pid in (ID_ESTAVEL, ID_VOLATIL):
    r_hw = au.avaliar_holt_winters(series[pid])
    linha = {
        "produto_id": pid,
        "nome": nomes[pid],
        "n_treino": int(len(r_hw["treino"])),
        "n_validacao": int(len(r_hw["validacao"])),
        "treino_ini": str(r_hw["treino"].index.min().date()),
        "treino_fim": str(r_hw["treino"].index.max().date()),
        "valid_ini": str(r_hw["validacao"].index.min().date()),
        "valid_fim": str(r_hw["validacao"].index.max().date()),
        "hw": {"mape": r_hw["metricas"].mape, "rmse": r_hw["metricas"].rmse,
               "mae": r_hw["metricas"].mae},
    }
    if PROPHET_OK:
        r_pr = au.avaliar_prophet(series[pid])
        linha["prophet"] = {"mape": r_pr["metricas"].mape, "rmse": r_pr["metricas"].rmse,
                            "mae": r_pr["metricas"].mae}
    resultados[str(pid)] = linha
dados["walkforward"] = resultados

# ── 4. Backtesting rolling-origin ───────────────────────────────────────────
backtest = {}
for pid in (ID_ESTAVEL, ID_VOLATIL):
    bt_hw = au.backtesting_rolling(series[pid], au.prever_hw)
    entrada = {"holt_winters": bt_hw.to_dict("records")}
    if PROPHET_OK:
        bt_pr = au.backtesting_rolling(series[pid], au.prever_prophet)
        entrada["prophet"] = bt_pr.to_dict("records")
    backtest[str(pid)] = entrada
dados["backtesting"] = backtest

# ── 5. KPIs de estoque (mesma regra do prediction_service) ──────────────────
kpis = []
for pid in (ID_ESTAVEL, ID_VOLATIL):
    s = series[pid]
    metr_hw, prev_hw = hw.treinar_e_avaliar(s)
    candidatos = {"holt_winters": (metr_hw, prev_hw)}
    if PROPHET_OK:
        candidatos["prophet"] = pr.treinar_e_avaliar(s)
    vencedor = min(candidatos, key=lambda k: candidatos[k][0].mape)
    previsao = candidatos[vencedor][1]

    demanda_media = float(previsao.mean())
    desvio = float(s.std())
    z = stock_service.calcular_z_score(0.95)
    es = stock_service.calcular_estoque_seguranca(z, 3, desvio, demanda_media, 1.0)
    ponto = stock_service.calcular_ponto_reposicao(demanda_media, 3, es)
    estoque_atual = meta[pid]["estoque_atual"]
    dias = stock_service.calcular_dias_ate_ruptura(estoque_atual, demanda_media)
    kpis.append({
        "produto_id": pid, "nome": nomes[pid], "vencedor": vencedor,
        "demanda_media": round(demanda_media, 3), "desvio": round(desvio, 3),
        "z": round(z, 4), "lead_time": 3, "variab_lt": 1.0,
        "estoque_seguranca": round(es, 2), "ponto_reposicao": round(ponto, 2),
        "estoque_atual": estoque_atual,
        "dias_ate_ruptura": round(dias, 2) if dias is not None else None,
    })
dados["kpis"] = kpis

# ── 6. Comparativo geral (lê o CSV já gerado pelo notebook) ─────────────────
csv = RAIZ / "analysis" / "results" / "comparativo_modelos.csv"
comparativo = pd.read_csv(csv)
dados["comparativo"] = comparativo.to_dict("records")
vitorias = comparativo[comparativo["vencedor"]]["modelo"].value_counts().to_dict()
dados["vitorias"] = {k: int(v) for k, v in vitorias.items()}
dados["margens"] = []
for pid, g in comparativo.groupby("produto_id"):
    if len(g) == 2:
        mapes = g.set_index("modelo")["mape"]
        dados["margens"].append({
            "produto_id": int(pid),
            "nome": g["nome"].iloc[0],
            "margem_pp": round(abs(float(mapes["holt_winters"] - mapes["prophet"])), 4),
        })

destino = RAIZ / "analysis" / "results" / "dados_documento.json"
destino.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
print("JSON salvo:", destino)
print("Prophet OK:", PROPHET_OK, "| vitórias:", dados["vitorias"])
