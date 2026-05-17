# CLAUDE.md — Motor de Otimização Preditiva de Estoque
> Arquivo de contexto do projeto para o Claude Code. Leia este arquivo integralmente antes de qualquer ação.

---

## 1. Visão Geral do Projeto

**Nome:** Motor de Otimização Preditiva e Análise de Estoque para Pequenos e Médios Mercados de Bairro  
**Tipo:** Trabalho de Conclusão de Curso (TCC) — Sistemas de Informação  
**Ano:** 2026  

**Objetivo:** Desenvolver um sistema web que substitui a gestão manual de estoque por uma solução orientada a dados. O sistema prevê a demanda futura por produto, calcula automaticamente o ponto de reposição e emite alertas de ruptura para gestores de mercadinhos de bairro — usuários sem perfil técnico.

**Problema resolvido:**
- Ruptura de estoque: produto acaba antes da reposição → perda de vendas
- Excesso de perecíveis: mercadorias vencendo → desperdício financeiro e ambiental
- Exclusão tecnológica: pequenos lojistas não têm acesso a sistemas preditivos

---

## 2. Equipe

| Nome | RA | Responsabilidade principal |
|---|---|---|
| Danilo Silvestre Faustino | 03231045 | — |
| Gabriel Boos Duarte | 03231030 | — |
| Gabriel Sanchez | 03231004 | — |
| Pedro Primon | 0323014 | — |
| Pedro Paulo Pinto | 0323015 | — |

---

## 3. Arquitetura do Sistema (C4 — Nível 2: Containers)

O sistema é composto por **4 containers** dentro de um único sistema chamado "Motor Preditivo de Estoque":

```
Lojista (usuário)
    │
    │ HTTPS (navegador)
    ▼
┌─────────────────────────────────────────────┐
│           Motor Preditivo de Estoque        │
│                                             │
│  ┌──────────────┐                           │
│  │   Web App    │  HTML / CSS / JS          │
│  │  (Frontend)  │  Upload CSV, dashboards,  │
│  │              │  alertas de reposição      │
│  └──────┬───────┘                           │
│         │ HTTPS / JSON                      │
│  ┌──────▼───────┐                           │
│  │     API      │  Kotlin / Spring Boot      │
│  │  Application │  Orquestrador central:    │
│  │              │  valida uploads, aciona   │
│  │              │  AI/ML, persiste dados    │
│  └──────┬───────┘                           │
│         │ HTTP / JSON — POST /predict        │
│  ┌──────▼───────┐     ┌──────────────────┐  │
│  │  AI/ML       │     │   Banco de Dados │  │
│  │  Service     │────▶│     MySQL        │  │
│  │ Python/      │JDBC │                  │  │
│  │ FastAPI      │     │ vendas, previsões,│  │
│  └──────────────┘     │ produtos, KPIs   │  │
│                       └──────────────────┘  │
└─────────────────────────────────────────────┘
```

### Responsabilidades por container

**Web App (Frontend — HTML/CSS/JS)**
- Upload do arquivo CSV/XLSX com histórico de vendas
- Dashboard com alertas de reposição por produto (semáforo 🟢🟡🔴)
- Visualização da Curva ABC
- Comparação de acurácia dos modelos (Holt-Winters vs Prophet)
- Registro manual de perdas de estoque (vencimento, avaria, furto)
- Relatório de dias até ruptura por produto
- Interface simples, sem exigir perfil técnico do usuário

**API Application (Kotlin / Spring Boot)**
- Orquestrador central de todo o sistema
- Recebe e valida arquivos de importação (planilhas)
- Aciona o AI/ML Service via requisição HTTP (POST /predict)
- Persiste os resultados nas tabelas `produto` e `previsao`
- Expõe endpoints REST consumidos pelo frontend
- Agendamento via cron: recalcula previsões uma vez ao mês automaticamente
- Popula valores padrão quando planilhas desejáveis não são enviadas:
  - `lead_time_medio = 3 dias`
  - `variabilidade_lead_time = 1.0`

**AI/ML Service (Python / FastAPI)**
- Motor preditivo principal
- Processa histórico de vendas importado via CSV
- Implementa e **compara empiricamente** dois modelos de séries temporais:
  - **Holt-Winters** (suavização exponencial tripla)
  - **Prophet** (Facebook/Meta)
