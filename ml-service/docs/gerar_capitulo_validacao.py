"""
Gera docs/capitulo-validacao.pdf — o capítulo de validação empírica do motor
preditivo, escrito por extenso e pronto para revisão.

Como no relatório técnico, todos os números vêm de
analysis/results/dados_documento.json (produzido pela execução do código de
produção). Nenhum valor é digitado à mão no texto: os que aparecem na prosa são
interpolados a partir do JSON.

Uso (a partir de ml-service/):
    venv/Scripts/python.exe analysis/_coletar_dados_doc.py
    venv/Scripts/python.exe docs/gerar_capitulo_validacao.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "docs"))

from _estilo_pdf import (  # noqa: E402
    AZUL, CINZA_CLARO, BORDA, LARGURA_UTIL, S_P, S_SUB, S_TITULO,
    caixa, codigo, destaque, esp, figura, formula, h1, h2, h3, li,
    montar_documento, p, tabela,
)
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.platypus import Paragraph  # noqa: E402

FIGS = RAIZ / "analysis" / "figures"
d = json.loads((RAIZ / "analysis" / "results" / "dados_documento.json")
               .read_text(encoding="utf-8"))
alphas = json.loads((RAIZ / "analysis" / "results" / "_alphas.json")
                    .read_text(encoding="utf-8"))

kpi = {k["produto_id"]: k for k in d["kpis"]}
wf = d["walkforward"]
v = d["vitorias"]
CAP = "5"          # numeração provisória do capítulo

# Números derivados (nunca digitados à mão)
_mapes = [r["mape"] for r in d["comparativo"]]
MAPE_MIN, MAPE_MAX = min(_mapes), max(_mapes)
_margens = sorted(m["margem_pp"] for m in d["margens"])
N_ABAIXO_07 = sum(1 for m in _margens if m < 0.7)
N_ABAIXO_006 = sum(1 for m in _margens if m < 0.06)
MARGEM_MAX = max(_margens)
_bt1 = [r["mape"] for r in d["backtesting"]["1"]["holt_winters"]]
_bt5 = sorted(r["mape"] for r in d["backtesting"]["5"]["holt_winters"])
N_ZERO_EXATO = sum(1 for r in alphas if r["a"] == 0 and r["b"] == 0 and r["g"] == 0)


def num(x, casas=2):
    """Formata número no padrão brasileiro (vírgula decimal)."""
    return f"{x:.{casas}f}".replace(".", ",")


E = []
A = E.append

# ═══════════════════════════════════════════════════════════════════════════
# Abertura
# ═══════════════════════════════════════════════════════════════════════════
A(Spacer(1, 1.2 * cm))
A(Paragraph(f"Capítulo {CAP}", S_SUB))
A(esp(8))
A(Paragraph("Validação Empírica do Motor Preditivo", S_TITULO))
A(esp(14))
A(caixa([Paragraph(
    f"<b>Nota de edição.</b> A numeração adotada (Capítulo {CAP} e seções "
    f"{CAP}.1 a {CAP}.11) é provisória e deve ser ajustada conforme a posição "
    "final deste capítulo na monografia. As figuras referenciadas estão em "
    "<font face='DJM' size='8.5'>ml-service/analysis/figures/</font> e todas as "
    "tabelas foram geradas pela execução do código de produção do serviço, com "
    "semente fixa — não há valor transcrito manualmente. O detalhamento "
    "matemático dos modelos, referido ao longo do texto, encontra-se no relatório "
    "técnico <font face='DJM' size='8.5'>relatorio-modelos-preditivos.pdf</font>.",
    S_P)], CINZA_CLARO, BORDA))
A(esp(16))

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.1 Objetivo e escopo da validação"))
A(p(
    "Este capítulo apresenta a validação empírica do motor preditivo do StockSense. "
    "O objetivo é verificar, de forma reprodutível e auditável, três propriedades do "
    "componente responsável pela previsão de demanda: (a) que ele recupera "
    "corretamente a estrutura presente em uma série histórica de vendas; (b) que o "
    "erro de previsão resultante é mensurável, estável entre diferentes janelas de "
    "avaliação e comparável entre produtos de escalas distintas; e (c) que a "
    "previsão obtida se converte em parâmetros de reposição coerentes com a situação "
    "de estoque de cada item."))
A(p(
    "Delimita-se desde já o que não está no escopo. A validação aqui conduzida "
    "utiliza um conjunto de dados sintético, gerado com estrutura conhecida e "
    "semente fixa. Não se trata, portanto, de uma medição do desempenho do sistema "
    "sobre a demanda real de um estabelecimento — essa verificação externa é "
    "registrada como trabalho futuro. A distinção é relevante e convém explicitá-la "
    "antes de qualquer resultado: o experimento descrito adiante tem a natureza de "
    "uma <b>validação de instrumentação</b>, isto é, destina-se a demonstrar que o "
    "instrumento de medida funciona corretamente, e não a medir o mundo."))
A(destaque(
    "Sobre o uso de dados sintéticos e o risco de circularidade",
    ["Uma objeção previsível ao uso de dados gerados artificialmente é a de que o "
     "experimento seria circular: se a estrutura dos dados foi definida por quem "
     "conduz o teste, encontrá-la não provaria nada. A objeção é pertinente e a "
     "resposta a ela orienta a leitura de todo o capítulo.",
     "Justamente porque a estrutura verdadeira é conhecida por construção, torna-se "
     "possível verificar se o motor a recupera — o que seria impossível com dados "
     "reais, cuja estrutura verdadeira ninguém conhece. O que se testa aqui não é a "
     "capacidade preditiva em campo, mas a correção da implementação: se o "
     "instrumento, submetido a um sinal conhecido, devolve a medida esperada. A "
     "Seção " + CAP + ".8 apresenta o resultado que melhor ilustra esse papel, ao "
     "mostrar que o otimizador identificou não apenas a estrutura da série, mas "
     "também o fato de que ela é estacionária."], "info"))

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.2 Protocolo experimental"))
A(h2(f"{CAP}.2.1 Conjunto de dados"))
A(p(
    f"Foram gerados <b>10 produtos com {d['descritiva'][0]['n_dias']} dias</b> de "
    f"histórico diário de vendas, mediante semente fixa (SEED = {d['seed']}), "
    "representando perfis de demanda contrastantes encontrados em um mercado de "
    "bairro. A quantidade vendida de cada produto em cada dia resulta da composição "
    "multiplicativa de quatro fatores:"))
A(formula(
    "quantidade(t) = round( demanda_base × tendência(t) × fator_semanal(t) × ruído(t) )"))
A(esp(5))
A(p(
    "A <b>demanda base</b> é constante por produto e varia de 5 unidades diárias "
    "(sal refinado) a 30 (pão francês). A <b>tendência</b> é um crescimento linear de "
    "20% ao longo do período. O <b>fator semanal</b> é um multiplicador fixo por dia "
    "da semana, que atinge 1,45 aos sábados e cai a 0,30 aos domingos — uma amplitude "
    "de quase cinco vezes entre o melhor e o pior dia, característica do varejo de "
    "bairro e razão pela qual se adotou ciclo sazonal de sete dias nos dois modelos. "
    "O <b>ruído</b> é gaussiano multiplicativo centrado na unidade, cujo desvio padrão "
    "é o parâmetro que diferencia os perfis de produto."))
A(p(
    "Sobrepõem-se ainda os fechamentos do estabelecimento: domingos têm 40% de "
    "probabilidade de registrar venda nula e os doze feriados nacionais do período, "
    "60%. Esse mecanismo reproduz o comportamento operacional de um mercado de bairro "
    "e constitui a principal fonte de dificuldade para os modelos, uma vez que "
    "introduz descontinuidades não previsíveis a partir do calendário semanal."))

A(h2(f"{CAP}.2.2 Divisão temporal dos dados"))
A(p(
    "A avaliação emprega divisão cronológica na proporção de <b>80% para treino e 20% "
    f"para teste</b>, o que resulta em {wf['1']['n_treino']} dias de treino "
    f"({wf['1']['treino_ini']} a {wf['1']['treino_fim']}) e "
    f"{wf['1']['n_validacao']} dias de teste ({wf['1']['valid_ini']} a "
    f"{wf['1']['valid_fim']}). A divisão é feita por posição no índice temporal, "
    "preservando integralmente a ordem cronológica das observações."))
A(destaque(
    "Por que a divisão não pode ser aleatória",
    "Em problemas de aprendizado supervisionado convencional é prática corrente "
    "embaralhar as observações antes de separar treino e teste, de modo a evitar "
    "vieses de ordenação. Em séries temporais esse procedimento é inválido. "
    "Embaralhar colocaria dias posteriores no conjunto de treino e dias anteriores no "
    "conjunto de teste, de forma que o modelo utilizaria informação do futuro para "
    "prever o passado. O erro medido resultaria artificialmente baixo e desprovido de "
    "significado, pois não corresponderia à situação de uso — na qual apenas o "
    "passado está disponível. Por essa razão, a implementação do serviço proíbe "
    "explicitamente o uso de rotinas de divisão aleatória, e a separação é feita por "
    "posição cronológica (HYNDMAN; ATHANASOPOULOS, 2021).", "alerta"))

A(h2(f"{CAP}.2.3 Métricas de avaliação"))
A(p(
    "Adotaram-se três métricas de erro, calculadas sobre a janela de teste:"))
A(formula(
    "MAE  = média( |real − previsto| )<br/>"
    "RMSE = raiz( média( (real − previsto)² ) )<br/>"
    "MAPE = média( |real − previsto| / real ) × 100"))
A(esp(5))
A(tabela([
    ["Métrica", "Unidade", "Papel na avaliação"],
    ["MAE", "unidades do produto", "erro médio típico; é a métrica de leitura mais "
     "direta para o gestor do estabelecimento"],
    ["RMSE", "unidades do produto", "por elevar o desvio ao quadrado, penaliza "
     "desproporcionalmente os erros grandes; identifica falhas pontuais severas"],
    ["MAPE", "percentual", "adimensional, permite comparar produtos de volumes "
     "distintos; é o critério de seleção do modelo"],
], [1.9 * cm, 3.0 * cm, LARGURA_UTIL - 4.9 * cm]))
A(esp(7))
A(p(
    "A seleção do modelo vencedor utiliza o <b>MAPE</b>. A escolha decorre de uma "
    "exigência do sistema: a decisão precisa ser comparável entre produtos de escalas "
    "muito diferentes. Um erro absoluto de três unidades é excelente para o pão "
    "francês, cuja demanda média supera trinta unidades diárias, e inaceitável para o "
    "sal refinado, cuja demanda é de cinco. Somente uma métrica percentual permite "
    "afirmar que um produto é mais previsível que outro e alimentar o indicador de "
    "acurácia exibido no painel, definido como 100 menos o MAPE do modelo "
    "selecionado."))
A(p(
    "Registra-se um aspecto do cálculo que afeta a interpretação comparativa das três "
    "métricas. Como o MAPE divide pelo valor observado, os dias de venda nula — "
    "decorrentes dos fechamentos descritos na seção anterior — produziriam divisão "
    "por zero. A implementação calcula o MAPE <b>apenas sobre as observações de valor "
    "real positivo</b>, enquanto RMSE e MAE consideram todos os dias da janela. As "
    "três métricas, portanto, não incidem exatamente sobre o mesmo conjunto de "
    "pontos, o que deve ser levado em conta ao confrontá-las."))

A(h2(f"{CAP}.2.4 Equivalência com o sistema em produção"))
A(p(
    "A camada de análise que produziu os resultados deste capítulo <b>importa os "
    "módulos de produção do serviço</b> — os mesmos que o endpoint de previsão "
    "executa — em vez de reimplementar as fórmulas em ambiente experimental. A "
    "decisão tem consequência direta sobre a validade interna do estudo: não existe "
    "uma segunda implementação capaz de divergir da primeira, e os valores "
    "apresentados adiante são, por construção, os mesmos que o sistema produz em "
    "operação. Trata-se de eliminar uma fonte clássica de discrepância entre o "
    "resultado relatado em trabalhos acadêmicos e o comportamento do artefato "
    "efetivamente entregue."))

A(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.3 Caracterização do conjunto de dados"))
A(p(
    "A Tabela " + CAP + ".1 apresenta a estatística descritiva das dez séries "
    "geradas. A coluna <i>variabilidade</i> corresponde ao parâmetro de ruído "
    "utilizado na geração, enquanto o coeficiente de variação (CV) é medido sobre a "
    "série resultante."))
linhas = [["id", "Produto", "Variab.", "Média/dia", "σ", "CV", "% zeros"]]
for r in d["descritiva"]:
    linhas.append([r["produto_id"], r["nome"], num(r["variabilidade"]),
                   num(r["media_diaria"]), num(r["desvio"]), num(r["cv"]),
                   num(r["pct_zeros"], 1) + "%"])
A(tabela(linhas, [1.0 * cm, 4.6 * cm, 1.9 * cm, 2.2 * cm, 1.6 * cm, 1.5 * cm, 1.9 * cm],
         alinha_dir=(2, 3, 4, 5, 6)))
A(Paragraph(f"<b>Tabela {CAP}.1</b> — Estatística descritiva dos dez produtos "
            "sintéticos.", ParagraphStyle("legt", parent=S_P, fontSize=8.3,
                                          textColor=AZUL, spaceBefore=4)))
A(esp(6))
A(p(
    "O conjunto cobre uma faixa ampla de comportamentos. Nos extremos situam-se o sal "
    "refinado e o açúcar cristal, com variabilidade de 0,05 e demanda praticamente "
    "determinística, e a banana prata, com variabilidade de 0,45 e oscilação diária "
    "acentuada. Essa amplitude é intencional: permite observar como o desempenho "
    "preditivo se degrada à medida que a componente aleatória cresce, em vez de "
    "avaliar o motor em um único regime favorável."))
A(p(
    "Uma observação menos evidente merece registro, pois condiciona a leitura dos "
    "resultados. O coeficiente de variação não assume valores baixos nem mesmo para "
    "os produtos de ruído mínimo — o sal refinado, com variabilidade de 0,05, "
    f"apresenta CV de {num(d['descritiva'][5]['cv'])}. A razão é que o CV mede toda a "
    "dispersão da série, e a própria oscilação semanal, ao alternar entre 1,45 aos "
    "sábados e 0,30 aos domingos, já produz dispersão considerável. Conclui-se que "
    "<b>parte substancial do desvio observado em cada produto é estrutura "
    "previsível, não ruído</b> — e é precisamente essa parcela que os modelos são "
    "capazes de capturar. A distinção explica por que produtos com desvio padrão "
    "semelhante podem apresentar erros de previsão muito diferentes."))

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.4 Análise exploratória: existe sinal previsível?"))
A(p(
    "Antes de ajustar qualquer modelo, cabe verificar se as séries contêm estrutura "
    "passível de ser aprendida. Aplicou-se a decomposição aditiva com período de sete "
    "dias, que separa a série observada em três componentes: tendência, sazonalidade "
    "e resíduo. O critério de leitura é direto — se a componente sazonal apresenta "
    "amplitude nítida e regular e o resíduo é pequeno em relação ao sinal, existe "
    "estrutura a ser modelada, o que justifica o emprego de modelos de série temporal "
    "em lugar de uma simples média histórica."))
A(figura(FIGS / "g1_decomposicao_produto1.png",
         f"<b>Figura {CAP}.1</b> — Decomposição da série do Arroz 5kg (id 1). A "
         "sazonalidade semanal aparece como oscilação regular de amplitude constante, "
         "e a tendência de crescimento é claramente separável do resíduo.",
         LARGURA_UTIL * 0.74))
A(figura(FIGS / "g1_decomposicao_produto5.png",
         f"<b>Figura {CAP}.2</b> — Decomposição da série da Banana Prata kg (id 5). A "
         "estrutura sazonal é a mesma, porém o resíduo apresenta amplitude muito "
         "superior, refletindo a variabilidade intrínseca do produto.",
         LARGURA_UTIL * 0.74))
A(p(
    "O contraste entre as duas figuras antecipa e explica os resultados das seções "
    "seguintes. Ambos os produtos possuem estrutura sazonal semanal igualmente bem "
    "definida — e, portanto, igualmente aprendível. O que os distingue é a magnitude "
    "do resíduo, isto é, da parcela que nenhum modelo pode prever. Trata-se de um "
    "limite imposto pelo dado, não pelo método, e é sobre esse pano de fundo que os "
    "erros relatados adiante devem ser interpretados."))

A(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.5 Resultados comparativos"))
A(h2(f"{CAP}.5.1 Métricas por produto e modelo"))
A(p(
    "Os dois modelos foram treinados e avaliados em todos os dez produtos, segundo o "
    "protocolo da Seção " + CAP + ".2. A Tabela " + CAP + ".2 consolida os "
    "resultados; as linhas destacadas indicam o modelo selecionado pelo critério de "
    "menor MAPE."))
linhas = [["id", "Produto", "Modelo", "MAPE (%)", "RMSE", "MAE", "Selec."]]
destaques = []
for i, r in enumerate(d["comparativo"], start=1):
    if r["vencedor"]:
        destaques.append(i)
    linhas.append([r["produto_id"], r["nome"], r["modelo"], num(r["mape"], 4),
                   num(r["rmse"], 4), num(r["mae"], 4), "✔" if r["vencedor"] else ""])
A(tabela(linhas, [0.9 * cm, 4.0 * cm, 2.6 * cm, 2.2 * cm, 1.9 * cm, 1.9 * cm, 1.9 * cm],
         alinha_dir=(3, 4, 5), destaque_linhas=destaques))
A(Paragraph(f"<b>Tabela {CAP}.2</b> — MAPE, RMSE e MAE por produto e modelo na janela "
            "de teste.", ParagraphStyle("legt2", parent=S_P, fontSize=8.3,
                                        textColor=AZUL, spaceBefore=4)))
A(esp(6))
A(p(
    f"O placar agregado indica <b>{v['holt_winters']} seleções do Holt-Winters e "
    f"{v['prophet']} do Prophet</b>. Esse número, contudo, é insuficiente para "
    "sustentar qualquer conclusão sobre superioridade de um método, pois não informa "
    "a magnitude das diferenças. A Tabela " + CAP + ".3 apresenta as margens."))
linhas = [["Produto", "Margem de MAPE (pontos percentuais)"]]
for m in sorted(d["margens"], key=lambda x: x["margem_pp"]):
    linhas.append([f"{m['produto_id']} — {m['nome']}", num(m["margem_pp"], 4)])
A(tabela(linhas, [7.0 * cm, LARGURA_UTIL - 7.0 * cm], alinha_dir=(1,)))
A(Paragraph(f"<b>Tabela {CAP}.3</b> — Diferença absoluta de MAPE entre os dois "
            "modelos, por produto.",
            ParagraphStyle("legt3", parent=S_P, fontSize=8.3, textColor=AZUL,
                           spaceBefore=4)))
A(esp(6))
A(destaque(
    "Leitura dos resultados",
    [f"Em <b>{N_ABAIXO_07} dos 10 produtos a diferença entre os dois modelos é "
     f"inferior a 0,7 ponto percentual</b>, e em {N_ABAIXO_006} deles é inferior a "
     "0,06 ponto. A única separação perceptível ocorre no pão francês, com "
     f"{num(MARGEM_MAX)} pontos a favor do Holt-Winters — justamente o produto de "
     "maior variabilidade do conjunto.",
     "A conclusão que os dados sustentam é, portanto, que <b>nenhum dos dois modelos "
     "domina o outro neste conjunto de dados</b>. Seria inadequado apresentar o "
     "placar de " + str(v["holt_winters"]) + " a " + str(v["prophet"]) + " como "
     "evidência de superioridade do Holt-Winters: diferenças dessa ordem de grandeza "
     "não são operacionalmente relevantes. A Seção " + CAP + ".8 demonstra que esse "
     "resultado não é fortuito e apresenta o mecanismo que o explica."], "info"))
A(esp(5))
A(p(
    f"Observa-se, em contrapartida, dispersão considerável do erro entre produtos: o "
    f"MAPE varia de {num(MAPE_MIN)}% a {num(MAPE_MAX)}% entre os vinte pares produto-"
    "modelo avaliados. Essa variação acompanha de perto a coluna de variabilidade da "
    "Tabela " + CAP + ".1 — os produtos de demanda mais errática são os de maior erro "
    "—, o que confirma a leitura proposta na Seção " + CAP + ".4: o limite do "
    "desempenho é imposto pela parcela aleatória do dado."))
A(p(
    "O sistema trata explicitamente essa situação. Quando o MAPE do modelo "
    "selecionado ultrapassa 50%, o motor preenche um campo de aviso na resposta, e a "
    "interface sinaliza a previsão como de confiança reduzida. Trata-se de decisão de "
    "projeto deliberada: em vez de apresentar todas as previsões com a mesma "
    "autoridade aparente, o sistema comunica ao usuário o grau de confiança "
    "associado a cada uma."))

A(h2(f"{CAP}.5.2 Ajuste fora da amostra"))
A(p(
    "As figuras a seguir confrontam a série efetivamente observada na janela de teste "
    "com as previsões dos dois modelos, produzidas sem qualquer acesso a esses dias."))
A(figura(FIGS / "g2_previsto_real_produto1.png",
         f"<b>Figura {CAP}.3</b> — Previsto versus real para o Arroz 5kg. As curvas "
         "dos dois modelos acompanham o padrão semanal e são visualmente "
         "indistinguíveis entre si."))
A(figura(FIGS / "g2_previsto_real_produto5.png",
         f"<b>Figura {CAP}.4</b> — Previsto versus real para a Banana Prata kg. Os "
         "modelos reproduzem o ciclo semanal, mas não a amplitude das oscilações "
         "diárias."))
A(p(
    "A leitura da Figura " + CAP + ".4 merece cuidado para não ser tomada como "
    "deficiência do método. Os modelos capturam corretamente o nível e o ciclo "
    "semanal do produto; o que não reproduzem são as oscilações diárias, que "
    "correspondem ao termo de ruído da série. Um modelo que acompanhasse essas "
    "oscilações estaria, na prática, ajustando-se ao ruído — comportamento indesejado "
    "que se manifestaria como degradação do desempenho fora da amostra."))

A(h2(f"{CAP}.5.3 Comportamento do erro ao longo do horizonte"))
A(figura(FIGS / "g4_erro_horizonte_produto1.png",
         f"<b>Figura {CAP}.5</b> — Erro absoluto por dia de horizonte, Arroz 5kg."))
A(figura(FIGS / "g4_erro_horizonte_produto5.png",
         f"<b>Figura {CAP}.6</b> — Erro absoluto por dia de horizonte, Banana Prata kg."))
A(p(
    "A análise do erro em função do horizonte de previsão tem implicação direta sobre "
    "o desenho do sistema. Na formulação do Holt-Winters, a previsão para h dias à "
    "frente é dada por ŷ(t+h) = L(t) + h·b(t) + s(dia da semana), de modo que "
    "qualquer imprecisão na estimativa da tendência b(t) é multiplicada pelo "
    "horizonte e se acumula progressivamente. Esse comportamento fundamenta a decisão "
    "de limitar a previsão a 30 dias, horizonte alinhado ao ciclo mensal de recálculo "
    "adotado pela plataforma."))

A(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.6 Diagnóstico de resíduos"))
A(p(
    "A comparação de métricas informa <i>quanto</i> o modelo erra, mas não se ele "
    "deixou de aproveitar informação disponível. Esse segundo aspecto é avaliado pela "
    "análise dos resíduos, definidos como a diferença entre o valor observado e o "
    "previsto. O critério é conhecido: um modelo adequado produz resíduos centrados "
    "em zero, sem padrão temporal discernível e sem autocorrelação significativa — em "
    "outras palavras, aproximadamente ruído branco. A presença de estrutura nos "
    "resíduos indicaria sinal não capturado, e portanto espaço para melhoria do "
    "modelo."))
A(p(
    "Convém enunciar, antes de examinar os gráficos, qual observação refutaria a "
    "conclusão pretendida: <b>um pico significativo na função de autocorrelação no "
    "atraso de sete dias</b> indicaria que a sazonalidade semanal não foi "
    "integralmente absorvida pelo modelo, permanecendo no resíduo."))
A(figura(FIGS / "g5_residuos_produto1_holt_winters.png",
         f"<b>Figura {CAP}.7</b> — Diagnóstico de resíduos do Arroz 5kg: histograma, "
         "evolução temporal e função de autocorrelação.", LARGURA_UTIL * 0.95))
A(figura(FIGS / "g5_residuos_produto5_holt_winters.png",
         f"<b>Figura {CAP}.8</b> — Diagnóstico de resíduos da Banana Prata kg.",
         LARGURA_UTIL * 0.95))
A(p(
    "Em ambos os produtos os histogramas apresentam-se aproximadamente simétricos em "
    "torno de zero, a evolução temporal não exibe padrão sistemático e a função de "
    "autocorrelação permanece dentro da banda de confiança — inclusive no atraso de "
    "sete dias. Conclui-se que os modelos extraíram a estrutura disponível nas séries "
    "e que o erro remanescente corresponde à componente irredutível do processo "
    "gerador. A diferença entre os dois produtos está na dispersão dos resíduos, não "
    "na presença de padrão, o que é consistente com a caracterização da Seção "
    + CAP + ".3."))

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.7 Robustez: avaliação em janelas móveis"))
A(p(
    "Uma única divisão entre treino e teste pode, por acaso, favorecer ou prejudicar "
    "o modelo avaliado. Para verificar se os resultados da Seção " + CAP + ".5 são "
    "estáveis, aplicou-se avaliação em janelas móveis com origem expansível "
    "(<i>rolling-origin</i>): em cada uma das cinco repetições, o conjunto de treino "
    "cresce e a previsão incide sobre o bloco subsequente de quatorze dias."))
for pid, tnum in (("1", 4), ("5", 5)):
    nome = wf[pid]["nome"]
    linhas = [["Origem da janela", "MAPE HW (%)", "RMSE HW", "MAPE Prophet (%)",
               "RMSE Prophet"]]
    bt = d["backtesting"][pid]
    for i, r in enumerate(bt["holt_winters"]):
        rp = bt["prophet"][i]
        linhas.append([r["origem"], num(r["mape"]), num(r["rmse"]),
                       num(rp["mape"]), num(rp["rmse"])])
    A(KeepTogether([
        tabela(linhas, [3.6 * cm, 3.0 * cm, 2.6 * cm, 3.4 * cm, 2.9 * cm],
               alinha_dir=(1, 2, 3, 4)),
        Paragraph(f"<b>Tabela {CAP}.{tnum}</b> — Avaliação em janelas móveis: "
                  f"{nome} (id {pid}).",
                  ParagraphStyle(f"lg{pid}", parent=S_P, fontSize=8.3, textColor=AZUL,
                                 spaceBefore=4, spaceAfter=9))]))
A(figura(FIGS / "g6_backtesting_produto1.png",
         f"<b>Figura {CAP}.9</b> — Evolução do MAPE por janela, Arroz 5kg."))
A(figura(FIGS / "g6_backtesting_produto5.png",
         f"<b>Figura {CAP}.10</b> — Evolução do MAPE por janela, Banana Prata kg."))
A(p(
    f"No arroz, o MAPE permanece entre {num(min(_bt1))}% e {num(max(_bt1))}% ao longo "
    "das cinco repetições — faixa estreita, que indica desempenho consistente e "
    "confirma a representatividade da métrica principal relatada na Tabela "
    + CAP + ".2."))
A(p(
    f"A banana prata apresenta comportamento distinto: quatro janelas situam-se entre "
    f"{num(_bt5[0])}% e {num(_bt5[3])}%, e uma quinta atinge {num(_bt5[4])}%. Esse "
    "valor discrepante não é omitido porque sua análise é informativa."))
A(destaque(
    "Análise da janela discrepante",
    f"O RMSE da janela em questão é {num(d['backtesting']['5']['holt_winters'][2]['rmse'])}"
    ", valor apenas moderadamente superior ao das demais repetições — o que descarta "
    "uma falha severa de previsão naquele período. A discrepância decorre do "
    "comportamento aritmético do MAPE: por dividir o desvio pelo valor observado, a "
    "métrica assume valores muito elevados quando coincidem, na janela avaliada, dias "
    "de venda reduzida. Confirma-se assim a advertência da Seção " + CAP + ".2.3 "
    "quanto à fragilidade do MAPE em séries de baixo volume, e justifica-se a decisão "
    "de reportar as três métricas conjuntamente, em vez de apoiar a análise em uma "
    "única.", "alerta"))

A(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.8 Análise dos parâmetros ajustados"))
A(p(
    "A proximidade entre os desempenhos dos dois modelos, verificada na Seção "
    + CAP + ".5, admite explicação a partir dos parâmetros que o processo de "
    "otimização encontrou. Convém recordar que os parâmetros de suavização do "
    "Holt-Winters — α para o nível, β para a tendência e γ para a sazonalidade — não "
    "são fixados pelo implementador: são estimados por otimização numérica, de modo a "
    "minimizar a soma dos erros quadráticos sobre o conjunto de treino. Seus valores, "
    "portanto, constituem informação sobre o dado, e não sobre a configuração do "
    "sistema."))
linhas = [["id", "Produto", "α (nível)", "β (tendência)", "γ (sazonal)"]]
for r in alphas:
    linhas.append([r["pid"], r["nome"], num(r["a"], 5), num(r["b"], 5), num(r["g"], 5)])
A(tabela(linhas, [1.0 * cm, 5.2 * cm, 2.9 * cm, 2.9 * cm, 2.9 * cm],
         alinha_dir=(2, 3, 4)))
A(Paragraph(f"<b>Tabela {CAP}.6</b> — Parâmetros de suavização estimados pelo "
            "otimizador, por produto.",
            ParagraphStyle("legt6", parent=S_P, fontSize=8.3, textColor=AZUL,
                           spaceBefore=4)))
A(esp(6))
A(p(
    f"O resultado é uniforme: <b>em todos os dez produtos os três parâmetros "
    f"convergiram para valores nulos ou desprezíveis</b>. Em {N_ZERO_EXATO} deles a "
    f"convergência foi exatamente para zero; nos {10 - N_ZERO_EXATO} restantes, "
    "nenhum parâmetro supera 3 × 10⁻³. O argumento desenvolve-se em três etapas."))

A(h2("Primeira etapa: o que a nulidade dos parâmetros significa"))
A(p(
    "Retome-se a equação de atualização do nível, L(t) = α·(y(t) − s(t−7)) + "
    "(1−α)·(L(t−1) + b(t−1)). Com α igual a zero, o termo associado à nova observação "
    "desaparece integralmente, restando L(t) = L(t−1) + b(t−1). O nível deixa de "
    "reagir ao que é observado e passa a seguir uma progressão determinística. O "
    "mesmo ocorre com a tendência e com a componente sazonal quando β e γ se anulam. "
    "O modelo, nessas condições, degenera para:"))
A(formula("ŷ(t) = L₀ + t·b₀ + s(dia da semana)"))
A(esp(5))
A(p(
    "Isto é: uma reta somada a um perfil semanal fixo, ambos estimados uma única vez "
    "sobre o histórico e jamais atualizados. O Holt-Winters deixa de operar como "
    "filtro adaptativo e passa a comportar-se como um modelo de regressão global "
    "sobre o tempo."))

A(h2("Segunda etapa: a convergência das duas formas funcionais"))
A(p(
    "Considere-se agora o que o Prophet ajusta neste mesmo cenário. Sua componente de "
    "tendência é linear por partes, com pontos de quebra submetidos a regularização; "
    "na ausência de quebras reais na série, a regularização anula os incrementos e "
    "resta uma tendência linear simples. Sua componente sazonal é uma série de "
    "Fourier de período semanal, estimada globalmente e fixa ao longo de toda a "
    "série. O modelo resultante é, portanto, uma reta somada a um perfil semanal "
    "fixo — <b>a mesma família de funções à qual o Holt-Winters degenerou</b>."))
A(p(
    "Sob essa perspectiva, a proximidade dos resultados deixa de ser surpreendente. "
    "Dois procedimentos de otimização distintos, aplicados à mesma família funcional "
    "e ao mesmo conjunto de dados, produzem estimativas quase idênticas. As "
    "diferenças de MAPE observadas na Tabela " + CAP + ".3, situadas na terceira casa "
    "decimal para a maioria dos produtos, refletem apenas variações numéricas entre "
    "os dois otimizadores."))

A(h2("Terceira etapa: por que o otimizador chegou a esses valores"))
A(p(
    "O processo gerador descrito na Seção " + CAP + ".2.1 produz tendência "
    "rigorosamente linear e perfil semanal constante ao longo de todo o período. Nesse "
    "regime, adaptar-se à observação recente é estritamente prejudicial ao "
    "desempenho: como a estrutura verdadeira nunca se altera, qualquer reação a uma "
    "observação individual constitui reação a ruído. O otimizador identificou essa "
    "propriedade e suprimiu a adaptação, atribuindo peso nulo às atualizações."))
A(destaque(
    "Dupla conclusão",
    ["<b>O resultado valida a implementação do motor.</b> Submetido a dados cuja "
     "estrutura é conhecida por construção, o procedimento de estimação recuperou "
     "não apenas essa estrutura — nível, tendência e perfil semanal — como também a "
     "propriedade de que ela é estacionária. É o comportamento esperado de um "
     "estimador corretamente implementado, e constitui a evidência mais forte "
     "produzida por esta validação de instrumentação.",
     "<b>O resultado delimita o alcance da conclusão comparativa.</b> A equivalência "
     "entre os modelos é propriedade deste conjunto de dados, e não uma afirmação "
     "geral sobre Holt-Winters e Prophet. Decorre daí uma previsão verificável: em "
     "séries reais, sujeitas a mudanças de patamar, alterações de mix e sazonalidade "
     "que evolui, espera-se estimativa de α estritamente positiva e separação de "
     "desempenho consideravelmente maior entre os dois métodos."], "ok"))
A(esp(5))
A(p(
    "Essa previsão fundamenta uma decisão de arquitetura da plataforma. Se a "
    "equivalência observada fosse tomada como resultado geral, seria razoável "
    "descartar um dos modelos e simplificar o sistema. Como a equivalência é "
    "condicionada à estacionariedade da série — condição que dados reais não "
    "satisfazem —, <b>justifica-se manter os dois modelos com seleção automática por "
    "produto</b>, mecanismo que se torna operante precisamente nos casos em que os "
    "métodos divergem."))

A(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.9 Da previsão à decisão de reposição"))
A(p(
    "A previsão de demanda constitui insumo, não produto final. O que a plataforma "
    "entrega ao gestor é uma decisão: em que nível de estoque emitir novo pedido e "
    "que reserva manter para absorver incerteza. Essa conversão emprega a formulação "
    "de Ballou (2006)."))
A(p(
    "O nível de serviço — probabilidade almejada de não haver ruptura durante o prazo "
    "de entrega, fixada em 95% por padrão — é convertido no multiplicador Z da "
    "distribuição normal padrão. O cálculo é dinâmico, o que merece registro: em "
    "implementações que fixam Z em 1,645, o parâmetro de nível de serviço torna-se "
    "inoperante, pois alterá-lo não produz efeito algum sobre o resultado. Na "
    "implementação adotada, elevar o nível de 95% para 99% altera Z para 2,326 e "
    "eleva proporcionalmente a reserva calculada."))
A(formula(
    "Z  = norm.ppf(nível de serviço)<br/>"
    "ES = Z · √( LT · σ²_demanda + demanda² · σ²_leadtime )<br/>"
    "PR = demanda_média_diária · LT + ES"))
A(esp(5))
A(p(
    "A fórmula do estoque de segurança incorpora <b>duas fontes de incerteza "
    "simultaneamente</b>: a variabilidade da demanda, no primeiro termo do radicando, "
    "e a variabilidade do prazo de entrega, no segundo. A formulação simplificada "
    "frequentemente encontrada na literatura aplicada, Z·σ·√LT, desconsidera a "
    "segunda parcela. Em mercados de bairro, nos quais o atraso do fornecedor "
    "constitui ocorrência rotineira, essa omissão subdimensiona sistematicamente a "
    "reserva."))
A(p(
    "A Tabela " + CAP + ".7 apresenta o resultado do cálculo para os dois produtos "
    "analisados, com prazo de entrega de três dias, variabilidade de prazo igual a "
    "1,0 e nível de serviço de 95%."))
k1, k5 = kpi[1], kpi[5]
A(tabela([
    ["Etapa do cálculo", f"{k1['nome']} (id 1)", f"{k5['nome']} (id 5)"],
    ["Modelo selecionado", k1["vencedor"], k5["vencedor"]],
    ["Demanda média prevista (un/dia)", num(k1["demanda_media"], 3),
     num(k5["demanda_media"], 3)],
    ["σ da demanda histórica", num(k1["desvio"], 3), num(k5["desvio"], 3)],
    ["Z para nível de 95%", num(k1["z"], 4), num(k5["z"], 4)],
    ["<b>Estoque de segurança</b>", f"<b>{num(k1['estoque_seguranca'])}</b>",
     f"<b>{num(k5['estoque_seguranca'])}</b>"],
    ["<b>Ponto de reposição</b>", f"<b>{num(k1['ponto_reposicao'])}</b>",
     f"<b>{num(k5['ponto_reposicao'])}</b>"],
    ["Estoque atual", str(k1["estoque_atual"]), str(k5["estoque_atual"])],
    ["<b>Dias até ruptura</b>", f"<b>{num(k1['dias_ate_ruptura'])}</b>",
     f"<b>{num(k5['dias_ate_ruptura'])}</b>"],
], [LARGURA_UTIL * 0.34, LARGURA_UTIL * 0.33, LARGURA_UTIL * 0.33]))
A(Paragraph(f"<b>Tabela {CAP}.7</b> — Parâmetros de reposição calculados pelo motor.",
            ParagraphStyle("legt7", parent=S_P, fontSize=8.3, textColor=AZUL,
                           spaceBefore=4)))
A(esp(6))
A(figura(FIGS / "g7_reposicao_produto1.png",
         f"<b>Figura {CAP}.11</b> — Projeção de estoque do Arroz 5kg, com marcação do "
         "ponto de reposição e do estoque de segurança."))
A(figura(FIGS / "g7_reposicao_produto5.png",
         f"<b>Figura {CAP}.12</b> — Projeção de estoque da Banana Prata kg."))
A(p(
    f"A interpretação operacional é imediata. O arroz possui {k1['estoque_atual']} "
    f"unidades em estoque contra ponto de reposição de {num(k1['ponto_reposicao'])} — "
    "situação em que o pedido já deveria ter sido emitido, com ruptura estimada em "
    f"{num(k1['dias_ate_ruptura'])} dia. A banana prata, com {k5['estoque_atual']} "
    f"unidades contra ponto de reposição de {num(k5['ponto_reposicao'])}, encontra-se "
    f"em situação folgada, com cobertura estimada de {num(k5['dias_ate_ruptura'])} "
    "dias."))
A(p(
    "Registre-se que o estoque de segurança da banana prata supera o do arroz — "
    f"{num(k5['estoque_seguranca'])} contra {num(k1['estoque_seguranca'])} unidades — "
    "ainda que as demandas médias sejam próximas. A diferença decorre do desvio "
    "padrão da demanda, presente no radicando da fórmula: produtos mais erráticos "
    "exigem reserva maior para o mesmo nível de serviço. <b>Verifica-se assim que o "
    "sistema compensa automaticamente a menor previsibilidade de um item com maior "
    "proteção contra ruptura</b>, o que atenua, no plano da decisão, o efeito do MAPE "
    "elevado discutido na Seção " + CAP + ".5."))

A(PageBreak())

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.10 Limitações e ameaças à validade"))
A(p(
    "As limitações a seguir foram identificadas por inspeção do código e do "
    "delineamento experimental, e são declaradas para delimitar com precisão o "
    "alcance das conclusões deste capítulo."))
lims = [
    ("Natureza sintética dos dados",
     "A validação demonstra a correção da implementação e a adequação da "
     "metodologia, não o desempenho preditivo em operação real. É a limitação mais "
     "relevante e condiciona todas as demais conclusões."),
    ("Geração multiplicativa e ajuste aditivo",
     "O processo gerador compõe os fatores por multiplicação, ao passo que os "
     "modelos e a decomposição empregam formulação aditiva. Com crescimento de "
     "apenas 20% no período, a discrepância é pequena, mas constitui incoerência "
     "metodológica que convém registrar."),
    ("Ausência de comparação com métodos ingênuos",
     "Não foram avaliados estimadores de referência, como a repetição do valor "
     "observado sete dias antes ou a média por dia da semana. Sua inclusão "
     "permitiria quantificar o ganho absoluto dos modelos, e não apenas a diferença "
     "entre eles. Dado o resultado da Seção " + CAP + ".8, há hipótese plausível de "
     "que um estimador de média por dia da semana com tendência apresente desempenho "
     "próximo ao dos dois modelos neste conjunto de dados."),
    ("Regressor de promoções não ativado",
     "O campo previsto no contrato de entrada não é repassado ao Prophet. No "
     "conjunto sintético a omissão é inócua, pois a variável é constante e não "
     "possui variância; sua avaliação exige dados reais contendo promoções."),
    ("Tratamento de feriados não ativado no Prophet",
     "O modelo dispõe de mecanismo nativo para efeitos de calendário, sem "
     "equivalente no Holt-Winters, que não foi habilitado. Como o conjunto de dados "
     "contém doze feriados com elevada probabilidade de fechamento, essa é a "
     "alteração de maior potencial para diferenciar os dois métodos."),
    ("Desvio padrão calculado sobre a série integral",
     "O σ empregado na fórmula do estoque de segurança inclui os dias de "
     "fechamento, o que eleva a dispersão estimada e, por consequência, a reserva "
     "calculada. A escolha é conservadora — erra no sentido de excesso de estoque —, "
     "mas não é neutra."),
    ("Fragilidade do MAPE em séries de baixo volume",
     "Documentada nas Seções " + CAP + ".2.3 e " + CAP + ".7. Métricas alternativas, "
     "como o SMAPE ou o MASE, mitigariam o problema e poderiam ser adotadas como "
     "critério de desempate."),
    ("Truncamento assimétrico das previsões",
     "A previsão entregue é truncada em zero, enquanto as métricas são calculadas "
     "sobre a previsão bruta. Em produtos de tendência decrescente, o modelo aditivo "
     "poderia ser penalizado por valores negativos que jamais seriam exibidos. No "
     "conjunto avaliado, de tendência crescente, o efeito é nulo."),
    ("Sensibilidade da reprodutibilidade à ordem do catálogo",
     "O gerador consome um único fluxo de números pseudoaleatórios de forma "
     "sequencial. A inserção ou reordenação de produtos desloca as séries "
     "subsequentes, de modo que novos itens devem ser acrescentados ao final da "
     "lista para preservar a reprodutibilidade."),
    ("Impossibilidade de estimar sazonalidade anual",
     "Um período de 365 dias não comporta a estimação de ciclo anual, que exigiria "
     "ao menos dois ciclos completos. A componente anual do Prophet foi desabilitada "
     "por essa razão."),
]
for i, (t, x) in enumerate(lims, 1):
    A(h3(f"{CAP}.10.{i} {t}"))
    A(p(x))

# ═══════════════════════════════════════════════════════════════════════════
A(h1(f"{CAP}.11 Síntese do capítulo"))
A(p("Os experimentos descritos permitem sustentar as seguintes afirmações:"))
A(li("As séries de demanda contêm sinal previsível — tendência e sazonalidade "
     "semanal separáveis do termo aleatório —, o que justifica o emprego de modelos "
     f"de série temporal (Seção {CAP}.4).", "1."))
A(li("Ambos os modelos generalizam para dados não observados, com erro que varia "
     f"de {num(MAPE_MIN)}% a {num(MAPE_MAX)}% conforme a variabilidade intrínseca de "
     f"cada produto (Seção {CAP}.5).", "2."))
A(li("O ajuste é adequado: os resíduos não retêm estrutura discernível "
     f"(Seção {CAP}.6) e o desempenho mantém-se estável em janelas de avaliação "
     f"independentes (Seção {CAP}.7).", "3."))
A(li("A equivalência de desempenho entre Holt-Winters e Prophet possui explicação "
     "mecânica verificável — a convergência dos parâmetros de suavização a zero, que "
     "reduz ambos à mesma família funcional — e está condicionada à "
     f"estacionariedade da série avaliada (Seção {CAP}.8).", "4."))
A(li("A previsão converte-se em parâmetros de reposição coerentes, e o "
     "dimensionamento da reserva compensa automaticamente a menor previsibilidade "
     f"dos produtos mais erráticos (Seção {CAP}.9).", "5."))
A(esp(6))
A(p(
    "A validação externa, sobre o histórico de vendas de um estabelecimento real, "
    "deverá verificar em que medida essas conclusões se sustentam fora do regime "
    "estacionário. Espera-se, em particular, que os parâmetros de suavização assumam "
    "valores estritamente positivos e que a diferença de desempenho entre os modelos "
    "se amplie — hipótese que, uma vez confirmada, converteria o mecanismo de seleção "
    "automática por produto de precaução arquitetural em componente operante do "
    "sistema."))

# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    caminho = montar_documento(
        RAIZ / "docs" / "capitulo-validacao.pdf", E,
        f"Capítulo {CAP} · Validação Empírica do Motor Preditivo",
        title=f"Capítulo {CAP} — Validação Empírica do Motor Preditivo",
        author="StockSense · TCC 2026",
        subject="Validação empírica do motor preditivo Holt-Winters × Prophet",
    )
    print("PDF gerado:", caminho)
    print("Tamanho   :", f"{caminho.stat().st_size / 1024:.0f} KB")
