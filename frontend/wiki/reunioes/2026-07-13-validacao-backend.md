---
tags: [reuniao, backend]
data: 2026-07-13
participantes: []
status: agendada
---

# Reunião — Validação do backend

## Objetivo
Validar o backend para em seguida iniciar a [[integracao-backend]] com o frontend. Depois da reunião, os arquivos do backend entram no ambiente para o mapeamento endpoint-a-endpoint.

## A confirmar na reunião (checklist)
- [ ] Endpoints reais e seus caminhos (bate com a tabela em [[integracao-backend]]?).
- [ ] Shape dos DTOs (nomes de campo, tipos, aninhamento `grafico`/`vendasSemana`) — ver [[modelo-de-dados]].
- [ ] Quem calcula os campos derivados (`pontoReposicao`, `estoqueSeguranca`, `tendencia`) — back ou front? Ver [[inteligencia-de-reposicao]].
- [ ] Contrato do comparativo: `/metricas` vs `/produtos/{id}/metricas`.
- [ ] Regra do "valor em risco" (coef. ABRAS) — back ou front?
- [ ] CORS habilitado para a origem do front.
- [ ] Formato de auth (JWT) para reativar `requireAuth()`.

## Decisões
- _(preencher após a reunião)_

## Próximos passos
- [ ] Subir os arquivos do backend no ambiente.
- [ ] Iniciar integração (desligar mock, casar shapes).

## Referências
- [[integracao-backend]] · [[modelo-de-dados]] · [[overview]]
