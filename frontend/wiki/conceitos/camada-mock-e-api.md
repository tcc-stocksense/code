---
tags: [conceito, arquitetura, integracao]
atualizado: 2026-07-13
fonte: web/js/core/apiClient.js, web/js/core/mock.js
---

# Camada de mock e API

Como o frontend roda **sem backend** hoje, e como liga no real.

## O flag de mock
`apiClient.js` decide entre mock e rede real:
```js
const USAR_MOCK = localStorage.getItem('stocksense_mock') !== 'off';
```
- **Ligado por padrão.** Um botão flutuante ("🟢 Mock ON") alterna via `localStorage`.
- Com mock ON → `mockApiGet/Post/Patch/Upload` (respostas fictícias em `mock.js`).
- Com mock OFF → `fetch(API_BASE_URL + path)` real, com `Authorization: Bearer <token>`.

> **O caminho de rede real já está implementado.** Integrar = desligar o mock e alinhar os shapes. Ver [[integracao-backend]].

## apiClient — contrato estável
```
apiGet(path)            → Promise<json>
apiPost(path, body)     → Promise<json>
apiPatch(path, body)    → Promise<json>
apiUpload(path, formData) → multipart (importação)
```
Em erro: lança `Error` com `.status` e `.detail` (do ProblemDetail RFC 7807). A tela trata e mostra `toast.erro`. Ver [[estados-de-ui]].

## Rotas que o mock implementa
`POST /auth/login` · `GET /dashboard` · `GET /produtos` · `GET /produtos/{id}/detalhe` · `PATCH /produtos/{id}/estoque` · `PATCH /produtos/{id}/parametros` · `GET /alertas` · `GET /curva-abc` · `GET /metricas` · `GET /sugestao-compra` · `POST /importacao` · `POST /motor/recalcular`

## serve.json (dev)
Servido com `npx serve` na porta 3000. O `serve.json` tem `cleanUrls:false` + rewrite de `/` e de URLs limpas para os `.html` — senão navegações `.html?id=` perderiam a query string (o `serve` fazia 301 que descartava `?id=`).

## ⚠️ Para integrar
1. Backend habilitar **CORS** para a origem do front.
2. Reativar `requireAuth()` (hoje é no-op) + fluxo JWT.
3. Alinhar `API_BASE_URL` por ambiente.
4. Casar os **shapes de JSON** — ver [[integracao-backend]].

Relacionado: [[stack-e-arquitetura]]
