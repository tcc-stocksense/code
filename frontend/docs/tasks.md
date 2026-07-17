# tasks.md — Front-end StockSense

> Backlog de execução do front-end. Cada tarefa é **autocontida**: pode ser dada a uma IA (Claude Code) ou a uma pessoa e executada isoladamente. Leia `frontend.md` antes de qualquer tarefa — ele define a estrutura, os contratos de `core/` e os componentes.
>
> ⚠️ **Contrato de API: a fonte da verdade é [`docs/contrato-api-frontend.md`](../../docs/contrato-api-frontend.md)** (raiz do monorepo), validado contra o backend real — **não** o `backend/CLAUDE.md` (desatualizado em pontos como a importação). Algumas rotas citadas nas tarefas abaixo divergem do contrato real (importação em 2 endpoints, sem `?periodo=` no ABC, métricas por produto etc.) — a reconciliação está em **[`tasks-integracao.md`](tasks-integracao.md)**, que prevalece sobre a seção "API consumida" destas tarefas.

## Como usar este arquivo
- Tarefas têm **dependências**. Não comece uma tarefa sem que suas dependências estejam concluídas.
- A **Fase 0 (Fundação)** deve ser feita primeiro e por uma só pessoa — todas as telas dependem dela.
- As tarefas de tela (Fase 1) são **paralelizáveis** entre os colegas.
- Cada tarefa só termina quando **todos os itens do "Critério de pronto"** passam.

## Formato de cada tarefa
**ID · Título** — Prioridade · Depende de
- **Objetivo:** o que entregar.
- **Arquivos:** o que criar/editar.
- **API consumida:** método, rota e forma resumida (detalhe em `backend/CLAUDE.md`).
- **Estados:** loading / vazio / erro / sucesso quando aplicável.
- **Critério de pronto:** checklist objetivo.

## Regra anti-conflito
Arquivos em `js/core/` e `js/components/` só são editados nas tarefas de Fundação. Tarefas de tela **apenas importam** desses módulos. Se faltar algo na fundação, abra uma tarefa nova (ex.: `F9`) para o dono da fundação, não edite direto.

---

# FASE 0 — Fundação (1 pessoa, antes de tudo)

### F1 · Scaffold do projeto — **MVP** · Depende de: —
- **Objetivo:** criar a estrutura de pastas de `frontend.md §2`, `index.html` (redireciona para `dashboard.html`, ou `login.html` se sem sessão) e o `README` de como rodar (`python3 -m http.server 5500`).
- **Arquivos:** `web/index.html`, árvore de pastas vazia, `web/README.md`.
- **Critério de pronto:** servir `web/` e o navegador abrir sem erro de console; `index.html` redireciona corretamente.

### F2 · Tokens e CSS base — **MVP** · Depende de: F1
- **Objetivo:** `tokens.css` (cores, semáforo, espaçamento de `frontend.md §5`), `base.css` (reset, tipografia, shell de layout responsivo).
- **Arquivos:** `css/tokens.css`, `css/base.css`.
- **Critério de pronto:** variáveis aplicáveis; uma página de teste mostra cores do semáforo e tipografia consistentes.

### F3 · `config.js` + `apiClient.js` — **MVP** · Depende de: F1
- **Objetivo:** wrapper de fetch com `Authorization` automático e conversão de erro RFC 7807 em `Error` com `.status` e `.detail`. Funções `apiGet/apiPost/apiPatch/apiUpload`.
- **Arquivos:** `js/core/config.js`, `js/core/apiClient.js`.
- **API consumida:** nenhuma diretamente (infra).
- **Critério de pronto:** chamada a um endpoint real retorna JSON; erro 4xx/5xx vira `Error` legível; `apiUpload` envia `multipart/form-data`.

### F4 · `auth.js` (login + guard) — **MVP** · Depende de: F3
- **Objetivo:** `login(email, senha)` → `POST /auth/login`, guarda token em `sessionStorage`; `requireAuth()` redireciona p/ `login.html` se sem sessão; `logout()`.
- **Arquivos:** `js/core/auth.js`.
- **API consumida:** `POST /api/auth/login` → `{ token }`.
- **Critério de pronto:** sem token, `requireAuth()` redireciona; com token, segue; `logout()` limpa e volta ao login.

