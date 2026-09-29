# Estrutura do artigo — StockSense no template da SPTech

Template oficial preenchido com o conteúdo real do projeto. Títulos fixos do
template estão marcados com `[fixo]`; os demais foram nomeados conforme o
conteúdo, que é o que o template espera (ele os preenche com lorem ipsum).

Legenda de status: `[✓]` escrito · `[ ]` a escrever · `[!]` depende de decisão
ou informação externa.

---

## Front matter

```
[cabeçalho: logo SPTECH + DOI Zenodo]
```

**Título (EN, caixa alta)** — proposta:
`PREDICTIVE INVENTORY OPTIMIZATION FOR NEIGHBORHOOD GROCERY STORES:`
`AN EMPIRICAL COMPARISON BETWEEN HOLT-WINTERS AND PROPHET`

**Título (PT, entre parênteses)** — proposta:
`(Otimização preditiva de estoque para mercados de bairro: uma comparação`
`empírica entre Holt-Winters e Prophet)`

O título nomeia a comparação, e não o produto, porque é a comparação que
constitui a contribuição do trabalho — o sistema é o instrumento.

**Autores** — Danilo Silvestre Faustino, Gabriel Boos Duarte, Gabriel Sanchez,
Pedro Primon, Pedro Paulo Pinto¹
**Orientador(a)** — `[CONFIRMAR: titulação e nome]`²
Faculdade São Paulo Tech School - São Paulo, SP, Brasil

- `[ ]` **ABSTRACT** (150–250 palavras) + `Keywords:` (3 a 5) — inglês vem primeiro
- `[ ]` **RESUMO** + `Palavras-chave:`

> Escrever por último, depois que os resultados estiverem fechados.
> Palavras-chave sugeridas: previsão de demanda; séries temporais; gestão de
> estoque; varejo de bairro; Holt-Winters.

---

## 1 Introdução `[fixo]`

- `[ ]` Abertura: o varejo alimentício de bairro e a gestão de estoque manual;
  ruptura e excesso como as duas faces do mesmo problema.

### 1.1 Problema de pesquisa `[fixo]` `[!]`

Uma pergunta única e explícita. Proposta, formulada para ser respondível pelo
que foi de fato medido:

> *Modelos de previsão de demanda por séries temporais aplicados ao histórico de
> vendas de um mercado de bairro produzem previsões acuradas o bastante para
> sustentar o cálculo automático de ponto de reposição — e qual dos modelos se
> adapta melhor a essas séries?*

A pergunta tem duas partes de propósito. A segunda (qual modelo vence) é a que a
proposta original prometia; a primeira (se algum deles vale a pena) é a que o
baseline ingênuo permitiu responder, e é a mais forte das duas.

`[!]` **Confirmar com o orientador** — a proposta do TCC não registra uma
pergunta de pesquisa explícita, apenas o objetivo de "identificar empiricamente
a abordagem de melhor desempenho para o contexto específico do varejo de bairro".

### 1.2 Objetivos `[fixo]`

- `[ ]` **Geral:** desenvolver e avaliar empiricamente um motor de otimização
  preditiva de estoque para mercados de bairro.
- `[ ]` **Específicos** (lista) — é aqui que entram as antigas hipóteses, já que
  o template não tem seção para elas:
  1. Implementar e comparar Holt-Winters e Prophet sobre séries de demanda diária;
  2. Estabelecer um critério objetivo de seleção do modelo por produto;
  3. Verificar se os modelos superam um baseline ingênuo sazonal;
  4. Converter a previsão em estoque de segurança, ponto de reposição e dias até
     ruptura pelas formulações de Ballou;
  5. Integrar o motor a uma aplicação web utilizável por gestor sem perfil técnico.

### 1.3 Justificativa `[fixo]`

- `[ ]` Impacto financeiro da ruptura — ABRAS (2023): derruba de 5% a 10% das
  vendas; 32% dos consumidores migram para o concorrente; a cada 4 pp de ruptura
  reduzidos, recupera-se 1 pp de vendas.
- `[ ]` A lacuna tecnológica — Sebrae (2023a, 2023b): entre a planilha, que não
  prevê nem alerta, e o ERP, inacessível por custo e complexidade, não existe
  solução intermediária com inteligência preditiva.

---

## 2 Fundamentação teórica `[fixo]`

> Fonte principal: `tcc-stocksense/docs/contexto/revisao_bibliografica.pdf`, que
> já traz 12 páginas redigidas e as referências em ABNT. Três reparos
> obrigatórios antes de aproveitar: completar os prenomes de FERREIRA/MOTA e
> SILVA/ARAÚJO; atualizar a fórmula de Ballou (a revisão traz a simplificada, o
> motor usa a completa); e remover a seção de ESG/ODS 12, que saiu do escopo.

