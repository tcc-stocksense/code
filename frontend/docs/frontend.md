# frontend.md — StockSense Web App

> Front-end do StockSense. Stack: **HTML / CSS / JavaScript puro (vanilla)**, sem framework e sem build tooling. Multi-página (MPA), ES Modules nativos, Chart.js via CDN. Consome a API do backend (Spring Boot) — ver `backend/CLAUDE.md` para o contrato dos endpoints (fonte da verdade).

---

## 1. Decisão de stack e princípios

- **Vanilla HTML/CSS/JS**, conforme o C4. Sem React/Vue, sem webpack/vite.
- **MPA (multi-página):** cada tela é um `.html` independente. Não há roteador client-side. Isso isola o trabalho — cada colega é dono dos arquivos da sua tela.
- **ES Modules nativos:** `import`/`export` direto no navegador via `<script type="module">`. Nada de bundler.
- **Fundação compartilhada primeiro:** `core/` (apiClient, auth, config) e `components/` são construídos **antes** das telas e não devem ser editados por quem faz tela (só consumidos).
- **Estado:** sem store global. Token de sessão no `sessionStorage`; cada página busca seus dados na API ao carregar.
- **Regra de ouro contra conflito:** ninguém edita arquivo de `core/` ou `components/` durante o desenvolvimento de uma tela. Se precisar de algo novo lá, abre tarefa para o dono da fundação.

---

## 2. Estrutura de diretórios

```
web/
├── index.html                      ← redireciona p/ dashboard (ou login se sem sessão)
│
├── pages/                          ← uma tela = um HTML (cada colega é dono do seu)
│   ├── login.html
│   ├── dashboard.html
│   ├── importar.html
│   ├── estoque.html
│   ├── alertas.html
│   ├── produto-detalhe.html
│   ├── curva-abc.html
│   ├── comparativo-modelos.html
│   ├── sugestao-compra.html        (Pós-MVP)
│   └── configuracoes.html          (Pós-MVP)
│
├── js/
│   ├── core/                       ← FUNDAÇÃO — só o dono da fundação edita
│   │   ├── config.js               ← API_BASE_URL e constantes
│   │   ├── apiClient.js            ← wrapper de fetch (auth header, parse RFC 7807)
│   │   ├── auth.js                 ← login, token, requireAuth(), logout()
│   │   └── format.js               ← datas, números e moeda no padrão BR
│   │
│   ├── components/                 ← FUNDAÇÃO — helpers reutilizáveis de UI
│   │   ├── layout.js               ← renderiza sidebar + header em cada página
│   │   ├── statusBadge.js          ← semáforo 🟢 🟡 🔴
│   │   ├── kpiCard.js              ← cartão de KPI
│   │   ├── dataTable.js            ← tabela com busca/ordenação/filtros
│   │   ├── uploadBlock.js          ← bloco de planilha (estados: vazio/processando/ok/erro)
│   │   ├── modal.js
│   │   ├── toast.js                ← notificações de sucesso/erro
│   │   └── charts.js               ← wrappers Chart.js (linha, barras, pareto)
│   │
│   └── pages/                      ← controlador de cada tela (do colega dono da tela)
│       ├── login.page.js
│       ├── dashboard.page.js
│       ├── importar.page.js
│       ├── estoque.page.js
│       ├── alertas.page.js
│       ├── produto-detalhe.page.js
│       ├── curva-abc.page.js
│       ├── comparativo-modelos.page.js
│       ├── sugestao-compra.page.js     (Pós-MVP)
│       └── configuracoes.page.js       (Pós-MVP)
│
├── css/
│   ├── tokens.css                  ← variáveis CSS (cores, espaçamento, semáforo)
│   ├── base.css                    ← reset, tipografia, shell de layout
│   ├── components.css              ← estilos dos componentes compartilhados
│   └── pages/                      ← CSS específico por tela (se necessário)
│       └── *.css
│
└── assets/                         ← logo, ícones
```

**Esqueleto de cada página** (`pages/estoque.html`):
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="../css/tokens.css">
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/components.css">
  <link rel="stylesheet" href="../css/pages/estoque.css">
</head>
<body>
  <div id="app"><!-- layout.js injeta sidebar+header; o resto é da página --></div>
  <script type="module" src="../js/pages/estoque.page.js"></script>
