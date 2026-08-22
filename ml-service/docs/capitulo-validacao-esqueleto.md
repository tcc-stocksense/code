# Capítulo X — Validação Empírica do Motor Preditivo

<!--
  ESQUELETO GERADO AUTOMATICAMENTE — StockSense / TCC 2026
  Todas as tabelas já estão preenchidas com números reais, extraídos da
  execução do código de produção (app/services/) com SEED=42.

  Como usar:
   1. Substitua cada bloco [ESCREVER] pela sua prosa e apague o marcador.
   2. Não altere os números das tabelas à mão — se precisar atualizá-los,
      rode analysis/_coletar_dados_doc.py e transponha.
   3. As figuras estão em ml-service/analysis/figures/ (14 PNGs).

  Referência de apoio: docs/relatorio-modelos-preditivos.pdf
-->

## X.1 Objetivo e escopo da validação

> **[ESCREVER]** Abra dizendo o que este capítulo se propõe a provar e, principalmente, o que ele NÃO se propõe. Sugestão de recorte: o objetivo é verificar se o motor preditivo (a) recupera corretamente a estrutura de uma série de demanda, (b) produz erro mensurável e reprodutível, e (c) converte a previsão em parâmetros de reposição coerentes. Deixe explícito que a validação externa sobre vendas reais de um mercado fica como trabalho futuro — declarar isso aqui, na abertura, é mais forte do que ser cobrado depois.

> **[ESCREVER]** Explique a escolha por dados sintéticos e antecipe a crítica de circularidade: como a estrutura verdadeira dos dados é conhecida por construção, é possível verificar se o motor a recupera. Trata-se de validação de instrumentação — provar que a régua mede certo — e não de medição do mundo real.


## X.2 Protocolo experimental

### X.2.1 Conjunto de dados

Foram gerados **10 produtos × 365 dias** de histórico diário, com semente fixa (`SEED = 42`), representando perfis de demanda contrastantes de um mercado de bairro.

> **[ESCREVER]** Descreva a fórmula geradora — quantidade = demanda_base × tendência × fator_semanal × ruído — e os fechamentos de domingo (40% de chance) e feriado (60%). Enfatize que o perfil semanal vai de 1,45 no sábado a 0,30 no domingo, porque é essa amplitude que justifica usar modelos sazonais.


### X.2.2 Divisão temporal

A avaliação usa divisão cronológica **80% treino / 20% teste**, resultando em 292 dias de treino (2024-01-01 a 2024-10-18) e 73 dias de teste (2024-10-19 a 2024-12-30).

> **[ESCREVER]** Este é o parágrafo mais importante do capítulo do ponto de vista metodológico. Justifique por que a divisão é por posição cronológica e nunca aleatória: embaralhar colocaria dias posteriores no treino e anteriores no teste, ou seja, o modelo usaria o futuro para prever o passado. O erro medido ficaria artificialmente baixo e sem valor. Cite Hyndman & Athanasopoulos.


### X.2.3 Métricas de avaliação

| Métrica | Fórmula | Unidade | Papel |
|---|---|---|---|
| MAE | média(\|real − previsto\|) | unidades | erro típico, interpretável pelo lojista |
| RMSE | raiz(média((real − previsto)²)) | unidades | penaliza erros grandes |
| MAPE | média(\|real − previsto\| / real) × 100 | % | adimensional, permite comparar produtos |

> **[ESCREVER]** Justifique por que a SELEÇÃO do modelo usa MAPE: é a única das três que é comparável entre produtos de escalas diferentes, e alimenta o KPI de acurácia do dashboard (100 − MAPE). Registre também o tratamento de dias sem venda: o MAPE é calculado apenas sobre observações com valor real maior que zero, para evitar divisão por zero, enquanto RMSE e MAE consideram todos os dias — logo, as três não são calculadas exatamente sobre o mesmo conjunto de pontos.


### X.2.4 Equivalência com o sistema em produção

