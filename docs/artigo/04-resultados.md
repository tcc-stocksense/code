<!--
  Numeração de figuras e tabelas é PROVISÓRIA — contínua a partir da seção 3
  (que termina na Figura 7 e na Tabela 3). O script de geração renumera.
  Todos os números vêm de ml-service/analysis/results/dados_documento.json.
-->

# 4 Resultados e discussão

Esta seção apresenta os resultados na ordem em que sustentam o argumento:
primeiro o que o levantamento de campo revelou sobre o problema, depois o que o
conjunto de dados de validação contém, em seguida o desempenho dos modelos e a
verificação de que esse desempenho não é acidente da janela escolhida e, por
fim, a conversão da previsão em decisão de reposição.

## 4.1 Caracterização do campo

O levantamento descrito na subseção 3.3.1 reuniu sete estabelecimentos, quatro
de porte médio, dois de porte pequeno e um de porte grande. A Tabela 4 consolida
as respostas fechadas.

**Tabela 4 - Síntese do levantamento de campo (n = 7)**

| Dimensão | Resposta | Freq. |
|---|---|---:|
| Critério de decisão de compra | Inspeção visual da prateleira | 7/7 |
| | Espera o produto acabar ou quase acabar | 2/7 |
| | Experiência, intuição | 2/7 |
| | Relatório ou lista de compra | 1/7 |
| Controle de estoque | Software com registro automático | 3/7 |
| | Controle manual (caderno, memória) | 3/7 |
| | Software com atualização manual | 1/7 |
| Exporta vendas por produto e por dia | Sim | 4/7 |
| Número de fornecedores | Mais de seis | 7/7 |
| Frequência de ruptura | Raramente | 4/7 |
| | Algumas vezes por mês | 3/7 |
| Sazonalidade percebida | Fim de mês, dia de pagamento | 6/7 |
| | Natal e Ano Novo | 5/7 |
| | Verão | 3/7 |
| Tempo semanal dedicado ao estoque | Mais de cinco horas | 3/7 |
| | Uma a duas horas | 3/7 |
| Perda mensal estimada | R$ 100 a R$ 300 | 3/7 |
| | R$ 600 a R$ 1.000 | 2/7 |
| | R$ 300 a R$ 600 | 1/7 |
| Adotaria um sistema de alerta de reposição | Sim, dependendo do funcionamento | 4/7 |
| | Sim, com certeza | 2/7 |
| | Talvez, precisaria ver funcionando | 1/7 |

Fonte: Autoral, 2026

O resultado mais nítido é a unanimidade do critério de decisão: **os sete
estabelecimentos decidem a compra olhando a prateleira**. Nenhum outro item do
questionário obteve concordância total. Isso converte a premissa da "gestão
intuitiva", que a literatura do setor descreve de forma geral, em observação
direta sobre a população de interesse. Note-se que a inspeção visual convive com
a informatização: entre os quatro estabelecimentos que possuem algum software,
todos continuam decidindo pela prateleira, e apenas um menciona relatório como
gatilho. O sistema existe e não participa da decisão — convergência direta com o
achado de Ferreira e Mota (2022).

Três respostas calibraram decisões de projeto que, de outro modo, teriam sido
arbitradas.

A primeira é o **formato de entrada**. Quatro dos sete conseguem visualizar e
exportar vendas por produto e por dia, o que torna a planilha eletrônica um
veículo de ingestão viável para a maioria — e, para os três que mantêm controle
manual, define o caminho de adoção: digitar o histórico nos modelos fornecidos.

A segunda é o **prazo de entrega**. Os prazos relatados para o fornecedor
principal variam de um a dez dias, com média de 3,9 e mediana de 2,0. O valor
padrão de três dias adotado pelo motor na ausência das planilhas opcionais situa-
se entre as duas medidas de tendência central, o que o torna uma escolha
defensável e não arbitrária.

A terceira diz respeito à **variabilidade do prazo**, e exige precisão. A
dispersão observada acima é *entre estabelecimentos*, não a oscilação do prazo de
um mesmo fornecedor ao longo do tempo — que é a grandeza exigida pela Equação
(1), e que o levantamento não mediu. O que ele sustenta é mais modesto e ainda
assim relevante: num universo em que **todos** os sete trabalham com mais de seis
fornecedores e os prazos praticados diferem em uma ordem de grandeza, tratar o
prazo de entrega como constante é insustentável. É o argumento empírico para a
formulação completa de Ballou (subseção 3.5.5).

