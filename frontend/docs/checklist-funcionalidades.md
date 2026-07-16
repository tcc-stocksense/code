# checklist-funcionalidades.md — Inventário completo do protótipo StockSense

> Lista exaustiva de tudo que existe no protótipo hoje — toda tela, todo botão, toda ação, todo cálculo — para validar contra o que já foi codado. Convenção: **✅ funcional no protótipo** (mock) · **🎭 simulado** (parece funcionar, não persiste/não é real) · **🚫 sem ação** (visual, não faz nada).

---

## Navegação global (shell — `app.jsx`)

**Sidebar** (esquerda, sempre visível após login):
- Logo + nome do sistema.
- Seção "Operação": Home, Estoque, Alertas de reposição, Curva ABC, Sugestão de compra — cada item ✅ navega e destaca o item ativo.
- Seção "Sistema": Importar dados, Configurações — mesma navegação.
- Seção "Acesso técnico" (rodapé): Comparativo de modelos — mesma navegação.

**Topbar** (topo, sempre visível):
- Nome do estabelecimento + CNPJ (texto fixo, não editável aqui).
- Avatar com iniciais do usuário → ✅ clique faz **logout** (volta para tela de login).

**Roteamento:** por hash (`#home`, `#estoque` etc.), com deep-link — abrir a URL direto numa tela pula o login (usado só para exportação/QA, não é requisito de produto).

---

## Tela 1 — Login (`LoginScreen`)

| Elemento | Comportamento |
|---|---|
| Campo Email | ✅ editável, pré-preenchido |
| Campo Senha | ✅ editável (type password), pré-preenchido |
| Botão "Entrar" | ✅ submit do form → loga e vai para Home |
| Link "Esqueci minha senha" | 🚫 sem ação (`preventDefault`) |
| Rodapé "v0.4 protótipo" | texto estático |

⚠️ Não há validação de credenciais — qualquer clique em "Entrar" loga.

---

## Tela 2 — Home / Dashboard (`HomeScreen`)

**Cabeçalho:** saudação "Bom dia, {nome}" + data fixa.

**Banner de alerta** (laranja, aparece sempre que há itens em risco):
- Texto: "Você tem N produtos que precisam ser pedidos hoje" + "M em estado crítico".
- Botão **"Ver lista"** → ✅ navega para Alertas.

**4 KPIs** (cartões):
1. **Risco de faltar** — conta produtos `diasRuptura ≤ 7`. Contexto: "nos próximos 7 dias".
2. **Crítico agora** — conta produtos `diasRuptura < 3` (cor vermelha). Contexto: "menos de 3 dias até zerar".
3. **Valor em risco** — `Σ (faturamento do produto × 0,07 ÷ 4)` somado só para produtos em risco (7d). Formatado compacto (`R$ 12.480`). Contexto: "venda perdida estimada (coef. ABRAS)".
4. **Acurácia do modelo** — `100 − MAPE do Prophet`. Contexto: "MAPE médio últimas 4 semanas".

**Gráfico "Previsão de faturamento":**
- Linha histórica (8 semanas) + linha tracejada de projeção (4 semanas).
- Eixo Y em R$ compacto; legenda "histórico" / "projeção".
- Dados gerados por fórmula sintética (seno + ruído aleatório) — 🎭 não é o modelo real.

**Tabela "Próximos alertas de reposição":**
- Botão **"Ver todos"** → ✅ navega para Alertas.
- Top 5 produtos com `diasRuptura ≤ 5`, ordenados por urgência.
- Colunas: semáforo (bolinha), produto, "até ruptura" (dias), "sugestão" (`demandaDiaria × (leadTime+7)`, arredondado), botão "Detalhe".
- ✅ Clique na linha inteira ou no botão "Detalhe" → navega para Detalhe do produto.

---

## Tela 3 — Importar dados (`ImportarScreen` + `ImportBlock`)

**5 blocos de planilha, cada um independente:**
1. Produtos (obrigatória) — campos: sku, nome, categoria, preço, unidade.
2. Vendas (obrigatória) — campos: data, sku, quantidade, valor_total.
3. Estabelecimento (desejável) — nome, cnpj, endereço.
4. Fornecedores (desejável) — id, nome, contato, lead_time_dias.
5. Produto × Fornecedor (desejável) — sku, id_fornecedor, preco_compra.

