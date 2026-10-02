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

## Verificação dos números

```bash
ml-service/venv/Scripts/python.exe docs/artigo/verificar_numeros.py saida.txt
```

Confere cada célula das tabelas do artigo contra `dados_documento.json`, além
das afirmações quantitativas do texto corrido ("supera em 10 de 10 produtos",
"margem inferior a 0,7 pp em nove deles"). **Rodar sempre que o texto ou os
dados mudarem.** Na primeira execução ele já pegou uma mediana calculada
errado — 49,4% onde o correto era 45,1% — antes de o número ir para o artigo.

## Verificacao das referencias cruzadas

```bash
ml-service/venv/Scripts/python.exe docs/artigo/verificar_referencias.py
```

Confere se figuras, tabelas e equacoes tem numeracao contigua e se toda
referencia no corpo aponta para um rotulo existente. **Rodar sempre que algo for
renumerado.**

Limite conhecido: ele acusa referencia *inexistente*, nao referencia *errada*.
Uma mencao a "Figuras 7 e 8" apontando para as figuras erradas passa, se 7 e 8
existirem. Renumeracao por substituicao simples quebra o plural -- foi assim que
quatro referencias ficaram erradas de uma vez.

## Marcadores no texto

- `[CITAR: ...]` — afirmação que precisa de fonte que ainda não está no repositório.
  **Nunca** preencher com citação de memória: referência inventada em TCC é fatal.
- `[CONFIRMAR: ...]` — dado factual que só os autores têm (nome de orientador,
  prenome de autor citado, data de banca).

## Material de estudo

O guia do grupo é [`docs/GUIA-DE-ESTUDO-TCC.md`](../GUIA-DE-ESTUDO-TCC.md): os
conceitos explicados do zero, os resultados comentados, as perguntas de banca com
resposta e a lista honesta de vulnerabilidades. Absorveu o antigo
`NOTAS-DEFESA.md`.

Ele existe porque o artigo passou por uma redução deliberada da carga matemática,
para diminuir a superfície de perguntas na arguição — a explicação que saiu do
artigo mora lá, mais longa e mais didática do que caberia num texto acadêmico.

## Geração do .docx

```bash
ml-service/venv/Scripts/python.exe -m pip install -r docs/artigo/requirements-artigo.txt
ml-service/venv/Scripts/python.exe docs/artigo/gerar_docx.py
```

Gera `docs/artigo/artigo-stocksense.docx`. Dependência isolada de propósito: o
`requirements.txt` do ml-service continua sendo só o runtime do serviço.

O script usa o template como **doador de formatação**: abre o arquivo, esvazia o
corpo preservando `sectPr` (margens), cabeçalho e rodapé, e reescreve o conteúdo.
Duas descobertas do template que o script precisa respeitar:

- **O template não define estilos de título.** "1 Introdução" e um parágrafo
  comum são ambos `Normal`; o que os distingue é negrito, `<w:caps/>`,
  justificação e `outlineLvl`. Aplicar `Heading 1` produziria um documento azul,
  com fonte diferente do modelo da faculdade.
- **A entrelinha do corpo é 1,5**, não o 1,08 do `docDefaults` — cada parágrafo
  sobrescreve o padrão.

Também não existem os estilos `List Number`, `List Bullet` nem `Table Grid`: as
listas recebem marcador textual com recuo manual e as tabelas ganham bordas
aplicadas via XML.

Figuras cujo arquivo existe são embarcadas; as que faltam viram um parágrafo
`[FIGURA PENDENTE: ...]` em negrito, para a lacuna não passar despercebida.
