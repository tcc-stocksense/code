---
tags: [tela, mvp]
endpoint: POST /importacao, POST /motor/recalcular
prioridade: MVP
status_integracao: a-validar
atualizado: 2026-07-13
---

# Tela — Importar dados

**Objetivo:** carregar planilhas de produtos/vendas e disparar o recálculo do motor.

**Endpoints:** `POST /importacao` (multipart, via `apiUpload`) → `POST /motor/recalcular`.

**Conteúdo:** 5 blocos de planilha — **Produtos** e **Vendas** obrigatórios; Estabelecimento, Fornecedores, Produto×Fornecedor desejáveis. Cada bloco com estados vazio/processando/sucesso/erro + contagem de linhas. Botão "Processar" habilita só com as obrigatórias OK; ao concluir, chama o recálculo.

**Estados:** loading ✓ · vazio ✓ · erro ✓.

**Integração:** hoje o upload/validação é simulado. No real, o backend faz o **parsing e validação** das planilhas e devolve linhas processadas/erros por linha. Ver [[integracao-backend]].

Relacionado: [[modelo-de-dados]] · [[overview]]
