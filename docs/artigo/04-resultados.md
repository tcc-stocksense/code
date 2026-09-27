<!--
  Numeração de figuras e tabelas é PROVISÓRIA — contínua a partir da seção 3
  (que termina na Figura 4 e na Tabela 2). O script de geração renumera.
  Todos os números vêm de ml-service/analysis/results/dados_documento.json.
-->

# 4 Resultados e discussão

Esta seção apresenta os resultados obtidos sobre o conjunto descrito na
subseção 3.3.3, na ordem em que sustentam o argumento: primeiro o que os dados
contêm, depois o desempenho dos modelos, em seguida a verificação de que esse
desempenho não é acidente da janela escolhida e, por fim, a conversão da
previsão em decisão de reposição.

## 4.1 Perfil do conjunto de dados

**Tabela 3 - Estatística descritiva dos dez produtos**

| id | Produto | Variab. | Média/dia | σ | CV | % zeros |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Arroz 5kg | 0,15 | 12,40 | 5,46 | 0,47 | 6,0% |
| 2 | Feijão Carioca 1kg | 0,15 | 8,27 | 3,86 | 0,51 | 8,5% |
| 3 | Leite Integral 1L | 0,35 | 21,52 | 11,62 | 0,58 | 7,7% |
| 4 | Pão Francês | 0,40 | 30,58 | 18,24 | 0,64 | 6,8% |
| 5 | Banana Prata kg | 0,45 | 16,53 | 10,57 | 0,68 | 6,3% |
| 6 | Sal Refinado 1kg | 0,05 | 5,21 | 2,29 | 0,48 | 7,7% |
| 7 | Açúcar Cristal 1kg | 0,05 | 7,27 | 3,21 | 0,48 | 7,4% |
| 8 | Óleo de Soja 900ml | 0,20 | 6,09 | 2,89 | 0,51 | 6,8% |
| 9 | Frango Inteiro kg | 0,30 | 10,44 | 5,45 | 0,56 | 7,4% |
| 10 | Refrigerante 2L | 0,25 | 14,49 | 7,11 | 0,53 | 6,8% |

Fonte: Autoral, 2026

O conjunto cobre uma faixa ampla de perfis: do sal refinado, de variabilidade
0,05 e comportamento quase determinístico, à banana prata, de variabilidade
0,45 e oscilação acentuada. A média diária considera apenas os dias com venda.

Há uma observação não óbvia na Tabela 3. O coeficiente de variação nunca é
baixo — permanece entre 0,47 e 0,68 mesmo nos produtos de ruído quase nulo. A
razão é que o CV mede a dispersão em torno da média global, e essa dispersão
inclui a oscilação semanal: um produto que vende 1,45 vez a média no sábado e
0,30 no domingo apresenta desvio padrão elevado ainda que não tenha ruído
algum. Parte do que o desvio captura, portanto, é **estrutura previsível**, não
aleatoriedade — e é exatamente essa parte que os modelos conseguem extrair. A
distinção prepara a leitura dos erros percentuais elevados que aparecem adiante.

**Figura 5 - Decomposição da série do produto 1 (Arroz 5kg)**

`[FIGURA: ml-service/analysis/figures/g1_decomposicao_produto1.png]`

Fonte: Autoral, 2026

**Figura 6 - Decomposição da série do produto 5 (Banana Prata kg)**

`[FIGURA: ml-service/analysis/figures/g1_decomposicao_produto5.png]`

Fonte: Autoral, 2026

A decomposição aditiva de período 7 separa cada série em tendência,
sazonalidade e resíduo. As Figuras 5 e 6 respondem à pergunta que precede
qualquer modelagem: existe sinal a capturar? Nos dois produtos a componente
sazonal tem amplitude nítida e período regular, o que confirma que a estrutura
semanal é recuperável e justifica o emprego de modelos sazonais em lugar de uma
média simples.

O contraste entre as duas figuras antecipa o resultado principal. A estrutura
sazonal é a mesma; o que difere é a amplitude do resíduo, muito maior na banana.
Como o resíduo é, por definição, a parcela que nenhum modelo pode prever, a
diferença de erro entre esses dois produtos está determinada antes de qualquer
modelo ser treinado.

## 4.2 Acurácia dos modelos e ganho sobre o baseline

**Tabela 4 - MAPE, RMSE e MAE por produto e modelo (janela de teste)**

