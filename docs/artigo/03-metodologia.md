# 3 Metodologia e desenvolvimento

Quanto à natureza, esta pesquisa classifica-se como aplicada, por produzir um
artefato de software destinado a um problema operacional concreto. Quanto à
abordagem, é quantitativa: as decisões de projeto são avaliadas por métricas de
erro calculadas sobre séries temporais, e não por juízo qualitativo. Quanto ao
procedimento, combina pesquisa bibliográfica — que fundamenta a escolha dos
modelos e das fórmulas de reposição — com pesquisa experimental, em que os
modelos são submetidos a um protocolo de avaliação controlado e comparados entre
si sob as mesmas condições. [CITAR: referência de metodologia científica adotada
pelo curso, p. ex. Gil ou Prodanov e Freitas]

Esta seção descreve como o trabalho foi organizado, qual arquitetura sustenta a
solução, de que base de dados partem os resultados, quais alternativas
tecnológicas foram descartadas e como o motor preditivo foi implementado e
avaliado.

## 3.1 Organização do projeto

O desenvolvimento foi conduzido por uma equipe de cinco estudantes ao longo de
cinco fases, entre fevereiro e outubro de 2026. As fases encadeiam-se por
dependência de insumo: a revisão bibliográfica e a modelagem do banco (fase 1)
precedem o tratamento de dados e o módulo de movimentação de estoque (fase 2),
que por sua vez habilitam o desenvolvimento do motor preditivo e a comparação
entre modelos (fase 3). A interface web e a integração com o backend (fase 4)
consomem o que o motor produz, e a validação, os testes e a redação do artigo
encerram o trabalho (fase 5).

O código está organizado em um monorepositório com três componentes de
responsabilidade separada — a aplicação web, a API e o serviço de previsão —,
além dos diretórios de documentação e infraestrutura. A separação não é
meramente organizacional: cada componente tem seu próprio ciclo de execução e
suas próprias dependências, e a fronteira entre eles é um contrato HTTP/JSON
explícito, o que permite substituir a implementação de um sem tocar nos demais.

Duas convenções atravessam o projeto. A primeira é que o vocabulário de domínio
permanece em português — tabelas, colunas e entidades chamam-se `produto`,
`estoque_atual`, `previsao` —, o que reduz o atrito entre o código e a linguagem
do lojista para quem o sistema é construído. A segunda é que o esquema do banco
é versionado por migrações incrementais, de modo que qualquer ambiente possa ser
reconstruído do zero de forma determinística.

## 3.2 Arquitetura da solução

**Figura 1 - Diagrama de containers da solução (C4, nível 2)**

`[FIGURA: tcc-stocksense/docs/arquitetura/diagram-container-c2.png]`

Fonte: Autoral, 2026

Conforme ilustrado na Figura 1, a solução é composta por quatro elementos: a
interface do lojista, a API orquestradora, o motor preditivo e o banco de dados.

**A. Aplicação web**

Interface consumida pelo lojista no navegador. Concentra as funções operacionais
do sistema: importação das planilhas, consulta do estoque, alertas de reposição,
curva ABC e o painel comparativo de modelos. Comunica-se exclusivamente com a
API, por HTTPS/JSON.

**B. API**

Implementada em Kotlin sobre Spring Boot (JVM 17), é o orquestrador central e o
único componente com acesso de escrita ao banco. Suas responsabilidades são
validar os arquivos de importação, acionar o motor preditivo, persistir os
resultados e expor os endpoints consumidos pela interface. Também calcula a
classificação ABC, decisão detalhada na subseção 3.4.

**C. Motor preditivo**

Serviço em Python com FastAPI, responsável pela previsão de demanda e pelo
cálculo dos parâmetros de reposição. É deliberadamente *stateless*: recebe a
série histórica de um produto em JSON, devolve previsão e parâmetros em JSON, e
não acessa o banco. A consequência prática é que o motor pode ser reexecutado,
reimplantado ou substituído sem risco de inconsistência de dados, porque não
detém estado algum.

**D. Banco de dados**

Instância MySQL 8.0 que armazena o histórico importado, as previsões geradas, as
métricas por modelo e os parâmetros calculados. A propriedade dos dados é
exclusiva da API.

**E. Fluxo de funcionamento**

Sob a perspectiva do usuário, o processamento ocorre da seguinte forma:

1. O lojista envia as planilhas de produtos e de vendas pela interface web.
2. A API valida o formato e o conteúdo dos arquivos e persiste os registros.
3. Concluída a importação, a API aciona o motor preditivo, uma requisição por
   produto, enviando a série histórica correspondente.
4. O motor treina os modelos, seleciona o de menor erro, gera a previsão e
   calcula estoque de segurança, ponto de reposição e dias até ruptura.
5. A API persiste previsões, métricas e parâmetros, e calcula a classificação
   ABC sobre o catálogo completo.
6. A interface passa a exibir dados já calculados, sem acionar o motor a cada
   acesso.

O passo 6 explicita uma decisão de projeto: o recálculo é uma operação em lote,
disparada pela importação ou por agendamento mensal, e não uma chamada
sincrônica a cada visita de tela. Isso mantém a navegação responsiva mesmo que o
ajuste dos modelos leve dezenas de segundos por produto.

Três invariantes governam esse fluxo e não são violadas em nenhum ponto do
sistema: a interface nunca chama o motor diretamente; o motor nunca acessa o
banco; e toda escrita passa pela API.

## 3.3 Base de dados

A base de dados do projeto tem dois níveis, que convém não confundir: o esquema
de ingestão, que define o que o sistema aceita de um estabelecimento real, e a
base de validação, sobre a qual os resultados deste artigo foram medidos.

### 3.3.1 Esquema de ingestão

A entrada do sistema são planilhas no formato `.xlsx`. Duas são obrigatórias:
o catálogo de produtos, com identificador, nome e estoque atual, e o histórico
de vendas, com identificador do produto, data e quantidade. Três são desejáveis
e enriquecem o cálculo: dados do estabelecimento, fornecedores e a relação
produto × fornecedor, que traz o prazo real de entrega. Quando as desejáveis não
são enviadas, o sistema assume um prazo de entrega de três dias e variabilidade
de prazo igual a 1,0.

O histórico de vendas exige no mínimo 90 dias. O limite não é arbitrário: abaixo
disso, um modelo com ciclo semanal dispõe de menos de treze repetições do padrão
que precisa estimar, e não há como separar variação normal de tendência real com
confiabilidade estatística. Produtos que não atingem esse mínimo são recusados
pelo motor, e a interface sinaliza a ausência de previsão em vez de exibir um
valor sem lastro.

### 3.3.2 Base de validação empírica

Os resultados apresentados na seção 4 foram obtidos sobre um conjunto de dados
sintético, gerado por código com semente fixa, e não sobre vendas reais de um
estabelecimento. Essa escolha precisa ser declarada de saída, porque delimita o
alcance de tudo o que se conclui adiante.

A justificativa é que os dois tipos de dado respondem a perguntas diferentes.
Dados reais permitiriam medir o desempenho do motor no mundo; dados sintéticos
permitem verificar se o motor **recupera uma estrutura conhecida**, porque a
estrutura verdadeira da série foi definida por construção. O que se valida aqui
é a instrumentação — se a régua mede o que diz medir —, não a magnitude do erro
em um mercado específico. A validação externa sobre histórico real permanece
como trabalho futuro, e a subseção 3.3.1 descreve o formato pelo qual esse
histórico entraria sem alteração de código.

O gerador produz 10 produtos ao longo de 365 dias do ano de 2024, totalizando
3.650 observações diárias. Cada produto recebe um perfil de demanda distinto,
da quase constância do sal refinado à alta volatilidade da banana. A quantidade
vendida de um produto em um dia resulta do produto de quatro fatores, conforme
a Equação (1):

    q(t) = d · T(t) · S(t) · ε(t)          (1)

Onde `q(t)` é a quantidade vendida no dia *t*; `d` é a demanda base diária do
produto; `T(t)` é o fator de tendência, que cresce linearmente de 1,00 a 1,20 ao
longo do ano; `S(t)` é o multiplicador do dia da semana; e `ε(t)` é um ruído
gaussiano multiplicativo de média 1,0, cujo desvio padrão é o parâmetro de
variabilidade do produto e cujo valor é truncado ao intervalo [0,1; 3,0].

O multiplicador semanal `S(t)` é o elemento que justifica o emprego de modelos
sazonais, e sua amplitude está na Tabela 1.

**Tabela 1 - Multiplicador de demanda por dia da semana**