> **[ESCREVER]** Registre a decisão de projeto: a camada de análise importa os módulos de produção (app/services/) em vez de reimplementar as fórmulas. Consequência: não existe uma segunda implementação que possa divergir da primeira, e os números deste capítulo são, por construção, os que o endpoint /predict devolve em execução. Isso é uma garantia de validade interna e vale ser afirmado explicitamente.


## X.3 Caracterização do conjunto de dados

**Tabela X.1** — Estatística descritiva dos 10 produtos

| id | Produto | Variab. | Média/dia | σ | CV | % zeros |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Arroz 5kg | 0.15 | 12.40 | 5.46 | 0.47 | 6.0% |
| 2 | Feijão Carioca 1kg | 0.15 | 8.27 | 3.86 | 0.51 | 8.5% |
| 3 | Leite Integral 1L | 0.35 | 21.52 | 11.62 | 0.58 | 7.7% |
| 4 | Pão Francês | 0.40 | 30.58 | 18.24 | 0.64 | 6.8% |
| 5 | Banana Prata kg | 0.45 | 16.53 | 10.57 | 0.68 | 6.3% |
| 6 | Sal Refinado 1kg | 0.05 | 5.21 | 2.29 | 0.48 | 7.7% |
| 7 | Açúcar Cristal 1kg | 0.05 | 7.27 | 3.21 | 0.48 | 7.4% |
| 8 | Óleo de Soja 900ml | 0.20 | 6.09 | 2.89 | 0.51 | 6.8% |
| 9 | Frango Inteiro kg | 0.30 | 10.44 | 5.45 | 0.56 | 7.4% |
| 10 | Refrigerante 2L | 0.25 | 14.49 | 7.11 | 0.53 | 6.8% |

> **[ESCREVER]** Comente a amplitude de perfis: de Sal Refinado (variabilidade 0,05, quase determinístico) a Banana Prata (0,45, altamente errático). Faça a observação não óbvia: o CV nunca fica muito baixo, mesmo no Sal, porque a própria oscilação semanal já produz dispersão — ou seja, parte do 'desvio' de cada produto é estrutura previsível, não ruído, e é justamente essa parte que os modelos conseguem capturar. Essa distinção prepara a leitura dos MAPEs altos mais adiante.


## X.4 Análise exploratória: existe sinal previsível?

**Figura X.1** — `analysis/figures/g1_decomposicao_produto1.png` (Arroz 5kg)  
**Figura X.2** — `analysis/figures/g1_decomposicao_produto5.png` (Banana Prata kg)

> **[ESCREVER]** Explique a decomposição aditiva de período 7 e o que ela prova: se a componente sazonal tem amplitude nítida e regular e o resíduo é pequeno frente ao sinal, existe estrutura a ser capturada — o que justifica usar modelos de série temporal em vez de uma média simples. Contraste as duas figuras: mesma estrutura sazonal nos dois produtos, mas resíduo de amplitude muito maior na Banana. Esse contraste antecipa e explica a diferença de MAPE entre eles.


## X.5 Resultados comparativos

### X.5.1 Métricas por produto e modelo

**Tabela X.2** — MAPE, RMSE e MAE por produto × modelo (janela de teste)

