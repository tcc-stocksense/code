"""
benchmark_motor.py — T-54: mede o custo do lote do motor preditivo (StockSense).

Objetivo
--------
Substituir a estimativa "10-20+ min" do relatório por um número **medido**, para
decidir com evidência se o Épico 7 (motor assíncrono) é MVP ou MVP-opcional.
O resultado é gravado em `docs/benchmark-motor.md` (usado na metodologia do TCC).

Por que medir via /predict e não via /motor/recalcular?
-------------------------------------------------------
O lote do backend (`POST /api/motor/recalcular`, T-23) é, na prática, **N chamadas
SEQUENCIAIS** a `POST /predict` no ml-service — o `MotorController` itera
`executarMotor(produtoId)`, e cada iteração faz um Feign `/predict`. A orquestração
Spring e as escritas no MySQL são desprezíveis perto do custo de treinar Prophet +
Holt-Winters por produto. Então dirigir N `/predict` sequenciais mede exatamente o
custo dominante do lote, com a vantagem de **não** exigir banco, JWT nem importação
de `.xlsx` — e de ser 100 % reprodutível (semente fixa).
Para o número ponta a ponta (com a folga de orquestração/DB), ver `medir_e2e()` abaixo
— deixado como stub porque exige o backend + dados já importados.

Pré-requisitos
--------------
- ml-service no ar:  `uvicorn main:app --port 8000`
- **Prophet FUNCIONANDO** (CmdStan instalado — ver SESSION.md > "Pendente e Bugs
  Conhecidos"). Se o Prophet falhar, o motor faz *fallback* para Holt-Winters e os
  tempos ficam artificialmente baixos, **não refletindo o custo real**. O script
  detecta isso no warm-up e AVISA — não confie no resultado se o aviso aparecer.

Uso
---
    python benchmark_motor.py                         # volumes 50, 150, 300
    python benchmark_motor.py --produtos 30 100 300   # volumes customizados
    python benchmark_motor.py --url http://localhost:8000 --dias 365

Rodar a partir da pasta `ml-service/` (para o import de `app.tests...` funcionar).
"""
from __future__ import annotations

import argparse
import statistics
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

# Reusa o gerador sintético já existente (T-54 pede reuso explícito).
from app.tests.generate_synthetic_data import PRODUTOS_META, _gerar_serie_produto

# ── Configuração padrão ───────────────────────────────────────────────────────
VOLUMES_PADRAO: list[int] = [50, 150, 300]
ML_URL_PADRAO: str = "http://localhost:8000"
DIAS_PADRAO: int = 365          # histórico por produto (mín. do motor: 90)
WARMUPS: int = 2                # chamadas descartadas p/ pagar o cold start do Prophet
LIMITE_FEIGN_S: float = 30.0    # read-timeout do Feign no backend — conta estouros
SEMENTE: int = 42


def construir_series(
    n: int,
    dias: int,
    data_inicio: str = "2024-01-01",
) -> list[tuple[int, pd.DataFrame]]:
    """
    Gera N produtos sintéticos ciclando os templates de PRODUTOS_META.

    Cada produto usa uma semente própria (SEMENTE + i), então as séries diferem
    entre si mas são reprodutíveis entre execuções. Retorna apenas os dias com
    venda (quantidade > 0), no formato consumido por montar_payload().
    """
    datas = pd.date_range(start=data_inicio, periods=dias, freq="D")
    produtos: list[tuple[int, pd.DataFrame]] = []
    for i in range(n):
        template = PRODUTOS_META[i % len(PRODUTOS_META)]
        meta = {**template, "produto_id": i + 1}
        rng = np.random.default_rng(SEMENTE + i)
        df = _gerar_serie_produto(meta, datas, rng)
        vendas = df[df["quantidade"] > 0][["data_hora", "quantidade"]].reset_index(drop=True)
        produtos.append((i + 1, vendas))
    return produtos