| Dia da semana | Multiplicador |
|---|---:|
| Segunda-feira | 0,85 |
| Terça-feira | 0,75 |
| Quarta-feira | 0,80 |
| Quinta-feira | 0,90 |
| Sexta-feira | 1,35 |
| Sábado | 1,45 |
| Domingo | 0,30 |

Fonte: Autoral, 2026

A razão entre o pico de sábado e o piso de domingo é de quase cinco vezes. Uma
previsão que ignorasse o dia da semana e trabalhasse com a média do período
erraria sistematicamente nos dois extremos — subestimando o sábado e
superestimando o domingo —, o que torna a sazonalidade semanal, e não a
tendência, o componente de maior peso na qualidade da previsão neste contexto.

Ao padrão contínuo somam-se dois eventos de fechamento, que introduzem zeros na
série: domingos têm 40% de chance de fechamento e os doze feriados nacionais de
2024 têm 60%. Esses zeros são mantidos na série, e não removidos, porque a
continuidade do índice temporal é requisito dos modelos empregados — mas sua
presença tem consequência metodológica sobre o MAPE, discutida na subseção 3.5.2.

A reprodutibilidade é garantida por semente fixa (`SEED = 42`) em todo o
pipeline: a mesma execução produz exatamente os mesmos números, e os resultados
da seção 4 podem ser regenerados por terceiros a partir do repositório.

## 3.4 Tecnologias consideradas e descartadas

Registram-se aqui as alternativas avaliadas e não adotadas, com a razão de cada
descarte. O objetivo é tornar explícito que as escolhas foram deliberadas, e não
o resultado de inércia.

### 3.4.1 ARIMA

A família ARIMA, formalizada por Box e Jenkins (1976), é a referência clássica
para modelagem estatística de séries temporais. Foi descartada por duas razões.
A primeira é de adequação: sua aplicação pressupõe estacionariedade da série e
estima coeficientes que não capturam diretamente padrões sazonais complexos,
enquanto a característica dominante das séries deste projeto é justamente um
ciclo semanal de grande amplitude. A segunda é de custo de operação: a
identificação da ordem do modelo exige análise caso a caso, inviável para um
catálogo de centenas de produtos que precisa ser reprocessado periodicamente sem
intervenção humana. Hyndman e Athanasopoulos (2021) recomendam os métodos de
suavização exponencial como ponto de partida robusto antes da adoção de modelos
mais complexos, especialmente quando os dados são limitados — recomendação que
orientou a escolha do Holt-Winters.

### 3.4.2 Modelos de aprendizado profundo

Arquiteturas de rede neural recorrente foram consideradas e descartadas por
incompatibilidade com as restrições do problema. Um mercado de bairro fornece,
por produto, algumas centenas de observações diárias — volume que não sustenta o
treinamento de modelos com grande número de parâmetros sem sobreajuste. Soma-se
a isso o requisito de interpretabilidade: o sistema precisa justificar ao lojista
por que recomenda um pedido, e a decomposição em nível, tendência e sazonalidade
dos modelos adotados é diretamente explicável, ao contrário dos pesos de uma rede
neural.

### 3.4.3 PostgreSQL

O projeto padronizou MySQL 8.0 como sistema gerenciador único. O PostgreSQL
chegou a figurar em versões iniciais da documentação de arquitetura, mas a
manutenção de dois dialetos distintos entre documentação e implementação gerava
divergência sem contrapartida técnica — nenhum recurso exigido pelo sistema é
exclusivo de um dos dois. A padronização eliminou o conflito.

### 3.4.4 Módulo de controle de validade e desperdício

A proposta original previa, como inovação desejável, um módulo de controle de
validade alinhado à redução de desperdício de perecíveis. O módulo foi retirado
do escopo. A razão é de foco: sua implementação exigiria uma nova entidade de
perdas, um fluxo de registro adicional e uma planilha de importação própria,
sem contribuir para a pergunta central do trabalho, que é comparativa e
preditiva. Reduzir a superfície de entrega preservou o núcleo do projeto.

### 3.4.5 Classificação ABC no motor preditivo

A classificação ABC chegou a ser implementada no serviço Python, junto aos
demais cálculos, e foi migrada para a API. A razão é estrutural: o motor opera
sobre um produto por vez e não enxerga o catálogo, enquanto a curva ABC é um
ranking relativo que exige o faturamento de todos os produtos simultaneamente.
Mantida no motor, a classificação dependeria de uma aproximação do faturamento
total; na API, que detém o catálogo e os valores de venda, o cálculo é exato.

