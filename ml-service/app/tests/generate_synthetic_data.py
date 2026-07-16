"""
Gerador de dataset sintético de vendas para testes do motor preditivo StockSense.

Simula 365 dias de histórico de vendas diárias de um mercadinho de bairro
com 10 produtos representando diferentes perfis de demanda.

Uso como script:
    python generate_synthetic_data.py

Saídas:
    fixtures/5_vendas_sintetico.csv  — 365 dias (2024), para os testes do motor
    fixtures/2_produtos.xlsx         — catálogo p/ POST /api/importacao/produtos
    fixtures/5_vendas.xlsx           — 180 dias terminando ontem, p/ POST /api/importacao/vendas
                                       (o backend rejeita data futura e o dashboard só agrega
                                       as últimas ~8 semanas — por isso a janela recente)

Uso como módulo nos testes:
    from app.tests.generate_synthetic_data import gerar_dataset, PRODUTOS_META
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ── Semente fixa para reprodutibilidade ───────────────────────────────────────
RANDOM_STATE: int = 42

# ── Feriados nacionais brasileiros 2024 ───────────────────────────────────────
_FERIADOS_2024: set[date] = {
    date(2024, 1, 1),    # Confraternização Universal
    date(2024, 2, 12),   # Carnaval (segunda-feira)
    date(2024, 2, 13),   # Carnaval (terça-feira)
    date(2024, 3, 29),   # Sexta-feira Santa
    date(2024, 4, 21),   # Tiradentes
    date(2024, 5, 1),    # Dia do Trabalho
    date(2024, 5, 30),   # Corpus Christi
    date(2024, 9, 7),    # Independência do Brasil
    date(2024, 10, 12),  # Nossa Senhora Aparecida
    date(2024, 11, 2),   # Finados
    date(2024, 11, 15),  # Proclamação da República
    date(2024, 12, 25),  # Natal
}

# ── Catálogo de produtos ───────────────────────────────────────────────────────
# variabilidade: desvio padrão relativo do ruído (0.05 = constante, 0.45 = alta)
# estoque_atual: calibrado p/ o teste do semáforo dos alertas (T5) — valores baixos
# em relação à demanda diária tendem ao VERMELHO (estoque ≤ PR), altos ao VERDE.
PRODUTOS_META: list[dict] = [
    # demanda estável
    {"produto_id": 1,  "nome": "Arroz 5kg",          "categoria": "Grãos",       "demanda_base": 12, "variabilidade": 0.15, "preco_venda": 28.90, "unidade_medida": "un", "estoque_atual": 15},
    {"produto_id": 2,  "nome": "Feijão Carioca 1kg",  "categoria": "Grãos",       "demanda_base":  8, "variabilidade": 0.15, "preco_venda":  8.50, "unidade_medida": "un", "estoque_atual": 120},
    # alta variabilidade — perecíveis
    {"produto_id": 3,  "nome": "Leite Integral 1L",   "categoria": "Laticínios",  "demanda_base": 20, "variabilidade": 0.35, "preco_venda":  4.99, "unidade_medida": "lt", "estoque_atual": 60},
    {"produto_id": 4,  "nome": "Pão Francês",          "categoria": "Padaria",     "demanda_base": 30, "variabilidade": 0.40, "preco_venda":  0.75, "unidade_medida": "un", "estoque_atual": 25},
    {"produto_id": 5,  "nome": "Banana Prata kg",      "categoria": "Frutas",      "demanda_base": 15, "variabilidade": 0.45, "preco_venda":  5.90, "unidade_medida": "kg", "estoque_atual": 200},
    # demanda quase constante
    {"produto_id": 6,  "nome": "Sal Refinado 1kg",     "categoria": "Condimentos", "demanda_base":  5, "variabilidade": 0.05, "preco_venda":  2.50, "unidade_medida": "un", "estoque_atual": 60},
    {"produto_id": 7,  "nome": "Açúcar Cristal 1kg",   "categoria": "Condimentos", "demanda_base":  7, "variabilidade": 0.05, "preco_venda":  4.20, "unidade_medida": "un", "estoque_atual": 10},
    # demanda moderada
    {"produto_id": 8,  "nome": "Óleo de Soja 900ml",   "categoria": "Óleos",       "demanda_base":  6, "variabilidade": 0.20, "preco_venda":  7.80, "unidade_medida": "un", "estoque_atual": 90},
    {"produto_id": 9,  "nome": "Frango Inteiro kg",    "categoria": "Carnes",      "demanda_base": 10, "variabilidade": 0.30, "preco_venda": 12.90, "unidade_medida": "kg", "estoque_atual": 45},
    {"produto_id": 10, "nome": "Refrigerante 2L",      "categoria": "Bebidas",     "demanda_base": 14, "variabilidade": 0.25, "preco_venda":  9.50, "unidade_medida": "un", "estoque_atual": 300},
]

# ── Fatores de sazonalidade semanal (0 = segunda … 6 = domingo) ──────────────
_FATOR_SEMANA: dict[int, float] = {
    0: 0.85,  # Segunda-feira
    1: 0.75,  # Terça-feira
    2: 0.80,  # Quarta-feira
    3: 0.90,  # Quinta-feira
    4: 1.35,  # Sexta-feira  — pico
    5: 1.45,  # Sábado       — pico
    6: 0.30,  # Domingo      — movimento reduzido
}


def _gerar_serie_produto(
    produto: dict,
    datas: pd.DatetimeIndex,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Gera série temporal diária para um único produto.

    Aplica em sequência: tendência linear de crescimento (+20 % ao ano),
    sazonalidade semanal via multiplicador por dia da semana, ruído
    gaussiano multiplicativo e eventos de fechamento (domingos e feriados).

    Args:
        produto: Dicionário com metadados do produto (de PRODUTOS_META).
        datas: Índice temporal a cobrir.
        rng: Gerador de números aleatórios já inicializado com a semente.

    Returns:
        DataFrame com colunas no formato da planilha 5_vendas, incluindo
        dias com quantidade zero.
    """
    n = len(datas)

    tendencia = np.linspace(1.0, 1.20, n)
    fator_semanal = np.array([_FATOR_SEMANA[d.dayofweek] for d in datas])
    ruido = np.clip(rng.normal(1.0, produto["variabilidade"], n), 0.1, 3.0)

    quantidades = np.round(
        produto["demanda_base"] * tendencia * fator_semanal * ruido
    ).astype(int)

    # domingos: 40 % de chance de ficar fechado
    mascara_domingo = np.array([d.dayofweek == 6 for d in datas])
    quantidades[mascara_domingo & (rng.random(n) < 0.40)] = 0

    # feriados nacionais: 60 % de chance de ficar fechado
    mascara_feriado = np.array([d.date() in _FERIADOS_2024 for d in datas])
    quantidades[mascara_feriado & (rng.random(n) < 0.60)] = 0

    quantidades = np.maximum(quantidades, 0)

    preco_variavel = produto["preco_venda"] * rng.uniform(0.98, 1.02, n)
    valor_venda = np.where(
        quantidades > 0,
        np.round(quantidades * preco_variavel, 2),
        0.0,
    )

    return pd.DataFrame({
        "produto_id":     produto["produto_id"],
        "data_hora":      datas.strftime("%Y-%m-%d"),
        "quantidade":     quantidades,
        "valor_venda":    valor_venda,
        "is_promocional": 0,
    })


