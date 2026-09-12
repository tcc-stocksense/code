"""
Gera UMA VEZ o esqueleto do capítulo de validação empírica do TCC, em Markdown,
com todas as tabelas já preenchidas com os números reais.

⚠️  Este script é um andaime (scaffold), não um pipeline. Depois que você começar
a escrever a prosa no .md, NÃO rode de novo — ele sobrescreve o arquivo inteiro.
Se precisar atualizar números depois de já ter texto escrito, regenere em outro
caminho e transponha só as tabelas.

Uso (a partir de ml-service/):
    venv/Scripts/python.exe analysis/_coletar_dados_doc.py     # se ainda não rodou
    venv/Scripts/python.exe docs/gerar_esqueleto_capitulo.py
"""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "capitulo-validacao-esqueleto.md"

d = json.loads((RAIZ / "analysis" / "results" / "dados_documento.json")
               .read_text(encoding="utf-8"))
alphas = json.loads((RAIZ / "analysis" / "results" / "_alphas.json")
                    .read_text(encoding="utf-8"))

kpi = {k["produto_id"]: k for k in d["kpis"]}
wf = d["walkforward"]
v = d["vitorias"]


def esc(nota: str) -> str:
    return f"> **[ESCREVER]** {nota}\n"


L: list[str] = []
A = L.append

# ═══════════════════════════════════════════════════════════════════════════
A("# Capítulo X — Validação Empírica do Motor Preditivo\n")
A("<!--")
A("  ESQUELETO GERADO AUTOMATICAMENTE — StockSense / TCC 2026")
A("  Todas as tabelas já estão preenchidas com números reais, extraídos da")
A("  execução do código de produção (app/services/) com SEED=42.")
A("")
A("  Como usar:")
A("   1. Substitua cada bloco [ESCREVER] pela sua prosa e apague o marcador.")
A("   2. Não altere os números das tabelas à mão — se precisar atualizá-los,")
A("      rode analysis/_coletar_dados_doc.py e transponha.")
A("   3. As figuras estão em ml-service/analysis/figures/ (14 PNGs).")
A("")
A("  Referência de apoio: docs/relatorio-modelos-preditivos.pdf")
A("-->\n")

# ── X.1 ────────────────────────────────────────────────────────────────────
A("## X.1 Objetivo e escopo da validação\n")
A(esc(
    "Abra dizendo o que este capítulo se propõe a provar e, principalmente, o que "
    "ele NÃO se propõe. Sugestão de recorte: o objetivo é verificar se o motor "
    "preditivo (a) recupera corretamente a estrutura de uma série de demanda, "
    "(b) produz erro mensurável e reprodutível, e (c) converte a previsão em "
    "parâmetros de reposição coerentes. Deixe explícito que a validação externa "
    "sobre vendas reais de um mercado fica como trabalho futuro — declarar isso "
    "aqui, na abertura, é mais forte do que ser cobrado depois."))
A(esc(
    "Explique a escolha por dados sintéticos e antecipe a crítica de circularidade: "
    "como a estrutura verdadeira dos dados é conhecida por construção, é possível "
    "verificar se o motor a recupera. Trata-se de validação de instrumentação — "
    "provar que a régua mede certo — e não de medição do mundo real."))

# ── X.2 ────────────────────────────────────────────────────────────────────
A("\n## X.2 Protocolo experimental\n")
A("### X.2.1 Conjunto de dados\n")
A(f"Foram gerados **10 produtos × {d['descritiva'][0]['n_dias']} dias** de histórico "
  f"diário, com semente fixa (`SEED = {d['seed']}`), representando perfis de demanda "
  "contrastantes de um mercado de bairro.\n")
A(esc(
    "Descreva a fórmula geradora — quantidade = demanda_base × tendência × "
    "fator_semanal × ruído — e os fechamentos de domingo (40% de chance) e feriado "
    "(60%). Enfatize que o perfil semanal vai de 1,45 no sábado a 0,30 no domingo, "
    "porque é essa amplitude que justifica usar modelos sazonais."))
A("\n### X.2.2 Divisão temporal\n")
A(f"A avaliação usa divisão cronológica **80% treino / 20% teste**, resultando em "
  f"{wf['1']['n_treino']} dias de treino ({wf['1']['treino_ini']} a "
  f"{wf['1']['treino_fim']}) e {wf['1']['n_validacao']} dias de teste "
  f"({wf['1']['valid_ini']} a {wf['1']['valid_fim']}).\n")