Dois achados contrariam decisões do projeto, e registrá-los é mais honesto que
omiti-los.

O primeiro é a **sazonalidade**. Seis dos sete respondentes apontam o fim de mês
e o dia de pagamento como o período de maior variação — um ciclo **mensal**. O
conjunto de dados sintético sobre o qual os modelos foram avaliados reproduz
apenas o ciclo **semanal**. A estrutura de demanda mais citada em campo,
portanto, não está representada no experimento, limitação retomada na seção 5.

O segundo é a **dor principal**. Perguntados sobre o único problema de estoque
que gostariam de resolver, três dos sete citam o controle de validade, e nenhum
cita previsão de demanda. É o módulo que foi deliberadamente retirado do escopo
(subseção 3.4.4). A decisão continua justificada pelo recorte do trabalho — a
pergunta de pesquisa é sobre previsão —, mas o levantamento indica que a
prioridade percebida pelo usuário é outra, e isso tem consequência para a adoção.

Essa tensão aparece na última linha da Tabela 4: apenas dois dos sete adotariam o
sistema sem reservas, enquanto quatro condicionam a adoção a ver o
funcionamento. A disposição existe, mas não é entusiasmo — e nenhum teste de uso
foi conduzido para qualificá-la, o que delimita o alcance desta subseção.

## 4.2 Perfil do conjunto de dados

**Tabela 5 - Estatística descritiva dos dez produtos**

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

Há uma observação não óbvia na Tabela 5. O coeficiente de variação nunca é
baixo — permanece entre 0,47 e 0,68 mesmo nos produtos de ruído quase nulo. A
razão é que o CV mede a dispersão em torno da média global, e essa dispersão
inclui a oscilação semanal: um produto que vende 1,45 vez a média no sábado e
0,30 no domingo apresenta desvio padrão elevado ainda que não tenha ruído
algum. Parte do que o desvio captura, portanto, é **estrutura previsível**, não
aleatoriedade — e é exatamente essa parte que os modelos conseguem extrair. A
distinção prepara a leitura dos erros percentuais elevados que aparecem adiante.

**Figura 8 - Decomposição da série do produto 1 (Arroz 5kg)**

`[FIGURA: ml-service/analysis/figures/g1_decomposicao_produto1.png]`

Fonte: Autoral, 2026

**Figura 9 - Decomposição da série do produto 5 (Banana Prata kg)**

`[FIGURA: ml-service/analysis/figures/g1_decomposicao_produto5.png]`

Fonte: Autoral, 2026

A decomposição aditiva de período 7 separa cada série em tendência,
sazonalidade e resíduo. As Figuras 8 e 9 respondem à pergunta que precede
qualquer modelagem: existe sinal a capturar? Nos dois produtos a componente
sazonal tem amplitude nítida e período regular, o que confirma que a estrutura
semanal é recuperável e justifica o emprego de modelos sazonais em lugar de uma
média simples.

O contraste entre as duas figuras antecipa o resultado principal. A estrutura
sazonal é a mesma; o que difere é a amplitude do resíduo, muito maior na banana.
Como o resíduo é, por definição, a parcela que nenhum modelo pode prever, a
diferença de erro entre esses dois produtos está determinada antes de qualquer
modelo ser treinado.

## 4.3 Acurácia dos modelos e ganho sobre o baseline

**Tabela 6 - MAPE, RMSE e MAE por produto e modelo (janela de teste)**

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
sugeriria leve vantagem do primeiro — leitura que a Tabela 7 desautoriza.

**Tabela 7 - Margem de MAPE entre Holt-Winters e Prophet, por produto**

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
subseção 4.6.

Esse resultado, porém, deixa em aberto a pergunta mais importante: se os dois
modelos são equivalentes entre si, algum deles é melhor que não modelar nada? É
o que a Tabela 8 responde, comparando o modelo vencedor de cada produto ao
baseline ingênuo sazonal descrito na subseção 3.5.3.

**Tabela 8 - Ganho do modelo vencedor sobre o baseline ingênuo sazonal**

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

A Tabela 8 também reenquadra os erros percentuais elevados da Tabela 6. Um MAPE
de 81,25% no pão francês, lido isoladamente, sugere falha do método; comparado
aos 93,17% da regra ingênua sobre a mesma série, revela que o erro é alto porque
a série é intrinsecamente difícil — e que o modelo, ainda assim, extrai sinal
dela. O mesmo vale para a banana prata, que cai de 99,14% para 66,63%. O erro
elevado é propriedade do dado, não do método, e o sistema trata esse caso: acima
de 50% de MAPE o motor marca a previsão como de baixa confiança.

