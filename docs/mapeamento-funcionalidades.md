# Mapeamento de Funcionalidades — Gestão de Estoque

> **StockSense — Motor de Otimização Preditiva de Estoque · TCC 2026**
> Revisão 2.0 — alinhada às decisões de arquitetura do projeto.

> ⚠️ **Status / fonte de verdade.** Este é o spec detalhado das telas T1–T10. Em caso de conflito, o `CLAUDE.md` da raiz prevalece. As fórmulas e os números do protótipo (Claude Design) **não devem ser copiados**: onde houver aviso "No sistema real", siga o aviso.

## Como ler este documento

Ele registra o que o protótipo (Claude Design) faz — fielmente. Onde o protótipo usa fórmula simplificada, número provisório ou simulação, há um aviso **"No sistema real"** indicando o comportamento correto a implementar. Quem for desenvolver deve seguir o aviso, nunca copiar o mock.

Três correções factuais já foram aplicadas em todo o texto:

- o banco passou a ser **MySQL** (não PostgreSQL);
- o módulo de perdas/ESG foi **removido do escopo**;
- o volume real de produtos deve ser confirmado (**≈312 SKUs**, não 30).

---

## Tela 1 — Login

- **Campos:** email + senha; botão Entrar; "Esqueci minha senha".
- **Consulta equivalente:** autenticação por estabelecimento (`SELECT … WHERE email = ? AND senha_hash = ?`).

**No sistema real:** A tela permanece igual — campos de email e senha são válidos. A decisão de arquitetura mudou apenas onde a credencial mora: o login é **por estabelecimento** (`email` e `senha_hash` na tabela `estabelecimento`), sem tabela de usuário no MVP. Hash com **BCrypt**.

---

## Tela 2 — Home (Dashboard)

**KPIs (4 cartões):**

| KPI | Fórmula no protótipo | Query equivalente |
|---|---|---|
| Risco de faltar (7 dias) | conta produtos com `diasRuptura ≤ 7` | `COUNT WHERE dias_ruptura <= 7` |
| Crítico agora | conta `diasRuptura < 3` | `COUNT WHERE dias_ruptura < 3` |
| Valor em risco | `Σ faturamento × 0,07 / 4` (coef. ABRAS) | soma de faturamento dos itens em risco |
| Acurácia do modelo | `100 − MAPE_prophet` | `SELECT mape … ORDER BY data DESC` |

**No sistema real:** Três ajustes neste dashboard.

1. **"Valor em risco"** — o coeficiente ABRAS (`0,07/4`) é número provisório e precisa de fonte; conceitualmente deveria ser a perda esperada dos produtos que vão romper (`demanda × preço × dias de ruptura`), não uma fração do faturamento total.
2. **"Acurácia do modelo"** deve usar o MAPE do **modelo selecionado** por produto (pode ser Holt-Winters), não fixo no Prophet.
3. A sugestão de pedido da tabela "próximos alertas" usa `demandaDiaria × (leadTime + 7)`; o "+7" é arbitrário — a sugestão deve derivar do **ponto de reposição** e do **estoque de segurança** calculados pelo motor.

- **Banner de alerta:** "7 produtos precisam ser pedidos hoje / 3 críticos" → botão "Ver lista".
- **Gráfico:** linha de Previsão de faturamento — 8 semanas históricas + 4 projetadas.
- **Tabela "Próximos alertas":** top 5 produtos por urgência, com dias até ruptura e sugestão de pedido.

---

## Tela 3 — Importar dados

- **5 blocos de planilha independentes:** Produtos e Vendas (obrigatórias); Estabelecimento, Fornecedores, Produto×Fornecedor (desejáveis).
- **Cada bloco:** upload, validação, estados sucesso / erro / vazio / processando, contagem de linhas, substituir/remover.
- **Botão Processar dados:** habilita só quando as obrigatórias estão OK.
- **Operação equivalente:** ingestão/ETL — parsing de XLSX, validação de schema, inserção nas tabelas do banco.