### F5 · `format.js` — **MVP** · Depende de: F1
- **Objetivo:** `moedaBR`, `dataBR`, `numero` no padrão brasileiro.
- **Arquivos:** `js/core/format.js`.
- **Critério de pronto:** `moedaBR(1890)→"R$ 1.890,00"`; `dataBR("2025-03-15")→"15/03/2025"`.

### F6 · `layout.js` (sidebar + header) — **MVP** · Depende de: F2
- **Objetivo:** `renderLayout(telaAtiva)` injeta navegação lateral (links para todas as telas MVP) e header com nome do estabelecimento e `logout`. Marca a tela ativa.
- **Arquivos:** `js/components/layout.js`, estilos em `css/components.css`.
- **Critério de pronto:** injetado em `#app`, navega entre telas, destaca a ativa, botão de logout funciona.

### F7 · Componentes de dados — **MVP** · Depende de: F2
- **Objetivo:** `statusBadge(diasRuptura)` (semáforo), `kpiCard({titulo,valor,sub})`, `dataTable({colunas,linhas,filtros,ordenacao})` com busca/ordenação/filtro client-side.
- **Arquivos:** `js/components/statusBadge.js`, `kpiCard.js`, `dataTable.js`, estilos em `css/components.css`.
- **Critério de pronto:** demo renderiza badge nos 3 estados, um card e uma tabela filtrável/ordenável.

### F8 · Componentes de interação e gráficos — **MVP** · Depende de: F2
- **Objetivo:** `modal.js`, `toast.js` (sucesso/erro), `uploadBlock.js` (estados vazio/processando/sucesso/erro + contagem de linhas), `charts.js` (wrappers Chart.js via CDN: `linha`, `barras`, `pareto`).
- **Arquivos:** `js/components/modal.js`, `toast.js`, `uploadBlock.js`, `charts.js`.
- **Critério de pronto:** modal abre/fecha; toasts aparecem e somem; uploadBlock transita pelos 4 estados; os 3 gráficos renderizam com dados de exemplo.

---

# FASE 1 — Telas MVP (paralelizáveis entre colegas)

### S1 · Tela Login — **MVP** · Depende de: F3, F4
- **Objetivo:** formulário email+senha, "esqueci a senha" (placeholder), erro de credencial via toast. Sem layout (sem sidebar).
- **Arquivos:** `pages/login.html`, `js/pages/login.page.js`, `css/pages/login.css`.
- **API consumida:** `POST /api/auth/login`.
- **Estados:** loading no submit; erro (credencial inválida) via toast.
- **Critério de pronto:** login válido guarda token e vai ao dashboard; inválido mostra erro; já logado pula direto ao dashboard.

### S2 · Tela Dashboard — **MVP** · Depende de: F4, F6, F7, F8
- **Objetivo:** 4 KPIs (risco 7d, crítico agora, valor em risco, acurácia), gráfico de linha (faturamento histórico + projeção), tabela "próximos alertas" (top 5), banner com link p/ Alertas.
- **Arquivos:** `pages/dashboard.html`, `js/pages/dashboard.page.js`, `css/pages/dashboard.css`.
- **API consumida:** `GET /api/dashboard`.
- **Estados:** loading; vazio ("importe dados para ver o dashboard"); erro.
- **Critério de pronto:** KPIs e gráfico vêm da API; banner aparece só quando há produtos em risco; "valor em risco" só exibe após confirmar a regra ABRAS com o backend.

### S3 · Tela Importar — **MVP** · Depende de: F4, F6, F8
- **Objetivo:** 5 blocos de planilha (Produtos e Vendas obrigatórios; demais desejáveis), cada um com upload, contagem de linhas e estados; botão "Processar" habilita só com obrigatórias OK; ao processar, chamar recálculo.
- **Arquivos:** `pages/importar.html`, `js/pages/importar.page.js`, `css/pages/importar.css`.
- **API consumida:** `POST /api/importacao` (multipart) → depois `POST /api/motor/recalcular`.
- **Estados:** por bloco — vazio/processando/sucesso/erro com lista de erros de validação.
- **Critério de pronto:** envio real persiste; erros de validação aparecem por bloco; recálculo dispara após sucesso; "Processar" respeita a regra de obrigatórias.