## 3.5 Implementação

### 3.5.1 Modelos de previsão

Foram implementados dois modelos, ambos ajustados individualmente por produto.

O **Holt-Winters** — suavização exponencial tripla, proposta por Holt (1957) e
estendida por Winters (1960) — decompõe a série em nível, tendência e
sazonalidade. Adotou-se a variante aditiva para os dois componentes, com ciclo
sazonal de sete dias, e a estimativa dos parâmetros de suavização é delegada ao
otimizador da biblioteca. A previsão para *h* dias à frente é dada pela
Equação (2):

    ŷ(t+h) = L(t) + h · b(t) + s(t + h − m·⌈h/m⌉)          (2)

Onde `L(t)` é o nível estimado no instante *t*; `b(t)` é a tendência por
período; `s(·)` é o componente sazonal do dia correspondente; e `m = 7` é o
comprimento do ciclo.

O **Prophet**, publicado por Taylor e Letham (2018), é um modelo aditivo que
decompõe a série em tendência, sazonalidade e efeitos de eventos, estimados por
regressão bayesiana. Foi configurado com sazonalidade semanal ativa e
sazonalidades anual e diária desativadas — a primeira porque 365 dias de
histórico não contêm os dois ciclos necessários para estimá-la, a segunda porque
os dados são agregados por dia e não há variação intradiária a modelar.

A sazonalidade semanal de ambos os modelos só é habilitada quando o conjunto de
treino contém ao menos dois ciclos completos; abaixo disso o componente é
desativado automaticamente, para evitar estimar um padrão a partir de uma única
repetição.

### 3.5.2 Métricas de avaliação

A comparação emprega as três métricas recomendadas por Hyndman e Athanasopoulos
(2021) para avaliação multidimensional, definidas pelas Equações (3), (4) e (5):

    MAE = (1/n) · Σ |y(t) − ŷ(t)|          (3)

    RMSE = √[ (1/n) · Σ (y(t) − ŷ(t))² ]          (4)

    MAPE = (100/k) · Σ |y(t) − ŷ(t)| / y(t),  para y(t) > 0          (5)

Onde `y(t)` é a quantidade observada; `ŷ(t)` é a prevista; `n` é o número de
dias da janela de avaliação; e `k` é o número de dias com venda estritamente
positiva.

A restrição `y(t) > 0` na Equação (5) merece registro explícito, porque tem duas
consequências. A primeira é necessária: o MAPE é indefinido quando o valor real
é zero, e a série contém zeros por construção, nos dias de fechamento. A segunda
é uma assimetria que precisa ser declarada — MAE e RMSE são calculados sobre
todos os dias da janela, o MAPE apenas sobre os dias com venda. As três métricas,
portanto, não incidem exatamente sobre o mesmo conjunto de pontos.

O MAPE é adotado como critério de seleção por ser a única das três que é
adimensional e, portanto, comparável entre produtos de escalas distintas — o pão
francês vende dezenas de unidades por dia, o sal refinado vende unidades. É
também o valor que alimenta o indicador de acurácia exibido ao lojista, na forma
de `100 − MAPE`.

### 3.5.3 Protocolo de avaliação

A avaliação principal usa divisão cronológica em 80% para treino e 20% para
teste, o que corresponde, no conjunto descrito na subseção 3.3.2, a 292 dias de
treino (de 1º de janeiro a 18 de outubro de 2024) e 73 dias de teste (de 19 de
outubro a 30 de dezembro de 2024).

A divisão é feita por posição temporal e **nunca** por amostragem aleatória.
A razão é que embaralhar as observações colocaria dias posteriores no conjunto
de treino e dias anteriores no de teste, permitindo que o modelo usasse
informação do futuro para prever o passado. O erro medido cairia
artificialmente e não teria valor preditivo algum — seria uma medida de ajuste,
não de generalização.

Uma única divisão, porém, pode ser favorável por acaso. Para verificar se o
desempenho se mantém, aplicou-se adicionalmente **backtesting com origem
móvel**: o conjunto de treino cresce a cada dobra e a previsão é feita sobre o
bloco seguinte de 14 dias, repetindo-se o experimento cinco vezes. Se o erro
oscilar pouco entre as dobras, a métrica principal é representativa; se oscilar
muito, ela é um acidente da janela escolhida.

