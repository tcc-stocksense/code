"""
Classificação ABC de produtos por representatividade no faturamento.

Implementa a curva ABC conforme definido no CLAUDE.md:
    A → top 80 % do faturamento acumulado
    B → de 80 % a 95 %
    C → de 95 % a 100 %

Fallback documentado: quando valor_venda não está disponível,
usa quantidade vendida como proxy e sinaliza abc_proxy=True.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_LIMIAR_A: float = 80.0
_LIMIAR_B: float = 95.0


@dataclass(frozen=True)
class ResultadoAbc:
    """Resultado da classificação ABC para um produto."""

    produto_id: int
    classe: str               # "A", "B" ou "C"
    percentual_acumulado: float


def classificar_abc(dados: list[dict]) -> tuple[list[ResultadoAbc], bool]:
    """
    Classifica uma lista de produtos nas classes A, B e C por faturamento.

    Ordena os produtos por faturamento decrescente, calcula o percentual
    acumulado sobre o total e atribui a classe conforme os limiares definidos
    no CLAUDE.md. Quando nenhum produto possui valor_venda, usa a quantidade
    vendida como proxy e sinaliza abc_proxy=True.

    Args:
        dados: Lista de dicionários, um por produto, com as chaves:
               - produto_id (int): identificador do produto.
               - faturamento (float | None): receita total do produto.
                 Obrigatório para não acionar o fallback.
               - quantidade (int): total de unidades vendidas. Usado
                 como proxy quando faturamento é None ou zero para todos.

    Returns:
        resultados: Lista de ResultadoAbc ordenada por faturamento
                    decrescente, com a classe e o percentual acumulado
                    de cada produto.
        abc_proxy: True quando a classificação usou quantidade como
                   substituto de faturamento.
    """
    if not dados:
        return [], False

    faturamentos = [d.get("faturamento") for d in dados]
    total_faturamento = sum(f or 0.0 for f in faturamentos)
    abc_proxy = any(f is None for f in faturamentos) or total_faturamento == 0.0

    if abc_proxy:
        logger.warning(
            "valor_venda ausente ou zerado — usando quantidade como proxy para classificação ABC"
        )
        valores = [float(d.get("quantidade", 0)) for d in dados]
    else:
        valores = [float(f) for f in faturamentos]  # type: ignore[arg-type]

    total = sum(valores)

    if total == 0.0:
        resultados = [
            ResultadoAbc(produto_id=d["produto_id"], classe="C", percentual_acumulado=100.0)
            for d in dados
        ]
        return resultados, abc_proxy

    # Ordena por valor decrescente; produto_id como critério de desempate
    indices_ordenados = sorted(
        range(len(dados)),
        key=lambda i: (-valores[i], dados[i]["produto_id"]),
    )

    # Produto único representa 100 % do faturamento — por definição é o mais
    # importante, logo sempre classe A independentemente do percentual acumulado.
    if len(indices_ordenados) == 1:
        return [
            ResultadoAbc(
                produto_id=dados[indices_ordenados[0]]["produto_id"],
                classe="A",
                percentual_acumulado=100.0,
            )
        ], abc_proxy

    resultados: list[ResultadoAbc] = []
    acumulado = 0.0

    for idx in indices_ordenados:
        acumulado += valores[idx]
        percentual = round((acumulado / total) * 100.0, 4)
        resultados.append(
            ResultadoAbc(
                produto_id=dados[idx]["produto_id"],
                classe=_atribuir_classe(percentual),
                percentual_acumulado=percentual,
            )
        )

    return resultados, abc_proxy


def _atribuir_classe(percentual_acumulado: float) -> str:
    """
    Atribui a classe ABC com base no percentual acumulado de faturamento.

    Limites (inclusive nos dois extremos de cada faixa):
        A → percentual_acumulado ≤ 80.0 %
        B → 80.0 % < percentual_acumulado ≤ 95.0 %
        C → percentual_acumulado > 95.0 %

    Args:
        percentual_acumulado: Percentual acumulado de faturamento (0 – 100).

    Returns:
        "A", "B" ou "C".
    """
    if percentual_acumulado <= _LIMIAR_A:
        return "A"
    if percentual_acumulado <= _LIMIAR_B:
        return "B"
    return "C"