| id | Produto | Modelo | MAPE (%) | RMSE | MAE | Vencedor |
|---:|---|---|---:|---:|---:|:---:|
| 1 | Arroz 5kg | Holt-Winters | 12,4887 | 2,2522 | 1,7583 | |
| 1 | Arroz 5kg | Prophet | 12,4606 | 2,2451 | 1,7488 | ✔ |
| 2 | Feijão Carioca 1kg | Holt-Winters | 13,2639 | 1,4155 | 1,1231 | ✔ |
| 2 | Feijão Carioca 1kg | Prophet | 13,3540 | 1,4191 | 1,1279 | |
| 3 | Leite Integral 1L | Holt-Winters | 42,0977 | 9,1086 | 7,4113 | ✔ |
| 3 | Leite Integral 1L | Prophet | 42,7739 | 9,1659 | 7,4487 | |
| 4 | Pão Francês | Holt-Winters | 81,2510 | 16,0704 | 11,9428 | ✔ |
| 4 | Pão Francês | Prophet | 84,1720 | 16,2863 | 12,1403 | |
| 5 | Banana Prata kg | Holt-Winters | 66,6753 | 8,0727 | 6,1818 | |
| 5 | Banana Prata kg | Prophet | 66,6271 | 8,0730 | 6,1818 | ✔ |
| 6 | Sal Refinado 1kg | Holt-Winters | 9,6252 | 1,0853 | 0,5875 | |
| 6 | Sal Refinado 1kg | Prophet | 9,5655 | 1,0844 | 0,5851 | ✔ |
| 7 | Açúcar Cristal 1kg | Holt-Winters | 8,8945 | 1,7412 | 0,9415 | ✔ |
| 7 | Açúcar Cristal 1kg | Prophet | 9,0065 | 1,7404 | 0,9452 | |
| 8 | Óleo de Soja 900ml | Holt-Winters | 21,4335 | 2,1356 | 1,4210 | ✔ |
| 8 | Óleo de Soja 900ml | Prophet | 21,4615 | 2,1373 | 1,4216 | |
| 9 | Frango Inteiro kg | Holt-Winters | 25,3962 | 3,7548 | 2,6511 | |
| 9 | Frango Inteiro kg | Prophet | 25,2870 | 3,7482 | 2,6434 | ✔ |
| 10 | Refrigerante 2L | Holt-Winters | 28,2987 | 4,7083 | 3,3909 | ✔ |
| 10 | Refrigerante 2L | Prophet | 28,3084 | 4,7087 | 3,3912 | |

Fonte: Autoral, 2026

O Holt-Winters venceu em seis produtos e o Prophet em quatro. O placar, isolado,
sugeriria leve vantagem do primeiro — leitura que a Tabela 5 desautoriza.

**Tabela 5 - Margem de MAPE entre Holt-Winters e Prophet, por produto**

| Produto | Margem (pontos percentuais) |
|---|---:|
| Refrigerante 2L | 0,0097 |
| Óleo de Soja 900ml | 0,0280 |
| Arroz 5kg | 0,0281 |
| Banana Prata kg | 0,0482 |
| Sal Refinado 1kg | 0,0597 |
| Feijão Carioca 1kg | 0,0901 |
| Frango Inteiro kg | 0,1092 |
| Açúcar Cristal 1kg | 0,1120 |
| Leite Integral 1L | 0,6762 |
| Pão Francês | 2,9210 |

Fonte: Autoral, 2026

Em nove dos dez produtos a diferença entre os modelos é inferior a 0,7 ponto
percentual, e em cinco deles inferior a 0,06 — magnitude sem qualquer
significado operacional para um lojista. Apenas o pão francês apresenta margem
superior a um ponto. **Nenhum dos dois modelos domina o outro neste conjunto de
dados**, e apresentar o placar de 6 × 4 como vantagem do Holt-Winters seria
sobreinterpretar ruído. A explicação mecânica desse empate é desenvolvida na
subseção 4.5.

Esse resultado, porém, deixa em aberto a pergunta mais importante: se os dois
modelos são equivalentes entre si, algum deles é melhor que não modelar nada? É
o que a Tabela 6 responde, comparando o modelo vencedor de cada produto ao
baseline ingênuo sazonal definido pela Equação (6).

**Tabela 6 - Ganho do modelo vencedor sobre o baseline ingênuo sazonal**

