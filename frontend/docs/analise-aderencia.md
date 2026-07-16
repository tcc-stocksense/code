# analise-aderencia.md — Protótipo × Plano de Front-end (StockSense)

> Análise de aderência entre o **protótipo navegável** (React/JSX, referência visual e de comportamento) e os documentos de planejamento `frontend.md` + `tasks.md`. Objetivo: resolver decisões de fundo, fechar lacunas de contrato de API e ajustar tarefas **antes** de iniciar o desenvolvimento com o Claude Code.
>
> Como ler: cada item tem **severidade** (🔴 bloqueante · 🟠 lacuna técnica · 🟡 ajuste menor), o **achado**, a **decisão/ação** necessária e o **dono sugerido**. Itens 🔴 e 🟠 devem ser resolvidos antes da Fase 1 (telas).

---

## 0. Sumário executivo

O plano está sólido: cobre as 10 telas, define fundação antes das telas, contratos de `core/`, componentes e os 4 estados (loading/vazio/erro/sucesso). Os cortes do semáforo (crítico `<3` · atenção `3–7` · ok `>7`) **batem** entre protótipo e plano.

Há **1 decisão de fundo** (stack + cor de marca), **7 lacunas técnicas** (sobretudo contratos de API e o componente `dataTable`) e **8 ajustes menores**. Nada invalida o plano — mas resolver os 🔴/🟠 antes evita retrabalho em 10 telas.

**Checklist de bloqueio (resolver antes da Fase 1):** itens 1, 2, 3, 4, 5, 6, 7, 8, 9.

---

## 1. 🔴 Stack: protótipo é React, plano é vanilla — reescrita, não reuso

- **Achado:** o protótipo é **React + JSX, single-page com roteamento por hash**. O plano é **vanilla JS + MPA + ES Modules + Chart.js**. São arquiteturas diferentes.
- **Implicações:**
  - O código JSX **não é reaproveitável** como base — serve como referência de layout e comportamento.
  - O **CSS migra bem**: portar `styles.css` → `tokens.css` + `base.css` + `components.css` em vez de recriar do zero.
  - Os **gráficos serão refeitos** em Chart.js (hoje são SVG custom).
- **Decisão/ação:** confirmar a stack vanilla como definitiva. Tarefa F2 deve **portar o CSS do protótipo**, não inventar novo.
- **Dono:** Líder técnico (A).

---

## 2. 🔴 Cor de marca divergente

- **Achado:** `tokens.css` do plano usa **azul** `--cor-primaria: #1f4e8c`. O protótipo inteiro usa **verde profundo** (`#163B25`, `#1F4A30`, `#2D6644`).
- **Decisão/ação:** definir a marca real. Se for o verde do protótipo, atualizar `tokens.css` **antes** de qualquer tela. Paleta do protótipo a portar:
  ```css
  --cor-primaria:      #1F4A30;  /* primary-800 */
  --cor-primaria-forte:#163B25;  /* primary-900 */
  --cor-primaria-clara:#2D6644;  /* primary-600 */
  --status-ok:         #2e9e5b;  /* manter — bate com o protótipo */
  --status-atencao:    #e0a91b;
  --status-critico:    #d64545;
  ```
- **Dono:** B (tokens/layout) após decisão do líder.

---

## 3. 🟠 `dataTable` genérico não cobre os casos reais

- **Achado:** o `dataTable({colunas, linhas, filtros, ordenacao})` previsto não atende às telas como elas são no protótipo:
  - **Estoque** usa células customizadas: semáforo, **estoque editável inline**, badge ABC, botão de ação.
  - **Alertas** **não é tabela** — são *cards* (`alert-row`) com layout próprio e 2 botões.
  - **Sugestão de compra** é **agrupada por fornecedor** (seções com subtotal), não tabela plana.
- **Decisão/ação:**
  1. `dataTable` deve aceitar **renderizador de célula por coluna**: `{ chave, titulo, render?: (linha) => Node }`. Sem isso não renderiza badge/edição/ação.
  2. **Alertas** usa **markup dedicado** (cards), não o `dataTable`.
  3. **Sugestão** usa layout **agrupado** próprio, não o `dataTable`.
- **Impacto nas tarefas:** atualizar F7 (capacidade de render por célula) e remover `dataTable` da lista de componentes-chave de S5 (Alertas).
- **Dono:** C (componentes de dados).

---

## 4. 🟠 Estatísticas de reposição: definir que o **backend** calcula

- **Achado:** no protótipo o **front** calcula ponto de reposição, estoque de segurança, média, desvio-padrão (σ), CV e tendência a partir do histórico.
- **Regra (do protótipo, para validar com o backend):**
  - `ponto_reposicao = média_demanda × lead_time + 1,65 × σ × √lead_time`
  - `estoque_seguranca = 1,65 × σ × √lead_time`  (o `1,65` corresponde ao nível de serviço de **95%**)
  - `dias_ate_ruptura = estoque_atual ÷ demanda_média_dia`