| id | Produto | Modelo | MAPE (%) | RMSE | MAE | Vencedor |
|---:|---|---|---:|---:|---:|:---:|
| 1 | Arroz 5kg | holt_winters | 12.4887 | 2.2522 | 1.7583 |  |
| 1 | Arroz 5kg | prophet | 12.4606 | 2.2451 | 1.7488 | **✔** |
| 2 | Feijão Carioca 1kg | holt_winters | 13.2639 | 1.4155 | 1.1231 | **✔** |
| 2 | Feijão Carioca 1kg | prophet | 13.3540 | 1.4191 | 1.1279 |  |
| 3 | Leite Integral 1L | holt_winters | 42.0977 | 9.1086 | 7.4113 | **✔** |
| 3 | Leite Integral 1L | prophet | 42.7739 | 9.1659 | 7.4487 |  |
| 4 | Pão Francês | holt_winters | 81.2510 | 16.0704 | 11.9428 | **✔** |
| 4 | Pão Francês | prophet | 84.1720 | 16.2863 | 12.1403 |  |
| 5 | Banana Prata kg | holt_winters | 66.6753 | 8.0727 | 6.1818 |  |
| 5 | Banana Prata kg | prophet | 66.6271 | 8.0730 | 6.1818 | **✔** |
| 6 | Sal Refinado 1kg | holt_winters | 9.6252 | 1.0853 | 0.5875 |  |
| 6 | Sal Refinado 1kg | prophet | 9.5655 | 1.0844 | 0.5851 | **✔** |
| 7 | Açúcar Cristal 1kg | holt_winters | 8.8945 | 1.7412 | 0.9415 | **✔** |
| 7 | Açúcar Cristal 1kg | prophet | 9.0065 | 1.7404 | 0.9452 |  |
| 8 | Óleo de Soja 900ml | holt_winters | 21.4335 | 2.1356 | 1.4210 | **✔** |
| 8 | Óleo de Soja 900ml | prophet | 21.4615 | 2.1373 | 1.4216 |  |
| 9 | Frango Inteiro kg | holt_winters | 25.3962 | 3.7548 | 2.6511 |  |
| 9 | Frango Inteiro kg | prophet | 25.2870 | 3.7482 | 2.6434 | **✔** |
| 10 | Refrigerante 2L | holt_winters | 28.2987 | 4.7083 | 3.3909 | **✔** |
| 10 | Refrigerante 2L | prophet | 28.3084 | 4.7087 | 3.3912 |  |

**Placar:** Holt-Winters venceu em **6** produtos, Prophet em **4**.

**Tabela X.3** — Margem de MAPE entre os dois modelos, por produto

| Produto | Margem (pontos percentuais) |
|---|---:|
| 10 — Refrigerante 2L | 0.0097 |
| 8 — Óleo de Soja 900ml | 0.0280 |
| 1 — Arroz 5kg | 0.0281 |
| 5 — Banana Prata kg | 0.0482 |
| 6 — Sal Refinado 1kg | 0.0597 |
| 2 — Feijão Carioca 1kg | 0.0901 |
| 9 — Frango Inteiro kg | 0.1092 |
| 7 — Açúcar Cristal 1kg | 0.1120 |
| 3 — Leite Integral 1L | 0.6762 |
| 4 — Pão Francês | 2.9210 |

> **[ESCREVER]** Aqui está o resultado central e ele exige honestidade. NÃO defenda que a seleção do melhor modelo trouxe ganho expressivo: os seus próprios números mostram que em 9 dos 10 produtos a diferença é menor que 0,7 pp, e em cinco deles menor que 0,06 pp. A leitura correta é: nenhum modelo domina o outro neste conjunto de dados. A explicação do porquê vem na seção X.8 — anuncie isso aqui para o leitor não achar que ficou sem resposta.

> **[ESCREVER]** Comente a amplitude do MAPE entre os 20 pares produto × modelo — de 8,89% a 84,17% — e conecte com a Tabela X.1: os produtos de maior variabilidade são os de maior erro. Isso é propriedade do dado, não falha do método. Mencione que o sistema trata esse caso: quando o MAPE do vencedor passa de 50%, o motor preenche o campo `aviso` e a interface sinaliza previsão de baixa confiança.


### X.5.2 Ajuste fora da amostra

**Figura X.3** — `g2_previsto_real_produto1.png`  
**Figura X.4** — `g2_previsto_real_produto5.png`

> **[ESCREVER]** Descreva o que o gráfico mostra: a linha preta é o realizado na janela de teste; as tracejadas são o que cada modelo previu sem nunca ter visto esses dias. Observe que as curvas dos dois modelos são praticamente indistinguíveis — evidência visual do que a Tabela X.3 mostra numericamente.


### X.5.3 Comportamento do erro ao longo do horizonte

**Figura X.5** — `g4_erro_horizonte_produto1.png`  
**Figura X.6** — `g4_erro_horizonte_produto5.png`

