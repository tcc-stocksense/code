# CLAUDE.md — Raiz do Monorepo (StockSense)

> ⚠️ **Arquivo reconstruído.** O CLAUDE.md original da raiz não estava disponível; este foi montado a partir dos diagramas C4, dos CLAUDE.md de backend e ml-service, do Guia de Importação e do mapeamento das telas. **Valide contra o que vocês já tinham** e ajuste convenções que eu não tinha como conhecer (padrão de commits, scripts de build, gerenciador do monorepo, etc.). Itens marcados como *(suposição)* precisam de confirmação.

As convenções gerais aqui **prevalecem** sobre as dos serviços. Cada serviço tem seu próprio `CLAUDE.md` com as regras específicas — leia o da raiz primeiro, depois o do serviço.

---

## 1. O que é o StockSense

Motor de otimização preditiva de estoque para **pequenos e médios mercados de bairro**. A partir do histórico de vendas, prevê a demanda por produto, calcula ponto de reposição e dias até ruptura, compara modelos de série temporal (Holt-Winters × Prophet) e gera alertas de reposição — substituindo a gestão manual e intuitiva por decisão orientada a dados.

Ator principal: o **Lojista** (gestor do mercadinho), que acessa via navegador. Fontes de dados: planilhas `.xlsx` exportadas pelo estabelecimento.

---

## 2. Estrutura do Monorepo *(suposição — confirmar nomes de pasta)*

```
stocksense/
├── CLAUDE.md                 ← este arquivo (convenções globais)
├── docker-compose.yml        ← sobe backend + ml-service + MySQL local  (suposição)
│
├── backend/                  ← Kotlin / Spring Boot (orquestrador, dono do banco)
│   ├── CLAUDE.md
│   └── src/main/resources/db/migration/   ← migrations Flyway (V1, V2, ...)
│
├── ml-service/               ← Python / FastAPI (motor preditivo, stateless)
│   └── CLAUDE.md
│
└── web/                      ← HTML / CSS / JS (interface do lojista)   (suposição)
```

---

## 3. Arquitetura e Fluxo entre Serviços (C4 Nível 2)

```
Lojista ──navegador──> Web App ──HTTPS/JSON──> API (Spring Boot) ──HTTP/JSON──> ML Service (FastAPI)
                                                     │  POST /predict ─────────────┘
                                                     │
                                                     └──JDBC/SQL──> MySQL
```

Regras de fluxo que **não podem ser violadas**:
- O **frontend nunca chama o ml-service diretamente** — só fala com a API.
- O **ml-service é stateless**: recebe JSON, devolve JSON, **não acessa banco**. Quem persiste é o backend.
- O backend é o **único dono do banco** (todas as escritas passam por ele).
- A API é **orquestradora**: valida importações, aciona o motor, persiste resultados e expõe os endpoints consumidos pelo front.

---

## 4. Stack por Componente

| Componente | Tecnologia | Papel |
|---|---|---|
| Web App | HTML / CSS / JS | Interface do lojista (upload, dashboards, alertas) |
| API | Kotlin 1.9.25 / Spring Boot 3.3.4 / JVM 17 | Orquestração, regras de negócio, persistência, ABC, login |
| ML Service | Python 3.10+ / FastAPI | Holt-Winters, Prophet, KPIs de estoque (stateless) |
| Banco | MySQL 8.0 | Histórico, previsões, métricas, parâmetros |
| Migrations | Flyway (`flyway-mysql`) | Versionamento do schema (gerido pelo backend) |

---

## 5. Convenções Globais

- **Idioma do domínio:** português. Tabelas, colunas e nomes de domínio em PT-BR (`produto`, `estoque_atual`, `previsao`).
- **Banco:** `snake_case`. **Código Kotlin/Python:** `camelCase` / `snake_case` conforme a linguagem.
- **Contrato entre serviços:** HTTP/JSON. O contrato do `/predict` é a fronteira backend↔ML — mudou de um lado, atualiza o outro e a versão.
- **Configuração:** nunca hardcodar URLs, portas ou credenciais — sempre variável de ambiente (`${ml.service.url}`, `.env`).
- **Segredos:** nunca commitar `.env` real nem senha/hash real (seeds usam placeholder).
- **Datas:** ISO 8601 (`YYYY-MM-DD`). Decimais com ponto.

---

