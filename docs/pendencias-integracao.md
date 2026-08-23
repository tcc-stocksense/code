# Pendências da integração front ↔ back

> Revisão da branch `pedpint/integracao` (commit `3b5f60d`) contra o contrato real da API.
> Data da revisão: **23/08/2026**.
>
> Documentos relacionados:
> - [`contrato-api-frontend.md`](contrato-api-frontend.md) — fonte da verdade dos endpoints
> - [`status-integracao.md`](status-integracao.md) — o que foi feito na rodada de 16/08
> - [`../frontend/docs/tasks-integracao.md`](../frontend/docs/tasks-integracao.md) — backlog original (I-01…I-11, P-01…P-06)

---

## Resumo para quem tem 30 segundos

**A integração está completa em cobertura.** Os 11 endpoints do backend estão consumidos
pelo front — conferido controller a controller, não pela documentação. As pendências
conhecidas (P-01 a P-06) foram todas tratadas de forma honesta: o que não tem endpoint
está desabilitado com aviso, não escondido.

**Mas 4 bugs passaram**, e há um padrão neles: **todos só aparecem depois que o motor
preditivo roda pela primeira vez.** Antes do recálculo, `pontoReposicao` é `null` em todo
produto — então a tela de Alertas volta vazia, o KPI "Crítico agora" é 0, e a tela de
Estoque mostra "sem cálculo" em tudo. Os três bugs mais graves ficam invisíveis
exatamente no estado em que o sistema foi testado até agora.

Por isso a tarefa **I-11 (teste de fumaça no navegador)** é a mais importante da lista:
não é burocracia de checklist, é o que teria pego B-01, B-02 e B-03.

| Bloco | Itens | Quem resolve |
|---|---|---|
| **B** — Bugs da revisão | 4 | Front (B-02 tem opção no back) |
| **M** — Menores | 3 | Front / Back |
| **I-11** — Teste E2E | 1 | Qualquer um, precisa do ambiente de pé |
| **P** — Depende do backend | 6 | Back |

---

## Bloco B — Bugs encontrados na revisão

### B-01 — A edição de estoque da tela Estoque (T4) está morta `CRÍTICO`

**Onde:** `frontend/web/js/pages/estoque.page.js:143-162`

**O que acontece:** o botão do lápis para editar o estoque aparece na tabela, mas clicar
nele não faz nada. O clique borbulha para o listener da linha e navega para o detalhe do
produto.

**Causa:** a linha da tabela é montada misturando `appendChild` com `innerHTML +=`:

```js
tdEstoque.addEventListener('click', (e) => e.stopPropagation());  // :148
renderEstoqueCell(tdEstoque, p);                                   // :149  cria o botão + listener
tr.appendChild(tdEstoque);                                         // :150
...
tr.innerHTML += `<td class="tabular">${prTxt}</td>`;               // :156  ← destrói tudo
tr.innerHTML += `<td>${classeBadge(p.classe)}</td>`;               // :159
tr.innerHTML += `<td><a href="...">Detalhe</a></td>`;              // :162
```

`tr.innerHTML +=` serializa os filhos existentes e **re-parseia tudo do zero**. Os nós são
recriados, e todo `addEventListener` neles morre — três vezes seguidas.

**Por que importa:** é justamente o `PATCH /api/produtos/{id}/estoque` que o commit
`3b5f60d` diz ter consertado ("o bug dos 400", body `{ estoqueAtual }`). A correção do body
está certa — mas o caminho de UI que dispara esse PATCH ficou inalcançável nesta tela. Só
funciona pelo detalhe do produto, o outro ponto de chamada.

**Correção:** trocar os três `tr.innerHTML +=` por `document.createElement('td')` +
`appendChild`, como já é feito para o `tdStatus` e o `tdEstoque` logo acima. Mesma correção
resolve o M-01 (abaixo).

**Esforço:** ~20 min.

---

### B-02 — A tela de Alertas lista o catálogo inteiro `ALTO`

**Onde:** `backend/.../service/AlertaService.kt:39-48` + `frontend/web/js/pages/alertas.page.js:92`

**O que acontece:** depois de um recálculo bem-sucedido, a tela "Produtos para pedir agora"
mostra **todos os produtos**, inclusive os saudáveis. Produto com estoque folgado aparece
pintado de amarelo (`alert-row warning`), com "Vai faltar em N dias" e "Pedir 0 un".

**Causa:** `GET /api/alertas` não é uma lista de alertas — é a lista de produtos com
semáforo. O service só descarta quem não tem ponto de reposição:

```kotlin
produtoRepository.findByEstabelecimentoId(estabelecimentoId)
    .mapNotNull { it.toAlerta() }   // toAlerta() retorna null só quando pontoReposicao == null
```