- Calcula métricas de acurácia: **MAPE, RMSE, MAE**
- Seleciona o modelo de melhor desempenho por produto
- Calcula: ranking ABC, desvio padrão da demanda, estoque de segurança, ponto de reposição, dias até ruptura
- Retorna resultados via JSON para a API Application

**Banco de Dados (MySQL)**
- Armazena: histórico de vendas, previsões geradas, parâmetros por produto, resultados do motor
- Os resultados do motor são **persistidos após cada execução** — o frontend consome dados já calculados, sem chamadas em tempo real ao Python

---

## 4. Stack Tecnológica

| Camada | Tecnologia | Versão mínima |
|---|---|---|
| Frontend | HTML5 / CSS3 / JavaScript (Vanilla ou leve framework) | — |
| Backend / API | Kotlin + Spring Boot | Java 17+ |
| HTTP Client (backend) | OpenFeign (Spring Cloud OpenFeign) | — |
| Motor preditivo | Python + FastAPI | Python 3.10+ |
| Modelos preditivos | statsmodels (Holt-Winters), Prophet (Meta) | — |
| Banco de dados | MySQL | 8.0+ |
| Driver JDBC | MySQL Connector/J | — |
| ORM / acesso a dados | Spring Data JPA (Kotlin) | — |
| Comunicação interna | REST HTTP / JSON | — |
| Hospedagem | AWS Free Tier ou similar | — |
| Controle de versão | Git + GitHub | — |

---

## 5. Modelo de Dados

### Entidades principais (baseadas no Guia de Importação v2.0)

#### `estabelecimento`
| Campo | Tipo | Obrigatoriedade |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Auto |
| nome_fantasia | VARCHAR(100) | Obrigatório |
| cnpj | VARCHAR(18) | Opcional |
| endereco | VARCHAR(200) | Opcional |

#### `produto`
| Campo | Tipo | Obrigatoriedade |
|---|---|---|
| produto_id | INTEGER PK | Obrigatório (gestor define) |
| nome | VARCHAR(100) | Obrigatório |
| estoque_atual | INTEGER | Obrigatório |
| categoria | VARCHAR(50) | Recomendado |
| unidade_medida | VARCHAR(10) | Recomendado |
| preco_custo | DECIMAL(10,2) | Recomendado |
| preco_venda | DECIMAL(10,2) | Recomendado |
| nivel_servico_alvo | DECIMAL(5,2) | Opcional (padrão: 0.95) |
| classe_abc | CHAR(1) | **Calculado pelo motor** |
| desvio_padrao_demanda | DECIMAL(10,4) | **Calculado pelo motor** |
| ponto_reposicao | DECIMAL(10,2) | **Calculado pelo motor** |
| estoque_seguranca | DECIMAL(10,2) | **Calculado pelo motor** |
| data_ultimo_calculo | TIMESTAMP | **Calculado pelo motor** |

> ⚠️ Os campos calculados **nunca** devem ser enviados pelo usuário via planilha.

#### `fornecedor`
| Campo | Tipo | Obrigatoriedade |
|---|---|---|
| fornecedor_id | INTEGER PK | Obrigatório (se enviado) |
| nome | VARCHAR(100) | Obrigatório (se enviado) |
| contato | VARCHAR(50) | Opcional |

#### `produto_fornecedor` (tabela associativa)
| Campo | Tipo | Notas |
|---|---|---|
| produto_id | FK → produto | — |
| fornecedor_id | FK → fornecedor | — |
| lead_time_medio | INTEGER | Dias entre pedido e entrega. Padrão backend: 3 |
| variabilidade_lead_time | DECIMAL(10,4) | Desvio padrão do lead time. Padrão: 1.0 |

#### `venda`
| Campo | Tipo | Obrigatoriedade |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Auto |
| produto_id | FK → produto | Obrigatório |
| data_hora | TIMESTAMP | Obrigatório (formato: YYYY-MM-DD) |
| quantidade | INTEGER | Obrigatório (> 0) |
| valor_venda | DECIMAL(10,2) | Recomendado (necessário para Curva ABC) |
| is_promocional | SMALLINT (0/1) | Opcional (melhora Prophet). Padrão: 0 |