**Figura 10 - Previsto × real na janela de teste — produto 1 (Arroz 5kg)**

`[FIGURA: ml-service/analysis/figures/g2_previsto_real_produto1.png]`

Fonte: Autoral, 2026

**Figura 11 - Previsto × real na janela de teste — produto 5 (Banana Prata kg)**

`[FIGURA: ml-service/analysis/figures/g2_previsto_real_produto5.png]`

Fonte: Autoral, 2026

As Figuras 10 e 11 mostram o realizado na janela de teste contra o que cada
abordagem previu sem jamais ter visto esses dias. As curvas do Holt-Winters e do
Prophet são visualmente indistinguíveis — evidência gráfica do que a Tabela 7
expressa numericamente —, enquanto a curva do baseline se descola das demais,
acompanhando o ruído da última semana de treino em vez do padrão médio.

## 4.4 Robustez e diagnóstico

Uma única divisão treino/teste pode favorecer um modelo por acaso. As Tabelas 7
e 8 repetem a avaliação em cinco janelas independentes, com origem móvel e
blocos de teste de 14 dias.

**Tabela 9 - Backtesting de origem móvel — produto 1 (Arroz 5kg)**

| Origem | MAPE HW (%) | MAPE Prophet (%) | MAPE ingênuo (%) |
|---|---:|---:|---:|
| 2024-10-22 | 11,84 | 11,85 | 16,68 |
| 2024-11-05 | 12,42 | 12,48 | 13,30 |
| 2024-11-19 | 11,35 | 11,34 | 28,44 |
| 2024-12-03 | 15,65 | 15,52 | 20,29 |
| 2024-12-17 | 10,50 | 10,42 | 17,54 |

Fonte: Autoral, 2026

**Tabela 10 - Backtesting de origem móvel — produto 5 (Banana Prata kg)**

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

No produto 5, a dobra de 19 de novembro merece análise. Nela o MAPE do
Holt-Winters salta para 188,42%, quatro vezes o valor das demais janelas — mas o
baseline ingênuo apresenta, ao mesmo tempo, **MAPE menor** (159,97%) e **RMSE
maior** (13,92 contra 11,64). As duas métricas apontam vencedores opostos sobre
exatamente os mesmos dados.

A contradição é diagnóstica: a janela concentra dias de venda muito baixa, e o
MAPE divide o erro pelo valor observado. Um desvio de três unidades sobre uma
venda de duas produz 150% de erro percentual; o mesmo desvio sobre uma venda de
trinta produz 10%. A métrica passa a medir o tamanho do denominador, não a
qualidade da previsão — limitação já registrada na subseção 3.5.2.

**Figura 12 - Backtesting de origem móvel — produto 1 (Arroz 5kg)**

`[FIGURA: ml-service/analysis/figures/g6_backtesting_produto1.png]`

Fonte: Autoral, 2026

**Figura 13 - Backtesting de origem móvel — produto 5 (Banana Prata kg)**

`[FIGURA: ml-service/analysis/figures/g6_backtesting_produto5.png]`

Fonte: Autoral, 2026

As Figuras 12 e 13 tornam visível o contraste entre os dois produtos. No arroz as
três linhas correm próximas e estáveis; na banana, a dobra de novembro produz um
pico que afeta as três abordagens simultaneamente — inclusive o baseline —, o
que é a assinatura gráfica de um problema da métrica, e não de um modelo.

**Figura 14 - Diagnóstico de resíduos — produto 1 (Holt-Winters)**

`[FIGURA: ml-service/analysis/figures/g5_residuos_produto1_holt_winters.png]`

Fonte: Autoral, 2026

**Figura 15 - Diagnóstico de resíduos — produto 5 (Holt-Winters)**

`[FIGURA: ml-service/analysis/figures/g5_residuos_produto5_holt_winters.png]`

Fonte: Autoral, 2026

O diagnóstico de resíduos verifica se o modelo extraiu toda a estrutura
disponível. Um ajuste adequado deixa resíduos centrados em zero, sem padrão
temporal e sem autocorrelação — aproximadamente ruído branco. O critério de
refutação é explícito: um pico na função de autocorrelação no atraso 7
indicaria sazonalidade semanal não capturada. A Figura 14 não apresenta esse
pico, o que sustenta a conclusão de que o que restou é ruído irredutível. A
Figura 15 mostra o mesmo padrão para a banana prata, com resíduos de amplitude
muito maior — coerente com a decomposição da Figura 9 — mas igualmente sem
estrutura remanescente.

