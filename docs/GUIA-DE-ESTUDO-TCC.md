# Guia de Estudo — TCC StockSense

Documento de estudo do grupo. Reúne o que o trabalho faz, o que foi escrito, os
conceitos que sustentam o artigo e as perguntas que a banca tende a fazer, com a
resposta e o ponteiro para a evidência.

**Não é material de entrega.** O artigo é o entregável; isto é o que você lê
antes da arguição.

> Por que este documento existe: o artigo passou por uma redução deliberada da
> carga matemática, para reduzir a superfície de perguntas na banca. A explicação
> que saiu do artigo está aqui — mais longa e mais didática do que caberia num
> texto acadêmico.

---

## Sumário

1. [O trabalho em uma página](#1-o-trabalho-em-uma-página)
2. [O que está escrito e onde](#2-o-que-está-escrito-e-onde)
3. [Conceitos — do zero](#3-conceitos--do-zero)
4. [Os resultados e o que significam](#4-os-resultados-e-o-que-significam)
5. [Perguntas de banca, por seção](#5-perguntas-de-banca-por-seção)
6. [Onde somos vulneráveis](#6-onde-somos-vulneráveis)
7. [Divisão de estudo entre o grupo](#7-divisão-de-estudo-entre-o-grupo)
8. [Como rodar as coisas](#8-como-rodar-as-coisas)

---

## 1. O trabalho em uma página

**O problema.** Mercados de bairro decidem o que comprar olhando a prateleira.
Isso gera ruptura (produto acaba, venda perdida) e excesso (capital parado,
perecível vencendo). Nas sete entrevistas que fizemos, **os sete** decidem assim
— inclusive os quatro que já têm software.

**A solução.** Um motor que lê o histórico de vendas, prevê a demanda dos
próximos 30 dias e calcula **quando pedir** (ponto de reposição) e **quanto
manter de reserva** (estoque de segurança), entregando isso numa interface web.

**A pergunta de pesquisa.** Modelos de série temporal produzem previsão boa o
bastante para sustentar esse cálculo — e qual deles se adapta melhor a essas
séries?

**A resposta, em duas partes.**

| Pergunta | Resposta | Número |
|---|---|---|
| Algum modelo vale a pena? | **Sim, sem exceção** | supera o baseline ingênuo em 10/10 produtos, redução mediana de erro de 45,1% |
| Qual dos dois vence? | **Nenhum domina** | 6 × 4 para Holt-Winters, mas em 9 de 10 a diferença é < 0,7 pp |

**A explicação do empate** (contribuição mais original): o otimizador zerou os
parâmetros de adaptação nos dez produtos, o que reduz o Holt-Winters à mesma
função que o Prophet ajusta num cenário sem quebras. Empataram porque, naqueles
dados, são o mesmo modelo.

**A limitação principal.** A avaliação quantitativa é sobre **dados sintéticos**,
não vendas reais. Isso é declarado na metodologia, não escondido nas limitações.

---

## 2. O que está escrito e onde

### Arquivos

```
docs/artigo/
├── 00-frontmatter.md     título, autores, resumo, abstract
├── 01-introducao.md      problema, pergunta, objetivos, justificativa
├── 02-fundamentacao.md   teoria + trabalhos relacionados
├── 03-metodologia.md     como foi feito (a maior seção)
├── 04-resultados.md      o que deu
├── 05-consideracoes.md   resposta à pergunta + limitações
├── referencias.md        ABNT
├── figuras/              as 7 figuras que não vêm da análise
├── gerar_docx.py         monta o .docx no template da SPTech
├── gerar_der.py          desenha o DER a partir das migrations
├── gerar_infra.py        desenha a infra a partir do Terraform
└── verificar_numeros.py  confere as tabelas contra o JSON
```

### Mapa das seções

| Seção | O que diz | Evidência |
|---|---|---|
| 1 Introdução | O problema, com o BPMN AS-IS e os números das entrevistas | Figura 1, ABRAS (2023) |
| 2 Fundamentação | Gestão de estoque, previsão, métricas, trabalhos relacionados | Tabela 1 |
| 3.1 Organização | Equipe, fases, monorepo | — |
| 3.2 Arquitetura | C4, blocos A–F (inclui implantação), BPMN TO-BE | Figuras 2–5 |
| 3.3 Base de dados | Entrevistas (método), DER, ingestão, dataset sintético | Figura 6, Tabela 2 |
| 3.4 Descartadas | ARIMA, deep learning, PostgreSQL, ESG, ABC no motor | — |
| 3.5 Implementação | Modelos, métricas, protocolo, Ballou, interface | Figura 7, Equações |
| 4.1 Campo | Resultados das entrevistas | Tabela 3 |
| 4.2 Perfil dos dados | Descritiva + decomposição | Tabela 4, Figuras 8–9 |
| 4.3 Acurácia | Métricas, margens e ganho sobre o baseline | Tabelas 5–7, Figuras 10–11 |
| 4.4 Robustez | Backtesting e resíduos | Tabelas 8–9, Figuras 12–15 |
| 4.5 Reposição | Da previsão à decisão de compra | Tabela 10, Figuras 16–17 |
| 4.6 Discussão | Por que empataram (α≈0) | Tabela 11 |
| 5 Considerações | Resposta + limitações e trabalhos futuros | — |

### A regra dos números

**Nenhum número do artigo foi digitado à mão.** Todos saem de
`ml-service/analysis/results/dados_documento.json`, gerado pelo código de
produção. O `verificar_numeros.py` confere célula por célula. Se alguém mudar um
número no texto sem mudar o dado, o verificador acusa.

Isso já pegou um erro real: uma "mediana de 49,4%" que era, na verdade, 45,1%.

---

## 3. Conceitos — do zero

### 3.1 Série temporal

Uma sequência de observações em intervalos regulares. As vendas diárias de um
produto formam uma série temporal. Ela se decompõe em três partes:

- **Tendência** — a direção de longo prazo. No nosso gerador, +20% ao ano.
- **Sazonalidade** — o padrão que se repete. No varejo de bairro, o ciclo é
  semanal: sábado vende 1,45× a média, domingo 0,30×.
- **Ruído** — o que sobra. Aleatório por definição; **nenhum modelo prevê isso**.

Prever = estimar tendência e sazonalidade, e aceitar que o ruído é irredutível.

> **Por que isso importa na banca:** quando perguntarem "por que o MAPE do pão
> francês é 81%?", a resposta é que aquela série tem muito ruído — não que o
> modelo é ruim. A prova é que o baseline ingênuo erra 93% na mesma série.

### 3.2 Holt-Winters

Mantém três estimativas, atualizadas a cada venda nova:

```
nível        "quanto vende em média agora"
tendência    "quanto isso sobe por dia"
sazonalidade "sábado vende 45% acima da média"
```

Três parâmetros — **α, β, γ** — controlam **o quanto cada estimativa reage a uma
venda nova**:

- α = 1 → "o nível de hoje é a venda de hoje" (reage a tudo, inclusive ruído)
- α = 0 → "ignore a venda de hoje, o nível já está estimado"

Esses parâmetros não são escolhidos por nós: o otimizador da biblioteca procura
os valores que minimizam o erro. **Foi essa busca que produziu o achado
principal do trabalho** (seção 4.6).

### 3.3 Prophet

Modelo do Meta, publicado por Taylor e Letham (2018). Também decompõe em
tendência + sazonalidade + eventos, mas difere em dois pontos:

- A tendência tem **pontos de quebra** — instantes em que a inclinação muda de
  uma vez, pensados para séries de negócio onde mudanças são abruptas.
- Aceita **calendário de feriados** como componente próprio.

> No nosso experimento, nenhuma dessas vantagens pôde se manifestar: os dados
> sintéticos não têm quebras, e o mecanismo de feriados não foi ativado (para
> equalizar a comparação). Isso está declarado nas limitações.

### 3.4 As três métricas de erro

Exemplo de três dias, para fixar:

```
real     = [10, 20,  0]    ← dia 3 a loja fechou
previsto = [12, 18,  3]
erros    = [ 2,  2,  3]

MAE  = (2 + 2 + 3) / 3            = 2,33   erro típico, em unidades
RMSE = √((4 + 4 + 9) / 3)         = 2,38   pune erro grande
MAPE = (2/10 + 2/20) / 2 × 100    = 15,0%  percentual, só dias com venda
```

**Por que o RMSE pune erro grande** — dois casos com o **mesmo MAE**:

```
erros {3, 3, 3}   → MAE 3,00   RMSE 3,00
erros {0, 0, 9}   → MAE 3,00   RMSE 5,20
```

Errar 3 todo dia e acertar dois dias mas errar 9 no terceiro dão o mesmo MAE. O
RMSE quase dobra no segundo caso. Em estoque isso importa: um erro grande
isolado é o que causa ruptura.

**Por que o MAPE seleciona o modelo** — é o único adimensional, comparável entre
o pão francês (30 un/dia) e o sal (5 un/dia). O preço: é indefinido quando a
venda é zero, então só é calculado nos dias com venda — enquanto MAE e RMSE usam
todos. **As três não incidem sobre o mesmo conjunto de pontos.**

### 3.5 O baseline ingênuo

```
previsão de amanhã = o que vendeu no mesmo dia da semana, na semana passada
```

Não estima parâmetro nenhum. Serve de **piso**: um modelo só demonstra valor se
superar essa regra.

> **Esta é a peça mais importante do trabalho do ponto de vista argumentativo.**
> Sem ela, a comparação Holt-Winters × Prophet só responde *qual dos dois é
> melhor* — e como eles empataram, o artigo não teria conclusão. Com ela, há
> resposta: ambos valem a pena, com 45,1% menos erro que a regra ingênua.

### 3.6 Divisão treino/teste cronológica

Separamos os primeiros 80% dos dias para treinar (292 dias) e os últimos 20%
para testar (73 dias). **Nunca aleatoriamente.**

> **Por quê:** embaralhar colocaria dias de dezembro no treino e dias de outubro
> no teste. O modelo usaria o futuro para prever o passado, o erro cairia
> artificialmente e mediria *ajuste*, não *capacidade de prever*. É o ponto em
> que série temporal difere de dados tabulares, e é pergunta clássica de banca.

### 3.7 Backtesting de origem móvel

Uma única divisão treino/teste pode dar sorte. No backtesting, repetimos cinco
vezes: o treino cresce e a previsão é feita sobre os 14 dias seguintes. Se o
erro varia pouco entre as dobras, a métrica principal é confiável.

### 3.8 Resíduos

`resíduo = real − previsto`. Um bom modelo deixa resíduos **sem padrão** — ruído
branco. Se houvesse um pico na autocorrelação no atraso 7, significaria que
sobrou sazonalidade semanal não capturada. Não há.

### 3.9 Ballou — o que o lojista realmente usa

Esta é a parte **mais fácil de defender** e a que gera os KPIs do sistema.
Exemplo real, o Arroz 5kg (Tabela 10 do artigo):

```
Entradas   demanda prevista       13,092 un/dia
           desvio da demanda       5,459
           lead time (entrega)     3 dias
           variabilidade do prazo  1,0
           nível de serviço        95%

Z = inversa da normal(0,95) = 1,6449

ES = Z · √( LT·σ²  +  demanda²·σ²_LT )
   = 1,6449 · √( 3·5,459² + 13,092²·1,0² )
   = 1,6449 · √( 89,402 + 171,400 )
   = 26,56 unidades          ← estoque de segurança

PR = 13,092 × 3 + 26,56 = 65,84 unidades    ← ponto de reposição
DR = 15 / 13,092        = 1,15 dias         ← dias até ruptura
```

**Em português:** *"nos 3 dias que o fornecedor leva, espero vender 39,3
unidades. Como a venda e o prazo variam, guardo mais 26,6 de reserva para ter 95%
de chance de não faltar. Logo, quando o estoque chegar a 65,8, faço o pedido.
Tenho 15 — já estou atrasado."*

**O nível de serviço muda tudo** (por isso Z é calculado, não fixo em 1,645):

| Nível | Z | Estoque de segurança | Ponto de reposição |
|---|---:|---:|---:|
| 90% | 1,2816 | 20,70 | 59,97 |
| 95% | 1,6449 | 26,56 | 65,84 |
| 99% | 2,3263 | 37,57 | 76,85 |

**Fórmula completa × simplificada** — número forte para a defesa:

```
simplificada  Z · σ · √LT  = 15,55    (supõe prazo de entrega fixo)
completa      com σ_LT     = 26,56    →  70,8% maior
```

A simplificada subdimensionaria a reserva do arroz em 70%. Olhando o radicando:
o termo do prazo (`13,092² = 171,4`) é quase o **dobro** do termo da demanda
(`89,4`). Neste produto, a incerteza do fornecedor pesa mais que a da venda — e
a fórmula simplificada simplesmente não a enxerga.

### 3.10 Curva ABC

Ordena os produtos por faturamento: **A** são os poucos que respondem pela maior
parte da receita, **C** os de baixa relevância. Serve para priorizar.

É **retrospectiva** — diz o que vendeu, não o que vai vender. Por isso compõe
com a previsão em vez de substituí-la. E é calculada no **backend**, não no
motor, porque exige o catálogo inteiro, enquanto o motor opera um produto por
vez.

### 3.11 Os KPIs da interface

| KPI | Como sai | Onde aparece |
|---|---|---|
| Dias até ruptura | `estoque ÷ demanda média prevista` | estoque, alertas, detalhe |
| Semáforo | 🔴 `estoque ≤ ponto de reposição` · 🟡 até `PR × 1,5` · 🟢 acima | estoque |
| Acurácia do motor | `100 − MAPE` do modelo **selecionado** | painel |
| Produtos em risco | contagem por dias até ruptura | painel |
| Classe ABC | faturamento acumulado | curva ABC |

---

## 4. Os resultados e o que significam

### 4.1 O campo (7 entrevistas)

| Achado | Resultado | Para que serve no artigo |
|---|---|---|
| Decidem pela prateleira | **7/7** | prova a premissa da gestão intuitiva |
| Controle manual | 3/7 | caracteriza o segmento |
| Exportam por produto/dia | 4/7 | justifica a entrada por planilha |
| Mais de 6 fornecedores | **7/7** | justifica a Ballou completa |
| Prazo de entrega | 1 a 10 dias (média 3,9, mediana 2) | justifica o padrão de 3 dias |
| Sazonalidade de fim de mês | 6/7 | **contraria** o dataset (só modela ciclo semanal) |
| Dor principal: validade | 3/7 | **contraria** o escopo (ESG foi cortado) |

### 4.2 O comparativo

- Holt-Winters venceu em **6**, Prophet em **4**
- Em **9 de 10** produtos a diferença é menor que 0,7 ponto percentual
- Em **5** deles, menor que 0,06 pp
- **Nenhum modelo domina o outro**

### 4.3 O ganho sobre o baseline — o número principal

| | |
|---|---|
| Supera o ingênuo em | **10 de 10 produtos** |
| Redução mediana de erro | **45,1%** |
| Menor ganho | Pão Francês, 12,8% (93,17% → 81,25%) |
| Maior ganho | Sal Refinado, 69,4% (31,25% → 9,57%) |

**Como isso reenquadra os MAPEs altos:** 81% no pão francês parece falha — até
comparar com os 93% da regra ingênua na mesma série. O erro é alto porque a
série é difícil, e o modelo ainda assim extrai sinal dela.

### 4.4 A dobra ruim do produto 5

Numa das cinco janelas do backtesting, o MAPE do Holt-Winters saltou para
188,42%. **Não escondemos — analisamos.**

| | MAPE | RMSE |
|---|---:|---:|
| Holt-Winters | 188,42% | 11,64 |
| Baseline ingênuo | 159,97% | **13,92** |

As duas métricas apontam **vencedores opostos** sobre os mesmos dados: por MAPE
o ingênuo ganha, por RMSE perde. Isso é a assinatura de um problema **da
métrica**, não do modelo — a janela concentra dias de venda baixa, e o MAPE
divide o erro pelo valor real. Errar 3 sobre venda de 2 dá 150%.

> Analisar a dobra desfavorável é mais forte que mostrar só as janelas boas. Se
> a banca perguntar "e esse 188%?", a resposta já está no artigo.

### 4.5 O α≈0 — a contribuição original

Nos dez produtos o otimizador convergiu para parâmetros de suavização nulos
(sete exatamente zero). Em três passos:

1. **A evidência.** α ≈ β ≈ γ ≈ 0 em 10/10.
2. **O que significa.** α controla o quanto o modelo reage a cada venda nova.
   Em zero, ele para de se adaptar e prevê sempre a mesma reta com o mesmo
   padrão semanal. E uma reta com padrão semanal fixo é exatamente o que o
   Prophet ajusta quando não há quebras. **Viraram o mesmo modelo.**
3. **Por que o otimizador fez isso.** O gerador produz tendência perfeitamente
   linear e perfil semanal constante. Nesse regime, reagir à venda de ontem é
   reagir só a ruído. O otimizador percebeu e desligou a adaptação.

**A pergunta que vem a seguir, e a resposta:** *"se o Holt-Winters virou
'tendência + média por dia da semana', por que não empata também com o baseline
ingênuo, que é igualmente simples?"*

Porque o ingênuo repete **uma** semana — uma realização ruidosa de cada dia da
semana. O Holt-Winters estima o perfil semanal a partir das **~40 semanas** do
treino, e a média entre elas cancela o ruído. O α≈0 não tornou o modelo trivial:
tornou-o um **estimador de perfil semanal**. É aí que estão os 45,1%.

**O que isso valida e o que delimita:** valida o motor (recuperou a estrutura
conhecida, inclusive a informação de que ela é estacionária) e delimita o
resultado (o empate é propriedade destes dados, não verdade geral). E produz uma
previsão testável: em dados reais, com quebras, espera-se α > 0 e separação
entre os modelos — que é o que justifica manter os dois no sistema.

---

## 5. Perguntas de banca, por seção

### Introdução e fundamentação

**Qual é a pergunta de pesquisa?**
Se modelos de série temporal produzem previsão boa o bastante para sustentar o
cálculo automático do ponto de reposição, e qual deles se adapta melhor. Duas
partes: a segunda pressupõe a primeira, e a primeira precisava ser testada.

**Por que Holt-Winters e Prophet, e não outros?**
Holt-Winters porque Hyndman e Athanasopoulos (2021) recomendam suavização
exponencial como ponto de partida robusto com dados limitados; Prophet por ser
de família diferente (regressão bayesiana), o que torna a comparação
informativa. ARIMA foi descartado: exige estacionariedade e identificação caso a
caso, inviável para centenas de produtos reprocessados sem intervenção.

**Por que não usaram redes neurais?**
Volume de dados e interpretabilidade. Algumas centenas de observações por
produto não sustentam modelos com muitos parâmetros sem sobreajuste, e o sistema
precisa justificar ao lojista por que recomenda um pedido.

**Qual a contribuição em relação ao GRP03?**
Ele aplicou Prophet a estoque farmacêutico **com um modelo só, sem comparação**,
e não chegou ao ponto de reposição. Nós comparamos dois modelos sob protocolo
idêntico, confrontamos ambos com um piso e levamos até a instrução de compra.

### Metodologia

**Por que dados sintéticos? Não é circular?**
Não — é outra pergunta. Com dado real mede-se desempenho no mundo; com sintético
verifica-se se o motor **recupera uma estrutura conhecida por construção**. É
validação de instrumentação. A circularidade existiria se os modelos tivessem
acesso à fórmula geradora — eles recebem só a série. E o limite está declarado
na metodologia, não escondido.

**Por que 80/20 cronológico e não validação cruzada?**
→ seção 3.6 deste guia.

**Por que a fórmula completa de Ballou?**
→ seção 3.9 deste guia. Número de bolso: 15,55 contra 26,56, diferença de 70,8%.

**Por que Z calculado e não 1,645?**
Porque a tela permite mudar o nível de serviço. Com Z fixo, mudar de 95% para
99% não teria efeito — o controle seria decorativo.

**Como garantem que os números do artigo são os que o sistema produz?**
A camada de análise **importa os módulos de produção** em vez de reimplementar
as fórmulas. Não existe segunda implementação capaz de divergir.

**Por que mínimo de 90 dias de histórico?**
Abaixo disso um modelo de ciclo semanal tem menos de 13 repetições do padrão que
precisa estimar. Produtos abaixo do mínimo são recusados e a tela sinaliza.

**Por que a ABC ficou no backend?**
O motor opera um produto por vez e não enxerga o catálogo; ABC é ranking
relativo que exige todos simultaneamente.

### Resultados

**Por que o MAPE de alguns produtos é tão alto?**
Propriedade da série, não do método. O pão francês tem o maior ruído do conjunto
— e o baseline ingênuo erra 93% nele, contra 81% do modelo. Acima de 50% o
sistema marca a previsão como de baixa confiança.

**E a dobra de 188%?**
→ seção 4.4 deste guia.

**Vocês dizem que os modelos empataram. Então o trabalho não concluiu nada?**
Concluiu duas coisas. Que ambos superam a referência mínima em 10/10 produtos,
com 45,1% menos erro — essa é a conclusão prática. E **por que** empataram, com
explicação verificável nos parâmetros ajustados — essa é a conclusão teórica, e
delimita o alcance do resultado a dados sem quebras.

**Se empataram, por que manter os dois modelos no sistema?**
Porque o empate é propriedade de dados estacionários. Em série real, com quebras
de patamar, espera-se que α > 0 e que os modelos se separem. A arquitetura foi
dimensionada para esse caso.

**Por que o baseline não aparece como terceiro modelo do motor?**
Porque é instrumento de avaliação, não candidato. Ele mede se a modelagem se
justifica; não é oferecido ao lojista.

### Arquitetura e infraestrutura

**Por que o motor não acessa o banco?**
Para reduzir acoplamento: ele recebe JSON e devolve JSON. Pode ser reexecutado,
reimplantado ou substituído sem risco de inconsistência, porque não detém
estado. O backend é o único dono do banco.

**Por que uma instância só, e banco em contêiner?**
Restrição de crédito acadêmico, não preferência técnica. Balanceador gerenciado
tem taxa fixa mensal alta e serviço de banco gerenciado consumiria metade do
crédito. Está declarado no artigo, com a ressalva de que em uso real o banco
precisaria ser revisto.

**Por que a sub-rede é pública?**
Uma privada exigiria NAT Gateway, que tem custo fixo. Decisão consciente,
registrada no Terraform.

---

## 6. Onde somos vulneráveis

Lista honesta. Melhor conhecer antes da banca.

| # | Vulnerabilidade | Resposta preparada |
|---|---|---|
| 1 | **Não há dados reais.** A proposta prometia validação com parceiro. | Está declarado na metodologia (3.3.4) e nas limitações. O caminho de ingestão existe e funciona; é o trabalho futuro prioritário. |
| 2 | **A sazonalidade mais citada não foi modelada.** 6/7 relatam ciclo mensal; o dataset só tem semanal. | Declarado nas limitações. Condição para que a validação externa seja conclusiva. |
| 3 | **A dor nº 1 dos entrevistados está fora do escopo.** 3/7 citam validade; nenhum cita previsão. | Declarado. A decisão segue justificada pelo recorte, mas a prioridade do usuário é outra — e isso está escrito. |
| 4 | **Amostra de 7, por conveniência.** | Declarada como tal. Não se afirma representatividade; serve para qualificar o problema e calibrar parâmetros. |
| 5 | **Nenhum teste de usabilidade.** A adoção medida é condicional (4/7 "dependeria"). | Declarado nas limitações. |
| 6 | **Recursos do Prophet desativados** (feriados, promoção). | Equaliza a comparação, mas subutiliza o modelo. Declarado. |
| 7 | **σ da demanda inclui dias de loja fechada**, inflando a reserva. | Escolha conservadora, declarada. |
| 8 | **Um ano de histórico** não permite sazonalidade anual. | Exigiria dois ciclos. Declarado. |

**Regra geral para a arguição:** tudo nessa tabela já está escrito no artigo. Se
a banca levantar qualquer um desses pontos, a resposta é *"sim, está na
seção X"* — e não uma defesa improvisada. Limitação declarada é força; limitação
descoberta pela banca é fraqueza.

---

## 7. Divisão de estudo entre o grupo

Sugestão, para ninguém precisar dominar tudo:

| Frente | O que estudar | Seções do guia |
|---|---|---|
| **Problema e campo** | entrevistas, BPMN, ABRAS, Sebrae, justificativa | 1, 4.1, 5 (intro) |
| **Modelos e métricas** | série temporal, HW, Prophet, MAE/RMSE/MAPE, baseline | 3.1–3.5, 4.2–4.3 |
| **Protocolo e validação** | split cronológico, backtesting, resíduos, a dobra de 188% | 3.6–3.8, 4.4 |
| **Negócio e KPIs** | Ballou, ponto de reposição, semáforo, curva ABC, telas | 3.9–3.11, 4.5 do artigo |
| **Arquitetura e infra** | C4, banco, Terraform, deploy, invariantes | 5 (arquitetura) |

**Todos devem saber, independentemente da frente:**

1. A pergunta de pesquisa e a resposta em duas partes
2. O número principal: **10/10 produtos, 45,1% de redução mediana**
3. Por que os dados são sintéticos, e que isso está declarado na metodologia
4. Que **7 de 7** entrevistados decidem pela prateleira

---

## 8. Como rodar as coisas

```bash
# Regenerar análise, figuras e números (ml-service/)
venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace analysis/analise_modelos.ipynb
venv/Scripts/python.exe analysis/_coletar_dados_doc.py

# Da raiz do repositório
ml-service/venv/Scripts/python.exe docs/artigo/verificar_numeros.py saida.txt   # confere as tabelas
ml-service/venv/Scripts/python.exe docs/artigo/gerar_der.py der.svg             # DER a partir das migrations
ml-service/venv/Scripts/python.exe docs/artigo/gerar_infra.py infra.svg         # infra a partir do Terraform
ml-service/venv/Scripts/python.exe docs/artigo/gerar_docx.py                    # monta o artigo .docx
```

O `.docx` sai em `docs/artigo/artigo-stocksense.docx`. Não é versionado — cada
um gera o seu.

**Sistema em produção:** http://107.20.236.251 — ver `infra/README.md`.
