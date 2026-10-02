<!--
  Regra de divisão com a seção 3, para não duplicar conteúdo:
  aqui ficam os CONCEITOS; lá ficam as FÓRMULAS e as decisões de projeto.
  Esta seção não traz nenhuma equação numerada — é proposital.
-->

# 2 Fundamentação teórica

A fundamentação percorre o caminho que o próprio sistema percorre: parte do
problema operacional do pequeno varejo, passa pelos instrumentos estatísticos
que o endereçam e chega aos modelos de previsão que alimentam esses
instrumentos. A subseção 2.1 estabelece o que precisa ser decidido — quanto
manter em estoque e quando repor. A 2.2 apresenta como estimar a demanda futura
que essa decisão exige. A 2.3 situa o trabalho entre os que já trataram do tema.

## 2.1 Gestão de estoque no pequeno varejo

### 2.1.1 Ruptura, excesso e gestão intuitiva

A ruptura de estoque — a indisponibilidade do produto no momento em que o
consumidor o procura — é o problema de maior impacto financeiro direto para o
varejista. A ABRAS (2023) quantifica esse impacto: a ruptura derruba entre 5% e
10% das vendas nos estabelecimentos afetados, e 32% dos consumidores migram para
um concorrente quando não encontram o produto que buscam. O prejuízo, portanto,
tem duas camadas: a receita não realizada na hora e a fidelidade comprometida
depois.

A mesma fonte documenta uma relação de proporcionalidade que permite estimar o
retorno de qualquer intervenção sobre o problema: a cada quatro pontos
percentuais reduzidos na taxa de ruptura de um item, o estabelecimento recupera
um ponto percentual nas vendas desse item. É um coeficiente que converte
melhoria operacional em receita, e é o que torna o ganho de uma solução
preditiva mensurável em vez de apenas plausível.

No extremo oposto está o excesso: capital imobilizado em mercadoria parada e,
no caso de perecíveis, perda direta. Os dois problemas têm a mesma origem —
decidir quanto comprar sem saber quanto vai vender — e é por isso que atacá-los
exige previsão, não apenas controle.

O Sebrae (2023a) orienta que pequenos varejistas iniciem o controle de estoque
por planilhas e evoluam para sistemas ERP conforme a operação se torna mais
complexa. Essa trajetória revela uma lacuna estrutural. A planilha registra, mas
não prevê, não alerta e não integra; o ERP integra, mas impõe barreiras de custo
e de complexidade. Entre os dois não existe, para o pequeno varejista, uma
solução intermediária com capacidade preditiva e interface acessível. O Sebrae
(2023b) complementa o diagnóstico ao apontar que a dificuldade de acessar
informações confiáveis de estoque é um dos principais sinais de que o negócio
superou sua ferramenta atual — transição que frequentemente não ocorre, deixando
o gestor com volume de operação suficiente para gerar dados relevantes e nenhuma
ferramenta para aproveitá-los.

A disponibilidade de software, isoladamente, não resolve. Ferreira e Mota (2022),
em estudo de caso num supermercado de pequeno porte em João Pessoa,
identificaram um estabelecimento que **possuía** sistema automatizado de controle
de estoque e o utilizava de forma incorreta. A consequência era divergência
sistemática entre o estoque registrado e o estoque físico, que levava o setor de
compras a pedir o que não era necessário e a deixar de pedir o que era —
produzindo excesso e ruptura simultaneamente. O achado desloca o problema: a
qualidade do dado de entrada, a usabilidade e os mecanismos de alerta são
requisitos críticos, não refinamentos opcionais.

### 2.1.2 Estoque de segurança, nível de serviço e ponto de reposição

Se a demanda futura e o prazo de entrega fossem conhecidos com exatidão, bastaria
pedir a quantidade exata no instante exato. Como nenhum dos dois é conhecido, a
reposição precisa ser dimensionada sob incerteza, e é esse o problema que Ballou
(2006) formaliza.

O **ponto de reposição** é o nível de estoque que dispara um novo pedido. Ele
cobre a demanda esperada durante o prazo de entrega do fornecedor — o *lead
time* — acrescida de uma reserva. O **estoque de segurança** é essa reserva:
existe para absorver a variação em torno do esperado, seja porque a venda foi
maior que a média, seja porque a entrega atrasou.

O tamanho da reserva não é arbitrário; decorre do **nível de serviço**, a
probabilidade alvo de não faltar estoque durante o período de reposição. Adotar
95% significa aceitar que, em cerca de uma reposição a cada vinte, o estoque se
esgotará antes da entrega. Elevar essa meta reduz o risco de ruptura e aumenta o
capital imobilizado — o nível de serviço é, portanto, a forma de tornar explícito
um trade-off que a gestão intuitiva resolve sem perceber que o está resolvendo.