### S4 · Tela Estoque — **MVP** · Depende de: F4, F6, F7
- **Objetivo:** tabela de produtos com semáforo, estoque **editável inline**, filtros (nome, categoria, status, classe), ordenação por urgência.
- **Arquivos:** `pages/estoque.html`, `js/pages/estoque.page.js`, `css/pages/estoque.css`.
- **API consumida:** `GET /api/produtos`; `PATCH /api/produtos/{id}/estoque`.
- **Estados:** loading; vazio; erro; sucesso de edição via toast.
- **Critério de pronto:** edição persiste via PATCH e atualiza a linha; filtros e ordenação funcionam; link para o detalhe do produto.

### S5 · Tela Alertas — **MVP** · Depende de: F4, F6, F7
- **Objetivo:** produtos com `dias_ruptura <= 7` por urgência, separando "próximos 3 dias"; por item: estoque, "falta em X dias", lead time, quantidade sugerida, fornecedor; ação "marcar como pedido".
- **Arquivos:** `pages/alertas.html`, `js/pages/alertas.page.js`, `css/pages/alertas.css`.
- **API consumida:** `GET /api/alertas`.
- **Estados:** loading; vazio ("nenhum produto em risco"); erro.
- **Critério de pronto:** lista ordenada por urgência; separação dos 3 dias; "marcar como pedido" reflete estado (local no MVP); link p/ detalhe.

### S6 · Tela Detalhe do produto — **MVP** · Depende de: F4, F6, F7, F8
- **Objetivo:** KPIs (demanda média, variabilidade σ+CV, tendência), painel de reposição (ponto de reposição, estoque de segurança, dias até ruptura, nível de serviço), gráfico 90d + projeção 30d, modal "editar parâmetros".
- **Arquivos:** `pages/produto-detalhe.html`, `js/pages/produto-detalhe.page.js`, `css/pages/produto-detalhe.css`.
- **API consumida:** `GET /api/produtos/{id}/detalhe`.
- **Estados:** loading; erro; produto inexistente (404).
- **Critério de pronto:** todos os campos vêm da API; gráfico renderiza histórico+projeção; modal de parâmetros abre (persistência sujeita a endpoint — confirmar).

### S7 · Tela Curva ABC — **MVP** · Depende de: F4, F6, F7, F8
- **Objetivo:** Pareto top-30 com linha de 80%, 3 cartões A/B/C, tabela com % acumulada, filtro de período que **recalcula via API**.
- **Arquivos:** `pages/curva-abc.html`, `js/pages/curva-abc.page.js`, `css/pages/curva-abc.css`.
- **API consumida:** `GET /api/curva-abc?periodo=...`.
- **Estados:** loading; vazio; erro.
- **Critério de pronto:** Pareto e cartões corretos; trocar o período **refaz a chamada** (não filtra só na tela).

### S8 · Tela Comparativo de modelos (T10) — **MVP** · Depende de: F4, F6, F7, F8
- **Objetivo:** MAPE/RMSE/MAE Holt-Winters × Prophet, barras agrupadas (alterna métrica), tabela por produto com recomendação de modelo. **Núcleo acadêmico.**
- **Arquivos:** `pages/comparativo-modelos.html`, `js/pages/comparativo-modelos.page.js`, `css/pages/comparativo-modelos.css`.
- **API consumida:** `GET /api/produtos/{id}/metricas` (e/ou listagem geral de métricas).
- **Estados:** loading; vazio ("rode o motor para gerar métricas"); erro.
- **Critério de pronto:** comparativo dos dois modelos com dados reais; alternância de métrica; recomendação destacada.

---

# FASE 1.5 — Motor assíncrono (evolução do recálculo)