A(esc(
    "Este é o parágrafo mais importante do capítulo do ponto de vista metodológico. "
    "Justifique por que a divisão é por posição cronológica e nunca aleatória: "
    "embaralhar colocaria dias posteriores no treino e anteriores no teste, ou seja, "
    "o modelo usaria o futuro para prever o passado. O erro medido ficaria "
    "artificialmente baixo e sem valor. Cite Hyndman & Athanasopoulos."))
A("\n### X.2.3 Métricas de avaliação\n")
A("| Métrica | Fórmula | Unidade | Papel |")
A("|---|---|---|---|")
A("| MAE | média(\\|real − previsto\\|) | unidades | erro típico, interpretável pelo lojista |")
A("| RMSE | raiz(média((real − previsto)²)) | unidades | penaliza erros grandes |")
A("| MAPE | média(\\|real − previsto\\| / real) × 100 | % | adimensional, permite comparar produtos |")
A("")
A(esc(
    "Justifique por que a SELEÇÃO do modelo usa MAPE: é a única das três que é "
    "comparável entre produtos de escalas diferentes, e alimenta o KPI de acurácia "
    "do dashboard (100 − MAPE). Registre também o tratamento de dias sem venda: o "
    "MAPE é calculado apenas sobre observações com valor real maior que zero, para "
    "evitar divisão por zero, enquanto RMSE e MAE consideram todos os dias — logo, "
    "as três não são calculadas exatamente sobre o mesmo conjunto de pontos."))
A("\n### X.2.4 Equivalência com o sistema em produção\n")
A(esc(
    "Registre a decisão de projeto: a camada de análise importa os módulos de "
    "produção (app/services/) em vez de reimplementar as fórmulas. Consequência: "
    "não existe uma segunda implementação que possa divergir da primeira, e os "
    "números deste capítulo são, por construção, os que o endpoint /predict "
    "devolve em execução. Isso é uma garantia de validade interna e vale ser "
    "afirmado explicitamente."))

# ── X.3 ────────────────────────────────────────────────────────────────────
A("\n## X.3 Caracterização do conjunto de dados\n")
A("**Tabela X.1** — Estatística descritiva dos 10 produtos\n")
A("| id | Produto | Variab. | Média/dia | σ | CV | % zeros |")
A("|---:|---|---:|---:|---:|---:|---:|")
for r in d["descritiva"]:
    A(f"| {r['produto_id']} | {r['nome']} | {r['variabilidade']:.2f} | "
      f"{r['media_diaria']:.2f} | {r['desvio']:.2f} | {r['cv']:.2f} | "
      f"{r['pct_zeros']:.1f}% |")
A("")
A(esc(
    "Comente a amplitude de perfis: de Sal Refinado (variabilidade 0,05, quase "
    "determinístico) a Banana Prata (0,45, altamente errático). Faça a observação "
    "não óbvia: o CV nunca fica muito baixo, mesmo no Sal, porque a própria "
    "oscilação semanal já produz dispersão — ou seja, parte do 'desvio' de cada "
    "produto é estrutura previsível, não ruído, e é justamente essa parte que os "
    "modelos conseguem capturar. Essa distinção prepara a leitura dos MAPEs altos "
    "mais adiante."))

# ── X.4 ────────────────────────────────────────────────────────────────────
A("\n## X.4 Análise exploratória: existe sinal previsível?\n")
A("**Figura X.1** — `analysis/figures/g1_decomposicao_produto1.png` (Arroz 5kg)  ")
A("**Figura X.2** — `analysis/figures/g1_decomposicao_produto5.png` (Banana Prata kg)\n")
A(esc(
    "Explique a decomposição aditiva de período 7 e o que ela prova: se a componente "
    "sazonal tem amplitude nítida e regular e o resíduo é pequeno frente ao sinal, "
    "existe estrutura a ser capturada — o que justifica usar modelos de série "
    "temporal em vez de uma média simples. Contraste as duas figuras: mesma estrutura "
    "sazonal nos dois produtos, mas resíduo de amplitude muito maior na Banana. Esse "
    "contraste antecipa e explica a diferença de MAPE entre eles."))

