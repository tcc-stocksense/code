# Guia de Importação de Dados — v2.0

> **Motor de Otimização Preditiva de Estoque (StockSense) · Mercados de Bairro · TCC 2026**

> ⚠️ **Status / fonte de verdade.** Spec de formato e regras das planilhas de importação. Em caso de conflito, o `CLAUDE.md` da raiz prevalece. **Nota:** a planilha `6_perdas_estoque` (módulo ESG) consta abaixo por fidelidade ao guia original, mas o ESG foi **removido do escopo** nas decisões de arquitetura — não implementar.

## 1. Introdução

Este documento descreve o formato e as regras para envio de dados históricos ao motor. O sistema usa esses dados para calcular previsões de demanda, pontos de reposição e alertas de ruptura. O gestor deve fornecer os dados nos formatos especificados, usando os modelos de planilha (`.xlsx`) disponibilizados junto a este guia.

**Legenda de obrigatoriedade:**

- **Obrigatório** — precisa estar preenchido para o funcionamento básico do sistema.
- **Recomendado** — aumenta a precisão das previsões; enviar quando disponível.
- **Opcional** — desejável para funcionalidades avançadas, não exigido na carga inicial.

## 2. Visão geral das planilhas

Os dados são organizados em seis planilhas independentes. O sistema opera em duas modalidades:

- **MVP (foco da entrega):** requer apenas `2_produtos` e `5_vendas`. O sistema assume valores padrão para todos os campos não fornecidos.
- **Completo (desejável):** inclui estabelecimento, fornecedores e relação produto × fornecedor, enriquecendo o cálculo do ponto de reposição com dados reais de lead time.

| Planilha | Entidade | Envio MVP | Descrição |
|---|---|---|---|
| `1_estabelecimento` | Estabelecimento | Desejável | Dados cadastrais do mercado |
| `2_produtos` | Produto | **Obrigatório** | Catálogo com preços e estoque atual |
| `3_fornecedores` | Fornecedor | Desejável | Fornecedores vinculados ao estabelecimento |
| `4_produto_fornecedor` | Produto × Fornecedor | Desejável | Lead time real por produto/fornecedor |
| `5_vendas` | Venda | **Obrigatório** | Histórico de vendas (mín. 90 dias) |
| `6_perdas_estoque` | Perda de Estoque | Opcional | Perdas por vencimento, avaria ou furto *(ESG — fora do escopo)* |

**Comportamento sem planilhas desejáveis:** o sistema assume `lead_time_medio = 3` dias, `variabilidade_lead_time = 1.0` e um fornecedor padrão mockado pelo backend. Recomenda-se enviar as planilhas desejáveis em um segundo momento.

## 3. Planilha 1 — Estabelecimento (`1_estabelecimento`)

Dados de identificação do mercado. Deve conter exatamente uma linha. Quando não enviada, o sistema usa o estabelecimento padrão do backend. **Desejável.**

| Campo | Tipo | Obrigatoriedade | Descrição / Regras |
|---|---|---|---|
| `nome_fantasia` | Texto (100) | Obrigatório | Nome do mercado. Ex: Mercadinho do Zé |
| `cnpj` | Texto (18) | Opcional | CNPJ no formato XX.XXX.XXX/XXXX-XX |
| `endereco` | Texto (200) | Opcional | Endereço completo do estabelecimento |

## 4. Planilha 2 — Produtos (`2_produtos`)

Catálogo completo de produtos. Cada linha é um produto único. O `produto_id` é definido pelo gestor e referenciado nas demais planilhas. **Obrigatória.**

| Campo | Tipo | Obrigatoriedade | Descrição / Regras |
|---|---|---|---|
| `produto_id` | Inteiro | Obrigatório | ID único do produto. Não repetir. |
| `nome` | Texto (100) | Obrigatório | Ex: Arroz Tipo 1 5kg |
| `estoque_atual` | Inteiro | Obrigatório | Quantidade em estoque na data de envio. Ex: 40 |
| `categoria` | Texto (50) | Recomendado | Ex: Grãos, Laticínios, Bebidas, Higiene |
| `unidade_medida` | Texto (10) | Recomendado | Ex: un, kg, lt, cx, pct |
| `preco_custo` | Decimal (10,2) | Recomendado | Preço de compra. Ex: 12.50 |
| `preco_venda` | Decimal (10,2) | Recomendado | Preço de venda. Ex: 18.90 |
| `nivel_servico_alvo` | Decimal (5,2) | Opcional | Nível de serviço (0 a 1). Padrão: 0.95 |

> ✕ **Campos calculados automaticamente — não incluir na planilha:** `classe_abc`, `desvio_padrao_demanda`, `ponto_reposicao`, `estoque_seguranca`, `data_ultimo_calculo`.

## 5. Planilha 3 — Fornecedores (`3_fornecedores`)

Lista de fornecedores. Quando não enviada, o sistema usa um fornecedor padrão mockado com lead time de 3 dias. **Desejável** — combinada com `4_produto_fornecedor`, permite usar o lead time real no cálculo do ponto de reposição.

| Campo | Tipo | Obrigatoriedade | Descrição / Regras |
|---|---|---|---|
| `fornecedor_id` | Inteiro | Se enviado | ID único do fornecedor |
| `nome` | Texto (100) | Se enviado | Nome ou razão social |
| `contato` | Texto (50) | Opcional | Telefone ou e-mail |

## 6. Planilha 4 — Produto × Fornecedor (`4_produto_fornecedor`)

