# Benchmark do lote do motor — T-54

> Gerado por `ml-service/benchmark_motor.py`. Mede N chamadas `/predict` sequenciais,
> que é o custo dominante do lote `POST /api/motor/recalcular` (ver docstring do script).

- **Data:** 2026-08-30 20:24
- **ml-service:** http://localhost:8000
- **Histórico por produto:** 365 dias (sintético, semente 42)
- **Prophet ativo:** ✅ sim

| Nº produtos | Tempo total | Médio/produto | Mediana | Máx/produto | Chamadas > 30 s | Falhas |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | 22.2 s (0.4 min) | 0.44 s | 0.43 s | 0.97 s | 0 | 0 |
| 150 | 63.6 s (1.1 min) | 0.42 s | 0.41 s | 0.91 s | 0 | 0 |
| 300 | 159.6 s (2.7 min) | 0.53 s | 0.50 s | 1.08 s | 0 | 0 |

## Como interpretar

- **Tempo total** é o que o lojista esperaria numa requisição síncrona única.
  Regra prática: se para 300 produtos ficar em poucos segundos, o lote síncrono
  basta e o **Épico 7 vira `MVP-opcional`**; se der minutos, o async é **`MVP`**.
- **Chamadas > 30 s** indicam produtos que estourariam o `read-timeout` do Feign
  em produção (falhariam individualmente no lote real).
- **Prophet ativo** precisa ser ✅; se ❌, rode de novo após instalar o CmdStan
  (SESSION.md), senão o custo real do modelo mais caro fica de fora.

## Conclusão

**Ambiente da medição:** máquina de desenvolvimento (12 CPUs lógicas), ml-service rodando fora do
Docker, via `uvicorn` com 1 worker. O benchmark é **sequencial** — vale o desempenho de um núcleo,
não a contagem de núcleos.

**O custo por produto é ~4x menor que a estimativa documentada.** O
`infraestrutura-nuvem.md` (R1) trabalhava com 1–5 s/produto e projetava **5 a 25 minutos** para
~312 SKUs. Medido: **0,42–0,53 s/produto**, com escala linear e projeção de **~2,8 min** para 312
SKUs. Nenhuma chamada passou de 1,1 s — ou seja, **zero risco** para o `read-timeout` de 30 s do
Feign, que era um risco aberto no relatório.

**Prophet ativo em 100% das chamadas** (`holt_winters: 500, prophet: 500`, 0 falhas). Os números
refletem o custo dos dois modelos, não um fallback silencioso — que é exatamente o que invalidaria
a comparação, núcleo acadêmico do TCC.

### Épico 7 (motor assíncrono) — leitura sugerida

Pela regra do próprio script, 2,7 min para 300 produtos é "minutos", e o Épico 7 **continua
justificado**. Mas a natureza do problema muda: de **bloqueador** para **melhoria de experiência**.

- Uma espera de ~3 min numa demonstração para a banca é constrangedora, não fatal.
- Uma espera de 25 min seria inviável — e era esse cenário que travava a decisão.
- O Caddy não impõe timeout de resposta (§9.5), então a requisição longa atravessa em qualquer um
  dos dois casos.

Sugestão: manter o Épico 7 como **MVP-opcional** — implementar se sobrar tempo depois da trilha B
(integração do frontend), que é o caminho crítico real do produto.

> ⚠️ **Este número não é o da t3.medium.** A instância tem 2 vCPU *burstable*, e o benchmark é
> sequencial: o que importa é o desempenho de núcleo único, onde a t3 fica bem atrás de um desktop
> moderno. Projeção grosseira: **5 a 8 min** para 312 SKUs na EC2, com risco adicional de
> *throttling* se o `CPUCreditBalance` zerar (§6.2). **A medição que fecha esta conclusão é a D-35**
> (cronometrar o lote real na instância), com o `CPUCreditBalance` monitorado em paralelo (D-42).