# ── X.5 ────────────────────────────────────────────────────────────────────
A("\n## X.5 Resultados comparativos\n")
A("### X.5.1 Métricas por produto e modelo\n")
A("**Tabela X.2** — MAPE, RMSE e MAE por produto × modelo (janela de teste)\n")
A("| id | Produto | Modelo | MAPE (%) | RMSE | MAE | Vencedor |")
A("|---:|---|---|---:|---:|---:|:---:|")
for r in d["comparativo"]:
    A(f"| {r['produto_id']} | {r['nome']} | {r['modelo']} | {r['mape']:.4f} | "
      f"{r['rmse']:.4f} | {r['mae']:.4f} | {'**✔**' if r['vencedor'] else ''} |")
A("")
A(f"**Placar:** Holt-Winters venceu em **{v['holt_winters']}** produtos, "
  f"Prophet em **{v['prophet']}**.\n")
A("**Tabela X.3** — Margem de MAPE entre os dois modelos, por produto\n")
A("| Produto | Margem (pontos percentuais) |")
A("|---|---:|")
for m in sorted(d["margens"], key=lambda x: x["margem_pp"]):
    A(f"| {m['produto_id']} — {m['nome']} | {m['margem_pp']:.4f} |")
A("")
A(esc(
    "Aqui está o resultado central e ele exige honestidade. NÃO defenda que a "
    "seleção do melhor modelo trouxe ganho expressivo: os seus próprios números "
    "mostram que em 9 dos 10 produtos a diferença é menor que 0,7 pp, e em cinco "
    "deles menor que 0,06 pp. A leitura correta é: nenhum modelo domina o outro "
    "neste conjunto de dados. A explicação do porquê vem na seção X.8 — anuncie "
    "isso aqui para o leitor não achar que ficou sem resposta."))
A(esc(
    "Comente a amplitude do MAPE entre os 20 pares produto × modelo — de "
    f"{min(r['mape'] for r in d['comparativo']):.2f}".replace(".", ",") + "% a "
    f"{max(r['mape'] for r in d['comparativo']):.2f}".replace(".", ",") +
    "% — e conecte com a Tabela X.1: "
    "os produtos de maior variabilidade são os de maior erro. Isso é propriedade do "
    "dado, não falha do método. Mencione que o sistema trata esse caso: quando o "
    "MAPE do vencedor passa de 50%, o motor preenche o campo `aviso` e a interface "
    "sinaliza previsão de baixa confiança."))
A("\n### X.5.2 Ajuste fora da amostra\n")
A("**Figura X.3** — `g2_previsto_real_produto1.png`  ")
A("**Figura X.4** — `g2_previsto_real_produto5.png`\n")
A(esc(
    "Descreva o que o gráfico mostra: a linha preta é o realizado na janela de "
    "teste; as tracejadas são o que cada modelo previu sem nunca ter visto esses "
    "dias. Observe que as curvas dos dois modelos são praticamente indistinguíveis — "
    "evidência visual do que a Tabela X.3 mostra numericamente."))
A("\n### X.5.3 Comportamento do erro ao longo do horizonte\n")
A("**Figura X.5** — `g4_erro_horizonte_produto1.png`  ")
A("**Figura X.6** — `g4_erro_horizonte_produto5.png`\n")
A(esc(
    "Relacione com a equação de previsão do Holt-Winters: como ŷ(t+h) = L_t + h·b_t "
    "+ sazonal, qualquer erro na estimativa da tendência é multiplicado por h e se "
    "acumula com o horizonte. Use isso para justificar o horizonte de 30 dias "
    "adotado no sistema, alinhado ao ciclo mensal de recálculo."))

# ── X.6 ────────────────────────────────────────────────────────────────────
A("\n## X.6 Diagnóstico de resíduos\n")
A("**Figura X.7** — `g5_residuos_produto1_holt_winters.png`  ")
A("**Figura X.8** — `g5_residuos_produto5_holt_winters.png`\n")
A(esc(
    "Este é o teste decisivo de qualidade do ajuste, e vale explicar o critério "
    "antes de aplicá-lo: resíduo = real − previsto, e um bom modelo deixa resíduos "
    "centrados em zero, sem padrão temporal e sem autocorrelação — aproximadamente "
    "ruído branco. Diga explicitamente o que refutaria a conclusão: um pico na ACF "
    "no lag 7 indicaria sazonalidade semanal não capturada. Como não há, conclui-se "
    "que o modelo extraiu a estrutura disponível e o que sobrou é ruído irredutível."))