> **[ESCREVER]** Relacione com a equação de previsão do Holt-Winters: como ŷ(t+h) = L_t + h·b_t + sazonal, qualquer erro na estimativa da tendência é multiplicado por h e se acumula com o horizonte. Use isso para justificar o horizonte de 30 dias adotado no sistema, alinhado ao ciclo mensal de recálculo.


## X.6 Diagnóstico de resíduos

**Figura X.7** — `g5_residuos_produto1_holt_winters.png`  
**Figura X.8** — `g5_residuos_produto5_holt_winters.png`

> **[ESCREVER]** Este é o teste decisivo de qualidade do ajuste, e vale explicar o critério antes de aplicá-lo: resíduo = real − previsto, e um bom modelo deixa resíduos centrados em zero, sem padrão temporal e sem autocorrelação — aproximadamente ruído branco. Diga explicitamente o que refutaria a conclusão: um pico na ACF no lag 7 indicaria sazonalidade semanal não capturada. Como não há, conclui-se que o modelo extraiu a estrutura disponível e o que sobrou é ruído irredutível.


## X.7 Robustez: backtesting rolling-origin

> **[ESCREVER]** Justifique a necessidade: uma única divisão treino/teste pode ser favorável por acaso. No backtesting rolling-origin o treino cresce a cada dobra e a previsão é feita sobre o bloco seguinte de 14 dias, repetindo o experimento 5 vezes.


**Tabela X.4** — Backtesting de Arroz 5kg (id 1)

| Origem da janela | MAPE HW (%) | RMSE HW | MAPE Prophet (%) | RMSE Prophet |
|---|---:|---:|---:|---:|
| 2024-10-22 | 11.84 | 1.82 | 11.85 | 1.80 |
| 2024-11-05 | 12.42 | 2.82 | 12.48 | 2.83 |
| 2024-11-19 | 11.35 | 1.50 | 11.34 | 1.50 |
| 2024-12-03 | 15.65 | 2.36 | 15.52 | 2.36 |
| 2024-12-17 | 10.50 | 2.11 | 10.42 | 2.10 |

**Tabela X.5** — Backtesting de Banana Prata kg (id 5)

| Origem da janela | MAPE HW (%) | RMSE HW | MAPE Prophet (%) | RMSE Prophet |
|---|---:|---:|---:|---:|
| 2024-10-22 | 34.13 | 6.30 | 34.30 | 6.37 |
| 2024-11-05 | 50.95 | 7.90 | 50.77 | 7.87 |
| 2024-11-19 | 188.42 | 11.64 | 185.02 | 11.60 |
| 2024-12-03 | 31.91 | 6.59 | 31.82 | 6.62 |
| 2024-12-17 | 30.23 | 7.68 | 30.21 | 7.67 |

**Figura X.9** — `g6_backtesting_produto1.png`  
**Figura X.10** — `g6_backtesting_produto5.png`

> **[ESCREVER]** Leitura do produto 1: MAPE entre 10,50% e 15,65% nas cinco dobras — faixa estreita, desempenho consistente, a métrica principal é representativa.

> **[ESCREVER]** Leitura do produto 5: quatro dobras entre 30,2% e 51,0% e uma quinta em 188,4%. NÃO omita essa dobra — analise-a. O RMSE da mesma janela (11,64) está apenas moderadamente acima das demais, o que descarta uma falha catastrófica de previsão; o que houve foi o efeito aritmético do MAPE quando o denominador é pequeno. Declarar e explicar a dobra ruim demonstra domínio do comportamento da métrica e é mais forte do que apresentar só as janelas favoráveis.


## X.8 Análise dos parâmetros ajustados: por que os modelos empatam

**Tabela X.6** — Parâmetros de suavização encontrados pelo otimizador (Holt-Winters)