Produtos `VERDE` vêm na resposta. O front itera a lista inteira sem filtrar, e como o
render é `isCritico ? 'critical' : 'warning'`, tudo que não é vermelho vira amarelo.

**Correção — decidir onde filtrar:**

- **No backend (recomendado):** adicionar a cláusula em `AlertaService.listar()` para
  devolver só `VERMELHO` e `AMARELO`. É uma linha, e faz o endpoint honrar o próprio nome.
  Mas muda o contrato: precisa atualizar `contrato-api-frontend.md` §3.7.
- **No front:** filtrar `semaforo !== 'ok'` antes de renderizar. Não mexe no contrato, mas
  o front continua baixando dados que joga fora.

**Esforço:** ~15 min de qualquer lado + atualizar o contrato se for pelo backend.

---

### B-03 — O KPI "Crítico agora" está com o rótulo errado `MÉDIO`

**Onde:** `frontend/web/js/pages/dashboard.page.js:53` e `:73`

**O que acontece:** o número exibido está certo, mas o texto que o descreve fala de outra
coisa.

O backend conta produtos que rompem em menos de 3 dias:

```kotlin
val LIMITE_CRITICO_DIAS = BigDecimal(3)
criticoAgora = produtoRepository
    .countByEstabelecimentoIdAndDiasAteRupturaLessThan(estabelecimentoId, LIMITE_CRITICO_DIAS)
```

O dashboard descreve esse número como **"estoque no ou abaixo do ponto de reposição"** —
no card e no banner. São critérios diferentes, que selecionam conjuntos diferentes de
produtos.

Agrava: a mesma frase é usada **corretamente** na tela de Alertas (`alertas.page.js:70-72`),
onde descreve o semáforo vermelho, que aí sim é `estoque ≤ PR`. Duas telas, a mesma frase,
significados diferentes.

**Correção:** trocar as duas strings do dashboard para algo como
`"produtos que rompem em menos de 3 dias"`.

**Esforço:** ~5 min.

---

### B-04 — A tela de Configurações finge que salvou `MÉDIO`

**Onde:** `frontend/web/js/pages/configuracoes.page.js:124-130`

**O que acontece:** o usuário mexe nas configurações, clica em Salvar, vê "✓ Salvo." e um
toast verde de sucesso. Nada foi persistido em lugar nenhum.

```js
document.getElementById('config-form').addEventListener('submit', (e) => {
  e.preventDefault();
  msg.style.display = 'inline-flex';
  toast.sucesso('Configurações salvas.');   // sem chamada de API
});
```

**Causa:** é o único arquivo de tela que a rodada de integração não tocou (o último commit
nele é `27585f3`, a consolidação da v1). `PUT /api/configuracoes/*` não existe — o contrato
marca a T9 como Pós-MVP. O problema não é a falta do endpoint, é a tela não avisar.

**Nota:** o `status-integracao.md` afirma "Telas servindo mock sem avisar: 4 → **0**".
Esta é a exceção — vale corrigir a afirmação junto.

**Correção:** aplicar o mesmo padrão já usado na Sugestão de compra
(`sugestao-compra.page.js:34-42`), que fora do modo mock explica que o endpoint não existe
em vez de exibir dados fictícios. Alternativa mais barata: desabilitar o botão Salvar com
um `title` explicando.

**Esforço:** ~30 min.

---

## Bloco M — Menores

### M-01 — XSS via nome de produto e mensagens de importação `BAIXO`

**Onde:** `estoque.page.js:143`, `dashboard.page.js:161`, `importar.page.js:141`

Nome de produto e mensagens de erro entram por `innerHTML` sem escape. O nome vem do
`.xlsx` que o próprio lojista sobe, então é auto-infligido — mas as mensagens de erro da
importação ecoam valores crus da planilha (`"Valor informado: '...'"`), o que amplia a
superfície.

É o tipo de detalhe que a banca pergunta. A correção de B-01 (trocar `innerHTML` por
`textContent` + `appendChild`) já resolve dois dos três pontos de graça.

### M-02 — Produto com ponto de reposição zero vira "sem cálculo" `BAIXO`

**Onde:** `frontend/web/js/core/apiClient.js:32`

```js
if (pr == null || est == null || pr <= 0) return null;
```

A guarda `pr <= 0` trata `PR = 0` como "motor nunca rodou". Mas `PR = 0` é legítimo: é o
que sai para um produto com demanda média zero. Esse produto aparece como "sem cálculo"
mesmo tendo sido calculado.

