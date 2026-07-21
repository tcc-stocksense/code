# Análise e validação empírica dos modelos — StockSense (TCC)

Camada de análise acadêmica do motor preditivo. Demonstra, de forma reprodutível,
**por que** o motor escolhe um modelo (Holt-Winters × Prophet) por produto e
**prova** que a previsão funciona — com gráficos de ajuste, erro e resíduos.

> Princípio: o material **reaproveita o código de produção** (`app/services/...`).
> As métricas (MAPE/RMSE/MAE) são idênticas às do endpoint `/predict`, porque saem
> do mesmo código — não há fórmula reimplementada aqui.

## Conteúdo

```
analysis/
├── analise_modelos.ipynb        # notebook principal (11 seções — ver abaixo)
├── analysis_utils.py            # helpers que reusam os internos dos serviços
├── requirements-analysis.txt    # deps SÓ de análise (fora do runtime do serviço)
├── data/                        # coloque aqui o dataset real: vendas_real.xlsx
├── figures/                     # PNGs gerados (prontos para colar no TCC)
└── results/
    └── comparativo_modelos.csv  # MAPE/RMSE/MAE por produto × modelo + vencedor
```

## Como rodar

A partir da raiz do `ml-service`:

```bash
# 1. dependências do serviço + as de análise
pip install -r requirements.txt -r analysis/requirements-analysis.txt

# 2. abrir o notebook
jupyter lab analysis/analise_modelos.ipynb
# (ou executar em lote:)
jupyter nbconvert --to notebook --execute --inplace analysis/analise_modelos.ipynb
```

O notebook usa **dados sintéticos reprodutíveis** (gerador do projeto, seed 42) —
não precisa de arquivo externo para rodar.

## Roteiro (passos de uma análise de dados com ML)

O notebook segue o ciclo CRISP-DM adaptado a séries temporais:

1. Entendimento do problema · 2. Coleta/entendimento dos dados · 3. EDA
(decomposição) · 4. Pré-processamento · 5. Divisão temporal walk-forward
(nunca aleatória) · 6. Treinamento · 7. Avaliação (MAPE/RMSE/MAE + resíduos) ·
8. Justificativa da decisão · 9. Aplicação de negócio (ES, ponto de reposição,
dias até ruptura) · 10. Limitações · 11. Reprodutibilidade.

## Gráficos gerados (`figures/`)

| Arquivo | O que prova |
|---|---|
| `g1_decomposicao_*` | Há sinal previsível (tendência + sazonalidade semanal) |
| `g2_previsto_real_*` | Ajuste do modelo fora da amostra (previsto × real) |
| `g3_barras_erro_*` | Comparativo MAPE/RMSE/MAE (espelha a Tela 10) |
| `g4_erro_horizonte_*` | Como o erro cresce ao prever mais dias à frente |
| `g5_residuos_*` | Resíduo ≈ ruído branco (modelo capturou o sinal) |
| `g6_backtesting_*` | Robustez em várias janelas (não foi sorte) |
| `g7_reposicao_*` | Da previsão à decisão: estoque × ponto de reposição × ruptura |

## Dataset real (opcional)

Deposite a planilha real em `analysis/data/vendas_real.xlsx`, no formato da
planilha `5_vendas` do Guia de Importação (colunas `produto_id`, `data_hora`,
`quantidade`). A última seção do notebook repete a avaliação sobre ela. Sem o
arquivo, essa seção é **pulada** com aviso.

## ⚠️ Prophet (T-12)

O comparativo completo exige o Prophet funcionando. Se, ao rodar o notebook, a
saída indicar `Prophet disponível: False`, o backend do Prophet (CmdStan) está
quebrado no ambiente — erro `'Prophet' object has no attribute 'stan_backend'`.
Conserto (instalação de dependência, **não** alteração de código):

```bash
python -c "import cmdstanpy; cmdstanpy.install_cmdstan(overwrite=True)"
```

> Esse download vem do GitHub e pode estar bloqueado em ambientes com política de
> rede restritiva (ex.: sandbox de CI). Rode num ambiente com acesso ao GitHub.

Enquanto o Prophet estiver indisponível, o notebook roda **apenas com Holt-Winters**
e sinaliza a limitação — nenhuma célula quebra.