**Painel expansível "Como preparar suas planilhas":**
- ✅ Clique expande/recolhe (seta gira).
- Link "Baixar modelos de planilha" → 🚫 sem ação.

**Por bloco, 4 estados possíveis:**
- **Vazio:** área de drop — ✅ clique simula envio (`enviar()`), dispara "processing" e após 1.6s vira "sucesso".
- **Processando:** spinner + "Validando N linhas…" (timeout fixo, não real).
- **Sucesso:** ✅ ícone check, nome do arquivo, contagem de linhas processadas, botões **"Substituir"** (reenviar) e **"Remover"** (volta a vazio).
- **Erro:** mensagem de erro fixa ("Linha 45: data fora do formato...") + botão de reenviar. 🎭 erro é sempre o mesmo, não depende do arquivo real.

**Rodapé:**
- Contador: "N planilhas enviadas" + status ("obrigatórias OK" ou "envie Produtos e Vendas").
- Botão **"Processar dados"** — habilitado só quando Produtos + Vendas = sucesso. 🚫 sem ação real ao clicar (não navega, não processa).

⚠️ Todo o upload/validação é **simulado** — não há parsing real de arquivo.

---

## Tela 4 — Estoque (`EstoqueScreen`)

**Filtros (barra superior):**
- Busca por nome (texto livre) — ✅ filtra em tempo real.
- Select Categoria (todas + 7 categorias) — ✅ filtra.
- Select Status (todos/crítico/atenção/ok) — ✅ filtra.
- Select Classe ABC (todas/A/B/C) — ✅ filtra.
- Todos os filtros combinam entre si.

**Tabela de produtos** (ordenada por urgência — `diasRuptura` crescente):
- Colunas: Status (semáforo + label), Produto, Categoria, **Estoque (editável)**, Até ruptura, ABC (badge), botão Detalhe.
- ✅ Clique em qualquer linha → navega para Detalhe do produto.
- ✅ **Célula de Estoque é editável inline**: clique abre stepper (− / input / +) com confirmar (✓ verde) ou cancelar (✕). Ao salvar, persiste em `localStorage` e recalcula `diasRuptura` = `estoque ÷ demandaDiaria`. Célula ganha destaque quando o valor foi ajustado manualmente.
- Linha "Nenhum produto bate com os filtros" quando filtro não retorna nada.

**Rodapé:**
- "Mostrando N de M produtos".
- Paginação — 🚫 visual apenas, sempre "Página 1 de 1", botões Anterior/Próxima desabilitados.

---

## Tela 5 — Alertas de reposição (`AlertasScreen`)

**Regra de entrada:** produtos com `diasRuptura ≤ 7`, ordenados por urgência.

**Estado vazio:** se não há nenhum alerta, mostra card "Nenhum produto precisa ser pedido hoje."

**Cabeçalho:**
- Subtítulo: "N produtos precisam ser pedidos nos próximos 3 dias · M no total".
- Botão **"Gerar relatório de compra"** → ✅ navega para Sugestão de compra. ⚠️ Ver nota de dependência abaixo.

**Por produto (card/linha `alert-row`, cor muda se crítico ou atenção):**
- Nome, categoria, "estoque atual X un".
- "Vai faltar em N dias" (ou "Já zerou" se `diasRuptura = 0`) + "lead time fornecedor: N dias".
- "Pedir X un" (`= demandaDiaria × (leadTime+7)`, arredondado para cima) + nome do fornecedor.
- Botão **"Detalhe"** → ✅ navega para Detalhe do produto.
- Botão **"Marcar como pedido"** → ✅ toggle de estado local (vira "Pedido" com check). **Não persiste** — estado só existe em memória da sessão/tela.

---

## Tela 6 — Detalhe do produto (`DetalheScreen`)

**Botão "Voltar para estoque"** → ✅ navega para Estoque.

**Cabeçalho:** nome do produto, categoria + classe, badge de status (semáforo).