#### `previsao`
| Campo | Tipo | Notas |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Auto |
| produto_id | FK → produto | — |
| data_previsao | DATE | Data para qual a previsão se refere |
| quantidade_prevista | DECIMAL(10,2) | — |
| modelo_utilizado | VARCHAR(50) | 'holt_winters' ou 'prophet' |
| mape | DECIMAL(8,4) | Métrica de erro do modelo |
| rmse | DECIMAL(10,4) | Métrica de erro do modelo |
| mae | DECIMAL(10,4) | Métrica de erro do modelo |
| executado_em | TIMESTAMP | Data/hora da execução do motor |

#### `perda_estoque` (módulo ESG — opcional)
| Campo | Tipo | Notas |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Auto |
| produto_id | FK → produto | — |
| quantidade | INTEGER | > 0 |
| motivo | VARCHAR(50) | vencimento, avaria, furto, excesso |
| data_perda | DATE | Formato: YYYY-MM-DD |

---

## 6. KPIs e Regras de Negócio do Motor Preditivo

### KPIs Ativos (MVP)

| KPI | Fórmula / Lógica | Onde é calculado |
|---|---|---|
| **MAPE** | `mean(|real - previsto| / real) * 100` | AI/ML Service (Python) |
| **RMSE** | `sqrt(mean((real - previsto)²))` | AI/ML Service (Python) |
| **MAE** | `mean(|real - previsto|)` | AI/ML Service (Python) |
| **Classificação ABC** | Ranking por % acumulado do faturamento: A=top 80%, B=80-95%, C=95-100% | AI/ML Service (Python) |
| **Estoque de Segurança** | `Z * sqrt(lead_time * σ²_demanda + demanda² * σ²_lead_time)` | AI/ML Service (Python) |
| **Nível de Serviço** | Z-score por produto (padrão: 95% → Z=1.645) | AI/ML Service (Python) |
| **Dias até Ruptura** | `estoque_atual / demanda_media_diaria_prevista` | AI/ML Service (Python) |
| **Ponto de Reposição** | `demanda_media * lead_time_medio + estoque_seguranca` | AI/ML Service (Python) |

### KPIs Em Análise (aproximação no MVP)

| KPI | Aproximação MVP | Limitação |
|---|---|---|
| **Giro de Estoque** | `CMV ÷ estoque_atual` | Precisão depende de snapshot histórico diário |
| **Redução de Desperdício (ESG)** | Volume em `perda_estoque` | Qualidade depende de preenchimento manual pelo gestor |

### Alertas de Reposição (semáforo)
- 🟢 **Verde:** `dias_ate_ruptura > ponto_reposicao * 1.5` — estoque confortável
- 🟡 **Amarelo:** `ponto_reposicao <= dias_ate_ruptura <= ponto_reposicao * 1.5` — atenção
- 🔴 **Vermelho:** `dias_ate_ruptura < ponto_reposicao` — repor imediatamente

---

## 7. Endpoints da API (Spring Boot)

> Endpoints planejados — implementar conforme necessidade de cada fase.

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/importacao/produtos` | Upload da planilha de produtos |
| POST | `/api/importacao/vendas` | Upload do histórico de vendas |
| POST | `/api/importacao/fornecedores` | Upload de fornecedores (desejável) |
| POST | `/api/motor/executar` | Dispara o motor preditivo manualmente |
| GET | `/api/produtos` | Lista todos os produtos com KPIs calculados |
| GET | `/api/produtos/{id}/previsao` | Previsão de demanda de um produto |
| GET | `/api/dashboard/alertas` | Lista produtos com alertas de reposição |
| GET | `/api/dashboard/abc` | Curva ABC dos produtos |
| GET | `/api/dashboard/acuracia` | Comparação Holt-Winters vs Prophet |
| POST | `/api/perdas` | Registra perda de estoque (ESG) |

---

## 8. Endpoint do AI/ML Service (FastAPI)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/predict` | Recebe histórico de vendas, retorna previsões e métricas |
| GET | `/health` | Health check do serviço |

**Payload de entrada (`POST /predict`):**
```json
{
  "produto_id": 1,
  "historico": [
    {"data": "2025-01-01", "quantidade": 15},
    {"data": "2025-01-02", "quantidade": 12}
  ],
  "lead_time_medio": 3,
  "variabilidade_lead_time": 1.0,
  "nivel_servico_alvo": 0.95,
  "estoque_atual": 40
}
```