def gerar_dataset(
    data_inicio: str = "2024-01-01",
    dias: int = 365,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, dict[int, pd.Series]]:
    """
    Gera dataset sintético completo de vendas para os 10 produtos do mercadinho.

    Args:
        data_inicio: Data de início da série no formato YYYY-MM-DD.
        dias: Número de dias a gerar. Mínimo recomendado para o motor: 365.
        random_state: Semente para reprodutibilidade total dos resultados.

    Returns:
        df_csv: DataFrame no formato da planilha 5_vendas — sem registros de
                quantidade zero, ordenado por produto_id e data, pronto para
                exportação via exportar_csv().
        series_por_produto: Dicionário produto_id → pd.Series com DatetimeIndex
                            completo, incluindo dias sem venda (quantidade = 0),
                            para uso direto nas funções do motor preditivo.

    Note:
        A série em series_por_produto mantém os zeros (domingos e feriados)
        para preservar a continuidade do índice temporal. Ao construir um
        PredictRequest, filtre os registros com quantidade > 0.
    """
    rng = np.random.default_rng(random_state)
    datas = pd.date_range(start=data_inicio, periods=dias, freq="D")

    frames: list[pd.DataFrame] = []
    series_por_produto: dict[int, pd.Series] = {}

    for produto in PRODUTOS_META:
        df_produto = _gerar_serie_produto(produto, datas, rng)
        frames.append(df_produto)

        series_por_produto[produto["produto_id"]] = pd.Series(
            df_produto["quantidade"].values,
            index=pd.to_datetime(df_produto["data_hora"]),
            name=str(produto["produto_id"]),
        )

    df_csv = (
        pd.concat(frames, ignore_index=True)
        .query("quantidade > 0")
        .sort_values(["produto_id", "data_hora"])
        .reset_index(drop=True)
    )

    return df_csv, series_por_produto