| id | Produto | Vencedor | MAPE venc. (%) | MAPE ingênuo (%) | Ganho (pp) | Redução |
|---:|---|---|---:|---:|---:|---:|
| 1 | Arroz 5kg | Prophet | 12,46 | 27,30 | 14,84 | 54,4% |
| 2 | Feijão Carioca 1kg | Holt-Winters | 13,26 | 29,02 | 15,76 | 54,3% |
| 3 | Leite Integral 1L | Holt-Winters | 42,10 | 52,09 | 9,99 | 19,2% |
| 4 | Pão Francês | Holt-Winters | 81,25 | 93,17 | 11,91 | 12,8% |
| 5 | Banana Prata kg | Prophet | 66,63 | 99,14 | 32,52 | 32,8% |
| 6 | Sal Refinado 1kg | Prophet | 9,57 | 31,25 | 21,68 | 69,4% |
| 7 | Açúcar Cristal 1kg | Holt-Winters | 8,89 | 22,18 | 13,28 | 59,9% |
| 8 | Óleo de Soja 900ml | Holt-Winters | 21,43 | 36,23 | 14,80 | 40,8% |
| 9 | Frango Inteiro kg | Prophet | 25,29 | 49,93 | 24,65 | 49,4% |
| 10 | Refrigerante 2L | Holt-Winters | 28,30 | 37,95 | 9,65 | 25,4% |

Fonte: Autoral, 2026

O motor supera o baseline em **dez dos dez produtos**, com redução mediana de
erro de 45,1% — mínimo de 12,8% no pão francês, máximo de 69,4% no sal refinado.
Não há exceção no catálogo. É esse resultado, e não o placar entre os dois
modelos, que responde à primeira parte do problema de pesquisa.

A Tabela 6 também reenquadra os erros percentuais elevados da Tabela 4. Um MAPE
de 81,25% no pão francês, lido isoladamente, sugere falha do método; comparado
aos 93,17% da regra ingênua sobre a mesma série, revela que o erro é alto porque
a série é intrinsecamente difícil — e que o modelo, ainda assim, extrai sinal
dela. O mesmo vale para a banana prata, que cai de 99,14% para 66,63%. O erro
elevado é propriedade do dado, não do método, e o sistema trata esse caso: acima
de 50% de MAPE o motor marca a previsão como de baixa confiança.

**Figura 7 - Previsto × real na janela de teste — produto 1 (Arroz 5kg)**

`[FIGURA: ml-service/analysis/figures/g2_previsto_real_produto1.png]`

Fonte: Autoral, 2026

**Figura 8 - Previsto × real na janela de teste — produto 5 (Banana Prata kg)**

`[FIGURA: ml-service/analysis/figures/g2_previsto_real_produto5.png]`

Fonte: Autoral, 2026

As Figuras 7 e 8 mostram o realizado na janela de teste contra o que cada
abordagem previu sem jamais ter visto esses dias. As curvas do Holt-Winters e do
Prophet são visualmente indistinguíveis — evidência gráfica do que a Tabela 5
expressa numericamente —, enquanto a curva do baseline se descola das demais,
acompanhando o ruído da última semana de treino em vez do padrão médio.

## 4.3 Robustez e diagnóstico

Uma única divisão treino/teste pode favorecer um modelo por acaso. As Tabelas 7
e 8 repetem a avaliação em cinco janelas independentes, com origem móvel e
blocos de teste de 14 dias.

**Tabela 7 - Backtesting de origem móvel — produto 1 (Arroz 5kg)**

| Origem | MAPE HW (%) | MAPE Prophet (%) | MAPE ingênuo (%) |
|---|---:|---:|---:|
| 2024-10-22 | 11,84 | 11,85 | 16,68 |
| 2024-11-05 | 12,42 | 12,48 | 13,30 |
| 2024-11-19 | 11,35 | 11,34 | 28,44 |
| 2024-12-03 | 15,65 | 15,52 | 20,29 |
| 2024-12-17 | 10,50 | 10,42 | 17,54 |

Fonte: Autoral, 2026

**Tabela 8 - Backtesting de origem móvel — produto 5 (Banana Prata kg)**

| Origem | MAPE HW (%) | RMSE HW | MAPE Prophet (%) | MAPE ingênuo (%) | RMSE ingênuo |
|---|---:|---:|---:|---:|---:|
| 2024-10-22 | 34,13 | 6,30 | 34,30 | 53,59 | 10,96 |
| 2024-11-05 | 50,95 | 7,90 | 50,77 | 64,09 | 11,22 |
| 2024-11-19 | 188,42 | 11,64 | 185,02 | 159,97 | 13,92 |
| 2024-12-03 | 31,91 | 6,59 | 31,82 | 59,78 | 12,15 |
| 2024-12-17 | 30,23 | 7,68 | 30,21 | 59,60 | 10,52 |