### 2.1 Gestão de estoque no pequeno varejo

- `[ ]` **2.1.1** Ruptura, excesso e gestão intuitiva — ABRAS (2023), Sebrae
  (2023c), Ferreira e Mota (2022)
- `[ ]` **2.1.2** Estoque de segurança, nível de serviço e ponto de reposição —
  Ballou (2006). **Apresentar a formulação completa**, com variabilidade de lead
  time, que é a implementada.
- `[ ]` **2.1.3** Classificação ABC — Sebrae (2023d), Silva e Araújo (2022)

### 2.2 Previsão de demanda e séries temporais

- `[ ]` Abertura: componentes de uma série — tendência, sazonalidade, ruído;
  ARIMA como marco formal (Box e Jenkins, 1976) e o arcabouço de Hyndman e
  Athanasopoulos (2021)
- `[ ]` **2.2.1** Holt-Winters — Holt (1957), Winters (1960)
- `[ ]` **2.2.2** Prophet — Taylor e Letham (2018)
- `[ ]` **2.2.3** Métricas de acurácia e suas limitações — MAE, RMSE, MAPE;
  o comportamento do MAPE com denominador pequeno, que reaparece na seção 4

### 2.3 Trabalhos relacionados `[fixo]`

- `[ ]` **Tabela 1** — comparativo no formato prescrito pelo template:
  `Autor (ano) | Abordagem | Resultado | Limitação`, com `Este trabalho (2026)`
  na última linha
- `[!]` Linhas previstas: Silva e Araújo (2022), Ferreira e Mota (2022),
  Taylor e Letham (2018) e os TCCs antecedentes **GRP03** (Prophet) e **GRP04** —
  `[CONFIRMAR: autores, título e ano dos dois, para citar em ABNT]`
- `[ ]` Fechar com a frase de lacuna que ancora o problema de pesquisa

---

## 3 Metodologia e desenvolvimento `[fixo]` — `[✓]` escrita

Arquivo: `03-metodologia.md`

- `[✓]` **3.1** Organização do projeto `[fixo]` — equipe, cinco fases, monorepo
- `[✓]` **3.2** Arquitetura da solução `[fixo]` — **Figura 1**: contexto C4 nível 1
  (`diagram-contexto.png`); **Figura 2**: containers C4 nível 2
  (`diagram-container-c2.png`); blocos A–E e fluxo em 6 passos
- `[✓]` **3.3** Base de dados `[fixo]`
  - 3.3.1 Modelo de dados — **Figura 3**: DER (`database/der-diagram.mwb`,
    exportar como imagem); as 7 tabelas em três blocos
  - 3.3.2 Esquema de ingestão (planilhas, mínimo de 90 dias)
  - 3.3.3 Base de validação sintética — **Tabela 2**: multiplicador semanal;
    **Equação (1)**: geradora
- `[✓]` **3.4** Tecnologias consideradas e descartadas `[fixo]` — ARIMA,
  aprendizado profundo, PostgreSQL, módulo ESG, ABC no motor
- `[✓]` **3.5** Implementação `[fixo]` — modelos, métricas, protocolo de
  avaliação, critério de seleção, parâmetros de reposição, interface
  (**Figura 4**: mosaico de telas) e equivalência com produção. Nove equações
  numeradas.
- `[!]` Pendência: `[CITAR: metodologia científica]` na abertura da seção

---

## 4 Resultados e discussão `[fixo]` — `[✓]` escrita

Arquivo: `04-resultados.md`. Todos os números saem de
`ml-service/analysis/results/dados_documento.json` e são conferidos por
`verificar_numeros.py`.

- `[✓]` **4.1** Perfil do conjunto de dados — **Tabela 3** (descritiva);
  **Figuras 5 e 6** (`g1_decomposicao_*`). O CV nunca é baixo porque a oscilação
  semanal já produz dispersão: parte do desvio é estrutura, não ruído.
- `[✓]` **4.2** Acurácia dos modelos e ganho sobre o baseline — **Tabela 4**
  (MAPE/RMSE/MAE, placar 6 × 4), **Tabela 5** (margens: 9 de 10 abaixo de
  0,7 pp), **Tabela 6** (ganho: 10 de 10, redução mediana de 45,1%);
  **Figuras 7 e 8** (`g2_previsto_real_*`).