## 6. Banco de Dados

- SGBD único: **MySQL 8.0** (decisão registrada — ver §9). Não há PostgreSQL no projeto; diagramas antigos que citavam Postgres estão desatualizados.
- Migrations vivem em `backend/src/main/resources/db/migration/`. `V1` está **congelado**; toda mudança é `V{n}` nova.
- Propriedade dos dados é do backend. O ml-service nunca toca o banco.

---

## 7. Prioridade MVP — visão de sistema

Escopo de entrega do TCC. Telas marcadas como **MVP** formam o produto mínimo defensável; **Pós-MVP** ficam para versão futura.

| Tela / Funcionalidade | Prioridade |
|---|---|
| T1 — Login (no estabelecimento) | **MVP** |
| T3 — Importação de planilhas (produtos + vendas) | **MVP** |
| T4 — Estoque (listar + editar) | **MVP** |
| T6 — Detalhe do produto (estatísticas + reposição) | **MVP** |
| T7 — Curva ABC | **MVP** |
| T10 — Comparativo de modelos (HW × Prophet) — núcleo acadêmico | **MVP** |
| T2 — Dashboard (KPIs + projeção) | **MVP** |
| T5 — Alertas de reposição | **MVP** |
| T8 — Sugestão de compra (PDF/WhatsApp) | **Pós-MVP** |
| T9 — Configurações completas / notificações | **Pós-MVP** |
| Importação completa (estabelecimento, fornecedores, produto×fornecedor) | **Pós-MVP** |
| Módulo ESG / controle de validade | **Fora do escopo** |

> A separação de perfil "Gestor × Equipe Técnica" e o módulo ESG foram retirados do MVP. O ESG saiu por completo (sem `perda_estoque`, sem KPI de desperdício).

---

## 8. Como rodar localmente *(suposição — ajustar ao real)*

```bash
# Sobe MySQL, backend e ml-service
docker-compose up

# Migrations Flyway rodam na subida do backend.
# ml-service em http://localhost:8000  |  API em http://localhost:8080  (portas a confirmar)
```

Variáveis essenciais: `ml.service.url` (backend → ML), credenciais do MySQL, `ML_SERVICE_PORT`.

---

## 9. Decisões de Arquitetura (ADRs resumidos)

Registre essas decisões no TCC — demonstram maturidade de engenharia.

| # | Decisão | Justificativa |
|---|---|---|
| 1 | **MySQL 8.0** como SGBD único | Schema e padrões do backend já em MySQL; elimina o conflito com diagramas que citavam Postgres |
| 2 | **ml-service stateless** (não persiste) | Reduz acoplamento; backend é o único dono do banco |
| 3 | **Classificação ABC no backend** | ABC é ranking relativo entre todos os produtos; o `/predict` é por produto e não vê o catálogo |
| 4 | **Login no estabelecimento** (sem tabela `usuario`) | Login não é o foco; uma credencial por mercado basta no MVP |
| 5 | **Preparado para multi-estabelecimento** | `estabelecimento_id` em `produto`, embora só 1 mercado seja cadastrado |
| 6 | **ESG fora do escopo** | Reduz superfície de entrega; `perda_estoque` removida |
| 7 | **previsao / metrica_modelo separadas** | Pontos diários e métricas por modelo têm cardinalidades diferentes; suporta a T10 |

---

## 10. O que NUNCA fazer (cross-cutting)

- ❌ Frontend chamando o ml-service direto — sempre via API.
- ❌ ml-service acessando banco — ele é stateless.
- ❌ Reintroduzir PostgreSQL ou ESG/`perda_estoque` sem revisar estas decisões.
- ❌ Editar `V1__create_schema.sql` — está congelado; use `V{n}`.
- ❌ Commitar segredos (`.env`, senha/hash real).
- ❌ Mudar o contrato `/predict` em um serviço sem atualizar o outro.

---

*Atualizar este arquivo quando uma decisão de arquitetura mudar ou um serviço/contrato for adicionado.*

## Especificações detalhadas das telas
As telas T1–T10 citadas no escopo MVP estão detalhadas em:
@docs/mapeamento-funcionalidades.md

Regras de importação de planilhas (Tela 3):
@docs/guia-importacao-dados.md

Definições de KPIs (Telas 2, 6, 7, 10):
@docs/dashboard-kpis.md
