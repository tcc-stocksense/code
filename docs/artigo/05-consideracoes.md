# 5 Considerações finais

O trabalho perguntou se modelos de previsão por séries temporais, aplicados ao
histórico de vendas de um mercado de bairro, produzem estimativas acuradas o
bastante para sustentar o cálculo automático do ponto de reposição — e qual
deles se adapta melhor a esse tipo de série. As duas partes têm resposta, e elas
têm forças distintas.

À primeira, a resposta é afirmativa e sem exceção no conjunto avaliado: os
modelos superaram o baseline ingênuo sazonal nos dez produtos, com redução
mediana de erro de 45,1%. Como o baseline reproduz o padrão semanal sem estimar
parâmetro algum, o ganho mede exatamente o que a modelagem estatística
acrescenta sobre a mera repetição do que aconteceu na semana anterior.

À segunda, a resposta é que **nenhum dos dois modelos domina o outro** neste
conjunto de dados. O Holt-Winters venceu em seis produtos e o Prophet em quatro,
mas em nove dos dez a diferença ficou abaixo de 0,7 ponto percentual de MAPE —
magnitude sem significado operacional. O achado tem explicação verificável: o
otimizador convergiu para parâmetros de suavização nulos em todos os produtos,
reduzindo o Holt-Winters à mesma família de função que o Prophet ajusta num
cenário sem quebras de patamar. O empate é propriedade dos dados, não uma
equivalência geral entre os métodos.

Cinco afirmações, cada uma amarrada à sua evidência, resumem o que ficou
demonstrado:

1. O problema que motiva o trabalho é real e homogêneo na população de
   interesse — os sete estabelecimentos consultados decidem a compra por
   inspeção visual da prateleira, inclusive os que dispõem de software (4.1);
2. As séries de demanda contêm sinal previsível, com tendência e sazonalidade
   semanal separáveis do ruído (4.2);
3. Os modelos generalizam para dados não vistos e superam a referência mínima em
   todo o catálogo, com erro que varia por produto conforme a variabilidade
   intrínseca de cada série (4.3);
4. O desempenho não é acidente da janela escolhida: mantém-se em cinco janelas
   independentes, e os resíduos não retêm estrutura (4.4);
5. A previsão se converte em parâmetros de reposição coerentes com a situação de
   cada produto, fechando o percurso da série temporal até a instrução de compra
   (4.5).

Do ponto de vista de engenharia, o sistema foi integrado e implantado em nuvem,
com infraestrutura declarada como código, demonstrando que o motor opera fora do
ambiente de desenvolvimento.

**Limitações e trabalhos futuros:** a limitação principal é de validade externa.
A avaliação quantitativa foi conduzida sobre dados sintéticos de estrutura
conhecida, o que permite verificar se o motor recupera essa estrutura, mas não
mede seu desempenho sobre a demanda real de um estabelecimento. O caminho para
essa validação já está implementado — o formato de ingestão descrito na
subseção 3.3.3 aceita o histórico sem alteração de código —, e é o trabalho
futuro de maior prioridade. Uma segunda limitação decorre do próprio
levantamento de campo: seis dos sete respondentes apontam o fim de mês e o dia
de pagamento como o período de maior variação, um ciclo **mensal** que o
conjunto sintético não reproduz, por modelar apenas o ciclo semanal. A estrutura
de demanda mais citada pelos gestores, portanto, não foi submetida aos modelos,
e incorporá-la é condição para que a validação externa seja conclusiva. Há ainda
limitações de menor alcance, registradas por inspeção do próprio código: o
desvio padrão da demanda é calculado sobre a série completa, incluindo os dias
de loja fechada, o que infla a reserva de segurança de forma conservadora; o
gerador combina os componentes de forma multiplicativa enquanto os modelos
operam em modo aditivo; os recursos de feriados e de regressor de promoção do
Prophet não foram ativados, o que equaliza a comparação mas subutiliza o modelo;
e um ano de histórico não permite estimar sazonalidade anual, que exigiria pelo
menos dois ciclos. No plano do produto, duas frentes se destacam. A primeira é a
avaliação de uso: nenhum teste de usabilidade foi conduzido, e a disposição de
adoção medida no levantamento é condicional — quatro dos sete respondentes
condicionaram a adoção a ver o sistema funcionando. A segunda é de escopo e
merece registro franco: perguntados sobre o único problema de estoque que
gostariam de resolver, três dos sete citaram o controle de validade, e nenhum
citou previsão de demanda. O módulo correspondente foi deliberadamente retirado
do escopo deste trabalho, cuja pergunta é sobre previsão; o levantamento indica,
contudo, que a prioridade percebida pelo usuário é outra, e que uma eventual
continuidade do projeto deveria considerá-la antes de refinar o motor preditivo.