Fonte: Autoral, 2026

No produto 1 o desempenho é consistente: o MAPE dos modelos varia entre 10,50% e
15,65% nas cinco dobras, faixa estreita que confirma a representatividade da
métrica principal, e ambos superam o baseline em todas as janelas.

O produto 5 exige análise mais cuidadosa, e a dobra de 19 de novembro não deve
ser omitida. Nela o MAPE do Holt-Winters salta para 188,42% — quatro vezes o
valor das demais janelas. Dois indícios mostram que se trata de artefato da
métrica, e não de falha de previsão. O primeiro é que o RMSE da mesma janela
(11,64) fica apenas moderadamente acima das outras dobras, o que exclui um erro
de magnitude catastrófica em unidades. O segundo é mais revelador: nessa janela
o baseline ingênuo apresenta **MAPE menor** que o dos modelos (159,97%) e, ao
mesmo tempo, **RMSE maior** (13,92 contra 11,64). As duas métricas apontam
vencedores opostos sobre exatamente os mesmos dados.

Essa contradição é diagnóstica. Ela ocorre porque a janela concentra dias de
venda muito baixa, e o MAPE divide o erro pelo valor real: um erro de três
unidades sobre uma venda de duas produz 150% de erro percentual, enquanto o
mesmo desvio sobre uma venda de trinta produz 10%. A métrica passa a medir o
tamanho do denominador, não a qualidade da previsão. Declarar e explicar a dobra
desfavorável é mais sólido que apresentar apenas as janelas convenientes, e
reforça a limitação do MAPE já registrada na subseção 3.5.2.

**Figura 9 - Diagnóstico de resíduos — produto 1 (Holt-Winters)**

`[FIGURA: ml-service/analysis/figures/g5_residuos_produto1_holt_winters.png]`

Fonte: Autoral, 2026

O diagnóstico de resíduos verifica se o modelo extraiu toda a estrutura
disponível. Um ajuste adequado deixa resíduos centrados em zero, sem padrão
temporal e sem autocorrelação — aproximadamente ruído branco. O critério de
refutação é explícito: um pico na função de autocorrelação no atraso 7
indicaria sazonalidade semanal não capturada. A Figura 9 não apresenta esse
pico, o que sustenta a conclusão de que o que restou é ruído irredutível.

## 4.4 Da previsão à decisão de reposição

A previsão só tem valor quando convertida em instrução operacional. A Tabela 9
apresenta o encadeamento completo do cálculo para dois produtos de situação
oposta, com prazo de entrega de três dias, variabilidade de prazo 1,0 e nível de
serviço de 95%.

**Tabela 9 - Parâmetros de reposição calculados pelo motor**

| Etapa | Arroz 5kg | Banana Prata kg |
|---|---:|---:|
| Modelo vencedor | Prophet | Prophet |
| Demanda média prevista (un/dia) | 13,092 | 15,267 |
| σ da demanda histórica | 5,459 | 10,573 |
| Z (nível de serviço 95%) | 1,6449 | 1,6449 |
| **Estoque de segurança** | **26,56** | **39,22** |
| **Ponto de reposição** | **65,84** | **85,02** |
| Estoque atual | 15 | 200 |
| **Dias até ruptura** | **1,15** | **13,10** |

Fonte: Autoral, 2026

Os dois produtos têm demanda média semelhante — 13,1 e 15,3 unidades por dia —,
mas estoques de segurança que diferem em quase 50%. A diferença vem inteiramente
da variabilidade: o desvio padrão da banana é praticamente o dobro do arroz, e a
Equação (7) converte essa incerteza em reserva. É o comportamento esperado de um
dimensionamento por nível de serviço — proteger mais o que oscila mais.

A leitura de negócio é imediata. O arroz tem 15 unidades contra um ponto de
reposição de 65,84: já deveria ter sido pedido, com ruptura estimada para pouco
mais de um dia. A banana tem 200 unidades contra 85,02 e está confortável por
cerca de treze dias. É essa tradução — de erro estatístico para instrução
acionável — que sustenta a proposta da plataforma.

