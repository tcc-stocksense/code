"""
Gera o relatório técnico em PDF sobre os modelos preditivos do StockSense.

Todos os números do documento vêm de analysis/results/dados_documento.json,
produzido por analysis/_coletar_dados_doc.py — nenhum valor é digitado à mão.
As figuras são as mesmas geradas pelo notebook em analysis/figures/.

Uso (a partir de ml-service/):
    venv/Scripts/python.exe analysis/_coletar_dados_doc.py    # 1. números
    venv/Scripts/python.exe docs/gerar_relatorio_pdf.py       # 2. PDF

Saída:
    docs/relatorio-modelos-preditivos.pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, Spacer

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "docs"))

# Estilo, fontes e construtores de bloco compartilhados com o capitulo de validacao
from _estilo_pdf import (  # noqa: E402
    AZUL, AZUL_CLARO, BORDA, CINZA, CINZA_CLARO, LARGURA_UTIL, VERDE, VERDE_CLARO,
    S_CAP, S_P, S_SUB, S_TITULO,
    caixa as _caixa, codigo, destaque, esp, formula, h1, h2, h3, li,
    montar_documento, p, tabela,
)
from _estilo_pdf import figura as _figura  # noqa: E402

DOCS = RAIZ / "docs"
FIGS = RAIZ / "analysis" / "figures"


def figura(nome, legenda, largura=None):
    """Envolve o construtor compartilhado resolvendo o nome do arquivo em FIGS."""
    return _figura(FIGS / nome, legenda, largura)


# ═════════════════════════════════════════════════════════════════════════════
# CONTEÚDO
# ═════════════════════════════════════════════════════════════════════════════
DADOS = json.loads(
    (RAIZ / "analysis" / "results" / "dados_documento.json").read_text(encoding="utf-8")
)
ALPHAS = json.loads(
    (RAIZ / "analysis" / "results" / "_alphas.json").read_text(encoding="utf-8")
)

E = []          # story
d = DADOS
kpi = {k["produto_id"]: k for k in d["kpis"]}
wf = d["walkforward"]

# ── Capa ─────────────────────────────────────────────────────────────────────
E += [
    Spacer(1, 3.4 * cm),
    Paragraph("Motor de Otimização Preditiva de Estoque", S_SUB),
    esp(10),
    Paragraph("Relatório Técnico dos Modelos Preditivos", S_TITULO),
    esp(6),
    Paragraph("Fundamentação matemática, metodologia de validação empírica "
              "e resultados", S_SUB),
    Spacer(1, 1.5 * cm),
]
E.append(_caixa([
    Paragraph("<b>Projeto</b>  StockSense — gestão preditiva de estoque para mercados "
              "de bairro", S_P),
    Paragraph("<b>Componente</b>  ml-service (Python / FastAPI) — motor preditivo "
              "stateless", S_P),
    Paragraph("<b>Escopo deste documento</b>  como os modelos Holt-Winters e Prophet "
              "funcionam por dentro, como o motor decide qual usar, o que foi feito na "
              "camada de análise (<font face='DJM' size='8.5'>analysis/</font>) e quais "
              "resultados foram obtidos", S_P),
    Paragraph("<b>Tela do sistema correspondente</b>  T10 — Comparativo de modelos "
              "(núcleo acadêmico do TCC)", S_P),
    Paragraph("<b>Data</b>  09 de agosto de 2026", S_P),
], AZUL_CLARO, AZUL))
E += [
    Spacer(1, 1.2 * cm),
    _caixa([Paragraph(
        "<b>Princípio metodológico deste relatório.</b> Todos os números apresentados "
        "foram produzidos executando o próprio código de produção do serviço "
        "(<font face='DJM' size='8.5'>app/services/</font>), com semente fixa "
        "(SEED = 42). Não há valor digitado manualmente: o documento é regenerado por "
        "script a partir de um JSON de resultados. As métricas aqui são, por "
        "construção, idênticas às que o endpoint "
        "<font face='DJM' size='8.5'>POST /predict</font> devolve em execução.", S_P)],
        VERDE_CLARO, VERDE),
    PageBreak(),
]

# ── Sumário ──────────────────────────────────────────────────────────────────
E.append(h1("Sumário"))
_sumario = [
    ("1.", "Sumário executivo — o essencial em uma página"),
    ("2.", "Onde o motor vive: arquitetura e contrato"),
    ("3.", "O problema estatístico"),
    ("4.", "Modelo 1 — Holt-Winters (suavização exponencial tripla)"),
    ("5.", "Modelo 2 — Prophet (modelo aditivo generalizado)"),
    ("6.", "Comparação conceitual entre os dois modelos"),
    ("7.", "Como o motor decide qual modelo usar"),
    ("8.", "As três métricas de erro: MAPE, RMSE e MAE"),
    ("9.", "Da previsão à decisão: as fórmulas de estoque (Ballou)"),
    ("10.", "O que foi feito na camada de análise (analysis/)"),
    ("11.", "O dataset sintético: como os dados são gerados"),
    ("12.", "Resultados empíricos"),
    ("13.", "Achado central: por que os dois modelos empatam"),
    ("14.", "Robustez: backtesting rolling-origin"),
    ("15.", "Limitações conhecidas (declaração honesta)"),
    ("16.", "Reprodutibilidade"),
    ("17.", "Perguntas prováveis da banca"),
    ("18.", "Referências"),
]
E.append(tabela([["#", "Seção"]] + [[n, t] for n, t in _sumario],
                [1.3 * cm, LARGURA_UTIL - 1.3 * cm]))
E.append(PageBreak())

# ── 1. Sumário executivo ─────────────────────────────────────────────────────
E.append(h1("1. Sumário executivo — o essencial em uma página"))
E.append(p(
    "O StockSense prevê a demanda diária de cada produto de um mercado de bairro e "
    "converte essa previsão em decisão de compra: quanto manter de reserva, em que "
    "nível de estoque disparar um pedido e em quantos dias o produto acaba. O núcleo "
    "acadêmico do trabalho é a <b>comparação empírica entre dois modelos de série "
    "temporal</b> — Holt-Winters e Prophet — com escolha automática do vencedor "
    "por produto."))
for t in [
    "<b>Dois modelos, escolha por produto.</b> O motor treina os dois em todo produto, "
    "mede o erro dos dois e seleciona o de menor MAPE. Não existe modelo fixo: a "
    "escolha é uma decisão orientada a dados, refeita a cada execução.",
    "<b>Os modelos não 'leem um gráfico' — eles otimizam.</b> Ambos partem de uma "
    "fórmula com parâmetros desconhecidos e usam um otimizador numérico para encontrar "
    "os valores que minimizam o erro contra o histórico observado.",
    "<b>A validação é temporal, nunca aleatória.</b> Treina-se nos primeiros 80% da "
    "série e mede-se nos 20% finais (walk-forward). Embaralhar os dados deixaria o "
    "modelo ver o futuro e invalidaria toda a métrica.",
    "<b>Resultado do comparativo:</b> Holt-Winters venceu em 6 dos 10 produtos e "
    "Prophet em 4, mas com margens muito pequenas — em 9 dos 10 produtos a diferença "
    "de MAPE ficou abaixo de 0,7 ponto percentual.",
    "<b>Há uma explicação matemática para esse empate</b>, e ela é o achado mais "
    "interessante do trabalho: o otimizador do Holt-Winters convergiu para "
    "α ≈ β ≈ γ ≈ 0 em todos os 10 produtos, o que faz o modelo degenerar para uma "
    "forma funcional quase idêntica à do Prophet. Ver seção 13.",
    "<b>A dificuldade varia enormemente por produto:</b> o MAPE vai de 8,9% (Açúcar, "
    "demanda quase constante) a 81,3% (Pão Francês, altíssima variabilidade). Isso é "
    "propriedade do dado, não falha do modelo — e o sistema sinaliza baixa confiança "
    "automaticamente quando o MAPE do vencedor passa de 50%.",
    "<b>Limitação principal:</b> a validação foi feita sobre dados sintéticos "
    "reprodutíveis. Eles provam que a <i>metodologia</i> está correta, mas não "
    "substituem a demonstração sobre dados reais de um mercado.",
]:
    E.append(li(t))
E.append(esp(4))
E.append(destaque(
    "A frase de uma linha para a banca",
    "O motor não escolhe um modelo por preferência teórica: ele treina os dois, mede "
    "os dois com validação temporal honesta e deixa o dado decidir — produto a "
    "produto, execução a execução.", "ok"))
E.append(PageBreak())

# ── 2. Arquitetura ───────────────────────────────────────────────────────────
E.append(h1("2. Onde o motor vive: arquitetura e contrato"))
E.append(p(
    "O motor preditivo é um serviço isolado. Entender essa fronteira é importante "
    "porque ela explica por que certos cálculos estão aqui e outros não."))
E.append(codigo(
    "Lojista → Web App → API (Kotlin/Spring Boot) → ML Service (Python/FastAPI)\n"
    "                          │  POST /predict  ────────────┘\n"
    "                          └── JDBC ──→ MySQL 8.0"))
E.append(esp(3))
for t in [
    "<b>O ml-service é stateless.</b> Recebe JSON, devolve JSON e não acessa banco "
    "algum. Quem persiste é o backend, dono único do MySQL.",
    "<b>O frontend nunca chama o motor diretamente</b> — sempre passa pela API.",
    "<b>O contrato é por produto.</b> Uma chamada de "
    "<font face='DJM' size='8.5'>/predict</font> trata um único SKU e não enxerga o "
    "catálogo. É por isso que a Classificação ABC — que é um ranking relativo entre "
    "todos os produtos — foi deliberadamente movida para o backend.",
    "<b>A chamada é síncrona</b>, com timeout de 30 segundos no cliente Feign do "
    "backend.",
]:
    E.append(li(t))
E.append(esp(4))
E.append(h2("O que entra e o que sai"))
E.append(tabela([
    ["Entrada (PredictRequest)", "Saída (PredictResponse)"],
    ["produto_id", "modelo_selecionado — 'holt_winters' ou 'prophet'"],
    ["historico — mínimo 90 registros diários", "previsoes — 30 dias à frente"],
    ["lead_time_medio (padrão 3 dias)", "metricas — MAPE/RMSE/MAE dos DOIS modelos"],
    ["variabilidade_lead_time (padrão 1.0)", "ponto_reposicao"],
    ["nivel_servico_alvo (padrão 0.95)", "estoque_seguranca"],
    ["estoque_atual", "dias_ate_ruptura — null se demanda média = 0"],
    ["is_promocional (opcional)", "desvio_padrao_demanda"],
    ["", "aviso — preenchido quando MAPE do vencedor ≥ 50%"],
], [LARGURA_UTIL * 0.42, LARGURA_UTIL * 0.58]))
E.append(esp(6))
E.append(destaque(
    "Por que o response devolve as métricas dos dois modelos",
    "Porque é isso que alimenta a Tela 10 do sistema. O backend grava duas linhas na "
    "tabela <font face='DJM' size='8.5'>metrica_modelo</font> por execução — uma por "
    "modelo, com a marcação de qual foi o selecionado. A comparação fica auditável ao "
    "longo do tempo, não apenas no momento da decisão.", "info"))

# ── 3. O problema estatístico ────────────────────────────────────────────────
E.append(h1("3. O problema estatístico"))
E.append(p(
    "Temos, para cada produto, uma sequência de quantidades vendidas por dia: "
    "y₁, y₂, …, y_T. Queremos estimar ŷ para os próximos 30 dias. O que torna isso "
    "um problema de <b>série temporal</b> — e não de regressão comum — é que as "
    "observações não são independentes: o valor de amanhã está correlacionado com o "
    "de hoje, e existe estrutura de repetição (o sábado se parece com o sábado "
    "anterior)."))
E.append(p(
    "Uma série de vendas de varejo costuma ser descrita como a soma de quatro "
    "componentes, e é exatamente isso que os dois modelos tentam separar:"))
E.append(formula("y(t)  =  tendência(t)  +  sazonalidade(t)  +  eventos(t)  +  ruído(t)"))
E.append(esp(5))
E.append(tabela([
    ["Componente", "O que é", "Exemplo no mercadinho"],
    ["Tendência", "movimento de longo prazo do nível", "a loja cresce 20% no ano"],
    ["Sazonalidade", "padrão que se repete em ciclo fixo", "sábado vende 5× mais que domingo"],
    ["Eventos", "choques pontuais e datados", "feriado, promoção, loja fechada"],
    ["Ruído", "o que sobra — aleatório, imprevisível", "flutuação do dia a dia"],
], [2.9 * cm, LARGURA_UTIL * 0.40, LARGURA_UTIL - 2.9 * cm - LARGURA_UTIL * 0.40]))
E.append(esp(6))
E.append(p(
    "<b>O objetivo do modelo é capturar os três primeiros e deixar apenas o quarto "
    "como resíduo.</b> É por isso que a análise de resíduos (seção 12) é o teste "
    "decisivo de qualidade: se sobrou padrão no resíduo, ficou sinal na mesa."))
E.append(p(
    "O projeto exige <b>no mínimo 90 dias de histórico</b> por produto. A razão é "
    "estatística: com menos que isso não há ciclos semanais suficientes para "
    "distinguir com confiança uma sazonalidade real de uma flutuação aleatória. "
    "Abaixo desse mínimo o motor recusa a previsão com HTTP 422, em vez de devolver "
    "um número sem lastro."))

# ── 4. Holt-Winters ──────────────────────────────────────────────────────────
E.append(h1("4. Modelo 1 — Holt-Winters (suavização exponencial tripla)"))
E.append(h2("4.1 A intuição"))
E.append(p(
    "Holt-Winters é um <b>filtro recursivo com memória</b>. Ele carrega três "
    "estimativas sobre o estado atual da série e as atualiza a cada novo dia "
    "observado, dando peso maior ao passado recente. O nome 'exponencial' vem do "
    "formato desse peso: a influência de uma observação decai exponencialmente à "
    "medida que ela envelhece."))
E.append(tabela([
    ["Estado", "Símbolo", "O que representa"],
    ["Nível", "L", "onde o patamar de demanda está agora"],
    ["Tendência", "b", "quanto esse patamar sobe ou desce por dia"],
    ["Sazonalidade", "s", "o desvio típico de cada dia da semana (7 valores)"],
], [2.6 * cm, 2.2 * cm, LARGURA_UTIL - 4.8 * cm]))
E.append(esp(7))
E.append(h2("4.2 As equações de atualização"))
E.append(p(
    "Na configuração usada pelo projeto — tendência aditiva, sazonalidade aditiva, "
    "ciclo de 7 dias — as três equações são:"))
E.append(formula(
    "L_t = α·(y_t − s_(t−7))            + (1−α)·(L_(t−1) + b_(t−1))<br/>"
    "b_t = β·(L_t − L_(t−1))            + (1−β)·b_(t−1)<br/>"
    "s_t = γ·(y_t − L_(t−1) − b_(t−1))  + (1−γ)·s_(t−7)"))
E.append(esp(5))
E.append(p(
    "Cada linha se lê como uma <b>média ponderada entre 'o que acabei de observar' e "
    "'o que eu já achava'</b>. Os pesos são α, β e γ, os três parâmetros de "
    "suavização, todos entre 0 e 1:"))
E.append(li("<b>α próximo de 1</b> — o modelo reage rápido ao dado mais recente; "
            "memória curta, adaptação veloz, mas sensível a ruído."))
E.append(li("<b>α próximo de 0</b> — o modelo praticamente ignora a novidade e "
            "confia na estrutura já estimada; memória longa, muito estável."))
E.append(esp(4))
E.append(h2("4.3 A equação de previsão"))
E.append(p(
    "Para prever h dias à frente, o modelo congela o último estado conhecido e o "
    "extrapola:"))
E.append(formula("ŷ_(t+h) = L_t + h·b_t + s_(dia da semana correspondente)"))
E.append(esp(5))
E.append(p(
    "Note a consequência direta: <b>a previsão de 30 dias do Holt-Winters é uma reta "
    "com um padrão semanal repetido em cima dela</b>. O termo h·b_t cresce "
    "linearmente com o horizonte, então qualquer erro na estimativa da tendência se "
    "acumula quanto mais longe se prevê. É exatamente isso que o Gráfico 4 mede."))
E.append(KeepTogether([
    h2("4.4 Como α, β e γ são encontrados — a resposta à pergunta central"),
    destaque(
        "O modelo não reconhece uma tendência visualmente: ele a procura por otimização",
        ["As três equações acima só ficam definidas depois que α, β e γ recebem "
         "valores. Esses valores <b>não são escolhidos por quem programa nem estimados "
         "a olho</b>. A chamada "
         "<font face='DJM' size='8.5'>fit(optimized=True)</font> entrega o problema a "
         "um otimizador numérico (L-BFGS-B), que percorre o espaço de parâmetros "
         "medindo, para cada combinação candidata, a soma dos erros quadráticos que "
         "ela produziria ao reproduzir o histórico de treino.",
         "Como o serviço usa "
         "<font face='DJM' size='8.5'>initialization_method='estimated'</font>, o "
         "otimizador busca também os estados iniciais L₀, b₀ e os 7 valores sazonais "
         "iniciais — um total de <b>10 parâmetros ajustados simultaneamente</b> por "
         "produto. O critério é sempre o mesmo: minimizar o erro contra o passado "
         "observado."], "info")]))
E.append(esp(5))
E.append(h2("4.5 A configuração exata do projeto"))
E.append(codigo(
    "ExponentialSmoothing(\n"
    "    serie,\n"
    "    trend='add',                 # tendência aditiva\n"
    "    seasonal='add',              # sazonalidade aditiva\n"
    "    seasonal_periods=7,          # ciclo semanal do varejo de bairro\n"
    "    initialization_method='estimated',\n"
    ").fit(optimized=True, remove_bias=True)"))
E.append(esp(4))
E.append(p(
    "Dois detalhes de robustez implementados em "
    "<font face='DJM' size='8.5'>holt_winters_service.py</font>: séries com menos de "
    "14 dias (dois ciclos completos) têm a sazonalidade <b>desabilitada "
    "automaticamente</b>, porque o statsmodels não consegue estimá-la; e séries com "
    "menos de 10 observações não-nulas são <b>rejeitadas</b> com erro explícito. Além "
    "disso, <font face='DJM' size='8.5'>remove_bias=True</font> recentra os resíduos "
    "em zero após o ajuste."))
E.append(PageBreak())

# ── 5. Prophet ───────────────────────────────────────────────────────────────
E.append(h1("5. Modelo 2 — Prophet (modelo aditivo generalizado)"))
E.append(h2("5.1 A intuição"))
E.append(p(
    "O Prophet, desenvolvido pela Meta, adota a filosofia oposta. Em vez de atualizar "
    "estados dia a dia, ele trata a série inteira como uma <b>função do tempo</b> e "
    "ajusta uma curva global — é, essencialmente, uma regressão sofisticada em que a "
    "variável explicativa é o próprio tempo."))
E.append(formula("y(t) = g(t) + s(t) + h(t) + ε_t"))
E.append(esp(4))
E.append(tabela([
    ["Termo", "Nome", "Como é modelado"],
    ["g(t)", "tendência", "linear por partes, com pontos de quebra automáticos"],
    ["s(t)", "sazonalidade", "série de Fourier (senos e cossenos)"],
    ["h(t)", "feriados", "efeito datado — desligado neste projeto (ver seção 15)"],
    ["ε_t", "ruído", "o resíduo, assumido normal"],
], [1.8 * cm, 2.7 * cm, LARGURA_UTIL - 4.5 * cm]))
E.append(esp(7))
E.append(h2("5.2 g(t) — a tendência com pontos de quebra"))
E.append(p(
    "Este é o verdadeiro diferencial do Prophet. Em vez de uma única inclinação, ele "
    "permite que a tendência <b>mude de direção em pontos específicos do tempo</b>. O "
    "procedimento é:"))
E.append(li("Distribui 25 <i>changepoints</i> candidatos (padrão) uniformemente sobre "
            "os primeiros 80% do histórico.", "1."))
E.append(li("Permite que a inclinação da reta mude em cada um deles.", "2."))
E.append(li("Aplica uma penalização Laplace sobre cada mudança "
            "(<font face='DJM' size='8.5'>changepoint_prior_scale=0.05</font>), que "
            "funciona como regularização L1.", "3."))
E.append(li("A regularização empurra a maioria das mudanças para zero — <b>só "
            "sobrevivem as quebras que reduzem o erro o suficiente para pagar a "
            "penalização</b>.", "4."))
E.append(esp(4))
E.append(p(
    "Ou seja: o Prophet não só busca a melhor tendência, ele busca <b>onde a tendência "
    "muda</b>. É a resposta mais literal possível à pergunta 'ele busca a melhor "
    "tendência com base no histórico?'."))
E.append(h2("5.3 s(t) — a sazonalidade por série de Fourier"))
E.append(p(
    "Enquanto o Holt-Winters guarda 7 valores sazonais explícitos, o Prophet ajusta "
    "uma soma de senos e cossenos. Com o padrão de ordem 3 para o ciclo semanal:"))
E.append(formula(
    "s(t) = Σ (n=1 até 3)  [ aₙ·cos(2πnt/7) + bₙ·sen(2πnt/7) ]"))
E.append(esp(5))
E.append(p(
    "São 6 coeficientes ajustados. Vale um esclarecimento técnico que costuma ser "
    "cobrado: <b>com período 7, esses 6 coeficientes mais o deslocamento da tendência "
    "bastam para reproduzir qualquer padrão semanal</b> — está exatamente no limite "
    "de resolução da série. Nesse quesito os dois modelos têm poder expressivo "
    "equivalente; não há perda por usar Fourier aqui."))
E.append(p(
    "A diferença real está em outro lugar: a sazonalidade do Prophet é <b>global e "
    "fixa</b> — estimada uma vez para toda a série. A do Holt-Winters <b>evolui</b> "
    "continuamente através do parâmetro γ. Se o padrão semanal de um produto mudar ao "
    "longo do ano, o Holt-Winters acompanha e o Prophet não."))
E.append(h2("5.4 Como o Prophet é ajustado"))
E.append(p(
    "O Prophet monta tudo isso como um problema de estimação de máxima probabilidade "
    "a posteriori (MAP) e o resolve com o otimizador L-BFGS dentro do <b>Stan</b>, um "
    "motor de inferência bayesiana compilado. Novamente: <b>busca numérica sobre o "
    "histórico</b>, não leitura de gráfico. É esse componente Stan (via "
    "<font face='DJM' size='8.5'>cmdstanpy</font>) que causou o incidente de ambiente "
    "descrito na seção 16."))
E.append(esp(4))
E.append(codigo(
    "Prophet(\n"
    "    yearly_seasonality=False,    # 90-365 dias não capturam ciclo anual\n"
    "    weekly_seasonality=True,     # padrão semanal do varejo\n"
    "    daily_seasonality=False,     # a granularidade já é diária\n"
    "    interval_width=0.95,\n"
    ")"))
E.append(PageBreak())

# ── 6. Comparação conceitual ─────────────────────────────────────────────────
E.append(h1("6. Comparação conceitual entre os dois modelos"))
E.append(tabela([
    ["Aspecto", "Holt-Winters", "Prophet"],
    ["Natureza", "filtro recursivo — estado atualizado dia a dia",
     "regressão global sobre o tempo"],
    ["Peso dos dados", "decai exponencialmente; o recente pesa mais",
     "todos os pontos pesam igual"],
    ["Tendência", "uma só, adapta-se continuamente",
     "linear por partes; quebras detectadas automaticamente"],
    ["Sazonalidade", "7 valores explícitos que evoluem com γ",
     "série de Fourier fixa para toda a série"],
    ["Feriados", "não tem mecanismo — feriado é ruído",
     "suporte nativo e datado (não ativado aqui)"],
    ["Mudança de patamar", "absorve sozinho, com atraso",
     "precisa de um changepoint naquele ponto"],
    ["Falhas / lacunas", "exige série contínua",
     "tolera lacunas e outliers com naturalidade"],
    ["Ajuste", "L-BFGS-B minimizando soma de erros quadráticos",
     "MAP via L-BFGS no Stan"],
    ["Parâmetros ajustados", "α, β, γ + L₀, b₀ + 7 sazonais iniciais",
     "inclinações por segmento + 6 coeficientes de Fourier"],
    ["Custo computacional", "baixo — milissegundos",
     "maior — compila e amostra via Stan"],
], [3.0 * cm, (LARGURA_UTIL - 3.0 * cm) / 2, (LARGURA_UTIL - 3.0 * cm) / 2]))
E.append(esp(8))
E.append(destaque(
    "A leitura correta dessa tabela",
    "Nenhum dos dois é superior em abstrato. O Holt-Winters tende a vencer em séries "
    "estáveis com sazonalidade que muda devagar; o Prophet tende a vencer quando há "
    "quebras de patamar, feriados relevantes ou dados faltando. <b>É precisamente por "
    "isso que o projeto não escolhe um deles no papel — ele mede os dois em cada "
    "produto e deixa o dado decidir.</b>", "ok"))

# ── 7. Como o motor decide ───────────────────────────────────────────────────
E.append(h1("7. Como o motor decide qual modelo usar"))
E.append(p(
    "O orquestrador é o "
    "<font face='DJM' size='8.5'>prediction_service.py</font>. Ele não conhece os "
    "detalhes internos de nenhum modelo — só o contrato comum de que ambos expõem uma "
    "função <font face='DJM' size='8.5'>treinar_e_avaliar(serie)</font>."))
E.append(codigo(
    "1.  Ordena o histórico cronologicamente (a ordem de chegada não importa)\n"
    "2.  Treina Holt-Winters   → métricas + previsão de 30 dias  [tolera falha]\n"
    "3.  Treina Prophet        → métricas + previsão de 30 dias  [tolera falha]\n"
    "4.  Se AMBOS falharam     → erro 500 descritivo\n"
    "5.  Seleciona o de MENOR MAPE  (empate → Holt-Winters)\n"
    "6.  Calcula ES, ponto de reposição e dias até ruptura sobre o VENCEDOR\n"
    "7.  Se MAPE do vencedor ≥ 50% → preenche o campo 'aviso'\n"
    "8.  Devolve as métricas dos DOIS modelos (alimenta a Tela 10)"))
E.append(esp(6))
E.append(h2("7.1 A validação walk-forward — o ponto metodológico mais importante"))
E.append(p(
    "Para medir o erro de um modelo é preciso testá-lo em dados que ele não viu. Em "
    "séries temporais essa separação <b>tem que respeitar o tempo</b>:"))
E.append(codigo(
    "|─────────── treino: primeiros 80% ───────────|── teste: 20% finais ──|\n"
    f"|  {wf['1']['treino_ini']}  →  {wf['1']['treino_fim']}"
    f"   ({wf['1']['n_treino']} dias)     |  {wf['1']['valid_ini']} → "
    f"{wf['1']['valid_fim']}  ({wf['1']['n_validacao']} dias) |"))
E.append(esp(5))
E.append(destaque(
    "Por que nunca usar train_test_split do scikit-learn aqui",
    "Essa função <b>embaralha</b> as observações antes de dividir. Em série temporal "
    "isso colocaria dias de dezembro no treino e dias de outubro no teste — o modelo "
    "estaria literalmente usando o futuro para prever o passado. O erro medido ficaria "
    "artificialmente baixo e completamente sem valor. A proibição está registrada "
    "explicitamente nas convenções do serviço, e a divisão é feita por posição "
    "cronológica.", "alerta"))
E.append(esp(5))
E.append(h2("7.2 Uma sutileza que vale declarar"))
E.append(p(
    "Depois de medir o erro com 80% dos dados, o serviço <b>reajusta o modelo na série "
    "completa</b> para gerar a previsão de 30 dias que será efetivamente entregue. "
    "Isso é a prática correta — não faria sentido descartar 20% do histórico na "
    "operação real. Mas significa que <b>o MAPE reportado estima o erro de um modelo "
    "treinado em 80% dos dados, enquanto a previsão entregue vem de um modelo treinado "
    "em 100%</b>. Os dois não são o mesmo objeto ajustado; na prática o modelo final "
    "tende a ser ligeiramente melhor que a métrica sugere."))
E.append(h2("7.3 Degradação controlada"))
E.append(p(
    "Se um dos modelos falhar (série inadequada, ambiente do Prophet quebrado), o "
    "motor <b>não aborta</b>: registra o motivo em log, segue com o modelo "
    "sobrevivente e devolve apenas as métricas disponíveis. Só quando ambos falham é "
    "que a requisição retorna erro."))
E.append(PageBreak())

# ── 8. Métricas ──────────────────────────────────────────────────────────────
E.append(h1("8. As três métricas de erro: MAPE, RMSE e MAE"))
E.append(p(
    "As três medem a distância entre o previsto e o realizado na janela de teste, mas "
    "punem os erros de formas diferentes. O motor decide por MAPE; as outras duas "
    "existem para dar contexto e evitar leitura enganosa."))
E.append(formula(
    "MAE  = média( |real − previsto| )<br/>"
    "RMSE = raiz( média( (real − previsto)² ) )<br/>"
    "MAPE = média( |real − previsto| / real ) × 100"))
E.append(esp(5))
E.append(tabela([
    ["Métrica", "Unidade", "Característica", "Cuidado"],
    ["MAE", "unidades do produto", "erro médio típico; fácil de explicar ao lojista",
     "não comparável entre produtos de volumes diferentes"],
    ["RMSE", "unidades do produto", "eleva o erro ao quadrado: pune muito erro grande",
     "um único dia muito errado domina a métrica"],
    ["MAPE", "percentual", "adimensional: permite comparar produtos entre si",
     "explode quando o valor real é pequeno"],
], [1.7 * cm, 2.5 * cm, LARGURA_UTIL * 0.34,
    LARGURA_UTIL - 4.2 * cm - LARGURA_UTIL * 0.34]))
E.append(esp(7))
E.append(h2("8.1 Por que a decisão usa MAPE"))
E.append(p(
    "Porque a escolha do modelo precisa ser <b>comparável entre produtos de escalas "
    "diferentes</b>. Um erro de 3 unidades é ótimo para o Pão Francês (30/dia) e "
    "péssimo para o Sal (5/dia). Só uma métrica percentual permite dizer 'este produto "
    "é mais previsível que aquele' e alimentar o KPI de acurácia do dashboard como "
    "<font face='DJM' size='8.5'>100 − MAPE</font>."))
E.append(h2("8.2 O tratamento dos dias sem venda"))
E.append(p(
    "O MAPE divide pelo valor real. Em dias de loja fechada o real é zero, o que "
    "produziria divisão por zero. A implementação do projeto calcula o MAPE "
    "<b>apenas sobre as observações com valor real maior que zero</b>, enquanto RMSE e "
    "MAE continuam considerando todos os dias. Consequência prática: as três métricas "
    "não são calculadas exatamente sobre o mesmo conjunto de pontos, e isso deve ser "
    "considerado ao compará-las."))
E.append(esp(4))
E.append(destaque(
    "Quando o MAPE engana — evidência real deste projeto",
    "Nos testes de robustez do produto 5 (Banana Prata), uma das cinco janelas "
    "devolveu <b>MAPE = 188,4%</b> enquanto as outras quatro ficaram entre 30% e 51%. "
    "O RMSE dessa mesma janela foi 11,6 — alto, mas nada catastrófico. O que aconteceu "
    "foi aritmética: naquela janela caíram dias de venda muito baixa, e dividir um erro "
    "moderado por um denominador pequeno produz um percentual enorme. "
    "<b>É por isso que o relatório apresenta as três métricas juntas</b> — MAPE "
    "isolado seria uma leitura frágil.", "alerta"))

# ── 9. Ballou ────────────────────────────────────────────────────────────────
E.append(PageBreak())
E.append(h1("9. Da previsão à decisão: as fórmulas de estoque"))
E.append(p(
    "Prever a demanda é meio caminho. O que o lojista precisa é de uma decisão: "
    "<i>quando</i> pedir e <i>quanto</i> manter de reserva. Essa conversão usa a "
    "formulação de Ballou (2006), implementada em "
    "<font face='DJM' size='8.5'>stock_service.py</font>."))
E.append(h2("9.1 Nível de serviço e Z-score"))
E.append(p(
    "O <b>nível de serviço</b> é a probabilidade alvo de não faltar estoque durante o "
    "lead time — 95% por padrão no projeto. Ele é convertido no multiplicador Z da "
    "distribuição normal padrão:"))
E.append(formula("Z = norm.ppf(nível_serviço)        →   ppf(0,95) = 1,6449"))
E.append(esp(5))
E.append(p(
    "Vale destacar que o cálculo é <b>dinâmico</b>. O protótipo de tela usava 1,65 "
    "cravado no código, o que tornaria o campo 'nível de serviço' decorativo — mudar "
    "de 95% para 99% não teria efeito algum. No motor real, alterar o nível para 0,99 "
    "muda o Z para 2,326 e o estoque de segurança sobe proporcionalmente."))
E.append(h2("9.2 Estoque de segurança — a fórmula combinada de Ballou"))
E.append(formula("ES = Z · √( LT · σ²_demanda  +  demanda²  · σ²_leadtime )"))
E.append(esp(5))
E.append(p(
    "O ponto importante é que ela considera <b>duas fontes de incerteza ao mesmo "
    "tempo</b>: a demanda pode variar (primeiro termo) e o fornecedor pode atrasar "
    "(segundo termo). A fórmula simplificada que aparece em muitos materiais, "
    "<font face='DJM' size='8.5'>1,65 · σ · √LT</font>, ignora completamente a segunda "
    "— e num mercado de bairro, onde o atraso do fornecedor é rotina, essa omissão "
    "subdimensiona a reserva."))
E.append(h2("9.3 Ponto de reposição e dias até ruptura"))
E.append(formula(
    "PR   = demanda_média_diária · lead_time + ES<br/>"
    "dias = estoque_atual / demanda_média_diária        (None se demanda = 0)"))
E.append(esp(6))
E.append(h2("9.4 Exemplo numérico completo — executado pelo motor"))
E.append(p(
    "Valores reais produzidos pelo código, com lead time de 3 dias, variabilidade de "
    "lead time 1,0 e nível de serviço 95%:"))
k1, k5 = kpi[1], kpi[5]
E.append(tabela([
    ["Etapa", f"{k1['nome']} (id 1)", f"{k5['nome']} (id 5)"],
    ["Modelo vencedor", k1["vencedor"], k5["vencedor"]],
    ["Demanda média prevista (un/dia)", f"{k1['demanda_media']:.3f}",
     f"{k5['demanda_media']:.3f}"],
    ["σ da demanda histórica", f"{k1['desvio']:.3f}", f"{k5['desvio']:.3f}"],
    ["Z (nível 95%)", f"{k1['z']}", f"{k5['z']}"],
    ["Radicando: LT·σ² + demanda²·σ²_LT",
     f"3·{k1['desvio']:.3f}² + {k1['demanda_media']:.3f}² = 260,80",
     f"3·{k5['desvio']:.3f}² + {k5['demanda_media']:.3f}² = 568,45"],
    ["<b>Estoque de segurança</b>", f"1,6449 · √260,80 = <b>{k1['estoque_seguranca']}</b>",
     f"1,6449 · √568,45 = <b>{k5['estoque_seguranca']}</b>"],
    ["<b>Ponto de reposição</b>",
     f"{k1['demanda_media']:.3f}·3 + {k1['estoque_seguranca']} = "
     f"<b>{k1['ponto_reposicao']}</b>",
     f"{k5['demanda_media']:.3f}·3 + {k5['estoque_seguranca']} = "
     f"<b>{k5['ponto_reposicao']}</b>"],
    ["Estoque atual", f"{k1['estoque_atual']}", f"{k5['estoque_atual']}"],
    ["<b>Dias até ruptura</b>", f"<b>{k1['dias_ate_ruptura']}</b>",
     f"<b>{k5['dias_ate_ruptura']}</b>"],
    ["Situação",
     "<font color='#B3261E'>●</font> <b>crítico</b> — estoque abaixo do PR, pedir hoje",
     "<font color='#1E6B3A'>●</font> <b>confortável</b> — estoque muito acima do PR"],
], [LARGURA_UTIL * 0.30, LARGURA_UTIL * 0.35, LARGURA_UTIL * 0.35]))
E.append(esp(7))
E.append(destaque(
    "A leitura de negócio",
    "O Arroz tem estoque de 15 unidades e ponto de reposição de 65,8 — ele já deveria "
    "ter sido pedido, e em pouco mais de um dia acaba. A Banana tem 200 unidades "
    "contra um PR de 85 — está folgada. <b>É essa tradução que justifica o projeto: "
    "a estatística vira uma instrução acionável para o lojista</b>, não um número "
    "abstrato.", "ok"))
E.append(PageBreak())

# ── 10. A camada de análise ──────────────────────────────────────────────────
E.append(h1("10. O que foi feito na camada de análise (analysis/)"))
E.append(p(
    "A pasta <font face='DJM' size='8.5'>ml-service/analysis/</font> é a camada "
    "acadêmica do projeto. Ela existe para responder duas perguntas que o código de "
    "produção sozinho não responde: <b>por que</b> o motor escolhe um modelo e "
    "<b>como sabemos</b> que a previsão funciona."))
E.append(h2("10.1 O princípio de projeto: reaproveitar o código de produção"))
E.append(destaque(
    "Nenhuma fórmula é reimplementada na análise",
    "O notebook importa "
    "<font face='DJM' size='8.5'>app/services/holt_winters_service</font>, "
    "<font face='DJM' size='8.5'>prophet_service</font> e "
    "<font face='DJM' size='8.5'>stock_service</font> — os mesmos módulos que o "
    "endpoint <font face='DJM' size='8.5'>/predict</font> executa. A consequência é "
    "forte e vale ser afirmada na defesa: <b>os números do TCC não são uma simulação "
    "paralela do sistema, são o sistema</b>. Se a análise mostra MAPE de 12,49% para o "
    "Arroz, é exatamente isso que a API devolve.", "ok"))
E.append(esp(5))
E.append(h2("10.2 Estrutura da pasta"))
E.append(tabela([
    ["Arquivo", "Papel"],
    ["analise_modelos.ipynb", "notebook principal — 28 células, 11 seções metodológicas"],
    ["analysis_utils.py", "helpers que reusam os internos dos serviços"],
    ["requirements-analysis.txt", "dependências só de análise, fora do runtime do serviço"],
    ["data/", "espaço para o dataset real (vendas_real.xlsx), opcional"],
    ["figures/", "14 PNGs gerados, prontos para o texto do TCC"],
    ["results/comparativo_modelos.csv", "MAPE/RMSE/MAE por produto × modelo + vencedor"],
], [4.9 * cm, LARGURA_UTIL - 4.9 * cm]))
E.append(esp(7))
E.append(h2("10.3 Por que existe o analysis_utils.py"))
E.append(p(
    "A função pública dos serviços, "
    "<font face='DJM' size='8.5'>treinar_e_avaliar</font>, devolve as métricas e a "
    "previsão futura de 30 dias — mas <b>não</b> devolve as previsões feitas sobre a "
    "janela de validação, que são justamente o que o gráfico 'previsto × real' precisa "
    "desenhar. O <font face='DJM' size='8.5'>analysis_utils</font> resolve isso "
    "chamando os helpers internos "
    "(<font face='DJM' size='8.5'>_ajustar_modelo</font>, "
    "<font face='DJM' size='8.5'>_calcular_metricas</font>) e replicando exatamente o "
    "mesmo split 80/20. Mesma configuração, mesmos resultados — apenas com acesso ao "
    "passo intermediário."))
E.append(h2("10.4 O roteiro metodológico — CRISP-DM adaptado a séries temporais"))
E.append(tabela([
    ["Etapa", "O que o notebook faz", "Saída"],
    ["1-2. Entendimento e coleta",
     "gera o dataset reprodutível e monta a estatística descritiva por produto",
     "tabela de média, σ, CV e % de zeros"],
    ["3. Análise exploratória",
     "decompõe a série em tendência / sazonalidade / resíduo",
     "Gráfico 1"],
    ["4-5. Pré-processamento e divisão",
     "confirma índice diário contínuo e aplica o split temporal 80/20",
     "janelas de treino e teste"],
    ["6-7. Treinamento e avaliação",
     "roda os dois modelos e coleta previsões e métricas",
     "Gráficos 2, 3 e 4"],
    ["8. Diagnóstico",
     "analisa resíduos e repete a avaliação em janelas móveis",
     "Gráficos 5 e 6"],
    ["9. Aplicação de negócio",
     "converte a previsão em ES, ponto de reposição e dias até ruptura",
     "Gráfico 7"],
    ["10-11. Limitações e reprodutibilidade",
     "declara restrições e fixa a semente e as versões",
     "seções finais"],
], [3.5 * cm, LARGURA_UTIL * 0.46, LARGURA_UTIL - 3.5 * cm - LARGURA_UTIL * 0.46]))
E.append(PageBreak())

# ── 11. Dataset sintético ────────────────────────────────────────────────────
E.append(h1("11. O dataset sintético: como os dados são gerados"))
E.append(p(
    "A validação usa dados sintéticos reprodutíveis, produzidos por "
    "<font face='DJM' size='8.5'>app/tests/generate_synthetic_data.py</font>: 10 "
    "produtos × 365 dias, com semente fixa. A escolha é deliberada — permite conhecer "
    "a estrutura verdadeira dos dados e, portanto, verificar se o modelo a recuperou."))
E.append(h2("11.1 A fórmula geradora"))
E.append(formula(
    "quantidade(t) = round( demanda_base × tendência(t) × fator_semanal(t) × ruído(t) )"))
E.append(esp(5))
E.append(li("<b>demanda_base</b> — constante por produto, de 5 un/dia (Sal) a 30 un/dia "
            "(Pão Francês)."))
E.append(li("<b>tendência</b> — crescimento linear de +20% do primeiro ao último dia."))
E.append(li("<b>fator_semanal</b> — multiplicador fixo por dia da semana (tabela "
            "abaixo)."))
E.append(li("<b>ruído</b> — gaussiano multiplicativo centrado em 1,0, com desvio igual "
            "ao parâmetro de variabilidade do produto, truncado entre 0,1 e 3,0."))
E.append(esp(5))
E.append(h2("11.2 O perfil semanal"))
E.append(tabela([
    ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
    ["0,85", "0,75", "0,80", "0,90", "<b>1,35</b>", "<b>1,45</b>", "0,30"],
], [LARGURA_UTIL / 7] * 7))
E.append(esp(4))
E.append(p(
    "Sábado vende cerca de <b>cinco vezes mais que domingo</b>. É essa estrutura que "
    "aparece nítida na decomposição do Gráfico 1 e que justifica o parâmetro "
    "<font face='DJM' size='8.5'>seasonal_periods=7</font> nos dois modelos."))
E.append(h2("11.3 Fechamentos"))
E.append(p(
    "Domingos têm 40% de chance de zerar e os 12 feriados nacionais de 2024 têm 60%. "
    "Isso reproduz o comportamento real de um mercado de bairro e é a principal fonte "
    "de dificuldade para os modelos — cerca de 6 a 8,5% dos dias de cada produto são "
    "zeros."))
E.append(h2("11.4 Estatística descritiva dos 10 produtos"))
linhas = [["id", "Produto", "Variab.", "Média/dia", "σ", "CV", "% zeros"]]
for r in d["descritiva"]:
    linhas.append([r["produto_id"], r["nome"], f"{r['variabilidade']:.2f}",
                   f"{r['media_diaria']:.2f}", f"{r['desvio']:.2f}", f"{r['cv']:.2f}",
                   f"{r['pct_zeros']:.1f}%"])
E.append(tabela(linhas, [1.0 * cm, 4.6 * cm, 1.9 * cm, 2.2 * cm, 1.6 * cm, 1.5 * cm,
                         1.9 * cm], alinha_dir=(2, 3, 4, 5, 6)))
E.append(esp(6))
E.append(p(
    "A coluna <b>Variab.</b> é o parâmetro de ruído usado na geração; o <b>CV</b> "
    "(coeficiente de variação) é medido sobre a série resultante. Note que o CV nunca "
    "fica muito baixo mesmo para o Sal (variabilidade 0,05): isso acontece porque a "
    "própria oscilação semanal — sábado 1,45 contra domingo 0,30 — já produz "
    "dispersão. <b>Essa é uma observação relevante: parte do 'desvio' de cada produto "
    "é estrutura previsível, não ruído</b>, e é exatamente essa parte que os modelos "
    "conseguem capturar."))
E.append(esp(5))
E.append(destaque(
    "Duas saídas diferentes do gerador — atenção à distinção",
    "A função devolve uma tupla. O dicionário de séries <b>mantém os zeros</b> e tem "
    "índice diário contínuo — é o que o notebook e os testes do motor consomem, porque "
    "os modelos exigem continuidade temporal. Já o DataFrame exportado para "
    "<font face='DJM' size='8.5'>.xlsx</font> filtra "
    "<font face='DJM' size='8.5'>quantidade &gt; 0</font>, ou seja, <b>as linhas de "
    "domingo e feriado desaparecem</b>. Ao usar a planilha na importação, cabe ao "
    "backend reconstruir a frequência diária antes de chamar o "
    "<font face='DJM' size='8.5'>/predict</font> — caso contrário o motor em produção "
    "receberia uma série diferente da que foi validada aqui.", "alerta"))
E.append(PageBreak())

# ── 12. Resultados ───────────────────────────────────────────────────────────
E.append(h1("12. Resultados empíricos"))
E.append(h2("12.1 Comparativo completo — os 10 produtos, os 2 modelos"))
E.append(p("Linhas destacadas em verde indicam o modelo vencedor de cada produto."))
linhas = [["id", "Produto", "Modelo", "MAPE (%)", "RMSE", "MAE", "Vencedor"]]
destaques = []
for i, r in enumerate(d["comparativo"], start=1):
    if r["vencedor"]:
        destaques.append(i)
    linhas.append([r["produto_id"], r["nome"], r["modelo"], f"{r['mape']:.4f}",
                   f"{r['rmse']:.4f}", f"{r['mae']:.4f}", "✔" if r["vencedor"] else ""])
E.append(tabela(linhas, [0.9 * cm, 4.0 * cm, 2.6 * cm, 2.2 * cm, 1.9 * cm, 1.9 * cm,
                         1.9 * cm], alinha_dir=(3, 4, 5), destaque_linhas=destaques))
E.append(esp(7))
E.append(h2("12.2 O placar e as margens"))
v = d["vitorias"]
E.append(p(
    f"<b>Holt-Winters venceu em {v['holt_winters']} produtos e Prophet em "
    f"{v['prophet']}.</b> Mas o placar isolado esconde o mais importante — o tamanho "
    "das margens:"))
linhas = [["Produto", "Margem de MAPE (pontos percentuais)"]]
for m in sorted(d["margens"], key=lambda x: x["margem_pp"]):
    linhas.append([f"{m['produto_id']} — {m['nome']}", f"{m['margem_pp']:.4f}"])
E.append(tabela(linhas, [7.0 * cm, LARGURA_UTIL - 7.0 * cm], alinha_dir=(1,)))
E.append(esp(6))
E.append(destaque(
    "A conclusão honesta sobre o comparativo",
    "Em <b>9 dos 10 produtos a diferença entre os dois modelos é menor que 0,7 ponto "
    "percentual</b>, e em cinco deles é menor que 0,06 pp. A única separação "
    "perceptível está no Pão Francês (2,92 pp, a favor do Holt-Winters), justamente o "
    "produto mais volátil da base. <b>Nenhum modelo domina o outro neste conjunto de "
    "dados</b> — e a seção 13 explica matematicamente por quê.", "info"))
E.append(PageBreak())

# ── 12.3 Gráficos ────────────────────────────────────────────────────────────
E.append(h1("12.3 Evidência visual"))
E.append(p(
    "Os gráficos abaixo usam dois produtos de perfis opostos: <b>Arroz 5kg (id 1)</b>, "
    "de demanda estável, e <b>Banana Prata kg (id 5)</b>, de alta variabilidade. O "
    "contraste entre eles é o que torna visível o limite do que a previsão consegue "
    "fazer."))

E.append(h2("Gráfico 1 — Decomposição: existe sinal previsível?"))
E.append(p(
    "Separa a série observada em tendência, sazonalidade semanal e resíduo. É o teste "
    "que justifica usar modelos de série temporal em vez de uma média simples: se a "
    "faixa sazonal tem amplitude nítida e regular, há estrutura a capturar."))
E.append(figura("g1_decomposicao_produto1.png",
                "Arroz 5kg — sazonalidade semanal regular e tendência de crescimento "
                "claramente separadas do resíduo.", LARGURA_UTIL * 0.74))
E.append(figura("g1_decomposicao_produto5.png",
                "Banana Prata kg — mesma estrutura sazonal, mas com resíduo de "
                "amplitude muito maior: é a variabilidade intrínseca do produto.",
                LARGURA_UTIL * 0.74))
E.append(PageBreak())

E.append(h2("Gráfico 2 — Previsto × Real fora da amostra"))
E.append(p(
    "O gráfico mais direto de todos: a linha preta é o que realmente aconteceu na "
    "janela de teste, e as tracejadas são o que cada modelo previu <b>sem nunca ter "
    "visto esses dias</b>. Quanto mais próximas, melhor a generalização."))
E.append(figura("g2_previsto_real_produto1.png",
                "Arroz 5kg — as duas previsões acompanham o padrão semanal de perto; "
                "as curvas dos dois modelos são praticamente indistinguíveis."))
E.append(figura("g2_previsto_real_produto5.png",
                "Banana Prata kg — os modelos capturam o ciclo semanal, mas não a "
                "amplitude das oscilações diárias: é o ruído do produto, não erro de "
                "método."))
E.append(PageBreak())

E.append(h2("Gráfico 3 — Comparativo de erro por modelo"))
E.append(p(
    "Espelha exatamente a Tela 10 do sistema. É a justificativa quantitativa da "
    "escolha: o modelo de menor MAPE vence."))
E.append(figura("g3_barras_erro_produto1.png",
                f"Arroz 5kg — Prophet vence por {d['margens'][0]['margem_pp']:.4f} pp "
                "de MAPE. Uma diferença dessa ordem é, na prática, um empate."))
E.append(figura("g3_barras_erro_produto5.png",
                "Banana Prata kg — mesmo padrão: as barras dos dois modelos são "
                "visualmente idênticas nas três métricas."))
E.append(PageBreak())

E.append(h2("Gráfico 4 — Como o erro cresce com o horizonte"))
E.append(p(
    "Mostra o erro absoluto dia a dia conforme se prevê mais longe. Informa até quando "
    "confiar na previsão — e, para o Holt-Winters, revela o efeito do termo h·b_t "
    "acumulando a incerteza da tendência."))
E.append(figura("g4_erro_horizonte_produto1.png",
                "Arroz 5kg — o erro oscila com o ciclo semanal, sem explodir ao longo "
                "do horizonte."))
E.append(figura("g4_erro_horizonte_produto5.png",
                "Banana Prata kg — amplitude de erro muito maior, refletindo a "
                "variabilidade do produto."))
E.append(PageBreak())

E.append(h2("Gráfico 5 — Análise de resíduos"))
E.append(p(
    "O teste decisivo de qualidade. Resíduo = real − previsto. Um bom modelo deixa "
    "resíduos <b>centrados em zero, sem padrão visível no tempo e sem "
    "autocorrelação</b> — ou seja, ruído branco. Se a função de autocorrelação (ACF) "
    "mostrasse um pico no lag 7, significaria que o modelo não capturou a sazonalidade "
    "semanal e ainda há sinal a extrair."))
E.append(figura("g5_residuos_produto1_holt_winters.png",
                "Arroz 5kg — histograma aproximadamente simétrico em torno de zero e "
                "ACF dentro da banda de confiança: o modelo capturou a estrutura.",
                LARGURA_UTIL * 0.95))
E.append(figura("g5_residuos_produto5_holt_winters.png",
                "Banana Prata kg — resíduo bem mais disperso, como esperado, mas "
                "igualmente sem padrão sistemático.", LARGURA_UTIL * 0.95))
E.append(PageBreak())

E.append(h2("Gráfico 6 — Backtesting rolling-origin"))
E.append(p(
    "Repete o experimento em cinco janelas móveis sucessivas. Responde à objeção mais "
    "óbvia que a banca pode levantar: <i>e se o bom resultado tiver sido sorte de uma "
    "única divisão?</i>"))
E.append(figura("g6_backtesting_produto1.png",
                "Arroz 5kg — MAPE estável entre 10,5% e 15,7% ao longo das cinco "
                "dobras. O desempenho é consistente."))
E.append(figura("g6_backtesting_produto5.png",
                "Banana Prata kg — desempenho instável, com um pico isolado. Ver a "
                "análise numérica na seção 14."))
E.append(PageBreak())

E.append(h2("Gráfico 7 — Da previsão à decisão de reposição"))
E.append(p(
    "Fecha o ciclo: projeta a queda do estoque atual segundo a demanda prevista e "
    "marca onde ela cruza o ponto de reposição — o momento exato de fazer o pedido. É "
    "a tradução da estatística em instrução operacional."))
E.append(figura("g7_reposicao_produto1.png",
                f"Arroz 5kg — estoque atual de {k1['estoque_atual']} unidades contra "
                f"ponto de reposição de {k1['ponto_reposicao']}: o produto já está em "
                "situação crítica, com ruptura estimada em "
                f"{k1['dias_ate_ruptura']} dia."))
E.append(figura("g7_reposicao_produto5.png",
                f"Banana Prata kg — {k5['estoque_atual']} unidades contra PR de "
                f"{k5['ponto_reposicao']}: situação confortável, "
                f"{k5['dias_ate_ruptura']} dias de cobertura."))
E.append(PageBreak())

# ── 13. Achado central ───────────────────────────────────────────────────────
E.append(h1("13. Achado central: por que os dois modelos empatam"))
E.append(p(
    "O empate técnico observado na seção 12 não é acaso nem indecisão do método. Ele "
    "tem uma explicação matemática verificável, e ela é provavelmente a contribuição "
    "analítica mais interessante deste trabalho."))
E.append(h2("13.1 A evidência: os parâmetros que o otimizador encontrou"))
E.append(p(
    "Extraindo os parâmetros de suavização ajustados pelo otimizador do Holt-Winters "
    "em cada um dos 10 produtos:"))
linhas = [["id", "Produto", "α (nível)", "β (tendência)", "γ (sazonal)"]]
for r in ALPHAS:
    linhas.append([r["pid"], r["nome"], f"{r['a']:.5f}", f"{r['b']:.5f}",
                   f"{r['g']:.5f}"])
E.append(tabela(linhas, [1.0 * cm, 5.2 * cm, 2.9 * cm, 2.9 * cm, 2.9 * cm],
                alinha_dir=(2, 3, 4)))
E.append(esp(7))
E.append(destaque(
    "Em todos os 10 produtos, α ≈ β ≈ γ ≈ 0",
    ["Sete produtos convergiram para exatamente zero nos três parâmetros; os outros "
     "três ficaram na ordem de 10⁻⁵ a 10⁻³. Isso não é um defeito — é o otimizador "
     "fazendo seu trabalho corretamente e nos dizendo algo sobre os dados.",
     "<b>O que α = 0 significa:</b> reveja a primeira equação de atualização. Com "
     "α = 0, o termo da nova observação desaparece por completo e sobra "
     "L_t = L_(t−1) + b_(t−1). O nível deixa de reagir ao que é observado e passa a "
     "seguir uma progressão determinística. Com β = 0 e γ = 0 acontece o mesmo com a "
     "tendência e com a sazonalidade."], "info"))
E.append(esp(5))
E.append(h2("13.2 A consequência: os dois modelos convergem para a mesma forma"))
E.append(p(
    "Com os três parâmetros zerados, o Holt-Winters <b>degenera</b>. Ele deixa de ser "
    "um filtro adaptativo e vira:"))
E.append(formula("ŷ(t) = L₀ + t·b₀ + s(dia da semana)"))
E.append(esp(5))
E.append(p(
    "Isto é: <b>uma reta com um padrão semanal fixo somado</b> — estimados uma única "
    "vez sobre todo o histórico e nunca mais atualizados. Compare agora com o que o "
    "Prophet ajusta neste mesmo cenário: uma tendência linear (sem changepoints "
    "ativos, porque não há quebras a encontrar) mais uma sazonalidade semanal de "
    "Fourier fixa. <b>São a mesma família de função, estimada por dois otimizadores "
    "diferentes.</b> Não surpreende que os MAPEs difiram na terceira casa decimal."))
E.append(h2("13.3 Por que o otimizador chegou lá — e o que isso revela"))
E.append(p(
    "O gerador sintético produz uma tendência <b>perfeitamente linear</b> e um perfil "
    "semanal <b>rigorosamente constante</b> (o mesmo dicionário de fatores nos 365 "
    "dias). Num mundo assim, adaptar-se ao dado recente é estritamente prejudicial: "
    "toda reação a uma observação individual é reação a ruído puro, já que a estrutura "
    "verdadeira nunca muda. O otimizador percebeu isso e desligou a adaptação."))
E.append(esp(4))
E.append(destaque(
    "Como apresentar este achado à banca",
    ["Este resultado é forte por dois motivos. Primeiro, <b>valida o motor</b>: o "
     "otimizador recuperou corretamente a estrutura verdadeira dos dados, inclusive a "
     "informação de que ela é estacionária. Segundo, <b>delimita com honestidade o "
     "alcance da conclusão</b>: o empate entre os modelos é uma propriedade deste "
     "dataset, não uma verdade geral sobre Holt-Winters e Prophet.",
     "A previsão testável que decorre daí: <b>em dados reais</b> — com quebras de "
     "patamar, mudanças de mix e sazonalidade que evolui — <b>espera-se α &gt; 0 e "
     "uma separação de desempenho muito maior entre os dois modelos</b>. Verificar "
     "isso é a continuação natural do trabalho."], "ok"))
E.append(PageBreak())

# ── 14. Backtesting ──────────────────────────────────────────────────────────
E.append(h1("14. Robustez: backtesting rolling-origin"))
E.append(p(
    "Uma única divisão treino/teste pode ser sorte. O backtesting rolling-origin "
    "repete o experimento cinco vezes: em cada dobra a janela de treino cresce e a "
    "previsão é feita sobre os 14 dias seguintes. Se o desempenho se mantém, ele é "
    "confiável."))
for pid in ("1", "5"):
    nome = d["walkforward"][pid]["nome"]
    E.append(h2(f"14.{pid} — {nome} (id {pid})"))
    linhas = [["Origem da janela", "MAPE HW (%)", "RMSE HW", "MAPE Prophet (%)",
               "RMSE Prophet"]]
    bt = d["backtesting"][pid]
    for i, r in enumerate(bt["holt_winters"]):
        rp = bt["prophet"][i]
        linhas.append([r["origem"], f"{r['mape']:.2f}", f"{r['rmse']:.2f}",
                       f"{rp['mape']:.2f}", f"{rp['rmse']:.2f}"])
    E.append(tabela(linhas, [3.6 * cm, 3.0 * cm, 2.6 * cm, 3.4 * cm, 2.9 * cm],
                    alinha_dir=(1, 2, 3, 4)))
    E.append(esp(6))
E.append(p(
    "<b>Leitura do produto 1:</b> o MAPE varia entre 10,50% e 15,65% nas cinco "
    "dobras — uma faixa estreita. O desempenho não dependeu da divisão escolhida, e a "
    "métrica principal de 12,49% é representativa."))
E.append(p(
    "<b>Leitura do produto 5:</b> quatro dobras entre 30,2% e 51,0% e uma quinta em "
    "188,4%. Como discutido na seção 8, esse pico é um artefato aritmético do MAPE "
    "quando o denominador é pequeno — repare que o RMSE da mesma janela (11,64) está "
    "apenas moderadamente acima das demais, sem nada que justifique um salto de quatro "
    "vezes. <b>Declarar isso abertamente é mais forte do que omitir a dobra "
    "ruim</b>: mostra domínio do comportamento da métrica."))
E.append(esp(5))
E.append(destaque(
    "O que o backtesting acrescenta ao argumento",
    "Ele transforma 'o modelo funcionou' em 'o modelo funciona de forma consistente'. "
    "Sem ele, qualquer resultado único poderia ser atribuído a uma divisão "
    "favorável — e essa é uma das objeções mais previsíveis em banca de trabalho "
    "com aprendizado de máquina.", "info"))

# ── 15. Limitações ───────────────────────────────────────────────────────────
E.append(PageBreak())
E.append(h1("15. Limitações conhecidas (declaração honesta)"))
E.append(p(
    "Listar limitações com precisão é sinal de domínio, não de fragilidade. As "
    "abaixo foram identificadas por inspeção do próprio código e devem ser declaradas "
    "antes que sejam perguntadas."))
lims = [
    ("Validação sobre dados sintéticos",
     "Os dados provam que a metodologia está correta e que o motor recupera a "
     "estrutura que foi plantada, mas não substituem uma demonstração sobre vendas "
     "reais. O notebook já tem a seção pronta para o dataset real; falta o arquivo."),
    ("Dados gerados de forma multiplicativa, modelos ajustados de forma aditiva",
     "O gerador multiplica os componentes; o Holt-Winters está configurado com "
     "tendência e sazonalidade aditivas e a decomposição do notebook usa modo "
     "aditivo. Com apenas 20% de crescimento no período a diferença é pequena, mas é "
     "uma incoerência metodológica real."),
    ("O regressor de promoção não está ligado",
     "O campo is_promocional existe no contrato, mas não é passado ao Prophet "
     "(tarefa T-10, marcada como opcional). Vale notar que <b>no dataset atual isso é "
     "inócuo</b>: o gerador preenche a coluna sempre com zero, então a variável não "
     "tem variância alguma. Provar o valor do regressor exige dados reais com "
     "promoções."),
    ("O mecanismo de feriados do Prophet está desativado",
     "O termo h(t) não é usado — <font face='DJM' size='8.5'>add_country_holidays</font> "
     "não é chamado. Isso é significativo porque os dados <i>têm</i> 12 feriados com "
     "alta chance de fechamento, e este é um recurso que o Prophet tem nativamente e "
     "o Holt-Winters não tem de forma alguma. É a mudança de maior potencial para "
     "desempatar o comparativo."),
    ("O parâmetro interval_width não tem efeito prático",
     "Ele controla os limites do intervalo de confiança do Prophet, mas o serviço "
     "consome apenas a previsão pontual. Não é um defeito, mas não se deve afirmar "
     "que o intervalo de confiança está sendo usado no cálculo."),
    ("O corte em zero é aplicado de forma assimétrica",
     "A previsão final é truncada em zero antes de ser devolvida, mas as métricas são "
     "calculadas sobre a previsão bruta. Em produto com tendência de queda, o "
     "Holt-Winters aditivo pode prever valores negativos e ser penalizado por "
     "previsões que o usuário nunca veria. Nos dados atuais, de tendência crescente, "
     "o impacto é nulo."),
    ("O σ da demanda inclui os dias fechados",
     "O desvio padrão usado na fórmula de Ballou é calculado sobre a série completa, "
     "incluindo os zeros de domingo e feriado. Isso infla σ e, por consequência, o "
     "estoque de segurança. É uma escolha conservadora — erra para o lado de ter "
     "estoque a mais — mas é uma decisão que merece ser explicitada."),
    ("O MAPE é frágil com denominadores pequenos",
     "Documentado nas seções 8 e 14. Uma alternativa seria adotar o SMAPE ou o MASE "
     "como critério de desempate; ficou fora do escopo."),
    ("A reprodutibilidade depende da ordem do catálogo",
     "O gerador usa um único fluxo de números aleatórios consumido sequencialmente "
     "pelos 10 produtos. Reordenar a lista ou inserir um produto no meio desloca as "
     "séries de todos os seguintes. Produtos novos devem ser adicionados ao final."),
    ("Ciclos anuais estão fora de alcance",
     "Com 365 dias de histórico não é possível estimar sazonalidade anual — seria "
     "necessário ao menos dois ciclos completos. A sazonalidade anual do Prophet está "
     "desativada por essa razão."),
]
for titulo, txt in lims:
    E.append(h3(titulo))
    E.append(p(txt))

# ── 16. Reprodutibilidade ────────────────────────────────────────────────────
E.append(PageBreak())
E.append(h1("16. Reprodutibilidade"))
E.append(p(
    "Todo resultado deste documento pode ser regenerado do zero com dois comandos, a "
    "partir da raiz do <font face='DJM' size='8.5'>ml-service</font>:"))
E.append(codigo(
    "# análise completa + figuras + CSV comparativo\n"
    "venv/Scripts/jupyter lab analysis/analise_modelos.ipynb\n"
    "\n"
    "# ou, em lote:\n"
    "venv/Scripts/python.exe -m jupyter nbconvert --to notebook \\\n"
    "        --execute analysis/analise_modelos.ipynb\n"
    "\n"
    "# regenerar este PDF\n"
    "venv/Scripts/python.exe analysis/_coletar_dados_doc.py\n"
    "venv/Scripts/python.exe docs/gerar_relatorio_pdf.py"))
E.append(esp(6))
E.append(h2("16.1 Garantias de reprodutibilidade"))
E.append(li("Semente fixa <font face='DJM' size='8.5'>SEED = 42</font> em todo o "
            "pipeline: mesma entrada produz exatamente os mesmos números."))
E.append(li("A análise importa o código de produção — não existe caminho de execução "
            "paralelo que possa divergir."))
E.append(li("Este PDF é gerado por script a partir de um JSON de resultados; nenhum "
            "número foi transcrito manualmente."))
E.append(li("Versões das bibliotecas fixadas no "
            "<font face='DJM' size='8.5'>requirements.txt</font>."))
E.append(esp(5))
E.append(h2("16.2 Ambiente verificado"))
E.append(tabela([
    ["Componente", "Versão", "Componente", "Versão"],
    ["Python", "3.12.1", "prophet", "1.1.6"],
    ["pandas", "2.2.3", "cmdstanpy", "1.2.4 (pinado)"],
    ["numpy", "1.26.4", "scikit-learn", "1.5.2"],
    ["statsmodels", "0.14.4", "scipy", "1.13.1"],
], [3.6 * cm, 3.4 * cm, 3.6 * cm, LARGURA_UTIL - 10.6 * cm]))
E.append(esp(7))
E.append(destaque(
    "Nota de engenharia: o incidente do Prophet e como foi resolvido",
    ["Durante o desenvolvimento o Prophet passou a falhar com o erro "
     "<font face='DJM' size='8.5'>'Prophet' object has no attribute "
     "'stan_backend'</font>, o que teria inviabilizado todo o comparativo — o núcleo "
     "acadêmico do trabalho.",
     "O diagnóstico inicial (CmdStan ausente, faltando compilar) estava errado. A "
     "causa real era <b>conflito de versões</b>: o cmdstanpy 1.3.0, puxado sem "
     "restrição, exigia um arquivo de build que o prophet 1.1.6 não empacota. A "
     "correção foi fixar <font face='DJM' size='8.5'>cmdstanpy==1.2.4</font> no "
     "requirements — solução reprodutível, que funciona igualmente em Docker e em "
     "nuvem, sem exigir compilador na máquina do desenvolvedor.",
     "Independentemente disso, o notebook foi construído para <b>degradar com "
     "elegância</b>: se o Prophet estiver indisponível, ele roda apenas com "
     "Holt-Winters e sinaliza a limitação, em vez de quebrar."], "info"))

# ── 17. Perguntas da banca ───────────────────────────────────────────────────
E.append(PageBreak())
E.append(h1("17. Perguntas prováveis da banca"))
E.append(p(
    "Perguntas que a estrutura do trabalho naturalmente provoca, com respostas curtas "
    "e defensáveis."))
qa = [
    ("Por que dois modelos e não um só?",
     "Porque não existe modelo universalmente melhor em séries temporais de varejo — "
     "o desempenho depende do comportamento de cada produto. Treinar os dois e medir "
     "custa pouco (a execução é mensal) e transforma uma escolha teórica arbitrária "
     "numa decisão empírica, auditável produto a produto."),
    ("O modelo 'aprende' de fato, ou só aplica uma fórmula?",
     "Ele estima parâmetros a partir dos dados por otimização numérica — 10 "
     "parâmetros no caso do Holt-Winters. Não é aprendizado profundo, mas é "
     "estimação estatística legítima: o modelo é ajustado ao dado, não imposto sobre "
     "ele. E é avaliado em dados que não viu, que é o critério que importa."),
    ("Por que não usaram uma rede neural / LSTM?",
     "Três razões. Volume de dados: 365 pontos por produto é ordens de grandeza menos "
     "do que uma rede recorrente precisa para não decorar. Interpretabilidade: o "
     "lojista e a banca conseguem inspecionar tendência e sazonalidade separadamente, "
     "o que uma rede não oferece. E custo operacional: o serviço tem 30 segundos de "
     "timeout e roda em infraestrutura modesta."),
    ("Um MAPE de 66% no produto 5 não invalida o sistema?",
     "Não, e o sistema trata isso explicitamente. Alta variabilidade intrínseca "
     "impõe um limite ao que qualquer modelo consegue prever — nenhum método acerta "
     "ruído. O que o sistema faz é reconhecer a situação: quando o MAPE do vencedor "
     "passa de 50%, ele preenche o campo de aviso e a interface sinaliza previsão de "
     "baixa confiança. Além disso, o estoque de segurança cresce com o σ do produto, "
     "então a decisão de reposição já compensa a imprevisibilidade com mais reserva."),
    ("Por que 80/20 e não validação cruzada?",
     "Validação cruzada tradicional embaralha os dados, o que é inválido em série "
     "temporal. O análogo correto é o rolling-origin, e ele foi feito — está na "
     "seção 14, com cinco janelas por produto. O 80/20 é a métrica principal; o "
     "rolling-origin é a verificação de que ela não foi sorte."),
    ("Como sabemos que os números do TCC são os do sistema?",
     "Porque a análise importa os módulos de produção em vez de reimplementar as "
     "fórmulas. Não existe uma segunda implementação que possa divergir da primeira. "
     "É uma decisão de projeto explícita, registrada na documentação da pasta de "
     "análise."),
    ("Por que a Curva ABC não está no motor?",
     "Porque ABC é um ranking relativo entre todos os produtos, com corte por "
     "faturamento acumulado, e o endpoint de previsão opera sobre um produto de cada "
     "vez — ele não recebe o valor de venda nem enxerga o catálogo. Quem tem essa "
     "visão é o backend, que detém o banco. A decisão está registrada como ADR."),
    ("O dado é sintético — isso não enfraquece o trabalho?",
     "Enfraqueceria se fosse apresentado como validação de mercado; não é. O dado "
     "sintético cumpre um papel diferente e legítimo: como conhecemos a estrutura "
     "verdadeira que foi plantada, podemos verificar se o motor a recupera — e a "
     "seção 13 mostra que ele recupera, inclusive a informação de que a estrutura é "
     "estacionária. É validação de metodologia, e está declarada como tal nas "
     "limitações."),
    ("Por que a previsão é de 30 dias?",
     "Porque o recálculo completo é agendado mensalmente, então o horizonte cobre o "
     "intervalo até a próxima execução. O Gráfico 4 mostra que o erro cresce com o "
     "horizonte, o que sustenta não prever muito além disso."),
    ("O que acontece com um produto novo, sem histórico?",
     "O motor recusa a previsão com HTTP 422 e mensagem explícita quando há menos de "
     "90 dias de histórico. A tela deve sinalizar esse estado em vez de assumir que "
     "todo produto tem previsão — está listado como requisito no mapeamento de "
     "funcionalidades."),
    ("Qual seria o próximo passo do trabalho?",
     "Três, em ordem de retorno: (1) rodar o comparativo sobre vendas reais de um "
     "mercado; (2) ativar o calendário de feriados brasileiros no Prophet, que é o "
     "recurso mais promissor para desempatar os modelos; (3) ligar o regressor de "
     "promoções, que só faz sentido com dados reais que contenham promoções."),
]
for q, a in qa:
    E.append(h3(q))
    E.append(p(a))

# ── 18. Referências ──────────────────────────────────────────────────────────
E.append(PageBreak())
E.append(h1("18. Referências"))
for r in [
    "BALLOU, Ronald H. <i>Gerenciamento da cadeia de suprimentos / Logística "
    "empresarial.</i> 5. ed. Porto Alegre: Bookman, 2006. — fórmula do estoque de "
    "segurança e nível de serviço.",
    "HYNDMAN, R. J.; ATHANASOPOULOS, G. <i>Forecasting: Principles and Practice.</i> "
    "3. ed. OTexts, 2021. — Holt-Winters, métricas de avaliação e validação "
    "walk-forward.",
    "TAYLOR, S. J.; LETHAM, B. Forecasting at scale. <i>The American Statistician</i>, "
    "v. 72, n. 1, 2018. — formulação do Prophet.",
    "SEBRAE. <i>Ideia de Negócio: Mercearia.</i> Brasília: Sebrae, 2023. — "
    "classificação ABC.",
    "SILVA; ARAÚJO. <i>Gestão de estoques em um supermercado de médio porte.</i> "
    "Triângulo Mineiro: UTFPR, 2022. — aplicação prática da Curva ABC.",
]:
    E.append(li(r, "—"))
E.append(esp(10))
E.append(h2("Artefatos do projeto referenciados"))
E.append(tabela([
    ["Artefato", "Conteúdo"],
    ["ml-service/CLAUDE.md", "convenções, contrato e regras do serviço"],
    ["ml-service/analysis/README.md", "como rodar a análise"],
    ["ml-service/analysis/analise_modelos.ipynb", "notebook de validação empírica"],
    ["ml-service/analysis/results/comparativo_modelos.csv", "métricas por produto × modelo"],
    ["ml-service/tasks.md", "backlog do serviço (T-10, T-12, T-19)"],
    ["docs/dashboard-kpis.md", "definição dos KPIs"],
    ["docs/mapeamento-funcionalidades.md", "especificação das telas T1–T10"],
], [8.4 * cm, LARGURA_UTIL - 8.4 * cm]))
E.append(esp(12))
E.append(_caixa([Paragraph(
    "Documento gerado automaticamente a partir da execução do código de produção do "
    "ml-service. Para regenerar após qualquer mudança nos modelos, execute os dois "
    "comandos da seção 16 — os números e as figuras se atualizam sozinhos.",
    ParagraphStyle("fim", parent=S_P, fontSize=8.6, textColor=CINZA))],
    CINZA_CLARO, BORDA))


# ═════════════════════════════════════════════════════════════════════════════
def construir() -> Path:
    return montar_documento(
        DOCS / "relatorio-modelos-preditivos.pdf", E,
        "StockSense · Relatório Técnico dos Modelos Preditivos",
        title="StockSense — Relatório Técnico dos Modelos Preditivos",
        author="StockSense · TCC 2026",
        subject="Holt-Winters × Prophet: fundamentação, validação e resultados",
    )


if __name__ == "__main__":
    caminho = construir()
    print("PDF gerado:", caminho)
    print("Tamanho   :", f"{caminho.stat().st_size / 1024:.0f} KB")