</body>
</html>
```

---

## 3. Módulos compartilhados — contrato (`core/`)

Estas assinaturas são **estáveis**. As telas dependem delas; mudá-las quebra todo mundo.

### `config.js`
```js
export const API_BASE_URL = "http://localhost:8080/api"; // ajustar por ambiente
```

### `apiClient.js`
```js
// Faz fetch com Authorization automático e converte erro RFC 7807 em Error legível.
export async function apiGet(path)            // -> Promise<json>
export async function apiPost(path, body)     // -> Promise<json>
export async function apiPatch(path, body)    // -> Promise<json>
export async function apiUpload(path, formData) // multipart (importação) -> Promise<json>
// Em erro: lança Error com .status e .detail (do ProblemDetail). A página trata e exibe toast.
```

### `auth.js`
```js
export async function login(email, senha)  // chama POST /auth/login, guarda token
export function requireAuth()              // redireciona p/ login.html se sem sessão — chamar no topo de toda page.js protegida
export function logout()                   // limpa sessão e volta ao login
export function getToken()
```

### `format.js`
```js
export function moedaBR(valor)   // 1890 -> "R$ 1.890,00"
export function dataBR(iso)      // "2025-03-15" -> "15/03/2025"
export function numero(v, casas) // formatação numérica BR
```

---

## 4. Catálogo de componentes (`components/`)

Cada componente é uma função que recebe dados e retorna um nó DOM (ou o injeta num container). Sem framework, sem estado interno escondido.

| Componente | Função | Usado em |
|---|---|---|
| `layout.js` | `renderLayout(telaAtiva)` — sidebar + header | todas (exceto login) |
| `statusBadge.js` | `statusBadge(diasRuptura)` → 🟢/🟡/🔴 | Estoque, Alertas, Dashboard |
| `kpiCard.js` | `kpiCard({titulo, valor, sub})` | Dashboard, Detalhe, ABC |
| `dataTable.js` | `dataTable({colunas, linhas, filtros, ordenacao})` | Estoque, ABC, Alertas, T10 |
| `uploadBlock.js` | bloco de planilha com estados vazio/processando/sucesso/erro + contagem de linhas | Importar |
| `modal.js` | `openModal({titulo, conteudo, onConfirm})` | Detalhe (editar parâmetros) |
| `toast.js` | `toast.sucesso(msg)` / `toast.erro(msg)` | todas |
| `charts.js` | `linha(ctx, dados)`, `barras(ctx, dados)`, `pareto(ctx, dados)` | Dashboard, Detalhe, ABC, T10 |

---

## 5. Design tokens (`tokens.css`)

```css
:root {
  /* cores base */
  --cor-primaria: #1f4e8c;
  --cor-fundo:    #f5f6f8;
  --cor-superficie:#ffffff;
  --cor-texto:    #1a1a1a;
  --cor-borda:    #e2e5ea;

  /* semáforo de ruptura — usado pelo statusBadge */
  --status-ok:       #2e9e5b;  /* 🟢 dias_ruptura > 7  */
  --status-atencao:  #e0a91b;  /* 🟡 3 <= dias <= 7    */
  --status-critico:  #d64545;  /* 🔴 dias_ruptura < 3  */

  /* espaçamento */
  --gap-1: 4px; --gap-2: 8px; --gap-3: 16px; --gap-4: 24px;
  --raio: 8px;
}
```

> O mapeamento das telas define o semáforo (🟢🟡🔴) e os cortes de urgência. Os limites de `dias_ruptura` acima devem bater com a regra do backend (`alertas` usa `<= 7`, "crítico" `< 3`).

---

## 6. Especificação das telas

Cada tela: objetivo, endpoint(s) consumidos, estados a tratar e componentes. Status MVP ao lado.

| Tela | Arquivo | Endpoint(s) | Componentes-chave | Prioridade |
|---|---|---|---|---|
| **Login** | `login.html` | `POST /auth/login` | toast | **MVP** |
| **Dashboard** | `dashboard.html` | `GET /dashboard` | kpiCard, charts.linha, dataTable, statusBadge | **MVP** |
| **Importar** | `importar.html` | `POST /importacao` → `POST /motor/recalcular` | uploadBlock, toast | **MVP** |
| **Estoque** | `estoque.html` | `GET /produtos`, `PATCH /produtos/{id}/estoque` | dataTable, statusBadge | **MVP** |
| **Alertas** | `alertas.html` | `GET /alertas` | dataTable, statusBadge, kpiCard | **MVP** |
| **Detalhe** | `produto-detalhe.html` | `GET /produtos/{id}/detalhe` | kpiCard, charts.linha, modal | **MVP** |
| **Curva ABC** | `curva-abc.html` | `GET /curva-abc` | charts.pareto, kpiCard, dataTable | **MVP** |
| **Comparativo (T10)** | `comparativo-modelos.html` | `GET /produtos/{id}/metricas` | charts.barras, dataTable | **MVP** |
| **Sugestão de compra** | `sugestao-compra.html` | `GET/POST /sugestao-compra` | dataTable, modal | **Pós-MVP** |
| **Configurações** | `configuracoes.html` | `PUT /configuracoes/*` | modal, toast | **Pós-MVP** |

### Detalhes por tela (resumo dos requisitos do protótipo)

- **Dashboard:** 4 KPIs (risco em 7 dias, crítico agora, valor em risco, acurácia do modelo), gráfico de linha (faturamento histórico + projeção), tabela "próximos alertas" (top 5 por urgência), banner de alerta com link para Alertas.
- **Importar:** 5 blocos de planilha — Produtos e Vendas **obrigatórios**, Estabelecimento/Fornecedores/Produto×Fornecedor desejáveis. Cada bloco com upload, contagem de linhas e estados. Botão "Processar" só habilita com obrigatórias OK. Ao concluir, chamar recálculo do motor.
- **Estoque:** tabela de todos os produtos com semáforo, estoque **editável inline** (PATCH), filtros (nome, categoria, status, classe ABC), ordenação por urgência.
- **Alertas:** produtos com `dias_ruptura <= 7` ordenados por urgência, separando "próximos 3 dias"; por item: estoque, "falta em X dias", lead time, quantidade sugerida, fornecedor; ação "marcar como pedido".
- **Detalhe:** KPIs (demanda média/dia, variabilidade σ+CV, tendência), painel de reposição (ponto de reposição, estoque de segurança, dias até ruptura, nível de serviço), gráfico 90d + projeção 30d, modal "editar parâmetros".
- **Curva ABC:** Pareto top-30 com linha de 80%, 3 cartões A/B/C, tabela com % acumulada, filtro de período (**deve recalcular via API**, diferente do protótipo).
- **Comparativo (T10):** MAPE/RMSE/MAE Holt-Winters × Prophet, barras agrupadas por produto, tabela com recomendação de modelo. **Núcleo acadêmico — capricho aqui.**

---

## 7. Tratamento de estados e erros (padrão obrigatório)

Toda tela que busca dados implementa os quatro estados:
1. **Loading:** skeleton/spinner enquanto o `apiClient` resolve.
2. **Sucesso:** renderiza os dados.
3. **Vazio:** mensagem clara quando a API retorna lista vazia (ex.: "Nenhum produto importado ainda — vá para Importar").
4. **Erro:** `toast.erro(...)` com o `.detail` do `ProblemDetail` (RFC 7807); nunca tela em branco.

> O protótipo simulava esses estados (timeout fixo, erro fixo na linha 45). No real, os estados vêm das respostas da API.

---

## 8. Do protótipo ao sistema real — o que muda

O mapeamento avisa explicitamente o que era mock. Ao construir, isto **deixa de ser fake**:
- Persistência: nada mais em `localStorage`. Estoque editável vira `PATCH /produtos/{id}/estoque`.
- Previsão: deixa de ser seno+ruído — vem do motor real (Holt-Winters/Prophet) via API.
- Métricas (T10): valores reais de `GET /produtos/{id}/metricas`, não fixos.
- Filtros de período (ABC e T10): **recalculam** chamando a API com o parâmetro de período, em vez de só filtrar visualmente.
- `dias_ruptura`: vem da API (estoque ÷ demanda prevista), não fixo.
- Coeficiente "valor em risco" (ABRAS 0,07/4): **confirmar a regra com o backend** antes de exibir o KPI.

---

## 9. Convenções

- HTML/JS/CSS: nomes em `kebab-case` para arquivos; funções em `camelCase`.
- Datas: exibir em `DD/MM/AAAA` (`format.dataBR`), mas enviar à API em ISO `YYYY-MM-DD`.
- Moeda: `format.moedaBR`.
- Nenhuma chamada `fetch` fora do `apiClient`. Nenhuma URL de API hardcodada fora do `config.js`.
- Cada `page.js` protegida começa com `requireAuth()`.

---

## 10. Como rodar localmente

```bash
# Servir a pasta web/ (ES Modules exigem servidor, não file://)
cd web && python3 -m http.server 5500
# ou a extensão "Live Server" do VS Code
```

> ⚠️ **Dependência de backend:** o backend precisa habilitar **CORS** para a origem do front (ex.: `http://localhost:5500`). Sem isso, todas as chamadas falham. Abrir tarefa no backend para um `WebConfig`/`SecurityConfig` com CORS liberado em dev.

---

## 11. Prioridade MVP (visão de front)

**MVP:** Login, Dashboard, Importar, Estoque, Alertas, Detalhe, Curva ABC, Comparativo (T10).
**Pós-MVP:** Sugestão de compra, Configurações completas, notificações.
**Fora do escopo:** qualquer tela/elemento de ESG / validade.
