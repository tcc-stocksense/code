---
tags: [conceito, integracao, plano]
atualizado: 2026-07-13
status: pendente
---

# Integração com o backend

Página-memória do processo de ligar o frontend no backend real (Kotlin/Spring, `:8080`). Atualizar conforme a integração avança.

## Estado atual
Frontend **pronto para integrar**: toda tela busca dados via `apiClient`, que já tem o `fetch` real atrás do flag de mock (ver [[camada-mock-e-api]]). Desligar o mock aponta tudo para o backend.

## Contrato esperado pelo front (endpoint → tela)

| Endpoint | Tela | Status |
|---|---|---|
| `POST /auth/login` | [[login]] | a validar |
| `GET /dashboard` | [[dashboard]] | a validar |
| `POST /importacao` (multipart) → `POST /motor/recalcular` | [[importar]] | a validar |
| `GET /produtos` | [[estoque]] | a validar |
| `PATCH /produtos/{id}/estoque` | [[estoque]] / [[produto-detalhe]] | a validar |
| `GET /alertas` | [[alertas]] | a validar |
| `GET /produtos/{id}/detalhe` | [[produto-detalhe]] | a validar |
| `PATCH /produtos/{id}/parametros` | [[produto-detalhe]] | a validar |
| `GET /curva-abc?periodo=` | [[curva-abc]] | a validar |
| `GET /produtos/metricas` | [[comparativo-modelos]] | alinhado à família `/produtos/…/metricas`; confirmar rota final com o back |
| `GET /sugestao-compra` | [[sugestao-compra]] | a validar |
| `PUT /configuracoes/*` | [[configuracoes]] | não ligado (Pós-MVP) |

## Passos da integração
1. Ler **controllers + DTOs** reais do backend → levantar endpoints e shapes.
2. Reconciliar campo a campo com o que o front espera ([[modelo-de-dados]]).
3. Onde divergir: adaptar o front (ou fina camada de mapeamento no `core/`).
4. Desligar mock, ajustar `API_BASE_URL`, reativar `requireAuth()`+JWT.
5. Backend: habilitar **CORS** em dev.

## Pendências/decisões abertas
- **Contrato do comparativo:** front agora usa `GET /produtos/metricas` (listagem geral). ✅ alinhado à família documentada — falta o backend confirmar a rota/shape final.
- **"Valor em risco" (dashboard):** coeficiente ABRAS 0,07÷4 — o back calcula ou o front? (`docs/frontend.md §8`).
- **Campos derivados** (`pontoReposicao`, `estoqueSeguranca`, `tendencia`): back devolve ou front computa? Ver [[inteligencia-de-reposicao]].
- **`dias_ruptura`:** deve vir da API (estoque ÷ demanda prevista).

## Ressalva
Teste end-to-end ao vivo exige o backend rodando aqui (JDK 17 + MySQL/Docker). Sem isso: integração feita e verificada contra contratos; teste final via `docker compose`.

Origem da reunião de validação: [[2026-07-13-validacao-backend]].