def exportar_csv(df: pd.DataFrame, destino: Path | None = None) -> Path:
    """
    Salva o DataFrame em CSV no formato da planilha 5_vendas.

    Cria o diretório de destino automaticamente se não existir.

    Args:
        df: DataFrame retornado por gerar_dataset().
        destino: Caminho do arquivo de saída. Padrão:
                 app/tests/fixtures/5_vendas_sintetico.csv.

    Returns:
        Caminho absoluto do arquivo gerado.
    """
    if destino is None:
        destino = Path(__file__).parent / "fixtures" / "5_vendas_sintetico.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, encoding="utf-8")
    return destino.resolve()


def exportar_planilha_produtos(destino: Path | None = None) -> Path:
    """
    Gera a planilha 2_produtos.xlsx no formato do Guia de Importação v2.0,
    pronta para o POST /api/importacao/produtos.

    Contém apenas os campos de entrada — os calculados (classe_abc,
    ponto_reposicao, etc.) são rejeitados pelo backend se preenchidos.

    Args:
        destino: Caminho do arquivo. Padrão: app/tests/fixtures/2_produtos.xlsx.

    Returns:
        Caminho absoluto do arquivo gerado.
    """
    if destino is None:
        destino = Path(__file__).parent / "fixtures" / "2_produtos.xlsx"
    destino.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame([
        {
            "produto_id":         p["produto_id"],
            "nome":               p["nome"],
            "categoria":          p["categoria"],
            "unidade_medida":     p["unidade_medida"],
            "preco_custo":        round(p["preco_venda"] * 0.70, 2),
            "preco_venda":        p["preco_venda"],
            "estoque_atual":      p["estoque_atual"],
            "nivel_servico_alvo": 0.95,
        }
        for p in PRODUTOS_META
    ])
    df.to_excel(destino, index=False)
    return destino.resolve()


def exportar_planilha_vendas(
    dias: int = 180,
    destino: Path | None = None,
) -> Path:
    """
    Gera a planilha 5_vendas.xlsx com a janela de datas terminando ONTEM,
    pronta para o POST /api/importacao/vendas.

    A janela recente é necessária porque o backend rejeita vendas com data
    futura e o dashboard (T2) agrega o faturamento das últimas ~8 semanas —
    com o dataset padrão de 2024 a série do dashboard voltaria vazia.

    Args:
        dias: Tamanho do histórico. Mínimo exigido pelo motor: 90.
        destino: Caminho do arquivo. Padrão: app/tests/fixtures/5_vendas.xlsx.

    Returns:
        Caminho absoluto do arquivo gerado.
    """
    if destino is None:
        destino = Path(__file__).parent / "fixtures" / "5_vendas.xlsx"
    destino.parent.mkdir(parents=True, exist_ok=True)

    inicio = date.today() - timedelta(days=dias)
    df, _ = gerar_dataset(data_inicio=inicio.isoformat(), dias=dias)
    df.to_excel(destino, index=False)
    return destino.resolve()


if __name__ == "__main__":
    df_csv, series = gerar_dataset()

    caminho = exportar_csv(df_csv)
    print(f"CSV exportado : {caminho}")
    print(f"Total registros: {len(df_csv)}\n")

    caminho_produtos = exportar_planilha_produtos()
    print(f"XLSX produtos : {caminho_produtos}")

    caminho_vendas = exportar_planilha_vendas()
    print(f"XLSX vendas   : {caminho_vendas} (180 dias terminando ontem)\n")

    nomes = {p["produto_id"]: p["nome"] for p in PRODUTOS_META}

    resumo = (
        df_csv.groupby("produto_id")
        .agg(
            dias_com_venda=("quantidade", "count"),
            total_vendido=("quantidade", "sum"),
            media_diaria=("quantidade", "mean"),
            faturamento=("valor_venda", "sum"),
        )
        .round(2)
    )
    resumo.insert(0, "nome", resumo.index.map(nomes))

    print("Resumo por produto:")
    print(resumo.to_string())

    print("\nVariabilidade (série completa com zeros):")
    for pid, serie in series.items():
        print(
            f"  [{pid:2d}] {nomes[pid]:<22}  "
            f"std={serie.std():6.2f}  "
            f"zeros={int((serie == 0).sum()):3d} dias"
        )
