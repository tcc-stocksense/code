<!--
  O template da SPTech coloca ABSTRACT antes do RESUMO, e é o que seguimos aqui.
  Atenção: GRP01, GRP02 e GRP04 fazem o inverso (RESUMO primeiro). Vale confirmar
  com o orientador qual ordem prevalece — a troca é mover dois blocos.
-->

PREDICTIVE INVENTORY OPTIMIZATION FOR NEIGHBORHOOD GROCERY STORES:
AN EMPIRICAL COMPARISON BETWEEN HOLT-WINTERS AND PROPHET

(Otimização preditiva de estoque para mercados de bairro: uma comparação
empírica entre Holt-Winters e Prophet)

Danilo Silvestre Faustino, Gabriel Boos Duarte, Gabriel Sanchez, Pedro Primon,
Pedro Paulo Pinto

Orientador: Thiago Bonnacelli

Faculdade São Paulo Tech School - São Paulo, SP, Brasil

**ABSTRACT**

Small neighborhood grocery stores operate with enough sales volume to generate
meaningful demand data, yet most manage inventory manually and reactively. A
field survey of seven establishments conducted for this study found that all
seven decide what to purchase by visually inspecting shelves, including the four
that already use inventory software. This article presents and empirically
evaluates a predictive inventory optimization engine that converts sales history
into replenishment recommendations. Two time series models — Holt-Winters and
Prophet — were implemented and compared per product under an identical
evaluation protocol, with chronological train/test splitting, rolling-origin
backtesting, and a seasonal naive baseline as a minimum reference. Forecasts
were converted into safety stock, reorder point, and days-to-stockout using
Ballou's formulation, incorporating both demand and lead time variability. On a
controlled synthetic dataset of ten products over 365 days, the engine
outperformed the naive baseline in all ten products, with a median error
reduction of 45.1%. Neither model dominated the other: Holt-Winters won in six
products and Prophet in four, but the margin was below 0.7 percentage points of
MAPE in nine of ten. Parameter analysis explains the tie — the optimizer
converged to null smoothing parameters, reducing Holt-Winters to the same
function family Prophet fits on a stationary series. External validation on real
sales history remains as future work.

**Keywords:** demand forecasting; time series; inventory management;
neighborhood retail; Holt-Winters.

**RESUMO**

Pequenos mercados de bairro operam com volume de vendas suficiente para gerar
dados sobre a própria demanda, mas gerenciam o estoque de forma manual e
reativa. Um levantamento com sete estabelecimentos constatou que todos decidem a
compra por inspeção visual da prateleira, inclusive os quatro que já utilizam
software de controle. Este artigo apresenta e avalia empiricamente um motor de
otimização preditiva de estoque que converte histórico de vendas em recomendação
de reposição. Dois modelos de séries temporais — Holt-Winters e Prophet — foram
implementados e comparados por produto sob protocolo de avaliação idêntico, com
divisão cronológica entre treino e teste, backtesting de origem móvel e um
baseline ingênuo sazonal como referência mínima. As previsões foram convertidas em estoque de segurança, ponto de reposição e
dias até ruptura pela formulação de Ballou, que incorpora a variabilidade da
demanda e a do prazo de entrega.
Sobre um conjunto sintético controlado de dez produtos ao longo de 365 dias, o
motor superou o baseline ingênuo nos dez produtos, com redução mediana de erro
de 45,1%. Nenhum dos modelos dominou o outro: o Holt-Winters venceu em seis
produtos e o Prophet em quatro, mas a margem ficou abaixo de 0,7 ponto
percentual de MAPE em nove dos dez. A análise dos parâmetros ajustados explica o
empate — o otimizador convergiu para parâmetros de suavização nulos, reduzindo o
Holt-Winters à mesma família de função que o Prophet ajusta sobre uma série
estacionária. A validação externa sobre histórico real permanece como trabalho
futuro.

**Palavras-chave:** previsão de demanda; séries temporais; gestão de estoque;
varejo de bairro; Holt-Winters.