# ── X.7 ────────────────────────────────────────────────────────────────────
A("\n## X.7 Robustez: backtesting rolling-origin\n")
A(esc(
    "Justifique a necessidade: uma única divisão treino/teste pode ser favorável por "
    "acaso. No backtesting rolling-origin o treino cresce a cada dobra e a previsão "
    "é feita sobre o bloco seguinte de 14 dias, repetindo o experimento 5 vezes."))
for pid in ("1", "5"):
    nome = wf[pid]["nome"]
    A(f"\n**Tabela X.{4 if pid == '1' else 5}** — Backtesting de {nome} (id {pid})\n")
    A("| Origem da janela | MAPE HW (%) | RMSE HW | MAPE Prophet (%) | RMSE Prophet |")
    A("|---|---:|---:|---:|---:|")
    bt = d["backtesting"][pid]
    for i, r in enumerate(bt["holt_winters"]):
        rp = bt["prophet"][i]
        A(f"| {r['origem']} | {r['mape']:.2f} | {r['rmse']:.2f} | "
          f"{rp['mape']:.2f} | {rp['rmse']:.2f} |")
A("")
A("**Figura X.9** — `g6_backtesting_produto1.png`  ")
A("**Figura X.10** — `g6_backtesting_produto5.png`\n")
A(esc(
    "Leitura do produto 1: MAPE entre 10,50% e 15,65% nas cinco dobras — faixa "
    "estreita, desempenho consistente, a métrica principal é representativa."))
A(esc(
    "Leitura do produto 5: quatro dobras entre 30,2% e 51,0% e uma quinta em 188,4%. "
    "NÃO omita essa dobra — analise-a. O RMSE da mesma janela (11,64) está apenas "
    "moderadamente acima das demais, o que descarta uma falha catastrófica de "
    "previsão; o que houve foi o efeito aritmético do MAPE quando o denominador é "
    "pequeno. Declarar e explicar a dobra ruim demonstra domínio do comportamento da "
    "métrica e é mais forte do que apresentar só as janelas favoráveis."))

# ── X.8 ────────────────────────────────────────────────────────────────────
A("\n## X.8 Análise dos parâmetros ajustados: por que os modelos empatam\n")
A("**Tabela X.6** — Parâmetros de suavização encontrados pelo otimizador "
  "(Holt-Winters)\n")
A("| id | Produto | α (nível) | β (tendência) | γ (sazonal) |")
A("|---:|---|---:|---:|---:|")
for r in alphas:
    A(f"| {r['pid']} | {r['nome']} | {r['a']:.5f} | {r['b']:.5f} | {r['g']:.5f} |")
A("")
A(esc(
    "Esta é a seção mais original do capítulo. Construa o argumento em três passos.\n"
    ">\n"
    "> **(1) A evidência.** Em todos os 10 produtos o otimizador convergiu para "
    "α ≈ β ≈ γ ≈ 0 — sete deles exatamente zero, os outros três na ordem de 10⁻⁵ a "
    "10⁻³.\n"
    ">\n"
    "> **(2) O que isso significa.** Retome a equação de atualização do nível: com "
    "α = 0 o termo da nova observação desaparece e sobra L_t = L_(t−1) + b_(t−1). O "
    "modelo deixa de ser um filtro adaptativo e degenera para ŷ(t) = L₀ + t·b₀ + "
    "s(dia da semana) — uma reta com padrão semanal fixo, estimados uma única vez. "
    "Compare com o que o Prophet ajusta neste cenário: tendência linear (sem "
    "changepoints ativos, pois não há quebras) mais sazonalidade semanal fixa. **São "
    "a mesma família de função.**\n"
    ">\n"
    "> **(3) Por que o otimizador chegou lá.** O gerador produz tendência "
    "perfeitamente linear e perfil semanal rigorosamente constante. Nesse regime, "
    "adaptar-se ao dado recente é prejudicial: toda reação a uma observação "
    "individual é reação a ruído puro. O otimizador identificou isso e desligou a "
    "adaptação."))