- **Decisão/ação:** essas estatísticas **devem vir prontas** de `GET /produtos/{id}/detalhe`. O front só exibe. Confirmar a fórmula (fator 1,65 e o uso de √lead_time) com a equipe de modelagem.
- **Dono:** Backend + D (tela Detalhe).

---

## 5. 🟠 Edição de estoque: quem recalcula `dias_ruptura`?

- **Achado:** ao editar o estoque, mudam `dias_ate_ruptura` e o status (semáforo). No protótipo isso é recalculado no cliente — no sistema real **não deve ser**.
- **Decisão/ação:** definir o retorno do `PATCH /produtos/{id}/estoque`:
  - **Recomendado:** o PATCH **retorna o produto já recalculado** (`{ estoque, dias_ruptura, status }`) e a tela atualiza a linha com a resposta.
  - Alternativa: a tela faz **refetch** do produto/listagem após o PATCH.
- **Dono:** Backend + B (tela Estoque).

---

## 6. 🟠 "Editar parâmetros" (modal do Detalhe) não tem endpoint

- **Achado:** o modal edita **lead time** e **nível de serviço**, mas não há rota para persistir nem para disparar o recálculo do ponto de reposição. (O task S6 já marca "persistência sujeita a endpoint — confirmar".)
- **Decisão/ação:** criar contrato, ex.: `PATCH /produtos/{id}/parametros` com `{ lead_time, nivel_servico }`, retornando as estatísticas recalculadas. Se a persistência ficar para Pós-MVP, o modal deve abrir em modo **somente leitura** no MVP (não prometer salvar).
- **Dono:** Backend + D.

---

## 7. 🟠 Comparativo (T10): endpoint por-id é insuficiente

- **Achado:** o plano lista `GET /produtos/{id}/metricas`, mas a tela mostra **KPIs agregados (MAPE/RMSE/MAE H-W × Prophet) + tabela de TODOS os produtos** com recomendação de modelo.
- **Decisão/ação:** firmar uma **listagem geral de métricas**, ex.:
  - `GET /metricas` → `{ agregado: { mape, rmse, mae por modelo }, porProduto: [...] }`
  - manter `GET /produtos/{id}/metricas` apenas se houver drill-down por produto.
- **Dono:** Backend + responsável por S8.

---

## 8. 🟠 Importação por bloco e quantidade sugerida no backend

- **Achado A — importação:** o protótipo sobe **cada planilha independentemente** (5 blocos: produtos, vendas, estabelecimento, fornecedores, produto×fornecedor). O `POST /importacao` precisa saber **qual tipo** está sendo enviado.
  - **Ação:** definir `POST /importacao` recebendo o **tipo** da planilha (ex.: campo `tipo` no multipart) e retornando contagem de linhas + lista de erros de validação por linha.
- **Achado B — quantidade sugerida:** `qtd_sugerida = demanda_dia × (lead_time + 7)` aparece em **Home, Alertas e Sugestão**. Deve vir do **backend** (consistente nas 3), não recalculada em cada tela.
  - **Ação:** incluir `qtd_sugerida` nos payloads de `/dashboard`, `/alertas` e `/sugestao-compra`.
- **Dono:** Backend + E (Importar/Alertas).

---

## 9. 🟠 Dependência MVP ↔ Pós-MVP: Alertas → Sugestão

- **Achado:** **Alertas (MVP)** tem o botão **"Gerar relatório de compra"** que leva à **Sugestão de compra (Pós-MVP)**. No MVP a tela de destino não existe.
- **Decisão/ação:** no MVP, **ocultar ou desabilitar** o botão "Gerar relatório de compra" em Alertas (com tooltip "em breve"), ou antecipar Sugestão para o MVP. Documentar a escolha em S5.
- **Dono:** E (Alertas).

---

## 10. 🟡 Estados loading / vazio / erro não têm referência visual

- **Achado:** o plano (corretamente) exige os 4 estados em toda tela, mas **o protótipo não os tem** (dados eram síncronos). Só **Alertas** e **Sugestão** têm estado vazio.
- **Decisão/ação:** desenhar **skeleton + empty + erro** como parte da fundação (componentes reutilizáveis), antes de distribuir as telas. Sugerido: um `skeleton.js`/CSS e um `emptyState({titulo, msg, acao})` no catálogo de componentes.
- **Dono:** C/D (fundação de componentes).

---

## 11. 🟡 `format.js` — falta formatação compacta de moeda

- **Achado:** o KPI **"valor em risco"** e os **eixos dos gráficos** usam `fmtBRLcompact` (`R$ 12.480`, sem centavos). O `format.js` do plano só tem `moedaBR/dataBR/numero`.
- **Decisão/ação:** adicionar `moedaBRcompacta(valor)` ao `format.js` **ou** decidir mostrar o valor cheio nesses pontos. Atualizar a tarefa F5.
- **Dono:** E (format).

---

## 12. 🟡 Telas com elementos não previstos no plano

