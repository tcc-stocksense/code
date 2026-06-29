# Métricas e Dashboards (KPIs)

> **Motor de Otimização Preditiva de Estoque (StockSense) · Mercados de Bairro · 2026**

> ⚠️ **Status / fonte de verdade.** Este documento consolida os KPIs do motor. Em caso de conflito, o `CLAUDE.md` da raiz prevalece. **Atenção a duas divergências herdadas:** (1) o KPI **Redução de Desperdício (ESG)** e a planilha de perdas foram **removidos do escopo** — ignorar; (2) a separação de personas **Gestor × Equipe Técnica** foi retirada do MVP (login único por estabelecimento) — as visões abaixo descrevem agrupamentos de tela, não perfis de acesso distintos.

Este documento integra a fundamentação teórica com os requisitos técnicos do projeto.

**Legenda de status dos KPIs:**

- **Ativo** — implementado e suportado pelo modelo de dados do MVP.
- **Em análise** — relevante, mas com restrições no MVP; implementado com aproximação documentada ou evoluído em versão futura.
- **Desejável** — alto valor, dependente de funcionalidades além do escopo atual.

---

## 1. KPIs estratégicos e operacionais

| Indicador | Descrição | Finalidade técnica / gestão | Status |
|---|---|---|---|
| **Acurácia Preditiva (MAPE / RMSE / MAE)** | Diferença entre o previsto e o real vendido. | Validar e comparar Holt-Winters e Prophet empiricamente. | **Ativo** |
| **Classificação ABC** | Ranking de produtos por representatividade no faturamento (A, B, C). | Priorizar gestão e recursos nos produtos de maior impacto. | **Ativo** |
| **Estoque de Segurança** | Reserva mínima para absorver flutuações da demanda ou atrasos. | Margem contra ruptura em itens de alta variabilidade. | **Ativo** |
| **Nível de Serviço** | Probabilidade alvo de não faltar estoque (ex.: 95%). | Definir o rigor estatístico do Ponto de Reposição. | **Ativo** |
| **Dias até Ruptura** | Estimativa de dias até o estoque atingir o ponto de reposição. | Alimentar os alertas do dashboard. | **Ativo** |
| **Giro de Estoque** | Velocidade de renovação do estoque num período. | Avaliar eficiência das compras vs saída real. | **Em análise** |
| **Redução de Desperdício (ESG)** | Volume descartado por validade, avaria ou furto. | *(Fora do escopo — não implementar.)* | ~~Em análise~~ |

> **Observações sobre KPIs Em Análise:**
> - **Giro de Estoque:** no MVP, `CMV ÷ estoque_atual` (aproximação). Cálculo preciso exigiria histórico diário de snapshots de estoque. Limitação documentada na metodologia.
> - **Redução de Desperdício (ESG):** removido do escopo. *(Conteúdo original mantido apenas como histórico.)*

---

## 2. Visões por tela

> No MVP há login único por estabelecimento; as "personas" abaixo são agrupamentos de funcionalidade, não perfis de acesso separados.

**Visão operacional (dia a dia):**

- Importação do arquivo `.xlsx` com histórico de vendas.
- Consulta de alertas de reposição por produto (semáforo 🟢🟡🔴).
- Acompanhamento de dias até ruptura por produto.

**Visão estratégica (rentabilidade):**

- Acompanhamento da Curva ABC e classificação dos produtos.
- Dashboard de acurácia preditiva — comparação Holt-Winters vs Prophet.
- Giro de estoque por categoria (sujeito à disponibilidade de dados).

**Visão técnica (monitoramento do motor — T10):**

- Quadro comparativo de métricas de erro (MAPE, RMSE, MAE) por modelo.
- Histórico de execuções do motor por produto.
- Parâmetros calculados: ponto de reposição, estoque de segurança, dias até ruptura.
- Status do banco e data do último recálculo por produto.

---

## 3. Implementação e orquestração técnica

- **AI/ML Service (Python / FastAPI):** processa o histórico importado via CSV/XLSX, calcula o ranking de erro, o desvio padrão da demanda, o estoque de segurança, o ponto de reposição e os dias até ruptura por produto. Retorna os resultados via JSON para o orquestrador. *(Nota: a Classificação ABC migrou para o backend — ver `CLAUDE.md` raiz, ADR #3.)*
- **API Application (Kotlin / Spring Boot):** orquestrador central. Recebe e valida os arquivos de importação, aciona o AI/ML Service via HTTP, persiste os resultados nas tabelas `produto`, `previsao` e `metrica_modelo`, e expõe os endpoints consumidos pelo frontend. Calcula a Classificação ABC (`AbcService`).
- **Agendamento (cron):** o recálculo completo é disparado pelo Spring Boot uma vez ao mês, garantindo que alertas e KPIs reflitam a demanda mais recente.

> **Persistência dos resultados:** ponto de reposição, estoque de segurança e dias até ruptura são persistidos após cada execução. O frontend consome dados já calculados, sem chamadas em tempo real ao serviço Python a cada acesso.

---

## 4. Referências bibliográficas

- **BALLOU, Ronald H.** *Gerenciamento da cadeia de suprimentos / Logística empresarial.* 5. ed. Porto Alegre: Bookman, 2006. *(Estoque de Segurança e Nível de Serviço)*
- **SEBRAE.** *Ideia de Negócio: Mercearia.* Brasília: Sebrae, 2023. *(Classificação ABC)*
- **SILVA; ARAÚJO.** *Gestão de estoques em um supermercado de médio porte.* Triângulo Mineiro: UTFPR, 2022. *(Aplicação prática da Curva ABC)*