## 4.5 Da previsão à decisão de reposição

A previsão só tem valor quando convertida em instrução operacional. A Tabela 11
apresenta o encadeamento completo do cálculo para dois produtos de situação
oposta, com prazo de entrega de três dias, variabilidade de prazo 1,0 e nível de
serviço de 95%.

**Tabela 11 - Parâmetros de reposição calculados pelo motor**

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
Equação (1) converte essa incerteza em reserva. É o comportamento esperado de um
dimensionamento por nível de serviço — proteger mais o que oscila mais.

A leitura de negócio é imediata. O arroz tem 15 unidades contra um ponto de
reposição de 65,84: já deveria ter sido pedido, com ruptura estimada para pouco
mais de um dia. A banana tem 200 unidades contra 85,02 e está confortável por
cerca de treze dias.

É essa tradução que a interface entrega. Os dois produtos recebem tratamento
visual oposto na tela de estoque — o arroz em vermelho, por estar abaixo do
ponto de reposição, e a banana em verde — e apenas o arroz aparece na lista de
alertas, com quantidade sugerida de 51 unidades, a diferença entre o ponto de
reposição e o estoque atual. O lojista não vê MAPE, desvio padrão ou escore
normal: vê um produto marcado como crítico, uma estimativa de quantos dias
restam e uma quantidade a pedir.

O efeito do nível de serviço também chega a ele de forma tangível. Elevar a meta
de 95% para 99% no arroz aumenta o estoque de segurança de 26,56 para 37,57
unidades e o ponto de reposição de 65,84 para 76,85 — ou seja, antecipa o pedido
e amplia a reserva. É um controle de risco exposto em unidades de mercadoria, e
não em probabilidade.

É essa cadeia — de série temporal a instrução de compra — que sustenta a
proposta da plataforma, e é também o que separa este trabalho de uma avaliação
puramente comparativa de modelos.

**Figura 16 - Projeção de estoque e ponto de reposição — produto 1 (Arroz 5kg)**

`[FIGURA: ml-service/analysis/figures/g7_reposicao_produto1.png]`

Fonte: Autoral, 2026

**Figura 17 - Projeção de estoque e ponto de reposição — produto 5 (Banana Prata kg)**

`[FIGURA: ml-service/analysis/figures/g7_reposicao_produto5.png]`

Fonte: Autoral, 2026

As Figuras 16 e 17 projetam o consumo do estoque atual à demanda média prevista
e marcam o instante em que a linha cruza o ponto de reposição. No arroz o
cruzamento já ocorreu; na banana, ocorre por volta do oitavo dia — bem antes da
ruptura, que é o comportamento desejado, já que o pedido precisa ser feito com a
antecedência do prazo de entrega.

## 4.6 Discussão

**Por que os modelos empatam.** A Tabela 12 traz os parâmetros de suavização
encontrados pelo otimizador do Holt-Winters.

**Tabela 12 - Parâmetros de suavização ajustados (Holt-Winters)**

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

Nos dez produtos o otimizador convergiu para parâmetros de suavização nulos —
sete exatamente zero, os demais desprezíveis. O parâmetro α controla o quanto o
modelo reage a cada venda nova; em zero, o modelo deixa de se adaptar e passa a
prever sempre a mesma reta com o mesmo padrão semanal, estimados uma única vez a
partir de todo o histórico.

O otimizador fez essa escolha porque os dados não contêm quebra alguma: a
tendência é linear e o perfil semanal, constante, de modo que reagir à venda de
ontem seria reagir apenas a ruído. E, reduzido a reta mais padrão semanal, o
Holt-Winters passa a descrever a mesma função que o Prophet ajusta num cenário
sem quebras. **Os dois empatam porque, ali, são o mesmo modelo.**

**O que isso valida e o que delimita.** O achado valida o motor em sentido
forte: submetido a dados de estrutura conhecida, ele recuperou essa estrutura,
inclusive a informação de que ela é estacionária. Ao mesmo tempo, delimita o
alcance do resultado — o empate é propriedade deste conjunto de dados, não uma
verdade geral sobre Holt-Winters e Prophet.

**Por que o baseline perde por tanto.** Há uma objeção natural ao parágrafo
anterior: se o Holt-Winters degenerou para tendência mais média por dia da
semana, por que não empata também com a regra ingênua, que é igualmente
simples? A Tabela 8 mostra que não empata — a diferença é de 45,1% de erro na
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
