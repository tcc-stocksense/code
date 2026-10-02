# docs/ — Documentação técnica do ml-service

Dois PDFs, com públicos diferentes:

| Arquivo | Público | Natureza |
|---|---|---|
| `capitulo-validacao.pdf` | banca / monografia | **capítulo escrito**, pronto para revisão e inclusão no TCC (19 pág.) |
| `relatorio-modelos-preditivos.pdf` | apoio interno | referência técnica exaustiva sobre os modelos e a análise (36 pág.) |

---

## `capitulo-validacao.pdf`

Capítulo de validação empírica do motor, redigido em linguagem acadêmica e pronto
para entrar na monografia. Estrutura em 11 seções: objetivo e escopo, protocolo
experimental, caracterização dos dados, análise exploratória, resultados
comparativos, diagnóstico de resíduos, robustez em janelas móveis, análise dos
parâmetros ajustados, conversão em decisão de reposição, limitações e síntese.

> **Numeração provisória.** O capítulo está numerado como **5** (seções 5.1 a
> 5.11). Para renumerar, altere a constante `CAP` no topo de
> `gerar_capitulo_validacao.py` e regenere.

Existe também `capitulo-validacao-esqueleto.md` — a versão em esqueleto, com
marcadores `[ESCREVER]` no lugar da prosa. Foi mantida caso você prefira
reescrever alguma seção com suas próprias palavras a partir da estrutura.

---

## `relatorio-modelos-preditivos.pdf`

Relatório técnico completo sobre o motor preditivo, escrito para a **banca do TCC**.
36 páginas cobrindo:

| Seção | Conteúdo |
|---|---|
| 1–3 | Sumário executivo, arquitetura do serviço e o problema estatístico |
| 4–5 | **Como cada modelo funciona por dentro** — equações do Holt-Winters e do Prophet, e como os parâmetros são encontrados por otimização |
| 6–7 | Comparação conceitual e a regra de seleção do motor (walk-forward, menor MAPE) |
| 8 | MAPE, RMSE e MAE — definição, unidade e quando cada uma engana |
| 9 | Fórmulas de estoque (Ballou) com exemplo numérico executado pelo motor |
| 10–11 | **O que foi feito em `analysis/`** e como o dataset sintético é gerado |
| 12 | Resultados: comparativo completo + os 14 gráficos com legenda explicativa |
| 13 | Achado central: por que os dois modelos empatam (α ≈ β ≈ γ ≈ 0) |
| 14–16 | Backtesting, limitações declaradas e reprodutibilidade |
| 17–18 | Perguntas prováveis da banca, com respostas, e referências |

### Princípio: nenhum número é digitado à mão

O PDF é **gerado por script** a partir de um JSON produzido pela execução do
próprio código de produção (`app/services/`). Trocar um modelo, um parâmetro ou o
dataset e regerar atualiza automaticamente todas as tabelas, todos os valores no
texto e todas as figuras.

## Como regenerar

A partir da raiz do `ml-service`, com o venv do projeto:

```bash
# 0. dependências de análise (inclui reportlab), uma vez só
venv/Scripts/python.exe -m pip install -r analysis/requirements-analysis.txt

# 1. regerar as figuras (só se os modelos ou os dados mudaram)
venv/Scripts/python.exe -m jupyter nbconvert --to notebook \
        --execute analysis/analise_modelos.ipynb

# 2. coletar os números do código de produção
venv/Scripts/python.exe analysis/_coletar_dados_doc.py

# 3. montar os PDFs
venv/Scripts/python.exe docs/gerar_capitulo_validacao.py   # capítulo do TCC
venv/Scripts/python.exe docs/gerar_relatorio_pdf.py        # relatório técnico
```

O passo 1 é opcional no dia a dia: as figuras versionadas em `analysis/figures/`
já estão atualizadas. Os passos 2 e 3 levam poucos minutos (o passo 2 treina os
dois modelos em todos os produtos).

## Arquivos

| Arquivo | Papel |
|---|---|
| `capitulo-validacao.pdf` | capítulo do TCC, escrito e pronto para revisão |
| `gerar_capitulo_validacao.py` | monta o capítulo (texto + tabelas + figuras) |
| `capitulo-validacao-esqueleto.md` | versão em esqueleto, com marcadores `[ESCREVER]` |
| `gerar_esqueleto_capitulo.py` | gera o esqueleto — **andaime de uso único** |
| `relatorio-modelos-preditivos.pdf` | relatório técnico de apoio |
| `gerar_relatorio_pdf.py` | monta o relatório (conteúdo + layout) |
| `_estilo_pdf.py` | fontes, paleta e construtores de bloco — compartilhado pelos dois PDFs |
| `../analysis/_coletar_dados_doc.py` | executa os modelos e despeja os números em JSON |
| `../analysis/results/dados_documento.json` | insumo numérico do relatório |
| `../analysis/results/_alphas.json` | parâmetros α/β/γ ajustados (seção 13) |
| `../analysis/figures/*.png` | as 14 figuras embutidas |

## Fontes

O PDF usa **DejaVu Sans / Sans Mono**, que vêm empacotadas com o matplotlib — sem
dependência de fonte instalada no sistema. Foi uma escolha necessária: as fontes
padrão do reportlab não têm os símbolos gregos e matemáticos (α, β, γ, σ, √, ŷ)
que as fórmulas exigem.

> Nota: a fonte monoespaçada não possui o glifo `ℓ` (U+2113), tradicional para o
> nível no Holt-Winters. O relatório usa **`L`** no lugar, de forma consistente
> entre texto e fórmulas.
