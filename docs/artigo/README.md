# Artigo do TCC — StockSense

Rascunho do artigo científico, escrito em Markdown e convertido para o template
oficial da SPTech ao final.

## Por que Markdown e não Word direto

`.docx` é binário: o Git não mostra diff. Escrevendo em `.md`, cada alteração de
texto aparece linha a linha no `git diff` e cada seção tem seu próprio commit.
A formatação (Arial 12, margens, legendas, cabeçalho com DOI) é aplicada no fim,
por script, a partir do template — não à mão.

## Estrutura oficial do template SPTech

Extraída de `7-sem-TCC/docs/exemplos/TEMPLATE_ARTIGO_TCC_SPTECH.docx`. **ABSTRACT
vem antes do RESUMO.** São cinco seções numeradas:

| Arquivo | Seção |
|---|---|
| `00-frontmatter.md` | Título (EN/PT), autores, ABSTRACT + Keywords, RESUMO + Palavras-chave |
| `01-introducao.md` | 1 Introdução — 1.1 Problema de pesquisa · 1.2 Objetivos · 1.3 Justificativa |
| `02-fundamentacao.md` | 2 Fundamentação teórica — 2.3 Trabalhos relacionados |
| `03-metodologia.md` | 3 Metodologia e desenvolvimento — 3.1 a 3.5 |
| `04-resultados.md` | 4 Resultados e discussão — 4.3 Discussão |
| `05-consideracoes.md` | 5 Considerações finais (inclui Limitações e trabalhos futuros) |
| `referencias.md` | Referências (ABNT) |

Observações do template que mudam o que costuma se assumir:

- **Arquitetura não é seção própria** — é a subseção `3.2`, dentro de Metodologia.
- **Limitações não é seção** — é um parágrafo com lead-in em negrito dentro da 5.
- **Não há slot para hipóteses** — o que seria H1/H2/H3 vira objetivo específico em 1.2.
- Legenda de figura/tabela **acima** (`Figura N - Título`), fonte abaixo (`Fonte: Autoral, 2026`).
- Equações numeradas à direita, seguidas de um parágrafo "Onde ...".

## Ordem de escrita

Diferente da ordem do documento: **3 → 4 → 2 → 1 → 5 → resumo**. As seções 3 e 4
estão presas aos dados e praticamente se escrevem sozinhas; a 2 fica mais enxuta
depois de saber qual teoria a discussão usou; problema e objetivos ficam melhores
escritos depois de conhecer os achados; resumo sempre por último.

## Regra dos números

**Nenhum número é digitado à mão.** Todos saem de
`ml-service/analysis/results/dados_documento.json`, gerado por
`ml-service/analysis/_coletar_dados_doc.py` a partir do código de produção.
Se o motor for reexecutado, os números se regeneram — não se caça divergência
entre texto e tabela.

Para atualizar:

```bash
cd ml-service
venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace analysis/analise_modelos.ipynb
venv/Scripts/python.exe analysis/_coletar_dados_doc.py
```

## Marcadores no texto

- `[CITAR: ...]` — afirmação que precisa de fonte que ainda não está no repositório.
  **Nunca** preencher com citação de memória: referência inventada em TCC é fatal.
- `[CONFIRMAR: ...]` — dado factual que só os autores têm (nome de orientador,
  prenome de autor citado, data de banca).

## Notas de defesa

`NOTAS-DEFESA.md` acumula, por seção, as perguntas que a banca tende a fazer, a
resposta em duas linhas e o ponteiro para a tabela ou figura que a sustenta.
Serve para revisar na véspera sem reler o artigo inteiro.

## Geração do .docx

```bash
pip install -r docs/artigo/requirements-artigo.txt
python docs/artigo/gerar_docx.py
```

O script abre o template, aplica os estilos dele e escreve
`docs/artigo/artigo-stocksense.docx`. Dependência isolada de propósito: o
`requirements.txt` do ml-service continua sendo só o runtime do serviço.