| id | Produto | α (nível) | β (tendência) | γ (sazonal) |
|---:|---|---:|---:|---:|
| 1 | Arroz 5kg | 0.00000 | 0.00000 | 0.00000 |
| 2 | Feijão Carioca 1kg | 0.00000 | 0.00000 | 0.00000 |
| 3 | Leite Integral 1L | 0.00004 | 0.00004 | 0.00009 |
| 4 | Pão Francês | 0.00202 | 0.00090 | 0.00036 |
| 5 | Banana Prata kg | 0.00001 | 0.00000 | 0.00009 |
| 6 | Sal Refinado 1kg | 0.00000 | 0.00000 | 0.00000 |
| 7 | Açúcar Cristal 1kg | 0.00000 | 0.00000 | 0.00000 |
| 8 | Óleo de Soja 900ml | 0.00000 | 0.00000 | 0.00000 |
| 9 | Frango Inteiro kg | 0.00000 | 0.00000 | 0.00000 |
| 10 | Refrigerante 2L | 0.00000 | 0.00000 | 0.00000 |

> **[ESCREVER]** Esta é a seção mais original do capítulo. Construa o argumento em três passos.
>
> **(1) A evidência.** Em todos os 10 produtos o otimizador convergiu para α ≈ β ≈ γ ≈ 0 — sete deles exatamente zero, os outros três na ordem de 10⁻⁵ a 10⁻³.
>
> **(2) O que isso significa.** Retome a equação de atualização do nível: com α = 0 o termo da nova observação desaparece e sobra L_t = L_(t−1) + b_(t−1). O modelo deixa de ser um filtro adaptativo e degenera para ŷ(t) = L₀ + t·b₀ + s(dia da semana) — uma reta com padrão semanal fixo, estimados uma única vez. Compare com o que o Prophet ajusta neste cenário: tendência linear (sem changepoints ativos, pois não há quebras) mais sazonalidade semanal fixa. **São a mesma família de função.**
>
> **(3) Por que o otimizador chegou lá.** O gerador produz tendência perfeitamente linear e perfil semanal rigorosamente constante. Nesse regime, adaptar-se ao dado recente é prejudicial: toda reação a uma observação individual é reação a ruído puro. O otimizador identificou isso e desligou a adaptação.

> **[ESCREVER]** Feche com a dupla conclusão. Primeiro, isso **valida o motor**: submetido a dados de estrutura conhecida, ele recuperou essa estrutura, inclusive a informação de que ela é estacionária. Segundo, **delimita o alcance do resultado**: o empate entre os modelos é propriedade deste conjunto de dados, não uma verdade geral sobre Holt-Winters e Prophet.
>
> Encerre com a previsão testável — em dados reais, com quebras de patamar e sazonalidade que evolui, espera-se α > 0 e separação de desempenho entre os modelos. É justamente isso que **justifica a decisão arquitetural de manter os dois modelos no sistema** com seleção automática por produto, em vez de fixar um. Amarre essa conclusão ao capítulo de arquitetura.


## X.9 Da previsão à decisão de reposição

> **[ESCREVER]** Faça a transição: prever é meio caminho; o que o lojista precisa é saber quando pedir e quanto manter de reserva. Apresente a fórmula combinada de Ballou — ES = Z · √(LT · σ²_demanda + demanda² · σ²_leadtime) — e destaque que ela considera duas fontes de incerteza simultaneamente, enquanto a fórmula simplificada (1,65 · σ · √LT) ignora a variabilidade do prazo de entrega. Num mercado de bairro, onde o atraso do fornecedor é rotina, essa omissão subdimensiona a reserva. Mencione também que Z = norm.ppf(nível de serviço) é calculado dinamicamente, de modo que alterar o nível de 95% para 99% de fato muda o resultado.


**Tabela X.7** — Parâmetros de reposição calculados pelo motor (lead time = 3 dias, σ_LT = 1,0, nível de serviço = 95%)

| Etapa | Arroz 5kg (id 1) | Banana Prata kg (id 5) |
|---|---|---|
| Modelo vencedor | prophet | prophet |
| Demanda média prevista (un/dia) | 13.092 | 15.267 |
| σ da demanda histórica | 5.459 | 10.573 |
| Z (nível 95%) | 1.6449 | 1.6449 |
| **Estoque de segurança** | **26.56** | **39.22** |
| **Ponto de reposição** | **65.84** | **85.02** |
| Estoque atual | 15 | 200 |
| **Dias até ruptura** | **1.15** | **13.1** |

