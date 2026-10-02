# 1 Introdução

Os pequenos e médios mercados de bairro ocupam uma posição particular no varejo
alimentício brasileiro: têm volume de operação suficiente para gerar dados
relevantes sobre a própria demanda e, na maioria dos casos, nenhuma ferramenta
para aproveitá-los. A gestão de estoque nesses estabelecimentos é
predominantemente manual e reativa — decide-se o que comprar observando a
prateleira e recorrendo à experiência acumulada do gestor.

Essa forma de decidir produz dois erros simétricos e igualmente onerosos. A
**ruptura** ocorre quando o produto acaba antes da reposição, e custa a venda
não realizada e o risco de perder o cliente. O **excesso** imobiliza capital em
mercadoria parada e, em perecíveis, converte-se em perda direta. Os dois nascem
da mesma causa: decidir quanto comprar sem estimar quanto se vai vender.

A dimensão do problema é documentada pelo setor. Segundo a ABRAS (2023), a
ruptura derruba entre 5% e 10% das vendas nos estabelecimentos afetados, e 32%
dos consumidores migram para um concorrente quando não encontram o produto que
procuram.

**Figura 1 - Processo de reposição atual (BPMN AS-IS)**

`[FIGURA: docs/artigo/figuras/bpmn-as-is.png]`

Fonte: Autoral, 2026

A Figura 1 modela o processo tal como ocorre hoje, levantado junto a
estabelecimentos do segmento. A cadeia de reposição parte da atividade
"verificar estoque visualmente ou por planilha" e passa por "identificar
produtos acabando", apoiada na intuição do responsável; o pedido é feito por
telefone ou aplicativo de mensagens e o estoque é atualizado manualmente depois
do recebimento. Não há, em nenhum ponto do fluxo, estimativa de demanda futura:
a decisão de compra se forma a partir do que já está faltando, nunca do que vai
faltar.

O diagrama também explicita a consequência. A raia do atendimento termina, num
de seus caminhos, no evento "venda perdida por ruptura de estoque" — o desfecho
que o processo atual não tem como evitar, porque só identifica a falta depois
que o cliente a encontra.

Um levantamento conduzido para este trabalho junto a sete estabelecimentos do
segmento confirma o diagrama de maneira categórica: **os sete** apontam a
inspeção visual da prateleira como critério de decisão de compra, inclusive os
quatro que já dispõem de algum software de controle. A informatização, quando
existe, registra o passado sem participar da decisão — o mesmo padrão que
Ferreira e Mota (2022) identificaram em estudo de caso num supermercado de
pequeno porte.

A lacuna é estrutural, e não de disposição do gestor. O Sebrae (2023a) descreve
a trajetória tecnológica esperada do pequeno varejista: começar por planilhas e
evoluir para sistemas integrados conforme a operação cresce. Entre os dois
extremos, porém, não existe oferta: a planilha registra mas não prevê nem
alerta, e o sistema integrado impõe barreiras de custo e complexidade que o
segmento raramente transpõe. É nesse intervalo que este trabalho se situa.

## 1.1 Problema de pesquisa

Modelos de previsão de demanda por séries temporais, aplicados ao histórico de
vendas de um mercado de bairro, produzem estimativas acuradas o bastante para
sustentar o cálculo automático do ponto de reposição — e qual deles se adapta
melhor a esse tipo de série?

A pergunta tem duas partes deliberadamente distintas. A segunda — qual modelo
vence — pressupõe que ao menos um deles seja útil, e essa suposição precisa ser
testada antes, não depois. Responder apenas qual dos dois é melhor seria
informativo somente se ambos já tivessem demonstrado valor sobre uma referência
mínima.

## 1.2 Objetivos

O objetivo geral deste trabalho é desenvolver e avaliar empiricamente um motor
de otimização preditiva de estoque voltado a pequenos e médios mercados de
bairro, capaz de converter histórico de vendas em recomendação de reposição.
Para alcançá-lo, foram definidos os seguintes objetivos específicos:

1. Implementar os modelos Holt-Winters e Prophet sobre séries de demanda diária
   por produto e compará-los sob protocolo de avaliação idêntico;
2. Estabelecer um critério objetivo e automatizável de seleção do modelo por
   produto, em vez de adotar um único modelo para todo o catálogo;
3. Verificar se os modelos adotados superam um baseline ingênuo sazonal,
   estabelecendo se a modelagem estatística se justifica neste contexto;
4. Converter a previsão de demanda em estoque de segurança, ponto de reposição e
   dias até ruptura, pelas formulações de Ballou (2006);
5. Integrar o motor a uma aplicação web operável por gestor sem perfil técnico e
   implantá-la em ambiente de produção.

## 1.3 Justificativa

A justificativa do trabalho apoia-se em três evidências convergentes.

A primeira é o **impacto financeiro mensurável**. A ABRAS (2023) documenta uma
relação de proporcionalidade entre redução de ruptura e recuperação de vendas:
a cada quatro pontos percentuais reduzidos na taxa de ruptura de um item,
recupera-se um ponto percentual nas vendas desse item. O coeficiente permite
estimar o retorno de uma intervenção preditiva em termos financeiros, em vez de
apenas qualitativos. No levantamento conduzido para este trabalho, seis dos sete
respondentes souberam estimar a própria perda, e todos a situaram entre R$ 100 e
R$ 1.000 por mês — valor expressivo para a margem do segmento.

A segunda é o **custo de oportunidade do tempo**. Três dos sete entrevistados
declaram dedicar mais de cinco horas semanais à conferência de estoque e à
montagem de pedidos. Em estabelecimentos de um a nove funcionários, esse tempo
é subtraído diretamente de atividades de atendimento e gestão.

A terceira é a **viabilidade técnica**. Quatro dos sete estabelecimentos
conseguem exportar vendas por produto e por dia a partir dos sistemas que já
possuem, o que torna a ingestão por planilha eletrônica um caminho de adoção
realista — sem exigir integração com sistemas de frente de caixa, que
reintroduziria a barreira de custo e complexidade que o trabalho pretende
contornar.

Há ainda uma justificativa de natureza acadêmica. A literatura aplicada
frequentemente adota um modelo de previsão por conveniência, sem confrontá-lo
com alternativas sobre os mesmos dados, e raramente avança da previsão até o
parâmetro operacional que a torna acionável. Este trabalho procura cobrir as
duas lacunas: compara dois modelos de famílias distintas sob protocolo idêntico,
confronta ambos com uma referência mínima e conduz o resultado até a instrução
de compra que chega ao gestor.