def montar_payload(produto_id: int, vendas: pd.DataFrame) -> dict:
    """
    Monta o corpo do POST /predict para um produto.

    Envia `is_promocional` VAZIO de propósito: é assim que o backend atual
    (`MotorService.montarRequest`) chama o motor hoje — medir o lote real exige
    reproduzir esse comportamento. (A omissão do regressor é tratada na T-55.)
    """
    historico = [
        {"data": row.data_hora, "quantidade": int(row.quantidade)}
        for row in vendas.itertuples(index=False)
    ]
    return {
        "produto_id": produto_id,
        "historico": historico,
        "lead_time_medio": 3,
        "variabilidade_lead_time": 1.0,
        "nivel_servico_alvo": 0.95,
        "estoque_atual": 40,
        "is_promocional": [],
    }


def warm_up(client: httpx.Client, url: str, produtos: list[tuple[int, pd.DataFrame]]) -> bool:
    """
    Dispara algumas chamadas descartadas para pagar o cold start do Prophet
    (compilação Stan) antes de cronometrar — mesma lógica da T-53.

    Retorna True se o Prophet respondeu (apareceu em `metricas`); False se só
    veio Holt-Winters (Prophet caiu → os números não refletirão o custo real).
    """
    pid, vendas = produtos[0]
    prophet_ok = False
    for _ in range(WARMUPS):
        r = client.post(f"{url}/predict", json=montar_payload(pid, vendas))
        r.raise_for_status()
        prophet_ok = "prophet" in r.json().get("metricas", {})
    return prophet_ok


def medir_volume(
    client: httpx.Client,
    url: str,
    produtos: list[tuple[int, pd.DataFrame]],
) -> dict:
    """Cronometra N chamadas /predict sequenciais (o lote do backend em essência)."""
    tempos: list[float] = []
    falhas = 0
    estouros = 0
    modelos: Counter = Counter()

    inicio = time.perf_counter()
    for pid, vendas in produtos:
        t = time.perf_counter()
        try:
            r = client.post(f"{url}/predict", json=montar_payload(pid, vendas))
            r.raise_for_status()
        except Exception as exc:  # noqa: BLE001 — benchmark tolera falha isolada, como o lote real
            falhas += 1
            print(f"    ! produto {pid} falhou: {exc}")
            continue
        dt = time.perf_counter() - t
        tempos.append(dt)
        if dt > LIMITE_FEIGN_S:
            estouros += 1
        modelos.update(r.json().get("metricas", {}).keys())
    total_wall = time.perf_counter() - inicio

    return {
        "n": len(produtos),
        "sucesso": len(tempos),
        "falhas": falhas,
        "total_s": total_wall,
        "media_s": statistics.mean(tempos) if tempos else 0.0,
        "mediana_s": statistics.median(tempos) if tempos else 0.0,
        "max_s": max(tempos) if tempos else 0.0,
        "estouros_30s": estouros,
        "modelos": dict(modelos),
    }