**Payload de saída:**
```json
{
  "produto_id": 1,
  "modelo_selecionado": "holt_winters",
  "previsoes": [
    {"data": "2025-04-01", "quantidade_prevista": 14.3}
  ],
  "metricas": {
    "holt_winters": {"mape": 8.2, "rmse": 2.1, "mae": 1.8},
    "prophet": {"mape": 10.5, "rmse": 2.7, "mae": 2.3}
  },
  "ponto_reposicao": 52.0,
  "estoque_seguranca": 10.0,
  "dias_ate_ruptura": 18,
  "classe_abc": "A"
}
```

---

## 9. Fluxo de Importação de Dados

O sistema aceita dados em planilhas `.xlsx`. Há 6 planilhas possíveis:

| Planilha | Entidade | MVP | Descrição |
|---|---|---|---|
| `1_estabelecimento` | Estabelecimento | Desejável | Dados cadastrais do mercado |
| `2_produtos` | Produto | **Obrigatório** | Catálogo com preços e estoque atual |
| `3_fornecedores` | Fornecedor | Desejável | Fornecedores do estabelecimento |
| `4_produto_fornecedor` | Produto × Fornecedor | Desejável | Lead time real por produto |
| `5_vendas` | Venda | **Obrigatório** | Histórico de vendas (mín. 90 dias) |
| `6_perdas_estoque` | Perda | Opcional | Perdas por vencimento/avaria/furto |

**Valores padrão quando planilhas desejáveis não são enviadas:**
- `lead_time_medio = 3`
- `variabilidade_lead_time = 1.0`
- Fornecedor padrão mockado pelo backend

**Formatos aceitos:**
- Datas: `YYYY-MM-DD` (ISO 8601) — nunca `DD/MM/AAAA`
- Decimais: ponto como separador (`12.50`) — nunca vírgula
- Booleanos: `0` ou `1`

---

## 10. Ordem de Desenvolvimento Recomendada

### Fase 1 — Fundação (Fev–Abr 2026)
- [ ] Modelagem do banco de dados MySQL (DDL completo)
- [ ] Setup do projeto Spring Boot (estrutura de pacotes, dependências)
- [ ] Configurar dependência do OpenFeign no `build.gradle.kts`
- [ ] Setup do projeto FastAPI (estrutura de pastas, dependências)
- [ ] Setup do frontend (estrutura HTML/CSS básica)
- [ ] Confirmar parceiro com dados reais

### Fase 2 — Gestão de Dados (Abr–Jun 2026)
- [ ] Endpoints de importação das planilhas (Spring Boot)
- [ ] Parser e validador de planilhas XLSX
- [ ] Módulo de entradas e saídas de estoque
- [ ] Análise exploratória dos dados reais (Python / Jupyter)
- [ ] Tratamento e limpeza do histórico de vendas

### Fase 3 — Motor Preditivo (Jun–Ago 2026)
- [ ] Implementação de Holt-Winters (statsmodels)
- [ ] Implementação de Prophet (Meta)
- [ ] Cálculo de MAPE, RMSE, MAE para cada modelo
- [ ] Lógica de seleção do melhor modelo por produto
- [ ] Cálculo de: Classificação ABC, Estoque de Segurança, Ponto de Reposição, Dias até Ruptura
- [ ] Endpoint `POST /predict` do FastAPI
- [ ] Integração Spring Boot → FastAPI via Feign Client (`MlServiceClient`)

### Fase 4 — Interface e Integração (Ago–Set 2026)
- [ ] Dashboard de alertas de reposição (semáforo)
- [ ] Dashboard de Curva ABC
- [ ] Dashboard de comparação de acurácia dos modelos
- [ ] Upload de planilhas via interface web
- [ ] Agendamento mensal via cron (Spring Boot)
- [ ] Módulo ESG (alertas de vencimento) — desejável

### Fase 5 — Validação e TCC (Set–Out 2026)
- [ ] Testes com dados reais do parceiro
- [ ] Cálculo dos indicadores de impacto
- [ ] Testes de sistema end-to-end
- [ ] Elaboração do artigo do TCC

---

## 11. Convenções e Regras do Projeto