Dois tipos de incerteza alimentam o cálculo. A **variabilidade da demanda** é a
oscilação das vendas em torno da média. A **variabilidade do lead time** é a
oscilação do prazo de entrega. A literatura aplicada frequentemente reproduz uma
formulação simplificada que considera apenas a primeira, supondo prazo de entrega
determinístico. A suposição é frágil no contexto do varejo de bairro, em que o
lead time é curto mas irregular, e seu efeito é subdimensionar a reserva
justamente nos casos de fornecedor menos confiável. A formulação completa, que
incorpora as duas fontes, é a adotada neste trabalho e está detalhada na
subseção 3.5.5.

### 2.1.3 Classificação ABC

Nem todo produto merece a mesma atenção de gestão. A classificação ABC ordena os
itens por representatividade no faturamento e os agrupa em três classes: A, os
poucos itens que respondem pela maior parte da receita; B, de importância
intermediária; e C, de baixa relevância individual. O Sebrae (2023c) recomenda
explicitamente sua aplicação em mercearias e supermercados de bairro como
ferramenta de priorização.

Silva e Araújo (2022) aplicaram a técnica em um supermercado de médio porte no
Triângulo Mineiro, extraindo estatísticas do ERP da empresa e construindo a
curva manualmente para identificar os itens de maior saída. O detalhe relevante
não é o resultado, mas o procedimento: a classificação foi conduzida **como
objeto de pesquisa acadêmica**, e não como rotina automatizada pelo sistema que
a empresa já possuía. Isso evidencia que, mesmo onde há ERP, a análise de
priorização não ocorre sozinha.

A limitação da técnica é ser retrospectiva: ela informa o que vendeu, não o que
tende a vender. É por isso que, neste trabalho, a classificação ABC não substitui
a previsão — compõe com ela, priorizando onde o erro de previsão custa mais caro.

## 2.2 Previsão de demanda e séries temporais

Uma série temporal é uma sequência de observações registradas em intervalos
regulares. O histórico de vendas diárias de um produto é uma série temporal, e
seu comportamento costuma decompor-se em três componentes: **tendência**, a
direção de crescimento ou queda ao longo do tempo; **sazonalidade**, os padrões
que se repetem em ciclos regulares, como o movimento maior aos sábados; e
**ruído**, a variação aleatória que nenhum modelo pode antecipar. Prever é
estimar os dois primeiros e aceitar o terceiro.

Box e Jenkins (1976) estabeleceram as bases formais da modelagem estatística de
séries temporais com a família ARIMA, que combina componentes autorregressivos,
de média móvel e de diferenciação. O modelo é consagrado, mas sua aplicação
pressupõe estacionariedade e estima coeficientes que não capturam diretamente
padrões sazonais complexos — limitações que motivaram o desenvolvimento de
abordagens mais especializadas.

Hyndman e Athanasopoulos (2021) sistematizam o campo com foco em aplicação
prática, cobrindo da suavização exponencial aos modelos de estado-espaço, e
fornecem o arcabouço que orienta tanto a escolha dos modelos quanto o protocolo
de avaliação adotados neste trabalho.

### 2.2.1 Holt-Winters

Proposto por Holt (1957) e estendido por Winters (1960), o método de Holt-Winters
é um modelo de suavização exponencial tripla. Ele mantém três estimativas
atualizadas a cada nova observação: o **nível**, que representa o patamar atual
de vendas; a **tendência**, que representa a variação por período; e a
**sazonalidade**, que representa o desvio típico de cada posição do ciclo — no
caso semanal, de cada dia da semana.

O termo "suavização exponencial" descreve como essas estimativas são atualizadas:
cada observação nova entra na estimativa com um peso, e as observações antigas
perdem peso exponencialmente. Esse peso é controlado por um parâmetro para cada
componente. Um peso alto produz um modelo que reage rapidamente a mudanças
recentes; um peso baixo produz um modelo que privilegia o padrão de longo prazo.
A escolha entre reagir e resistir é, portanto, parametrizada — e pode ser
estimada a partir dos próprios dados, o que se revelou decisivo nos resultados
deste trabalho.

O método admite variante aditiva, quando o efeito sazonal tem amplitude
constante, e multiplicativa, quando a amplitude acompanha o nível da série. É
interpretável, computacionalmente leve e não exige grandes volumes de dados para
convergir — características que o tornam adequado ao varejo de bairro e que
levaram Hyndman e Athanasopoulos (2021) a recomendarem a suavização exponencial
como ponto de partida robusto antes da adoção de modelos mais complexos.

### 2.2.2 Prophet

