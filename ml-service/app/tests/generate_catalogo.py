"""
Gera um catálogo sintético de N produtos com histórico de vendas, no formato do
Guia de Importação v2.0 — duas planilhas .xlsx prontas para
POST /api/importacao/produtos e POST /api/importacao/vendas.

POR QUE ESTE ARQUIVO EXISTE

O `generate_synthetic_data.py` tem `PRODUTOS_META` fixo em 10 produtos, o que é
suficiente para testar o motor mas não para exercitar CARGA. As tasks D-07,
D-35 e D-43 pedem medição com catálogo realista (~312 SKUs) e seguem parciais
justamente por isso: com 10 produtos o lote termina em segundos e o pico de
memória fica igual ao ocioso.

Este script não duplica a geração de série: ele substitui `PRODUTOS_META` e
reaproveita `gerar_dataset` e os dois `exportar_planilha_*` do módulo original,
então o formato das colunas e a janela de datas continuam vindo de um lugar só.

USO

    python generate_catalogo.py                      # 312 produtos, 180 dias
    python generate_catalogo.py --produtos 50        # catálogo menor
    python generate_catalogo.py --primeiro-id 11     # não colidir com o que já existe
    python generate_catalogo.py --saida ./massa      # onde gravar

IMPORTAR

    curl -X POST http://<host>/api/importacao/produtos \\
         -H "Authorization: Bearer $TOKEN" -F "arquivo=@produtos.xlsx"
    curl -X POST http://<host>/api/importacao/vendas \\
         -H "Authorization: Bearer $TOKEN" -F "arquivo=@vendas.xlsx"

A importação é incremental: produtos fazem upsert por `produto_id` e vendas são
acrescentadas. Reimportar o MESMO arquivo de vendas duplica as linhas — para
recomeçar do zero, recrie o volume do banco.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import generate_synthetic_data as g  # noqa: E402

SEMENTE_PADRAO = 42

# Arquétipos de um mercado de bairro. Os intervalos vêm dos 10 produtos do
# generate_synthetic_data, estendidos para cobrir o sortimento típico:
#   demanda        unidades/dia na base da série
#   variabilidade  desvio relativo do ruído — perecível oscila mais
#   preco          faixa de preço de venda em R$
CATEGORIAS: dict[str, dict] = {
    "Grãos":       {"demanda": (5, 16),  "variabilidade": (0.10, 0.20), "preco": (5.0, 35.0),  "unidade": "un",
                    "nomes": ["Arroz", "Feijão Carioca", "Feijão Preto", "Lentilha", "Grão de Bico", "Milho para Pipoca", "Canjica", "Ervilha Seca"]},
    "Laticínios":  {"demanda": (10, 26), "variabilidade": (0.30, 0.42), "preco": (4.0, 28.0),  "unidade": "un",
                    "nomes": ["Leite Integral", "Leite Desnatado", "Queijo Mussarela", "Queijo Prato", "Requeijão", "Iogurte Natural", "Manteiga", "Creme de Leite", "Leite Condensado"]},
    "Padaria":     {"demanda": (18, 42), "variabilidade": (0.35, 0.48), "preco": (0.5, 18.0),  "unidade": "un",
                    "nomes": ["Pão Francês", "Pão de Forma", "Bolo Caseiro", "Broa de Milho", "Rosquinha", "Pão de Queijo", "Croissant"]},
    "Hortifruti":  {"demanda": (10, 28), "variabilidade": (0.40, 0.52), "preco": (2.5, 14.0),  "unidade": "kg",
                    "nomes": ["Banana Prata", "Maçã Gala", "Tomate", "Cebola", "Batata", "Cenoura", "Alface", "Laranja Pera", "Mamão", "Abacaxi", "Limão"]},
    "Carnes":      {"demanda": (7, 16),  "variabilidade": (0.25, 0.38), "preco": (10.0, 55.0), "unidade": "kg",
                    "nomes": ["Frango Inteiro", "Peito de Frango", "Coxa de Frango", "Patinho", "Acém", "Costela Bovina", "Linguiça Toscana", "Bacon", "Carne Moída"]},
    "Bebidas":     {"demanda": (9, 22),  "variabilidade": (0.20, 0.32), "preco": (2.5, 18.0),  "unidade": "un",
                    "nomes": ["Refrigerante Cola", "Refrigerante Guaraná", "Suco de Uva", "Suco de Laranja", "Água Mineral", "Água com Gás", "Cerveja Lata", "Energético", "Chá Gelado"]},
    "Higiene":     {"demanda": (3, 9),   "variabilidade": (0.12, 0.24), "preco": (4.0, 32.0),  "unidade": "un",
                    "nomes": ["Sabonete", "Shampoo", "Condicionador", "Creme Dental", "Escova de Dente", "Papel Higiênico", "Desodorante", "Absorvente"]},
    "Limpeza":     {"demanda": (4, 11),  "variabilidade": (0.12, 0.26), "preco": (3.0, 26.0),  "unidade": "un",
                    "nomes": ["Detergente", "Sabão em Pó", "Amaciante", "Água Sanitária", "Desinfetante", "Esponja", "Saco de Lixo", "Multiuso"]},
    "Condimentos": {"demanda": (3, 9),   "variabilidade": (0.05, 0.15), "preco": (2.0, 16.0),  "unidade": "un",
                    "nomes": ["Sal Refinado", "Açúcar Cristal", "Açúcar Refinado", "Vinagre", "Molho de Tomate", "Ketchup", "Maionese", "Mostarda", "Orégano", "Pimenta do Reino"]},
    "Mercearia":   {"demanda": (5, 14),  "variabilidade": (0.18, 0.30), "preco": (4.0, 34.0),  "unidade": "un",
                    "nomes": ["Café Torrado", "Achocolatado", "Biscoito Recheado", "Biscoito Água e Sal", "Macarrão Espaguete", "Macarrão Parafuso", "Farinha de Trigo", "Fubá", "Aveia", "Granola"]},
    "Congelados":  {"demanda": (4, 12),  "variabilidade": (0.30, 0.42), "preco": (8.0, 40.0),  "unidade": "un",
                    "nomes": ["Pizza Congelada", "Lasanha Congelada", "Hambúrguer Congelado", "Nuggets", "Batata Frita Congelada", "Sorvete", "Polpa de Fruta"]},
    "Óleos":       {"demanda": (4, 11),  "variabilidade": (0.15, 0.26), "preco": (6.0, 45.0),  "unidade": "un",
                    "nomes": ["Óleo de Soja", "Óleo de Girassol", "Azeite Extra Virgem", "Óleo de Milho", "Banha"]},
}

# Sufixos que diferenciam SKUs do mesmo produto base, como num mercado real.
VARIANTES = ["500g", "1kg", "2kg", "5kg", "900ml", "1L", "2L", "200ml", "350ml",
             "un", "pct 6", "cx 12", "fardo", "400g", "180g", "pote 1kg"]


def gerar_meta(n: int, primeiro_id: int, semente: int) -> list[dict]:
    """
    Monta N dicionários no formato de PRODUTOS_META, distribuídos entre as
    categorias e com nomes únicos.

    A distribuição é round-robin sobre as categorias para que nenhuma domine o
    catálogo, e cada SKU recebe demanda, variabilidade e preço sorteados dentro
    da faixa da sua categoria — é isso que produz a dispersão de faturamento
    necessária para a Curva ABC fazer sentido (sem ela, todos cairiam na mesma
    classe).
    """
    rng = np.random.default_rng(semente)
    categorias = list(CATEGORIAS.items())
    meta: list[dict] = []
    usados: set[str] = set()

    for i in range(n):
        nome_cat, cfg = categorias[i % len(categorias)]

        # Nome único: base da categoria + variante. Se a combinação já saiu,
        # tenta outras antes de cair no sufixo numérico.
        nome = ""
        for _ in range(40):
            base = cfg["nomes"][int(rng.integers(len(cfg["nomes"])))]
            variante = VARIANTES[int(rng.integers(len(VARIANTES)))]
            candidato = f"{base} {variante}"
            if candidato not in usados:
                nome = candidato
                break
        if not nome:
            nome = f"{cfg['nomes'][0]} tipo {i + 1}"
        usados.add(nome)

        # Popularidade log-normal: é o que produz a cauda longa do varejo, onde
        # poucos itens respondem pela maior parte da receita. Sem ela, sorteio
        # uniforme dentro da faixa da categoria achata o faturamento e a Curva
        # ABC (T7) sai irreal — medido: 54% do catálogo na classe A, contra os
        # ~20% que a regra de Pareto descreve.
        # sigma e clamps calibrados por varredura: sigma 1.8 com teto de 120
        # un/dia põe ~24% do catálogo na classe A, próximo do Pareto, mantendo
        # a demanda do campeão de vendas plausível para um mercado de bairro.
        # Tetos maiores chegam a 19%, mas exigiriam 250 un/dia — já não é
        # mercadinho, e realismo do dado vale mais que a curva perfeita.
        popularidade = float(np.clip(rng.lognormal(mean=0.0, sigma=1.8), 0.08, 20.0))

        demanda = float(np.clip(rng.uniform(*cfg["demanda"]) * popularidade, 0.4, 120.0))
        preco = round(float(rng.uniform(*cfg["preco"])), 2)

        # Cobertura de estoque em dias, entre 0,4 e 22. A cauda baixa é
        # proposital: garante produtos críticos e em atenção nas telas T4/T5,
        # em vez de um catálogo inteiro confortável que não exercita alerta.
        cobertura = float(rng.uniform(0.4, 22.0))

        meta.append({
            "produto_id": primeiro_id + i,
            "nome": nome,
            "categoria": nome_cat,
            "demanda_base": round(demanda, 1),
            "variabilidade": round(float(rng.uniform(*cfg["variabilidade"])), 2),
            "preco_venda": preco,
            "unidade_medida": cfg["unidade"],
            "estoque_atual": max(1, int(demanda * cobertura)),
        })

    return meta


def main() -> int:
    p = argparse.ArgumentParser(
        description="Gera catálogo sintético de N produtos + histórico de vendas (.xlsx).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--produtos", type=int, default=312,
                   help="Quantos SKUs gerar. Padrão 312, o volume estimado do estabelecimento.")
    p.add_argument("--dias", type=int, default=180,
                   help="Dias de histórico, terminando ontem. Mínimo exigido pelo motor: 90.")
    p.add_argument("--primeiro-id", type=int, default=1,
                   help="produto_id inicial. Use 11+ para não colidir com o catálogo já importado.")
    # Default relativo AO SCRIPT, não ao diretório de onde se chama: o caminho
    # fica previsível e cai dentro de fixtures/, que o ml-service/.gitignore já
    # ignora — senão os .xlsx gerados apareceriam como untracked no git.
    p.add_argument("--saida", type=Path,
                   default=Path(__file__).parent / "fixtures" / "massa-sintetica",
                   help="Diretório de saída. Padrão: app/tests/fixtures/massa-sintetica/")
    p.add_argument("--semente", type=int, default=SEMENTE_PADRAO,
                   help="Semente aleatória — mesma semente, mesmo catálogo.")
    # Sobrescritas aplicadas ao PRIMEIRO produto. Servem para montar um SKU
    # reconhecível numa demonstração, em vez do nome sorteado, que combina base
    # e variante e às vezes produz coisas como "Arroz fardo".
    p.add_argument("--nome", type=str, default=None,
                   help="Nome do primeiro produto. Sobrescreve o sorteio.")
    p.add_argument("--categoria", type=str, default=None,
                   choices=sorted(CATEGORIAS), metavar="CATEGORIA",
                   help=f"Categoria do primeiro produto. Uma de: {', '.join(sorted(CATEGORIAS))}")
    p.add_argument("--estoque", type=int, default=None,
                   help="Estoque atual do primeiro produto. Baixo o põe em Alertas.")
    args = p.parse_args()

    if args.dias < 90:
        print(f"ERRO: --dias {args.dias} é menor que os 90 exigidos pelo motor.", file=sys.stderr)
        print("      Holt-Winters e Prophet não identificam padrão semanal com menos.", file=sys.stderr)
        return 1
    if args.produtos < 1:
        print("ERRO: --produtos precisa ser >= 1.", file=sys.stderr)
        return 1

    args.saida.mkdir(parents=True, exist_ok=True)
    caminho_produtos = args.saida / "produtos.xlsx"
    caminho_vendas = args.saida / "vendas.xlsx"

    print(f"Gerando {args.produtos} produtos, {args.dias} dias de histórico, ids a partir de {args.primeiro_id}...")

    # Reaproveita o pipeline do módulo original: colunas e janela de datas
    # continuam definidas num lugar só.
    meta = gerar_meta(args.produtos, args.primeiro_id, args.semente)

    if args.categoria:
        # Trocar a categoria sem ressortear demanda e preço deixaria o SKU com
        # números de outra faixa. Regenera o primeiro item já na categoria certa.
        cfg = CATEGORIAS[args.categoria]
        rng = np.random.default_rng(args.semente)
        meta[0]["categoria"] = args.categoria
        meta[0]["unidade_medida"] = cfg["unidade"]
        meta[0]["demanda_base"] = round(float(rng.uniform(*cfg["demanda"])), 1)
        meta[0]["variabilidade"] = round(float(rng.uniform(*cfg["variabilidade"])), 2)
        meta[0]["preco_venda"] = round(float(rng.uniform(*cfg["preco"])), 2)
        meta[0]["estoque_atual"] = max(1, int(meta[0]["demanda_base"] * 8))
    if args.nome:
        meta[0]["nome"] = args.nome
    if args.estoque is not None:
        meta[0]["estoque_atual"] = max(1, args.estoque)

    g.PRODUTOS_META = meta

    g.exportar_planilha_produtos(destino=caminho_produtos)
    g.exportar_planilha_vendas(dias=args.dias, destino=caminho_vendas)

    dfp = pd.read_excel(caminho_produtos)
    dfv = pd.read_excel(caminho_vendas)
    mb_vendas = caminho_vendas.stat().st_size / 1_048_576

    faturamento = dfv.groupby("produto_id")["valor_venda"].sum().sort_values(ascending=False)
    acumulado = faturamento.cumsum() / faturamento.sum()
    n_classe_a = int((acumulado <= 0.80).sum()) + 1

    print()
    print(f"  produtos.xlsx : {caminho_produtos}  ({len(dfp)} linhas)")
    print(f"  vendas.xlsx   : {caminho_vendas}  ({len(dfv):,} linhas, {mb_vendas:.2f} MB)")
    print()
    print(f"  categorias    : {dfp['categoria'].nunique()}")
    print(f"  periodo       : {dfv['data_hora'].min()}  ate  {dfv['data_hora'].max()}")
    print(f"  faturamento   : R$ {dfv['valor_venda'].sum():,.2f}")
    print(f"  curva ABC     : ~{n_classe_a} produtos concentram 80% do faturamento "
          f"({n_classe_a / len(dfp) * 100:.0f}% do catalogo)")
    print()
    print(f"  lote estimado : ~{args.produtos * 0.5 / 60:.1f} min "
          f"(0,50 s/produto, medido na t3.medium no D-35)")

    if mb_vendas > 4.5:
        print()
        print(f"  AVISO: vendas.xlsx tem {mb_vendas:.2f} MB e o backend aceita no maximo 5 MB")
        print(f"         (spring.servlet.multipart.max-file-size). Reduza --dias ou --produtos,")
        print(f"         ou importe em lotes.")

    ontem = date.today() - timedelta(days=1)
    ultima = pd.to_datetime(dfv["data_hora"]).max().date()
    if ultima > ontem:
        print(f"  ERRO: ultima venda {ultima} e futura — o backend rejeitaria.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