Relaciona produtos a fornecedores e informa o lead time. Um produto pode ter mais de um fornecedor — uma linha por combinação. **Desejável** e depende de `3_fornecedores`.

| Campo | Tipo | Obrigatoriedade | Descrição / Regras |
|---|---|---|---|
| `produto_id` | Inteiro | Se enviado | Deve existir em `2_produtos` |
| `fornecedor_id` | Inteiro | Se enviado | Deve existir em `3_fornecedores` |
| `lead_time_medio` | Inteiro | Se enviado | Dias entre pedido e entrega. Padrão backend: 3 |
| `variabilidade_lead_time` | Decimal (10,4) | Opcional | Desvio padrão do lead time. Padrão: 1.0 |

> **Sobre `variabilidade_lead_time`:** é o desvio padrão do lead time — o quanto o prazo de entrega oscila. Ex.: entrega normalmente em 3 dias, às vezes 4 ou 5 → variabilidade ≈ 1.0. Quando não informado, usa o padrão 1.0 (conservador e estatisticamente seguro). O `lead_time_medio` é o campo mais impactante para a qualidade do ponto de reposição.

## 7. Planilha 5 — Vendas (`5_vendas`)

Histórico de vendas — a planilha mais crítica para o motor. Cada linha é uma venda individual ou um agrupamento diário por produto. **Obrigatória — mínimo 90 dias de histórico.**

| Campo | Tipo | Obrigatoriedade | Descrição / Regras |
|---|---|---|---|
| `produto_id` | Inteiro | Obrigatório | Deve existir em `2_produtos` |
| `data_hora` | Data/Hora | Obrigatório | `YYYY-MM-DD` ou `YYYY-MM-DD HH:MM:SS`. Só data → assume 00:00:00 |
| `quantidade` | Inteiro | Obrigatório | Unidades vendidas. Maior que zero. |
| `valor_venda` | Decimal (10,2) | Recomendado | Valor total da venda. **Necessário para a Curva ABC.** |
| `is_promocional` | Inteiro (0/1) | Opcional | 1 se promoção, 0 caso contrário. Padrão: 0. Melhora o Prophet. |

> **Formato de data:** padrão ISO 8601 (`YYYY-MM-DD`). **Não** usar formatos regionais como `DD/MM/AAAA`.

> **Por que mínimo 90 dias?** É o necessário para que Holt-Winters e Prophet identifiquem padrões semanais e mensais com confiabilidade estatística. Com menos, o modelo não distingue variação normal de tendência real.

## 8. Planilha 6 — Perdas de Estoque (`6_perdas_estoque`) — *ESG, fora do escopo*

> ⚠️ **Não implementar no MVP.** O módulo ESG/perdas foi removido do escopo. Mantido aqui apenas por fidelidade ao guia original.

| Campo | Tipo | Obrigatoriedade | Descrição / Regras |
|---|---|---|---|
| `produto_id` | Inteiro | Se enviado | Deve existir em `2_produtos` |
| `quantidade` | Inteiro | Se enviado | Unidades perdidas. Maior que zero. |
| `motivo` | Texto (50) | Recomendado | Ex: vencimento, avaria, furto, excesso |
| `data_perda` | Data | Recomendado | `YYYY-MM-DD`. Padrão: data de envio |

## 9. Regras gerais de preenchimento

### 9.1 Formatos aceitos

| Tipo de dado | Formato esperado | Exemplos |
|---|---|---|
| Data | `YYYY-MM-DD` | `2025-03-15` |
| Data e Hora | `YYYY-MM-DD HH:MM:SS` | `2025-03-15 14:30:00` |
| Decimal | Ponto como separador | `12.50`, `0.95`, `1890.00` |
| Booleano | `0` ou `1` (inteiro) | `0` = falso, `1` = verdadeiro |
| Inteiro | Número sem casas decimais | `1`, `40`, `120` |
| Texto | Sem aspas na planilha | `Arroz Tipo 1 5kg` |

### 9.2 Checklist antes de enviar

- `2_produtos` preenchida com ao menos `produto_id`, `nome` e `estoque_atual`.
- `5_vendas` com pelo menos 90 dias de histórico.
- Todo `produto_id` em vendas existe em produtos.
- Se enviou `4_produto_fornecedor`: todos os `fornecedor_id` existem em `3_fornecedores`.
- Datas em `YYYY-MM-DD` (não `DD/MM/AAAA`).
- Decimais com ponto (`.`), não vírgula.
- Sem linhas completamente vazias no meio dos dados.
- `quantidade` sempre maior que zero.

## 10. Dúvidas frequentes

**O sistema de caixa não exporta por produto.** Se gera só totais diários de faturamento, preencha a planilha de vendas agrupando por produto e data: uma linha por produto por dia, com a soma das quantidades.

**Não tenho histórico digital.** O sistema aceita apenas `.xlsx`. Histórico em papel pode ser digitado nos modelos fornecidos. O mínimo de 90 dias deve ser respeitado.

**Posso enviar só as obrigatórias?** Sim — `2_produtos` e `5_vendas` bastam para o funcionamento básico. O sistema assume padrões para lead time (3 dias) e fornecedor. As desejáveis enriquecem o ponto de reposição.

**E se não enviar fornecedores?** O backend popula um fornecedor padrão com `lead_time_medio = 3` e `variabilidade_lead_time = 1.0`. As previsões funcionam, mas o ponto de reposição usa esse padrão em vez do prazo real.

**O `data_hora` exige horário?** Não. Só a data (`YYYY-MM-DD`) é suficiente; o sistema completa com `00:00:00`.