def escrever_relatorio(
    resultados: list[dict],
    url: str,
    dias: int,
    prophet_ok: bool,
    destino: Path,
) -> Path:
    """Grava/atualiza a tabela de benchmark em docs/ (formato Markdown do TCC)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")

    linhas = [
        "# Benchmark do lote do motor — T-54",
        "",
        "> Gerado por `ml-service/benchmark_motor.py`. Mede N chamadas `/predict` sequenciais,",
        "> que é o custo dominante do lote `POST /api/motor/recalcular` (ver docstring do script).",
        "",
        f"- **Data:** {agora}",
        f"- **ml-service:** {url}",
        f"- **Histórico por produto:** {dias} dias (sintético, semente {SEMENTE})",
        f"- **Prophet ativo:** {'✅ sim' if prophet_ok else '❌ NÃO — números NÃO confiáveis (fallback Holt-Winters)'}",
        "",
        "| Nº produtos | Tempo total | Médio/produto | Mediana | Máx/produto | Chamadas > 30 s | Falhas |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in resultados:
        linhas.append(
            f"| {r['n']} "
            f"| {r['total_s']:.1f} s ({r['total_s']/60:.1f} min) "
            f"| {r['media_s']:.2f} s "
            f"| {r['mediana_s']:.2f} s "
            f"| {r['max_s']:.2f} s "
            f"| {r['estouros_30s']} "
            f"| {r['falhas']} |"
        )

    linhas += [
        "",
        "## Como interpretar",
        "",
        "- **Tempo total** é o que o lojista esperaria numa requisição síncrona única.",
        "  Regra prática: se para 300 produtos ficar em poucos segundos, o lote síncrono",
        "  basta e o **Épico 7 vira `MVP-opcional`**; se der minutos, o async é **`MVP`**.",
        "- **Chamadas > 30 s** indicam produtos que estourariam o `read-timeout` do Feign",
        "  em produção (falhariam individualmente no lote real).",
        "- **Prophet ativo** precisa ser ✅; se ❌, rode de novo após instalar o CmdStan",
        "  (SESSION.md), senão o custo real do modelo mais caro fica de fora.",
        "",
        "## Conclusão (preencher após rodar)",
        "",
        "> _Decisão de prioridade do Épico 7 com base nos números acima: ..._",
        "",
    ]
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return destino.resolve()


def medir_e2e() -> None:
    """
    STUB — medição ponta a ponta via POST /api/motor/recalcular (backend real).

    Captura, além do custo dos modelos, a orquestração Spring + escritas no MySQL.
    Exige um setup bem maior, por isso fica como evolução opcional:
      1. Subir backend + MySQL + ml-service (docker-compose).
      2. POST /api/auth/login → obter JWT.
      3. Importar N produtos e vendas: POST /api/importacao/produtos e /vendas
         (multipart .xlsx — gerar com openpyxl a partir de construir_series()).
      4. Cronometrar POST /api/motor/recalcular (Authorization: Bearer <jwt>).
      5. Repetir por volume, limpando o banco entre execuções.
    Como a orquestração/DB é desprezível perto do Prophet, a medição via /predict
    acima já responde à pergunta da T-54; este modo é só para o número "oficial".
    """
    raise NotImplementedError("Modo E2E opcional — ver docstring.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark do lote do motor (T-54).")
    parser.add_argument("--url", default=ML_URL_PADRAO, help="URL base do ml-service.")
    parser.add_argument("--produtos", type=int, nargs="+", default=VOLUMES_PADRAO,
                        help="Volumes de SKUs a medir (ex.: --produtos 50 150 300).")
    parser.add_argument("--dias", type=int, default=DIAS_PADRAO,
                        help="Dias de histórico por produto (mín. 90).")
    parser.add_argument("--saida", type=Path, default=None,
                        help="Arquivo de saída (padrão: ../docs/benchmark-motor.md).")
    args = parser.parse_args()

    destino = args.saida or (Path(__file__).parent.parent / "docs" / "benchmark-motor.md")

    print(f"Benchmark do motor · ml-service={args.url} · {args.dias} dias/produto")
    # Gera o maior volume uma vez e fatia — séries são reprodutíveis por índice.
    maior = max(args.produtos)
    todos = construir_series(maior, args.dias)

    with httpx.Client(timeout=httpx.Timeout(120.0)) as client:
        print(f"  Warm-up ({WARMUPS} chamadas) para o cold start do Prophet...")
        prophet_ok = warm_up(client, args.url, todos)
        if not prophet_ok:
            print("  ⚠️  Prophet NÃO respondeu — medindo só Holt-Winters. "
                  "Números NÃO refletem o custo real (ver SESSION.md > CmdStan).")

        resultados: list[dict] = []
        for n in sorted(args.produtos):
            print(f"  Medindo {n} produtos...")
            r = medir_volume(client, args.url, todos[:n])
            print(f"    total={r['total_s']:.1f}s  médio={r['media_s']:.2f}s/produto  "
                  f">30s={r['estouros_30s']}  falhas={r['falhas']}  modelos={r['modelos']}")
            resultados.append(r)

    caminho = escrever_relatorio(resultados, args.url, args.dias, prophet_ok, destino)
    print(f"\nRelatório gravado em: {caminho}")


if __name__ == "__main__":
    main()