> **Por quê.** O recálculo do motor (disparado ao importar e por um botão manual) processa
> **todos os produtos no backend**; com volume alto de SKUs isso leva **minutos**. Se o front
> chamar `POST /api/motor/recalcular` e **esperar a resposta síncrona**, o navegador estoura o
> timeout muito antes de terminar. A decisão de arquitetura (ver `docs/relatorio-motor-assincrono.md`)
> é: o backend responde **`202` na hora** e o front **acompanha por polling** de um endpoint de
> status. Rastreabilidade com o backend: `backend/tasks.md` Épico 7 (`T-41`, `T-42`, `T-44`, `T-47`–`T-51`).
>
> 🔒 **STATUS: SUSPENSO (validação do orientador, 2026-07-12).** Não iniciar a implementação
> destas tarefas até o backend liberar o Épico 7 — que por sua vez aguarda a **confirmação do
> volume de SKUs** pelo parceiro (ver `backend/tasks.md` Épico 7 e `docs/relatorio-motor-assincrono.md`).
> Boa notícia: o **contrato de `GET /api/motor/status` foi CONGELADO** na validação, então
> `motorStatus.js` (F9) já pode ser escrito contra um formato estável assim que o épico for liberado.
>
> ⚠️ **Depende do backend.** Estas tarefas só podem ser concluídas depois que `T-41`
> (recalcular async → 202), `T-42` (`GET /api/motor/status`, contrato congelado), `T-44` (disparo
> na importação) e `T-52` (guard de concorrência → `409`) estiverem prontos.
>
> ⚠️ **Regra anti-conflito.** `F9` é **tarefa de Fundação** — cria módulo em `core/` e
> componente em `components/`; só o dono da fundação edita esses arquivos. `S3+` e `S6+` são
> ajustes de tela e **apenas importam** de `F9`.

### F9 · Núcleo de acompanhamento do motor (`motorStatus.js` + UI de progresso) — **MVP** · Depende de: F3, F8
- **Objetivo:** módulo de fundação que **dispara** o recálculo, recebe o `202`, faz o **polling**
  de `GET /api/motor/status` a cada ~3 s e reporta progresso/conclusão/erro via callbacks; mais
  um componente visual de progresso (banner/barra com "N de M"). Substitui qualquer espera
  síncrona pelo recálculo. Cobre `T-47` (disparo + estado processando), `T-48` (polling) e
  `T-51` (erros/falha parcial) do backend.
- **Arquivos:** `js/core/motorStatus.js`, `js/components/progressoMotor.js`, estilos em `css/components.css`.
- **API consumida:** `POST /api/motor/recalcular` → `202 { statusUrl }`; `GET /api/motor/status`
  → `{ estado: "PENDENTE|PROCESSANDO|CONCLUIDO|FALHOU", feitos, total, produtosComFalha?, executadoEm? }`.
- **Contrato do módulo (estável — telas dependem):**
  ```js
  // dispara o recálculo e acompanha até terminar; retorna o resumo final.
  export async function recalcularMotor({ onProgresso, onConcluido, onErro }) // -> Promise<resumo>
  export function acompanharStatus({ onProgresso, onConcluido, onErro })      // só polling (sem disparar)
  ```
- **Estados:** processando (barra + "N de M"); concluído (resumo: "N processados, X falhas");
  `409 Conflict` (já há recálculo em andamento) → apenas acompanha o job existente; `FALHOU` /
  timeout do polling → `toast.erro` + opção de tentar de novo. Teto de tentativas para não pollar
  infinito se o backend cair.
- **Critério de pronto:** disparar recálculo mostra progresso; ao concluir, `onConcluido` recebe
  o resumo; falha e `409` tratados; nenhum `fetch` fora do `apiClient`; loop de polling encerra
  em `CONCLUIDO`/`FALHOU` e no teto de tentativas.

### S3+ · Ajustar Tela Importar ao fluxo assíncrono — **MVP** · Depende de: F9, S3
- **Objetivo:** trocar a antiga sequência síncrona (`POST /importacao` → `POST /motor/recalcular`
  e **esperar**) pelo fluxo assíncrono: no sucesso do **"Processar dados"**, disparar via
  `motorStatus.recalcularMotor`, exibir o progresso e, ao concluir, **recarregar os dados** (ou
  orientar a navegar ao Dashboard já atualizado). Cobre `T-49` (recarregar ao concluir).