**Figura X.11** — `g7_reposicao_produto1.png`  
**Figura X.12** — `g7_reposicao_produto5.png`

> **[ESCREVER]** Interprete em termos de negócio: o Arroz tem 15 unidades contra um ponto de reposição de 65.84 — já deveria ter sido pedido, com ruptura estimada em 1.15 dia. A Banana tem 200 unidades contra PR de 85.02, situação confortável. É essa tradução — de erro estatístico para instrução acionável — que sustenta a proposta da plataforma.


## X.10 Limitações e ameaças à validade

> **[ESCREVER]** Introduza dizendo que as limitações abaixo foram identificadas por inspeção do próprio código e são declaradas antes de serem questionadas. Desenvolva cada uma em um parágrafo curto.


| # | Limitação | Natureza |
|---:|---|---|
| 1 | Validação sobre dados sintéticos | prova a metodologia e a instrumentação, não o desempenho em mercado real; risco de circularidade a ser explicitado |
| 2 | Geração multiplicativa × ajuste aditivo | o gerador multiplica os componentes, enquanto os modelos e a decomposição usam modo aditivo; com apenas 20% de crescimento no período o impacto é pequeno, mas é uma incoerência metodológica real |
| 3 | Regressor de promoção não ativado | o campo `is_promocional` não é passado ao Prophet; no dataset atual isso é inócuo, pois a coluna é constante e não tem variância |
| 4 | Mecanismo de feriados do Prophet desativado | o termo h(t) não é usado, apesar de os dados conterem 12 feriados; é um recurso nativo do Prophet sem equivalente no Holt-Winters |
| 5 | σ da demanda calculado sobre a série completa | inclui os dias de loja fechada, o que infla o desvio e, por consequência, o estoque de segurança — escolha conservadora, mas que merece registro |
| 6 | Fragilidade do MAPE com denominadores pequenos | documentado na seção X.7; SMAPE ou MASE seriam alternativas |
| 7 | Corte em zero aplicado de forma assimétrica | a previsão entregue é truncada em zero, mas as métricas usam a previsão bruta |
| 8 | Reprodutibilidade sensível à ordem do catálogo | o gerador consome um único fluxo aleatório sequencialmente; inserir produto no meio da lista desloca as séries seguintes |
| 9 | Sazonalidade anual fora de alcance | 365 dias não permitem estimar ciclo anual — seriam necessários dois ciclos |
| 10 | Ausência de baseline ingênuo | não há comparação contra seasonal naive ou média por dia da semana, o que limita a afirmação sobre o ganho absoluto dos modelos |

> **[ESCREVER]** A limitação nº 10 merece um parágrafo próprio e uma decisão sua: ou você implementa os baselines (é barato — seasonal naive é ŷ(t) = y(t−7)) e fecha a lacuna, ou a declara como trabalho futuro. Dado o achado da seção X.8, há uma hipótese interessante a testar: como o Holt-Winters degenerou para 'média por dia da semana mais tendência', um baseline desse tipo pode empatar com os dois modelos neste dataset.


## X.11 Síntese do capítulo

> **[ESCREVER]** Feche com três a cinco afirmações do que ficou demonstrado, cada uma amarrada à evidência correspondente. Sugestão de esqueleto:
>
> 1. A série de demanda contém sinal previsível — tendência e sazonalidade semanal separáveis do ruído (X.4).
> 2. Os dois modelos generalizam para dados não vistos, com erro que varia por produto conforme a variabilidade intrínseca (X.5).
> 3. O ajuste é adequado: os resíduos não retêm estrutura (X.6) e o desempenho se mantém em janelas independentes (X.7).
> 4. O empate entre os modelos tem explicação mecânica verificável e delimita o alcance do resultado a este conjunto de dados (X.8).
> 5. A previsão se converte em parâmetros de reposição coerentes com a situação de cada produto (X.9).
>
> Encerre indicando o que a validação externa com dados reais deverá verificar.


---

<!-- Fim do esqueleto. Material de apoio: docs/relatorio-modelos-preditivos.pdf (seções 7 a 15). -->