**Gráfico "Demanda diária":** 90 dias histórico + 30 dias projeção (linha tracejada). Fórmula sintética (seno + tendência + ruído) — 🎭 não é modelo real.

**3 KPIs:**
1. **Demanda média/dia** — média aritmética do histórico de 90 dias.
2. **Variabilidade** — desvio-padrão (±) + coeficiente de variação (CV%).
3. **Tendência** — compara média dos primeiros 14 dias vs últimos 14 dias; mostra "subindo"/"descendo"/"estável" com ícone e % de variação.

**Tabela "Vendas por semana"** — últimas 4 semanas: total vendido e média/dia por semana (agregado do histórico sintético).

**Painel lateral direito:**
- **Estoque atual (editável)** — mesmo componente da tela Estoque, variante painel: botão "Editar" abre stepper grande (− / input / +) com Salvar/Cancelar. Se editado manualmente, mostra tag "ajustado manualmente" + link **"desfazer"** (✅ reverte ao valor original).
- **"Você precisa pedir?"** — Sim (vermelho) se `diasRuptura ≤ 7`, senão Não (verde).
- **Ponto de reposição** — `média × leadTime + 1,65 × desvio × √leadTime` (unidade do produto).
- **Estoque de segurança** — `1,65 × desvio × √leadTime`.
- **Dias até ruptura** — `estoque atual ÷ demanda média/dia`, recalculado ao vivo.
- **Lead time fornecedor** — valor fixo do produto (dias).
- **Nível de serviço alvo** — fixo em 95% (tooltip explicando o que significa).
- Botão **"Marcar para pedido"** → 🚫 sem ação.
- Botão **"Editar parâmetros"** → ✅ abre modal.

**Card "Fornecedor"** (abaixo do painel): nome do fornecedor + preço médio por unidade.

**Modal "Editar parâmetros"** (`ParametrosModal`):
- Campo "Lead time do fornecedor (dias)" — ✅ editável localmente.
- Campo "Nível de serviço alvo (%)" — ✅ editável localmente (min 50, max 99).
- Botão "Cancelar" → fecha modal sem salvar.
- Botão "Salvar parâmetros" → 🎭 fecha o modal mas **não persiste** o valor nem recalcula ponto de reposição/estoque de segurança na tela.

---

## Tela 7 — Curva ABC (`ABCScreen`)

**Select de período** (30/60/90 dias / personalizado) → 🎭 muda o valor selecionado mas **não recalcula** nada na tela (dados são sempre os mesmos).

**Gráfico Pareto:** top 30 produtos por faturamento (barras, cor por classe A/B/C) + linha de % acumulado + linha de referência 80% (vermelha).

**3 cards por classe (A/B/C):** contagem de produtos + "% do faturamento" + rótulo de prioridade ("prioridade máxima" / "monitorar" / "gestão por exceção").

**Tabela completa** (todos os produtos, ordenados por faturamento desc): Classe (badge), Produto, Faturamento, % do total, % acumulada.

---

## Tela 8 — Sugestão de compra (`SugestaoScreen`)

**Regra de entrada:** produtos com `diasRuptura ≤ 10`, agrupados por fornecedor.

**Estado vazio:** card "Nenhuma compra sugerida no momento." se não há itens.

**Card de Resumo** (canto superior direito): valor total (soma dos subtotais **apenas dos itens marcados**) + "N itens · M fornecedores".

**Por grupo de fornecedor (um card cada):**
- Cabeçalho: nome do fornecedor, "N itens sugeridos · lead time X dias", subtotal do grupo (só itens marcados).
- Botão **"PDF"** → 🚫 sem ação.
- Botão **"WhatsApp"** → 🚫 sem ação.
- **Tabela do grupo**, por item:
  - ✅ Checkbox — inclui/exclui o item do total (afeta subtotal do grupo e total geral).
  - Nome do produto.
  - ✅ **Quantidade editável** (input numérico) — inicial = `demandaDiaria × (leadTime+7)` arredondado para cima. Editar recalcula subtotal ao vivo.
  - Preço unitário (fixo).
  - Subtotal = quantidade × preço unitário (recalculado ao vivo).

