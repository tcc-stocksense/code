# Notas de defesa — artigo StockSense

Perguntas que a banca tende a fazer, por seção, com a resposta curta e o ponteiro
para a evidência. Serve para revisar na véspera sem reler o artigo inteiro.

Não é material de entrega — é roteiro de estudo.

---

## Seção 3 — Metodologia e desenvolvimento

**1. Por que dados sintéticos e não vendas reais? Isso não é circular?**

Não, porque a pergunta é outra. Com dado real mede-se o desempenho no mundo; com
dado sintético verifica-se se o motor **recupera uma estrutura que se conhece por
construção**. É validação de instrumentação: prova que a régua mede certo. A
circularidade existiria se os modelos tivessem acesso à fórmula geradora — eles
não têm, recebem apenas a série. O limite está declarado na própria metodologia
(3.3.2), não escondido nas limitações.
→ Seção 3.3.2.

**2. Por que 80/20 cronológico e não validação cruzada?**

Porque embaralhar as observações colocaria dias posteriores no treino e
anteriores no teste — o modelo usaria o futuro para prever o passado. O erro
cairia artificialmente e mediria ajuste, não generalização. É o ponto em que a
validação de série temporal difere da de dados tabulares.
→ Seção 3.5.3, parágrafo 2.

**3. Uma única divisão treino/teste não pode ter dado sorte?**

Pode, e é por isso que há backtesting de origem móvel: cinco dobras, treino
crescente, blocos de teste de 14 dias. Se o erro oscilasse muito entre dobras, a
métrica principal seria acidente da janela.
→ Seção 3.5.3, parágrafo 3; resultados na seção 4.

**4. Por que MAPE para selecionar, se ele tem problemas conhecidos?**

Porque é a única das três métricas que é adimensional e comparável entre
produtos de escalas diferentes — pão francês vende dezenas por dia, sal vende
unidades. Os problemas do MAPE são reais e estão declarados: ele é indefinido em
zero, o que obriga a calculá-lo só sobre dias com venda, e isso cria uma
assimetria (MAE e RMSE usam todos os dias, MAPE não). O comportamento com
denominador pequeno aparece nos resultados e é analisado lá.
→ Seção 3.5.2, Equação (5).

**5. Por que a fórmula completa de Ballou e não a simplificada?**

A simplificada (`Z · σ_d · √LT`) supõe prazo de entrega determinístico e só
considera a incerteza da demanda. Em mercado de bairro o atraso do fornecedor é
rotina, então ela subdimensiona a reserva exatamente quando ela é mais
necessária. A completa carrega as duas fontes de incerteza no radicando.
→ Seção 3.5.5, Equação (7).

**6. Por que Z é calculado e não fixado em 1,645?**

Porque a tela permite ao lojista alterar o nível de serviço. Com Z fixo, mudar o
nível de 95% para 99% não produziria efeito nenhum no resultado — o controle
seria decorativo. Z sai da inversa da normal acumulada aplicada ao nível
escolhido.
→ Seção 3.5.5, último parágrafo antes da Equação (9).

**7. Por que descartaram ARIMA?**

Dois motivos. Adequação: pressupõe estacionariedade e não captura diretamente
sazonalidade complexa, enquanto o traço dominante das séries é um ciclo semanal
de grande amplitude (razão sábado/domingo de quase 5×). Operação: identificar a
ordem do modelo exige análise caso a caso, inviável para centenas de produtos
reprocessados sem intervenção humana. Hyndman e Athanasopoulos (2021) recomendam
suavização exponencial como ponto de partida robusto.
→ Seção 3.4.1; Tabela 1 para a amplitude semanal.

**8. Por que a classificação ABC ficou no backend e não no motor?**

Porque o motor opera um produto por vez e não enxerga o catálogo, enquanto ABC é
ranking relativo que exige o faturamento de todos simultaneamente. No motor, o
cálculo dependeria de uma aproximação do total; na API, que tem catálogo e
valores de venda, é exato.
→ Seção 3.4.5.

**9. Como garantem que os números do artigo são os que o sistema produz?**

A camada de análise importa os módulos de produção em vez de reimplementar as
fórmulas. Não existe segunda implementação capaz de divergir. É a diferença
entre "o script auxiliar calculou isso" e "o sistema calcula isso".
→ Seção 3.5.6.

**10. Por que o mínimo de 90 dias de histórico?**

Abaixo disso um modelo de ciclo semanal tem menos de treze repetições do padrão
que precisa estimar, e não dá para separar variação normal de tendência real.
Produtos que não atingem o mínimo são recusados e a interface sinaliza a ausência
de previsão, em vez de exibir valor sem lastro.
→ Seção 3.3.1.

---

## Seção 4 — Resultados e discussão

*(a escrever)*

## Seção 2 — Fundamentação teórica

*(a escrever)*

## Seção 1 — Introdução

*(a escrever)*

## Seção 5 — Considerações finais

*(a escrever)*