**No sistema real:** No protótipo, upload e validação são simulados (timeout fixo, erro fixo na linha 45). No real, a importação é **`POST /api/importacao`** (multipart, Apache POI), com validação pelo Guia de Importação v2.0 e persistência no MySQL; ao concluir com sucesso, dispara o recálculo do motor. O formato aceito é `.xlsx`.

---

## Tela 4 — Estoque

- **Tabela de produtos:** Status (semáforo), Produto, Categoria, Estoque (editável), Até ruptura, Classe ABC, Detalhe.
- **Filtros:** busca por nome, categoria, status (crítico/atenção/ok), classe (A/B/C). Ordenado por urgência.

**No sistema real:** A edição de estoque, que no protótipo persiste em `localStorage`, no real é **`PATCH /api/produtos/{id}/estoque`**. A paginação "sempre Página 1 de 1" deve ser real ou removida (com ~312 SKUs, filtro/ordenação no cliente comporta sem paginação). E o semáforo **não deve usar 3/7 dias fixos**: o limiar correto é relativo ao **ponto de reposição** — 🔴 `estoque_atual ≤ ponto_reposicao`; 🟡 até `ponto_reposicao × 1,5`; 🟢 acima. Isso usa o lead time por produto que o motor calcula.

---

## Tela 5 — Alertas de reposição

- **Lista:** produtos por urgência; separa "próximos 3 dias".
- **Por item:** estoque atual, "vai faltar em X dias", lead time, quantidade sugerida, fornecedor.
- **Ações:** "Marcar como pedido", ir ao detalhe, "Gerar relatório de compra".

**No sistema real:** A urgência e a quantidade sugerida devem nascer do motor (ponto de reposição e estoque de segurança), não de cortes fixos de dias nem de buffer arbitrário. Mesma correção do "+7" citada na Tela 2.

---

## Tela 6 — Detalhe do produto

**KPIs:**

- Demanda média/dia; Variabilidade (desvio-padrão + CV); Tendência (média dos primeiros 14 vs últimos 14 dias).

**Painel de reposição (no protótipo):**

- Ponto de reposição = `média × leadTime + 1,65 × σ × √leadTime`
- Estoque de segurança = `1,65 × σ × √leadTime`
- Nível de serviço 95%.

**No sistema real:** O painel mostra a fórmula simplificada. O motor (ml-service) usa a **fórmula de Ballou completa**, com variabilidade de lead time e `Z = norm.ppf(nível_serviço)` — não fixo em 1,65:

```
ES = Z · √(LT · σ²_demanda + demanda² · σ²_leadtime)
```

A tela deve exibir os valores que o motor devolve. Atenção: o modal "Editar parâmetros" (lead time, nível de serviço) precisa, no real, **persistir e fazer o cálculo reagir** ao novo nível — com 1,65 cravado, mudar o nível não teria efeito.

**Contrato resolvido (2026-07-10):** o ml-service devolve `desvio_padrao_demanda` no `PredictResponse`; o backend grava em `produto.desvioPadraoDemanda` a cada execução do motor. A tela pode consumir o campo diretamente.

---

## Tela 7 — Curva ABC

- Gráfico de Pareto dos top 30 produtos por faturamento (linha de 80%).
- 3 cartões A/B/C: nº de produtos e % do faturamento por classe.
- Tabela completa: classe, faturamento, % do total, % acumulada.

**No sistema real:** O filtro de período, que no protótipo é visual e não recalcula, deve **refazer a chamada à API** com o período selecionado. E a classificação ABC é calculada no **backend** (`AbcService`), que tem o catálogo inteiro e o `valor_venda` — não no ml-service, que opera por produto.

---

## Tela 8 — Sugestão de compra

- Produtos a repor agrupados por fornecedor; quantidade editável, preço unitário, subtotal, total geral.
- **Ações:** exportar PDF, enviar WhatsApp (visuais), salvar rascunho, confirmar pedidos.

**Prioridade: Pós-MVP.** Tela completa fica para versão posterior; a quantidade sugerida segue a mesma origem (motor) das telas 2 e 5.

---

## Tela 9 — Configurações

- **Abas:** Estabelecimento (nome, CNPJ, endereço), Usuário (nome, email, alterar senha), Notificações.