A(esc(
    "Feche com a dupla conclusão. Primeiro, isso **valida o motor**: submetido a "
    "dados de estrutura conhecida, ele recuperou essa estrutura, inclusive a "
    "informação de que ela é estacionária. Segundo, **delimita o alcance do "
    "resultado**: o empate entre os modelos é propriedade deste conjunto de dados, "
    "não uma verdade geral sobre Holt-Winters e Prophet.\n"
    ">\n"
    "> Encerre com a previsão testável — em dados reais, com quebras de patamar e "
    "sazonalidade que evolui, espera-se α > 0 e separação de desempenho entre os "
    "modelos. É justamente isso que **justifica a decisão arquitetural de manter os "
    "dois modelos no sistema** com seleção automática por produto, em vez de fixar "
    "um. Amarre essa conclusão ao capítulo de arquitetura."))

# ── X.9 ────────────────────────────────────────────────────────────────────
A("\n## X.9 Da previsão à decisão de reposição\n")
A(esc(
    "Faça a transição: prever é meio caminho; o que o lojista precisa é saber quando "
    "pedir e quanto manter de reserva. Apresente a fórmula combinada de Ballou — "
    "ES = Z · √(LT · σ²_demanda + demanda² · σ²_leadtime) — e destaque que ela "
    "considera duas fontes de incerteza simultaneamente, enquanto a fórmula "
    "simplificada (1,65 · σ · √LT) ignora a variabilidade do prazo de entrega. Num "
    "mercado de bairro, onde o atraso do fornecedor é rotina, essa omissão "
    "subdimensiona a reserva. Mencione também que Z = norm.ppf(nível de serviço) é "
    "calculado dinamicamente, de modo que alterar o nível de 95% para 99% de fato "
    "muda o resultado."))
A("\n**Tabela X.7** — Parâmetros de reposição calculados pelo motor "
  "(lead time = 3 dias, σ_LT = 1,0, nível de serviço = 95%)\n")
k1, k5 = kpi[1], kpi[5]
A(f"| Etapa | {k1['nome']} (id 1) | {k5['nome']} (id 5) |")
A("|---|---|---|")
A(f"| Modelo vencedor | {k1['vencedor']} | {k5['vencedor']} |")
A(f"| Demanda média prevista (un/dia) | {k1['demanda_media']:.3f} | "
  f"{k5['demanda_media']:.3f} |")
A(f"| σ da demanda histórica | {k1['desvio']:.3f} | {k5['desvio']:.3f} |")
A(f"| Z (nível 95%) | {k1['z']} | {k5['z']} |")
A(f"| **Estoque de segurança** | **{k1['estoque_seguranca']}** | "
  f"**{k5['estoque_seguranca']}** |")
A(f"| **Ponto de reposição** | **{k1['ponto_reposicao']}** | "
  f"**{k5['ponto_reposicao']}** |")
A(f"| Estoque atual | {k1['estoque_atual']} | {k5['estoque_atual']} |")
A(f"| **Dias até ruptura** | **{k1['dias_ate_ruptura']}** | "
  f"**{k5['dias_ate_ruptura']}** |")
A("")
A("**Figura X.11** — `g7_reposicao_produto1.png`  ")
A("**Figura X.12** — `g7_reposicao_produto5.png`\n")
A(esc(
    f"Interprete em termos de negócio: o Arroz tem {k1['estoque_atual']} unidades "
    f"contra um ponto de reposição de {k1['ponto_reposicao']} — já deveria ter sido "
    f"pedido, com ruptura estimada em {k1['dias_ate_ruptura']} dia. A Banana tem "
    f"{k5['estoque_atual']} unidades contra PR de {k5['ponto_reposicao']}, situação "
    "confortável. É essa tradução — de erro estatístico para instrução acionável — "
    "que sustenta a proposta da plataforma."))

# ── X.10 ───────────────────────────────────────────────────────────────────
A("\n## X.10 Limitações e ameaças à validade\n")
A(esc(
    "Introduza dizendo que as limitações abaixo foram identificadas por inspeção do "
    "próprio código e são declaradas antes de serem questionadas. Desenvolva cada "
    "uma em um parágrafo curto."))