**Figura 10 - Projeção de estoque e ponto de reposição — produto 1**

`[FIGURA: ml-service/analysis/figures/g7_reposicao_produto1.png]`

Fonte: Autoral, 2026

## 4.5 Discussão

**Por que os modelos empatam.** A Tabela 10 traz os parâmetros de suavização
encontrados pelo otimizador do Holt-Winters.

**Tabela 10 - Parâmetros de suavização ajustados (Holt-Winters)**

| id | Produto | α (nível) | β (tendência) | γ (sazonal) |
|---:|---|---:|---:|---:|
| 1 | Arroz 5kg | 0,00000 | 0,00000 | 0,00000 |
| 2 | Feijão Carioca 1kg | 0,00000 | 0,00000 | 0,00000 |
| 3 | Leite Integral 1L | 0,00004 | 0,00004 | 0,00009 |
| 4 | Pão Francês | 0,00202 | 0,00090 | 0,00036 |
| 5 | Banana Prata kg | 0,00001 | 0,00000 | 0,00009 |
| 6 | Sal Refinado 1kg | 0,00000 | 0,00000 | 0,00000 |
| 7 | Açúcar Cristal 1kg | 0,00000 | 0,00000 | 0,00000 |
| 8 | Óleo de Soja 900ml | 0,00000 | 0,00000 | 0,00000 |
| 9 | Frango Inteiro kg | 0,00000 | 0,00000 | 0,00000 |
| 10 | Refrigerante 2L | 0,00000 | 0,00000 | 0,00000 |

Fonte: Autoral, 2026

Em todos os dez produtos o otimizador convergiu para α ≈ β ≈ γ ≈ 0 — sete deles
exatamente zero, os demais na ordem de 10⁻⁵ a 10⁻³. O significado é direto: na
equação de atualização do nível, com α = 0 o termo da nova observação
desaparece, restando `L(t) = L(t−1) + b(t−1)`. O modelo deixa de ser um filtro
adaptativo e degenera para `ŷ(t) = L₀ + t·b₀ + s(dia da semana)` — uma reta com
padrão semanal fixo, ambos estimados uma única vez. É precisamente a mesma
família de função que o Prophet ajusta neste cenário: tendência linear, sem
pontos de quebra ativos porque não há quebras, somada a sazonalidade semanal
fixa. Os dois modelos empatam porque, aqui, são a mesma função.

O otimizador chegou a esse ponto por uma razão identificável. O gerador produz
tendência perfeitamente linear e perfil semanal rigorosamente constante; nesse
regime, adaptar-se ao dado recente é prejudicial, porque toda reação a uma
observação individual é reação a ruído puro. O otimizador identificou isso e
desligou a adaptação.

**O que isso valida e o que delimita.** O achado valida o motor em sentido
forte: submetido a dados de estrutura conhecida, ele recuperou essa estrutura,
inclusive a informação de que ela é estacionária. Ao mesmo tempo, delimita o
alcance do resultado — o empate é propriedade deste conjunto de dados, não uma
verdade geral sobre Holt-Winters e Prophet.

**Por que o baseline perde por tanto.** Há uma objeção natural ao parágrafo
anterior: se o Holt-Winters degenerou para tendência mais média por dia da
semana, por que não empata também com a regra ingênua, que é igualmente
simples? A Tabela 6 mostra que não empata — a diferença é de 45,1% de erro na
mediana. A razão está em *como* cada um estima o perfil semanal. O baseline
repete uma única semana, ou seja, uma realização ruidosa por dia da semana; o
Holt-Winters estima esse perfil a partir das aproximadamente quarenta semanas do
conjunto de treino, e a média entre elas cancela o ruído. O α ≈ 0 não tornou o
modelo trivial: tornou-o um estimador de perfil semanal, e estimar bem esse
perfil é justamente onde está o ganho medido.

**Consequência arquitetural.** O conjunto desses resultados produz uma previsão
testável. Em dados reais, com quebras de patamar, mudanças de mix e sazonalidade
que evolui, espera-se α > 0 e, com ele, separação de desempenho entre os dois
modelos. É essa expectativa que justifica a decisão de manter ambos no sistema,
com seleção automática por produto, em vez de fixar aquele que venceu por margem
desprezível em um cenário estacionário. A arquitetura foi dimensionada para o
caso em que os modelos divergem, e não para o caso observado aqui — no qual, por
construção dos dados, eles não poderiam divergir.