Por fim, incorporou-se um **baseline ingênuo sazonal** como piso de comparação,
definido pela Equação (6):

    ŷ(t+h) = y(t + h − m·⌈h/m⌉),  com m = 7          (6)

Ou seja, cada dia previsto recebe o valor observado no mesmo dia da semana da
última semana completa do conjunto de treino. O baseline não estima parâmetro
algum e não é um terceiro candidato do motor: sua função é responder a uma
pergunta que a comparação entre Holt-Winters e Prophet, sozinha, não responde.
Comparar os dois modelos informa qual deles é melhor; comparar ambos com o
ingênuo informa se **algum** deles vale o custo de existir. Sem esse piso, uma
diferença pequena entre os modelos seria indistinguível de ausência de
capacidade preditiva nos dois.

### 3.5.4 Critério de seleção do modelo

Para cada produto, o motor treina os dois modelos, calcula as três métricas
sobre a mesma janela de teste e seleciona o de menor MAPE. Em caso de empate
exato, prevalece o Holt-Winters, por ser o modelo de menor custo computacional.
A seleção é, portanto, individual por produto: nada impede — e os resultados
confirmam — que modelos diferentes vençam em produtos diferentes do mesmo
catálogo.

Quando o MAPE do modelo vencedor ultrapassa 50%, a resposta do motor inclui um
aviso de baixa confiança, propagado até a interface. A decisão de exibir uma
previsão sinalizada, em vez de suprimi-la, parte do princípio de que uma
estimativa ruim identificada como tal é mais útil ao lojista do que a ausência
de informação.

### 3.5.5 Parâmetros de reposição

A previsão só tem valor operacional quando convertida em decisão de compra. Essa
conversão usa as formulações de Ballou (2006) para estoque de segurança e ponto
de reposição, nas Equações (7) e (8):

    ES = Z · √( LT · σ²_d + d̄² · σ²_LT )          (7)

    PR = d̄ · LT + ES          (8)

Onde `ES` é o estoque de segurança em unidades; `Z` é o escore da distribuição
normal padrão correspondente ao nível de serviço alvo; `LT` é o prazo médio de
entrega em dias; `σ_d` é o desvio padrão da demanda; `d̄` é a demanda média
diária prevista pelo modelo vencedor; `σ_LT` é o desvio padrão do prazo de
entrega; e `PR` é o ponto de reposição.

Adotou-se a formulação completa, e não a simplificação `ES = Z · σ_d · √LT`,
frequente na literatura aplicada. A diferença está no segundo termo do
radicando: a versão simplificada supõe prazo de entrega determinístico e
considera apenas a incerteza da demanda. Em um mercado de bairro, em que o
atraso do fornecedor é ocorrência rotineira, essa suposição subdimensiona
sistematicamente a reserva justamente nos casos em que ela é mais necessária.

O escore `Z` é obtido pela função inversa da distribuição normal acumulada
aplicada ao nível de serviço, e não fixado em 1,645. A distinção é funcional, e
não apenas formal: com o valor fixo, a opção de alterar o nível de serviço
exposta ao usuário não produziria efeito algum sobre o resultado.

Completa o conjunto a estimativa de dias até ruptura, na Equação (9):

    DR = E / d̄          (9)

Onde `DR` é o número de dias até o esgotamento; `E` é o estoque atual; e `d̄` é
a demanda média diária prevista. Quando a demanda prevista é nula, o indicador
não é definido — o que, semanticamente, significa que o produto não romperá sob
a demanda observada.

Na ausência das planilhas desejáveis, os parâmetros assumem os valores padrão de
três dias para o prazo de entrega, 1,0 para sua variabilidade e 95% para o nível
de serviço.

### 3.5.6 Equivalência entre a análise e o sistema em produção

Uma decisão de implementação sustenta a validade interna de todos os resultados
da seção 4: a camada de análise **importa os módulos de produção** em vez de
reimplementar as fórmulas. As métricas, os ajustes de modelo e os cálculos de
reposição apresentados neste artigo são executados exatamente pelo mesmo código
que atende às requisições do sistema.

A consequência é que não existe uma segunda implementação capaz de divergir da
primeira. Números publicados em um artigo e obtidos por um script auxiliar
frequentemente deixam de corresponder ao que o sistema faz, à medida que este
evolui; aqui, essa classe de erro é impossível por construção.