### Gerais
- Sempre use inglês para nomes de variáveis, funções, classes e tabelas
- Use português apenas em comentários de negócio e mensagens de log
- Todos os commits devem ter mensagem em português descrevendo o que foi feito
- Nunca commite credenciais, API keys ou senhas — use variáveis de ambiente

### Python (AI/ML Service)
- Estrutura de pastas: `app/`, `models/`, `services/`, `schemas/`, `tests/`
- Use `pandas` para manipulação de dados, `numpy` para cálculos
- Funções de previsão devem retornar sempre o mesmo schema JSON
- Implemente tratamento de exceção para séries com dados insuficientes (< 90 dias)
- Docstrings obrigatórias em todas as funções do motor preditivo

### Kotlin / Spring Boot
- Use arquitetura em camadas: `controller` → `service` → `repository`
- DTOs separados das entidades JPA
- Validação de dados de entrada com Bean Validation (`@NotNull`, `@Min`, etc.)
- Logs em todos os pontos de integração com o AI/ML Service
- Respostas de erro padronizadas com `ProblemDetail` (RFC 7807)
- **Feign Client:** declarar interface `MlServiceClient` com `@FeignClient(name = "ml-service", url = "\${ml.service.url}")`
  - URL do AI/ML Service via variável de ambiente (`ML_SERVICE_URL`) — nunca hardcoded
  - Configurar timeout no Feign: `connectTimeout` e `readTimeout` para chamadas ao Python
  - Tratar `FeignException` no service e retornar erro amigável ao frontend

### Frontend
- Sem frameworks pesados — HTML/CSS/JS vanilla ou biblioteca leve
- Interface deve funcionar sem perfil técnico do usuário
- Mensagens de erro em português, amigáveis ao gestor
- Upload de planilha com feedback visual de progresso

### Banco de Dados (MySQL)
- Nomes de tabelas em `snake_case` no singular
- Toda tabela deve ter `id INT AUTO_INCREMENT PRIMARY KEY` (exceto associativas)
- Charset padrão: `utf8mb4`, Collation: `utf8mb4_unicode_ci` — declarar em todas as tabelas
- Migrations versionadas com Flyway (prefixo `V1__`, `V2__`, etc.)
- Nunca altere uma migration já commitada — crie uma nova
- Usar `DATETIME` para timestamps (não `TIMESTAMP`, que tem limitação de fuso horário no MySQL)
- Não usar `SERIAL` — sintaxe PostgreSQL; no MySQL usar `INT AUTO_INCREMENT`

---

## 12. O que NÃO fazer

- ❌ Não criar endpoints sem validação de entrada
- ❌ Não retornar stack traces completos para o frontend (log interno, resposta amigável para o usuário)
- ❌ Não chamar o AI/ML Service de forma síncrona em operações longas sem timeout configurado no Feign
- ❌ Não hardcodar a URL do AI/ML Service — usar variável de ambiente `ML_SERVICE_URL`
- ❌ Não usar sintaxe PostgreSQL no MySQL (`SERIAL`, `SERIAL PRIMARY KEY`) — usar `INT AUTO_INCREMENT`
- ❌ Não omitir `utf8mb4` no DDL — MySQL usa `latin1` por padrão, que não suporta caracteres especiais
- ❌ Não permitir que o usuário envie os campos calculados pelo motor (`classe_abc`, `ponto_reposicao`, etc.) via planilha
- ❌ Não aceitar datas no formato `DD/MM/AAAA` — rejeitar e retornar erro claro
- ❌ Não treinar modelos com menos de 90 dias de histórico — retornar aviso ao usuário
- ❌ Não hardcodar o `nivel_servico_alvo` — deve vir do cadastro do produto (padrão: 0.95)

---

## 13. Referências Bibliográficas do Projeto

- BALLOU, Ronald H. *Gerenciamento da cadeia de suprimentos / Logística empresarial.* 5. ed. Porto Alegre: Bookman, 2006. *(Estoque de Segurança e Nível de Serviço)*
- SEBRAE. *Ideia de Negócio: Mercearia.* Brasília: Sebrae, 2023. *(Classificação ABC)*
- SILVA; ARAÚJO. *Gestão de estoques em um supermercado de médio porte.* UTFPR, 2022. *(Curva ABC aplicada)*

---

*Este arquivo deve ser atualizado sempre que houver mudanças arquiteturais, de stack ou de regras de negócio relevantes.*
