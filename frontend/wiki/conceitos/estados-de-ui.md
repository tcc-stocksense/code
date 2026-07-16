---
tags: [conceito, ui, padrao]
atualizado: 2026-07-13
fonte: ../docs/frontend.md §7
---

# Estados de UI (padrão obrigatório)

Toda tela que busca dados implementa **quatro estados** (`docs/frontend.md §7`):

1. **Loading** — skeleton/spinner enquanto o `apiClient` resolve. (componentes `skeleton*`)
2. **Sucesso** — renderiza os dados.
3. **Vazio** — mensagem clara quando a API retorna lista vazia (ex.: "Nenhum produto importado — vá para Importar"). (componente `emptyState`)
4. **Erro** — `toast.erro(.detail)` do ProblemDetail; **nunca** tela em branco.

## Situação por tela (auditado 2026-07-13)

| Tela | loading | vazio | erro |
|---|:--:|:--:|:--:|
| [[dashboard]] | ✓ | ✓ | ✓ |
| [[estoque]] | ✓ | ✓ | ✓ |
| [[alertas]] | ✓ | ✓ | ✓ |
| [[produto-detalhe]] | ✓ | ✓ (404) | ✓ |
| [[curva-abc]] | ✓ | ✓ | ✓ |
| [[comparativo-modelos]] | ✓ | ✓ | ✓ |
| [[sugestao-compra]] | ✓ | ✓ | ✓ |
| [[importar]] | ✓ | ✓ | ✓ |
| [[login]] | ✓ | n/a | ✓ |
| [[configuracoes]] | — | — | — (form local, sem fetch) |

Relacionado: [[camada-mock-e-api]] · [[stack-e-arquitetura]]