A("")
lims = [
    ("Validação sobre dados sintéticos",
     "prova a metodologia e a instrumentação, não o desempenho em mercado real; "
     "risco de circularidade a ser explicitado"),
    ("Geração multiplicativa × ajuste aditivo",
     "o gerador multiplica os componentes, enquanto os modelos e a decomposição usam "
     "modo aditivo; com apenas 20% de crescimento no período o impacto é pequeno, "
     "mas é uma incoerência metodológica real"),
    ("Regressor de promoção não ativado",
     "o campo `is_promocional` não é passado ao Prophet; no dataset atual isso é "
     "inócuo, pois a coluna é constante e não tem variância"),
    ("Mecanismo de feriados do Prophet desativado",
     "o termo h(t) não é usado, apesar de os dados conterem 12 feriados; é um recurso "
     "nativo do Prophet sem equivalente no Holt-Winters"),
    ("σ da demanda calculado sobre a série completa",
     "inclui os dias de loja fechada, o que infla o desvio e, por consequência, o "
     "estoque de segurança — escolha conservadora, mas que merece registro"),
    ("Fragilidade do MAPE com denominadores pequenos",
     "documentado na seção X.7; SMAPE ou MASE seriam alternativas"),
    ("Corte em zero aplicado de forma assimétrica",
     "a previsão entregue é truncada em zero, mas as métricas usam a previsão bruta"),
    ("Reprodutibilidade sensível à ordem do catálogo",
     "o gerador consome um único fluxo aleatório sequencialmente; inserir produto no "
     "meio da lista desloca as séries seguintes"),
    ("Sazonalidade anual fora de alcance",
     "365 dias não permitem estimar ciclo anual — seriam necessários dois ciclos"),
    ("Ausência de baseline ingênuo",
     "não há comparação contra seasonal naive ou média por dia da semana, o que "
     "limita a afirmação sobre o ganho absoluto dos modelos"),
]
A("| # | Limitação | Natureza |")
A("|---:|---|---|")
for i, (t, x) in enumerate(lims, 1):
    A(f"| {i} | {t} | {x} |")
A("")
A(esc(
    "A limitação nº 10 merece um parágrafo próprio e uma decisão sua: ou você "
    "implementa os baselines (é barato — seasonal naive é ŷ(t) = y(t−7)) e fecha a "
    "lacuna, ou a declara como trabalho futuro. Dado o achado da seção X.8, há uma "
    "hipótese interessante a testar: como o Holt-Winters degenerou para 'média por "
    "dia da semana mais tendência', um baseline desse tipo pode empatar com os dois "
    "modelos neste dataset."))

# ── X.11 ───────────────────────────────────────────────────────────────────
A("\n## X.11 Síntese do capítulo\n")
A(esc(
    "Feche com três a cinco afirmações do que ficou demonstrado, cada uma amarrada à "
    "evidência correspondente. Sugestão de esqueleto:\n"
    ">\n"
    "> 1. A série de demanda contém sinal previsível — tendência e sazonalidade "
    "semanal separáveis do ruído (X.4).\n"
    "> 2. Os dois modelos generalizam para dados não vistos, com erro que varia por "
    "produto conforme a variabilidade intrínseca (X.5).\n"
    "> 3. O ajuste é adequado: os resíduos não retêm estrutura (X.6) e o desempenho "
    "se mantém em janelas independentes (X.7).\n"
    "> 4. O empate entre os modelos tem explicação mecânica verificável e delimita o "
    "alcance do resultado a este conjunto de dados (X.8).\n"
    "> 5. A previsão se converte em parâmetros de reposição coerentes com a situação "
    "de cada produto (X.9).\n"
    ">\n"
    "> Encerre indicando o que a validação externa com dados reais deverá verificar."))

A("\n---\n")
A("<!-- Fim do esqueleto. Material de apoio: "
  "docs/relatorio-modelos-preditivos.pdf (seções 7 a 15). -->")

DESTINO.write_text("\n".join(L) + "\n", encoding="utf-8")
print("Esqueleto gerado:", DESTINO)
print("Linhas:", len(L))
print("Marcadores [ESCREVER]:", sum(1 for x in L if "[ESCREVER]" in x))