O Prophet, publicado por Taylor e Letham (2018), decompõe a série em tendência,
sazonalidade e efeitos de eventos, estimando os componentes por regressão
bayesiana. Diferencia-se do Holt-Winters em dois pontos conceituais. O primeiro é
o tratamento da tendência: em vez de uma inclinação continuamente atualizada, o
Prophet ajusta uma curva com **pontos de quebra**, instantes em que a inclinação
pode mudar — mecanismo pensado para séries de negócio, nas quais mudanças de
patamar costumam ser abruptas. O segundo é a capacidade de incorporar
calendários de eventos e feriados como componente próprio.

Os autores reportam desempenho competitivo em ampla variedade de séries de
negócio, superando implementações automatizadas de ARIMA em acurácia e robustez,
e projetaram o modelo para ser utilizável por analistas sem formação estatística
aprofundada — alinhamento direto com o perfil do usuário final deste sistema.

### 2.2.3 Métricas de acurácia e suas limitações

Comparar modelos exige critério objetivo. Hyndman e Athanasopoulos (2021)
recomendam o uso de métricas complementares, para evitar conclusões enviesadas
por uma única medida. Três são adotadas neste trabalho.

O **MAE** mede o erro médio em valor absoluto, na mesma unidade da variável
prevista. É a mais intuitiva e a adequada para comunicar resultado a um usuário
não técnico: "o sistema erra, em média, duas unidades por dia".

O **RMSE** eleva os erros ao quadrado antes de calcular a média, o que penaliza
desproporcionalmente os erros grandes. Dois modelos com o mesmo erro médio podem
ter RMSE muito distintos se um deles concentra o erro em poucos dias. A distinção
importa em gestão de estoque, onde um erro grande isolado é o que causa ruptura.

O **MAPE** expressa o erro em termos percentuais relativos ao valor observado.
É a única das três que é adimensional e, por isso, a única comparável entre
produtos de escalas diferentes — propriedade que a torna o critério natural de
seleção quando o catálogo é heterogêneo. Tem, em contrapartida, duas fragilidades
conhecidas: é indefinida quando o valor observado é zero, e cresce sem limite
quando o valor observado é pequeno, passando a medir o tamanho do denominador
mais do que a qualidade da previsão. As duas se manifestam nos resultados deste
trabalho e são analisadas na seção 4.

Uma métrica de erro, por si só, não diz se um modelo é bom — diz apenas que um é
melhor que outro. Responder se algum deles compensa exige confrontá-los com uma
referência mínima, papel desempenhado pelo baseline descrito na subseção 3.5.3.

## 2.3 Trabalhos relacionados

**Tabela 1 - Comparativo entre trabalhos relacionados**

| Autor (ano) | Abordagem | Resultado | Limitação |
|---|---|---|---|
| Silva e Araújo (2022) | Curva ABC construída manualmente a partir do ERP de um supermercado de médio porte | Identificação dos itens de maior saída e priorização da gestão | Análise retrospectiva e manual; não prevê demanda nem automatiza a classificação |
| Ferreira e Mota (2022) | Estudo de caso sobre o uso de sistema de controle de estoque em supermercado de pequeno porte | Diagnóstico da divergência entre estoque registrado e físico, gerando excesso e ruptura | Diagnóstico sem proposta de solução técnica |
| Taylor e Letham (2018) | Modelo Prophet aplicado a séries temporais de negócio em escala | Desempenho competitivo frente a ARIMA automatizado | Validação em séries de grande porte, distantes do varejo de bairro |
| Begattini *et al.* (2025) | Prova de conceito de gestão de estoque farmacêutico com Prophet | Modelo preditivo aplicado sobre histórico de vendas para apoiar decisão de compra | **Modelo único, sem comparação com alternativa**; não calcula parâmetros de reposição |
| **Este trabalho (2026)** | Holt-Winters e Prophet comparados por produto, com baseline ingênuo, e conversão em parâmetros de reposição | Seleção automática por produto e ganho mensurado sobre a referência mínima | Validação sobre dados sintéticos |

Fonte: Autoral, 2026

Conforme sintetizado na Tabela 1, os trabalhos revisados cobrem o problema por
ângulos complementares e deixam uma lacuna específica. Silva e Araújo (2022) e
Ferreira e Mota (2022) documentam a realidade do pequeno varejo brasileiro, mas
permanecem no plano descritivo. Taylor e Letham (2018) validam um modelo
preditivo, porém em séries de porte muito distante do mercado de bairro.
Begattini *et al.* (2025) aplicam previsão a estoque em contexto nacional e de pequeno
porte — o antecedente mais próximo —, mas adotam **um único modelo, sem
comparação**, e não avançam até o cálculo de ponto de reposição.

A lacuna é, portanto, dupla: falta avaliar empiricamente **qual** modelo se
adequa às séries de demanda do varejo de bairro, em vez de adotar um por
conveniência; e falta fechar o percurso que vai da previsão até a instrução de
compra. É essa lacuna que o presente trabalho se propõe a ocupar.