- `[✓]` **4.3** Robustez e diagnóstico — **Tabelas 7 e 8** (backtesting);
  **Figuras 9 e 10** (`g6_backtesting_*`), **Figuras 11 e 12**
  (`g5_residuos_*`). A dobra de 19/11 do produto 5 é analisada, não omitida:
  MAPE e RMSE apontam vencedores opostos sobre os mesmos dados.
- `[✓]` **4.4** Da previsão à decisão de reposição — **Tabela 9**;
  **Figuras 13 e 14** (`g7_reposicao_*`).
- `[✓]` **4.5** Discussão `[fixo]` — **Tabela 10** (α, β, γ) e quatro blocos com
  lead-in em negrito: por que os modelos empatam · o que isso valida e o que
  delimita · por que o baseline perde por tanto · consequência arquitetural.

## 5 Considerações finais `[fixo]`

- `[ ]` Retomar a pergunta de 1.1 e respondê-la nos termos em que foi feita
- `[ ]` Três a cinco afirmações do que ficou demonstrado, cada uma amarrada à
  evidência: há sinal previsível (4.1); os modelos generalizam e superam o piso
  ingênuo (4.2); o desempenho se mantém fora da janela principal (4.3); a
  previsão vira parâmetro de reposição coerente (4.4); o empate tem explicação
  mecânica verificável (4.5)
- `[ ]` **Limitações e trabalhos futuros:** — parágrafo com lead-in em negrito,
  **não é seção**. Selecionar as mais relevantes das dez mapeadas em
  `ml-service/docs/capitulo-validacao-esqueleto.md` §X.10, priorizando: validação
  sobre dados sintéticos; geração multiplicativa contra ajuste aditivo; σ da
  demanda calculado sobre a série completa, incluindo dias fechados; ausência de
  sazonalidade anual em 365 dias. Trabalho futuro principal: validação externa
  com histórico real e, se houver tempo, o dataset Favorita (Kaggle).

---

## Referências `[fixo]`

- `[ ]` ABNT, ordem alfabética. Base pronta na revisão bibliográfica:
  ABRAS (2023), BALLOU (2006), BOX e JENKINS (1976), FERREIRA e MOTA (2022),
  HOLT (1957), HYNDMAN e ATHANASOPOULOS (2021), KAGGLE, SEBRAE (2023a–e),
  SILVA e ARAÚJO (2022), TAYLOR e LETHAM (2018), WINTERS (1960)
- `[!]` A acrescentar: metodologia científica; GRP03 e GRP04

```
[rodapé: licença CC BY-NC-SA]
```

---

## Numeração de figuras e tabelas

Contínua no documento inteiro. **Fechada para as seções 3 e 4**; só a Tabela 1
depende da seção 2 ainda não escrita.

| Seção | Figuras | Tabelas |
|---|---|---|
| 2 | nenhuma prevista | **1** — trabalhos relacionados |
| 3 | **1** contexto C4 · **2** containers C4 · **3** DER · **4** telas | **2** — multiplicador semanal |
| 4 | **5–6** decomposição · **7–8** previsto × real · **9–10** backtesting · **11–12** resíduos · **13–14** reposição | **3** descritiva · **4** métricas · **5** margens · **6** ganho · **7–8** backtesting · **9** reposição · **10** α β γ |
| 5 | nenhuma | nenhuma |

Total: **14 figuras e 10 tabelas**. Das 14 figuras da camada de análise, entram
12 — ficam de fora `g3_barras_erro_*` (redundante com a Tabela 4) e
`g4_erro_horizonte_*` (o argumento sobre acúmulo de erro no horizonte cabe em
texto). As outras duas figuras são os diagramas C4 e o DER.

Pela densidade dos artigos GRP01–GRP05 (230–250 palavras por página com muitas
figuras), 14 figuras cabem folgadamente no teto de 30 páginas — o GRP02 tem 29
figuras em 24 páginas.

---

## Pendências que dependem de terceiros

| # | O que falta | Bloqueia |
|---|---|---|
| 1 | Prenomes de FERREIRA/MOTA e SILVA/ARAÚJO | Referências (ABNT inválida sem eles) |
| 2 | Autores, título e ano de GRP03 e GRP04 | 2.3 Trabalhos relacionados |
| 3 | Referência de metodologia científica do curso | Abertura da seção 3 |
| 4 | Titulação e nome do orientador | Front matter |
| 5 | Aval do orientador à pergunta de pesquisa de 1.1 | 1.1, e por tabela 1.2 e a seção 5 |
| 6 | Exportar o DER de `database/der-diagram.mwb` como imagem | Figura 3 (seção 3.3.1) |
| 7 | Capturas das telas principais da aplicação | Figura 4 (seção 3.5.6) |