- ⚠️ **Disparo único (alinhado à T-44):** o recálculo é disparado **uma só vez**, no clique de
  "Processar dados" (com as obrigatórias OK) — **nunca** por bloco/planilha individual, ainda que
  Produtos e Vendas sejam enviados em uploads separados. Se o backend responder `409` (já há
  recálculo em andamento), apenas **acompanhar** o job existente em vez de disparar outro.
- **Arquivos:** `js/pages/importar.page.js`, `css/pages/importar.css` (sem tocar em `core/`/`components/`).
- **API consumida:** `POST /api/importacao/*` (multipart); recálculo via `F9` (não chamar
  `/motor/recalcular` direto).
- **Estados:** importando (por bloco, já existente) → recalculando (progresso do motor) →
  concluído (resumo + CTA "ver dashboard"); erro em qualquer etapa via toast.
- **Critério de pronto:** importação real dispara o recálculo assíncrono; a tela mostra o
  progresso sem travar; ao concluir, os dados refletem o novo cálculo (recarga/redirecionamento);
  o botão "Processar" não fica preso esperando minutos.

### S6+ · Botão "recalcular este produto" na Tela Detalhe (síncrono) — **MVP-opcional** · Depende de: S6
- **Objetivo:** ação para recalcular **um único produto** (rápido — sem polling, é síncrono),
  útil após reimportar vendas de um item. Ao concluir, atualiza os KPIs do produto na tela.
  Cobre `T-50`.
- **Arquivos:** `js/pages/produto-detalhe.page.js`, `css/pages/produto-detalhe.css`.
- **API consumida:** `POST /api/produtos/{id}/recalcular` (ou `POST /api/motor/recalcular/{id}` —
  confirmar a rota final com o backend, `T-43`).
- **Estados:** loading local no botão (spinner); sucesso → KPIs atualizados + toast; erro → toast.
- **Critério de pronto:** o botão dispara o recálculo do produto, aguarda a resposta (rápida, sem
  polling) e re-renderiza os KPIs; erro tratado; não afeta as demais telas.

---

# FASE 2 — Pós-MVP

### S9 · Tela Sugestão de compra — **Pós-MVP** · Depende de: F4, F6, F7
- **Objetivo:** produtos `dias_ruptura <= 10` agrupados por fornecedor; quantidade editável; subtotais e total; exportar PDF / WhatsApp (visuais); confirmar pedidos.
- **API consumida:** `GET/POST /api/sugestao-compra`.
- **Critério de pronto:** agrupamento e totais corretos; rascunho/confirmação persistem.

### S10 · Tela Configurações — **Pós-MVP** · Depende de: F4, F6
- **Objetivo:** abas Estabelecimento (nome/CNPJ/endereço) e Notificações; alterar senha.
- **API consumida:** `PUT /api/configuracoes/*`.
- **Critério de pronto:** salvar persiste de verdade (não simulado como no protótipo).

---

# Sugestão de distribuição (5 colegas)

| Pessoa | Fase 0 | Fase 1 |
|---|---|---|
| **A (líder técnico)** | F1, F3, F4 (fundação crítica) | S1 Login |
| **B** | F2, F6 (layout/tokens) | S4 Estoque |
| **C** | F7 (componentes de dados) | S2 Dashboard |
| **D** | F8 (interação/gráficos) | S6 Detalhe + S7 ABC |
| **E** | F5 (format) | S3 Importar + S5 Alertas |
| (rodízio) | — | S8 Comparativo (quem terminar antes) |

> A Fase 0 é o gargalo: enquanto a fundação não fecha, ninguém avança nas telas. Vale concentrar A/B/C/D nela nos primeiros dias e só então abrir as telas em paralelo. S8 (T10) é o capricho acadêmico — dar a quem tiver mais fôlego.

# Definition of Done (global)
- Sem erros no console.
- Os 4 estados (loading/vazio/erro/sucesso) tratados quando há dados.
- Nenhum `fetch` fora do `apiClient`; nenhuma URL hardcodada fora do `config.js`.
- `requireAuth()` no topo de toda página protegida.
- Responsivo o suficiente para uso em tela de balcão/desktop.
- Datas e moeda via `format.js`.