**No sistema real:** O salvamento, simulado no protótipo, deve persistir de verdade. Recomenda-se enxugar esta tela no MVP (nome do mercado + logout) e deixar notificações como evolução — login e configurações não são o foco do TCC.

**Prioridade: Pós-MVP.**

---

## Tela 10 — Comparativo de modelos (técnica)

- **KPIs agregados:** MAPE, RMSE, MAE — Holt-Winters vs Prophet.
- **Gráfico:** barras agrupadas por produto (alterna métrica).
- **Detalhe:** tabela por produto com recomendação de modelo.
- **Log de execuções:** retraining e persistência das métricas.

**No sistema real:** As métricas, fixas/aleatórias no protótipo, vêm do motor real. A persistência é em **MySQL** — tabela `metrica_modelo` (duas linhas por execução, uma por modelo, com a flag "selecionado") — e não em PostgreSQL como dizia a versão anterior. **Esta é a tela-núcleo do TCC:** é onde o diferencial preditivo é demonstrado empiricamente.

---

## Modelo de dados (campos por produto)

`id, nome, categoria, estoque, unidade, diasRuptura, classe (A/B/C), precoMedio, demandaDiaria, leadTime, fornecedor, faturamento.`

**Entidades relacionadas:** Fornecedores (contato, lead time), Estabelecimento (com credencial de login), Métricas de modelo (MAPE/RMSE/MAE por modelo e execução), Previsões.

**No sistema real:** Removido o bloco "Perdas recentes (data, motivo, valor)". O módulo de perdas/validade (ESG) saiu do escopo do projeto — sem tabela `perda_estoque`, sem KPI de desperdício e sem a planilha de perdas na importação.

---

## Divergências protótipo → sistema real (resumo)

Tabela-guia para quem for implementar. Onde o mock deve ser substituído pelo comportamento real:

| Tela | No protótipo | No sistema real |
|---|---|---|
| T2 Dashboard | Acurácia = `100 − MAPE_prophet` | MAPE do modelo selecionado por produto |
| T2 Dashboard | Valor em risco = `Σfat × 0,07/4` (ABRAS) | Perda esperada dos itens em risco — regra a confirmar |
| T2/T5 | Sugestão = `demanda × (leadTime + 7)` | Derivada do ponto de reposição e estoque de segurança |
| T4/T5 | Semáforo fixo 3 / 7 dias | Relativo ao ponto de reposição (lead time por produto) |
| T4 | Estoque em `localStorage` | `PATCH /api/produtos/{id}/estoque` (MySQL) |
| T6 | ES = `1,65·σ·√leadTime` | Ballou completa, `Z = norm.ppf(nível)`, com σ de lead time |
| T6 | Modal de parâmetros não persiste | Persiste e recalcula ao mudar o nível de serviço |
| T7/T10 | Filtro de período não recalcula | Refaz a chamada à API com o período |
| T10 | Métricas fixas; persistência PostgreSQL | Métricas reais do motor; persistência MySQL (`metrica_modelo`) |
| Geral | Previsão = seno + ruído | Holt-Winters / Prophet via ml-service |
| Geral | Nada persiste (mock) | Tudo persiste via backend (MySQL) |

---

## Premissas para o sistema real

Requisitos do sistema final (reescritura dos antigos "pontos críticos" do protótipo):

- Toda informação persiste no banco (MySQL), via backend; o frontend **nunca** chama o ml-service diretamente.
- A previsão é gerada pelos modelos reais (Holt-Winters e Prophet) e a acurácia mostrada é a do **modelo selecionado**.
- Filtros de período (ABC e técnica) recalculam consultando a API.
- Confirmar o volume real de produtos (**≈312 SKUs**) para dimensionar testes e paginação.
- Definir e documentar a regra do KPI "valor em risco" — substituir o coeficiente provisório.
- `diasRuptura` sai de `estoque_atual ÷ demanda média diária prevista`, não de valor fixo.
- Tratar o estado "histórico insuficiente (< 90 dias)": o motor não prevê e a tela deve sinalizar, em vez de assumir que todo produto tem previsão.
- Sinalizar visualmente previsões de baixa confiança (campo `aviso` quando `MAPE > 50%`).
