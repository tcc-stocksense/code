"""
Cálculo dos KPIs de estoque do motor preditivo StockSense.

Implementa as fórmulas de Ballou (2006) para estoque de segurança,
ponto de reposição e dias até ruptura, além do Z-score por nível de serviço.

Referência:
    BALLOU, Ronald H. Gerenciamento da cadeia de suprimentos /
    Logística empresarial. 5. ed. Porto Alegre: Bookman, 2006.
"""
import numpy as np
from scipy import stats


def calcular_z_score(nivel_servico: float) -> float:
    """
    Converte nível de serviço alvo em Z-score da distribuição normal padrão.

    Args:
        nivel_servico: Probabilidade de não faltar estoque durante o lead time.
                       Deve estar entre 0.5 e 0.999 (ex: 0.95 para 95 %).

    Returns:
        Z-score correspondente (ex: 0.95 → ≈ 1.645, 0.99 → ≈ 2.326).

    Examples:
        >>> round(calcular_z_score(0.95), 3)
        1.645
        >>> calcular_z_score(0.50)
        0.0
    """
    return float(stats.norm.ppf(nivel_servico))


def calcular_estoque_seguranca(
    z: float,
    lead_time_medio: int,
    desvio_demanda: float,
    demanda_media: float,
    variabilidade_lead_time: float,
) -> float:
    """
    Calcula o estoque de segurança pela fórmula combinada de Ballou (2006).

    A fórmula considera simultaneamente a variabilidade da demanda e a
    variabilidade do lead time, produzindo um buffer mais preciso do que
    a fórmula simplificada que ignora a incerteza no prazo de entrega.

    Fórmula:
        ES = Z × √(LT × σ²_demanda + demanda² × σ²_lead_time)

    Args:
        z: Z-score do nível de serviço alvo (obtido via calcular_z_score).
        lead_time_medio: Prazo médio de entrega do fornecedor em dias.
        desvio_demanda: Desvio padrão da demanda diária (σ_demanda).
        demanda_media: Demanda média diária do produto.
        variabilidade_lead_time: Desvio padrão do lead time em dias (σ_lead_time).

    Returns:
        Estoque de segurança em unidades (não-negativo).
    """
    radicando = (
        lead_time_medio * desvio_demanda ** 2
        + demanda_media ** 2 * variabilidade_lead_time ** 2
    )
    return float(z * np.sqrt(radicando))


def calcular_ponto_reposicao(
    demanda_media: float,
    lead_time_medio: int,
    estoque_seguranca: float,
) -> float:
    """
    Calcula o ponto de reposição — nível de estoque que dispara um novo pedido.

    Quando o estoque cai abaixo do ponto de reposição, um pedido deve ser
    feito imediatamente para que a mercadoria chegue antes do estoque zerar.

    Fórmula:
        PR = demanda_media_diária × lead_time_medio + estoque_segurança

    Args:
        demanda_media: Demanda média diária prevista pelo motor (unidades/dia).
        lead_time_medio: Prazo médio de entrega do fornecedor em dias.
        estoque_seguranca: Estoque de segurança calculado via
                           calcular_estoque_seguranca.

    Returns:
        Ponto de reposição em unidades.
    """
    return float(demanda_media * lead_time_medio + estoque_seguranca)


def calcular_dias_ate_ruptura(
    estoque_atual: int,
    demanda_media_diaria: float,
) -> float | None:
    """
    Estima quantos dias o estoque atual suporta antes de atingir zero.

    Retorna None quando a demanda média é zero ou negativa para evitar
    divisão por zero — semanticamente significa que o produto nunca vai
    faltar com a demanda observada.

    Fórmula:
        dias = estoque_atual / demanda_media_diária

    Args:
        estoque_atual: Quantidade em estoque no momento do cálculo.
        demanda_media_diaria: Demanda média diária prevista pelo motor.

    Returns:
        Número de dias até ruptura, ou None se demanda_media_diaria <= 0.
    """
    if demanda_media_diaria <= 0:
        return None
    return float(estoque_atual / demanda_media_diaria)