- **Detalhe** (no protótipo, ausentes na spec do plano):
  - tabela **"Vendas por semana"** (4 semanas) — decidir se entra no MVP;
  - **card de Fornecedor** (nome + preço médio) no painel lateral;
  - botão **"Marcar para pedido"**.
- **Configurações:** plano cita abas **Estabelecimento + Notificações**; o protótipo tem **3 abas** (inclui **Usuário**: nome/email + alterar senha). Decidir se a aba Usuário entra.
- **Decisão/ação:** confirmar inclusão/exclusão de cada item e refletir em S6/S10.
- **Dono:** D (Detalhe), responsável por S10 (Config).

---

## 13. 🟡 Gráficos em Chart.js — pontos de atenção

- **Linha** (Dashboard, Detalhe): histórico + projeção. Diferenciar visualmente o trecho projetado (linha tracejada).
- **Pareto** (ABC): é **mixed chart** — barras de faturamento + **linha de % acumulada em eixo Y secundário** + linha de referência em 80%. É o gráfico mais trabalhoso; reservar tempo.
- **Barras agrupadas** (T10): Holt-Winters × Prophet, com alternância de métrica (MAPE/RMSE/MAE).
- **Decisão/ação:** o wrapper `charts.js` (F8) deve expor `linha`, `barras` e `pareto` cobrindo esses casos. Validar o Pareto cedo, com dados de exemplo.
- **Dono:** D (gráficos).

---

## 14. 🟡 Ícones e dados mortos

- **Ícones:** o protótipo usa **SVGs lucide-style inline** (`ui.jsx`). O plano só cita `assets/`. Decidir: portar os SVGs para um `icons.js`/sprite **ou** adotar uma lib de ícones. Padronizar antes das telas.
- **Dados mortos:** `PERDAS_RECENTES` existe no modelo do protótipo mas **nunca é exibido**, e validade/ESG está **fora de escopo**. Não migrar esse dado.
- **Dono:** B (assets/ícones).

---

## 15. ✅ Já está correto — não mexer

- Estrutura de pastas, separação fundação/telas e **regra anti-conflito**.
- Sequência de fases e distribuição entre 5 pessoas.
- Cortes do semáforo (crítico `<3` · atenção `3–7` · ok `>7`).
- Avisos de "o que era mock → vira real" (`frontend.md §8`).
- Filtro de período do **ABC deve recalcular via API** — já capturado corretamente.
- Coeficiente **ABRAS (0,07/4)** do "valor em risco" — já marcado para confirmar com o backend (manter o aviso; só exibir o KPI após confirmação).

---

## 16. Contratos de API a fechar (consolidado para o backend)

> Lista derivada dos itens acima. `backend/CLAUDE.md` continua sendo a fonte da verdade — estes são os pontos a confirmar/criar.

| Endpoint | Precisa retornar / aceitar | Item |
|---|---|---|
| `GET /produtos/{id}/detalhe` | estatísticas **já calculadas**: média, σ, CV, tendência, ponto_reposicao, estoque_seguranca, dias_ruptura, nivel_servico + série 90d/proj 30d | 4 |
| `PATCH /produtos/{id}/estoque` | retornar produto **recalculado** (estoque, dias_ruptura, status) | 5 |
| `PATCH /produtos/{id}/parametros` | **(novo)** `{ lead_time, nivel_servico }` → estatísticas recalculadas | 6 |
| `GET /metricas` | **(novo/listagem)** agregado (MAPE/RMSE/MAE por modelo) + porProduto[] | 7 |
| `POST /importacao` | aceitar **tipo** da planilha; retornar linhas + erros por linha | 8A |
| `GET /dashboard`, `GET /alertas`, `GET /sugestao-compra` | incluir `qtd_sugerida` calculada no backend | 8B |
| `GET /dashboard` | confirmar regra do **valor em risco** (ABRAS) antes de expor | 15 |

---

## 17. Ajustes recomendados nas tarefas (sem reescrever os docs)

- **F2 (tokens/base):** portar o **CSS do protótipo**; corrigir cor primária (verde) — itens 1, 2.
- **F5 (format):** adicionar `moedaBRcompacta` — item 11.
- **F7 (componentes de dados):** `dataTable` com **render de célula por coluna**; remover `dataTable` de Alertas — item 3.
- **F8 (interação/gráficos):** incluir **skeleton + emptyState** no catálogo; validar **Pareto** cedo — itens 10, 13.
- **S5 (Alertas):** layout em **cards** (não dataTable); ocultar/desabilitar "Gerar relatório de compra" no MVP — itens 3, 9.
- **S6 (Detalhe):** confirmar "Vendas por semana", card de fornecedor e "Marcar para pedido"; modal de parâmetros em leitura se sem endpoint — itens 6, 12.
- **S8 (Comparativo):** consumir **listagem geral** de métricas — item 7.
- **S10 (Config):** decidir sobre a **aba Usuário** — item 12.