**Rodapé:**
- Botão **"Salvar rascunho"** → 🚫 sem ação.
- Botão **"Confirmar pedidos"** → 🚫 sem ação.

⚠️ Chegada a esta tela também acontece pelo botão "Gerar relatório de compra" em Alertas.

---

## Tela 9 — Configurações (`ConfigScreen`)

**3 abas:**

**Aba "Estabelecimento":**
- Campos editáveis: Nome fantasia, CNPJ, Endereço (estado local, pré-preenchido).

**Aba "Usuário":**
- Campos editáveis: Nome, Email.
- Link "Alterar senha" → 🚫 sem ação.

**Aba "Notificações":**
- Toggle **"Alerta de estoque crítico"** — ✅ liga/desliga (estado local).
- Select **"Resumo por email"** — Diário 08:00 / Semanal segunda 08:00 / Não enviar.

**Botão "Salvar"** (comum às 3 abas) → 🎭 mostra mensagem "✓ Salvo." por 2 segundos, **não persiste** nenhum campo — ao trocar de aba ou recarregar, os valores voltam ao mock original.

---

## Tela 10 — Comparativo de modelos / Acesso técnico (`TecnicaScreen`)

**Banner:** "Acesso técnico · este painel é destinado à equipe de modelagem e à banca avaliadora. Não tem efeito no fluxo do gestor." (aviso, não interativo).

**3 KPIs agregados** (MetricCard): MAPE, RMSE, MAE — comparando Holt-Winters × Prophet, com badge "melhor" no menor valor + diferença absoluta.

**Gráfico de barras agrupadas:**
- Select de métrica (MAPE/RMSE/MAE) → ✅ troca os dados do gráfico.
- Compara Holt-Winters × Prophet por produto (12 produtos mock).

**Tabela "Métricas detalhadas por produto":** MAPE/RMSE/MAE de cada modelo por produto + badge "Recomendado" (o modelo com menor MAPE).

**Log de execuções:** bloco de texto monoespaçado simulando log de retraining (timestamps, contagem de séries, MAPE agregado, persistência em banco) — texto estático, não é log real.

---

## Modelo de dados (campos existentes, para conferência com o back-end real)

**Produto:** `id, nome, categoria, estoque, unidade, diasRuptura, classe (A/B/C), precoMedio, demandaDiaria, leadTime, fornecedor, faturamento`.

**Fornecedor:** `id, nome, contato, leadTime`.

**Estabelecimento:** `nome, cnpj, endereco`.

**Usuário:** `nome, email, iniciais`.

**Perdas recentes** (`PERDAS_RECENTES`): `data, produto, quantidade, unidade, motivo, valor` — existe no código mas **nunca é exibido em nenhuma tela**.

**Métricas de modelo** (`COMPARATIVO_MODELOS`, `MAPE_GLOBAL`, `RMSE_GLOBAL`, `MAE_GLOBAL`): valores aleatórios gerados a cada carregamento — não são métricas reais de um modelo treinado.

---

## ⚠️ Resumo dos pontos que são só simulação (checar prioridade de implementação real)

1. Login não valida credenciais.
2. Upload/validação de planilhas (Importar) é 100% simulado (timeout fixo).
3. "Processar dados" (Importar) não faz nada ao clicar.
4. "Marcar como pedido" (Alertas) não persiste.
5. "Editar parâmetros" (Detalhe) não persiste nem recalcula.
6. Filtro de período (Curva ABC) não recalcula os dados.
7. PDF, WhatsApp, "Salvar rascunho", "Confirmar pedidos" (Sugestão de compra) sem ação.
8. "Salvar" em Configurações não persiste.
9. Todas as previsões/gráficos de demanda usam fórmula sintética (seno + ruído), não os modelos reais.
10. Métricas de Holt-Winters/Prophet (Tela 10) são valores aleatórios a cada carregamento.
11. Paginação da tabela de Estoque é só visual.
12. **Única coisa que persiste de fato hoje:** edição manual de estoque (Estoque e Detalhe), salva em `localStorage` do navegador — não é banco de dados real.