Some-se a isso que a tela de Estoque usa dois critérios diferentes para o mesmo estado —
o filtro usa `p.semaforo == null` (`estoque.page.js:74`) e o banner usa `p.semCalculo`
(`:87`), que só olha `pontoReposicao == null`. Nesse caso os dois discordam.

### M-03 — CORS liberado sem restrição de ambiente `BAIXO`

**Onde:** `backend/.../config/SecurityConfig.kt:35-50`

`allowedOriginPatterns = ["http://localhost:*", "http://127.0.0.1:*"]` com
`allowCredentials = true`, sem `@Profile("dev")`. Vale em qualquer ambiente onde o jar
rodar. Para o TCC não é um problema prático, mas anotar como decisão consciente evita a
pergunta na apresentação.

---

## I-11 — Teste de fumaça E2E no navegador `PENDENTE`

Único item do backlog original ainda em aberto — e, como dito no resumo, o que teria pego
B-01, B-02 e B-03.

**Pré-requisitos:**

```bash
docker compose up db -d                                              # MySQL
cd backend && DB_USERNAME=appuser DB_PASSWORD=<senha> ./gradlew bootRun   # :8080
cd ml-service && uvicorn main:app --port 8000                        # :8000
cd frontend/web && npx serve -l 3000                                 # front
```

Credencial de dev (seed): `admin@stocksense.local` / `admin123`.
O botão flutuante no canto inferior direito precisa estar em **🟢 API real**.

**Roteiro** (espelha a coleção `docs/postman/StockSense_E2E.postman_collection.json`):

1. Login.
2. **Conferir as telas ANTES de recalcular** — é o estado que revela os `null`:
   T4 deve mostrar "sem cálculo", T5 vazia, T2 com acurácia "—", T10 com "rode o motor".
3. Importar `2_produtos.xlsx`, depois `5_vendas.xlsx` (gerados por
   `ml-service/app/tests/generate_synthetic_data.py`). Vendas fica bloqueada até Produtos
   dar certo — confirmar que o bloqueio funciona.
4. Rodar o recálculo (`Processar dados`).
5. **Conferir as telas DEPOIS** — T4, T6, T10, T5, T2, T7.

**Critérios de aceite:**

- Console do navegador sem erro.
- Na T4, clicar no lápis abre a edição inline e o valor persiste após F5 *(pega B-01)*.
- Na T5, só aparecem produtos que realmente precisam ser pedidos *(pega B-02)*.
- Os números do dashboard batem com o que os rótulos prometem *(pega B-03)*.
- Estados de erro exercitados: planilha `.csv` (deve dar 400), planilha com SKU
  inexistente nas vendas (erro por linha), histórico < 90 dias (aviso, não erro).

---

## Bloco P — Depende do backend

Copiado do backlog original, com o estado de hoje. Nada aqui bloqueia o MVP — todos já têm
tratamento no front.

| # | O quê | Impacto hoje | Estado |
|---|---|---|---|
| **P-01** | `PATCH /api/produtos/{id}/parametros` (lead time, nível de serviço) | Modal "Editar parâmetros" desabilitado na T6 | Aberto |
| **P-02** | `GET /api/curva-abc?periodo=` | ABC sempre sobre todo o histórico; filtro escondido | Aberto |
| **P-03** | Endpoint agregado de métricas | T10 faz N chamadas (mitigado: concorrência 4) | Aberto — decidir se vale |
| **P-04** | CORS de dev | — | ✅ Resolvido em `3b5f60d` |
| **P-05** | Motor assíncrono (`202` + `GET /api/motor/status`) | Recálculo trava a tela de Importar | Suspenso (Épico 7) |
| **P-06** | Disparo automático do motor pós-importação | Front chama o motor manualmente | Suspenso (Épico 7) |
| — | `GET /api/sugestao-compra` | Tela T8 indisponível fora do mock | Pós-MVP |
| — | `PUT /api/configuracoes/*` | Tela T9 — ver B-04 | Pós-MVP |
| — | Endpoint de pedidos | "Marcar como pedido" não persiste | Pós-MVP |

---

## Sugestão de ordem

1. **B-03** (5 min) e **B-01** (20 min) — baratos, e o B-01 destrava a T4 de verdade.
2. **I-11** — subir o ambiente e rodar o roteiro. É o que valida tudo.
3. **B-02** — decidir front ou back em grupo, porque mexe no contrato.
4. **B-04** e o bloco **M** — antes de fechar a documentação para a banca.

O bloco **P** não precisa de ação agora: está tratado no front e documentado no contrato.

---

*Ao concluir um item, marcar aqui e refletir a mudança em `status-integracao.md`. Se o
contrato mudar (caso do B-02 pelo backend), `contrato-api-frontend.md` é o que precisa ser
atualizado primeiro — os outros documentos derivam dele.*
