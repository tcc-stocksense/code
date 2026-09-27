# -*- coding: utf-8 -*-
"""
Confere cada numero das tabelas do artigo contra o JSON gerado pela analise.

Rodar a partir da raiz do repo, sempre que o texto ou os dados mudarem:
    ml-service/venv/Scripts/python.exe docs/artigo/verificar_numeros.py saida.txt

Existe porque numero digitado a mao no texto diverge do que o codigo produz --
e foi assim que a "mediana de 49,4%" (na verdade 45,1%) foi pega, antes de ir
para o artigo. Fonte da verdade: analysis/results/dados_documento.json.
"""
import json, re, sys, io
from pathlib import Path

RAIZ = Path("ml-service/analysis/results")
d = json.loads((RAIZ / "dados_documento.json").read_text(encoding="utf-8"))
alphas = json.loads((RAIZ / "_alphas.json").read_text(encoding="utf-8"))
md = Path("docs/artigo/04-resultados.md").read_text(encoding="utf-8")

out = io.StringIO()
erros = []

def num(s):
    return float(s.strip().replace(".", "").replace(",", ".")) if "," in s else float(s.strip())

def linhas_tabela(titulo):
    """Devolve as linhas de dados da tabela cujo titulo contem `titulo`."""
    i = md.index(titulo)
    bloco = md[i:md.index("Fonte:", i)]
    return [l for l in bloco.splitlines() if l.startswith("|") and "---" not in l][1:]

# ── Tabela 3: descritiva ────────────────────────────────────────────────────
esperado = {r["produto_id"]: r for r in d["descritiva"]}
for l in linhas_tabela("Tabela 3 -"):
    c = [x.strip() for x in l.strip("|").split("|")]
    pid = int(c[0]); e = esperado[pid]
    for idx, chave in ((2, "variabilidade"), (3, "media_diaria"), (4, "desvio"), (5, "cv")):
        if abs(num(c[idx]) - e[chave]) > 1e-9:
            erros.append(f"T3 pid={pid} {chave}: md={c[idx]} json={e[chave]}")
    if abs(num(c[6].rstrip("%")) - e["pct_zeros"]) > 1e-9:
        erros.append(f"T3 pid={pid} zeros: md={c[6]} json={e['pct_zeros']}")
out.write(f"Tabela 3 (descritiva): {len(linhas_tabela('Tabela 3 -'))} linhas conferidas\n")

# ── Tabela 4: comparativo ───────────────────────────────────────────────────
comp = {(r["produto_id"], r["modelo"]): r for r in d["comparativo"]}
mapa = {"Holt-Winters": "holt_winters", "Prophet": "prophet"}
n = 0
for l in linhas_tabela("Tabela 4 -"):
    c = [x.strip() for x in l.strip("|").split("|")]
    pid = int(c[0]); modelo = mapa[c[2]]; e = comp[(pid, modelo)]
    for idx, chave in ((3, "mape"), (4, "rmse"), (5, "mae")):
        if abs(num(c[idx]) - e[chave]) > 1e-9:
            erros.append(f"T4 pid={pid} {modelo} {chave}: md={c[idx]} json={e[chave]}")
    venceu = "✔" in c[6]
    if venceu != bool(e["vencedor"]):
        erros.append(f"T4 pid={pid} {modelo} vencedor: md={venceu} json={e['vencedor']}")
    n += 1
out.write(f"Tabela 4 (metricas): {n} linhas conferidas\n")

# ── Tabela 5: margens ───────────────────────────────────────────────────────
marg = {r["nome"]: r["margem_pp"] for r in d["margens"]}
for l in linhas_tabela("Tabela 5 -"):
    c = [x.strip() for x in l.strip("|").split("|")]
    if abs(num(c[1]) - marg[c[0]]) > 1e-9:
        erros.append(f"T5 {c[0]}: md={c[1]} json={marg[c[0]]}")
out.write(f"Tabela 5 (margens): {len(linhas_tabela('Tabela 5 -'))} linhas conferidas\n")

# ── Tabela 6: ganho sobre o baseline ────────────────────────────────────────
ganho = {r["produto_id"]: r for r in d["ganho_vs_baseline"]}
for l in linhas_tabela("Tabela 6 -"):
    c = [x.strip() for x in l.strip("|").split("|")]
    pid = int(c[0]); e = ganho[pid]
    for idx, chave in ((3, "mape_vencedor"), (4, "mape_naive"), (5, "ganho_pp")):
        if abs(num(c[idx]) - round(e[chave], 2)) > 0.005:
            erros.append(f"T6 pid={pid} {chave}: md={c[idx]} json={e[chave]}")
    if abs(num(c[6].rstrip("%")) - e["ganho_rel_pct"]) > 0.05:
        erros.append(f"T6 pid={pid} ganho_rel: md={c[6]} json={e['ganho_rel_pct']}")
out.write(f"Tabela 6 (ganho): {len(linhas_tabela('Tabela 6 -'))} linhas conferidas\n")

# ── Tabelas 7 e 8: backtesting ──────────────────────────────────────────────
for titulo, pid, cols in (("Tabela 7 -", "1", {1: ("holt_winters", "mape"), 2: ("prophet", "mape"), 3: ("naive_sazonal", "mape")}),
                          ("Tabela 8 -", "5", {1: ("holt_winters", "mape"), 2: ("holt_winters", "rmse"),
                                               3: ("prophet", "mape"), 4: ("naive_sazonal", "mape"), 5: ("naive_sazonal", "rmse")})):
    bt = d["backtesting"][pid]
    for l in linhas_tabela(titulo):
        c = [x.strip() for x in l.strip("|").split("|")]
        origem = c[0]
        for idx, (modelo, metrica) in cols.items():
            reg = next(x for x in bt[modelo] if x["origem"] == origem)
            if abs(num(c[idx]) - round(reg[metrica], 2)) > 0.005:
                erros.append(f"{titulo} {origem} {modelo}.{metrica}: md={c[idx]} json={reg[metrica]}")
    out.write(f"{titulo[:9]} (backtest p{pid}): {len(linhas_tabela(titulo))} linhas conferidas\n")

# ── Tabela 9: KPIs de reposicao ─────────────────────────────────────────────
kpi = {r["nome"]: r for r in d["kpis"]}
pares = {"Demanda média prevista (un/dia)": "demanda_media", "σ da demanda histórica": "desvio",
         "Z (nível de serviço 95%)": "z", "**Estoque de segurança**": "estoque_seguranca",
         "**Ponto de reposição**": "ponto_reposicao", "Estoque atual": "estoque_atual",
         "**Dias até ruptura**": "dias_ate_ruptura"}
for l in linhas_tabela("Tabela 9 -"):
    c = [x.strip() for x in l.strip("|").split("|")]
    if c[0] not in pares:
        continue
    chave = pares[c[0]]
    for col, nome in ((1, "Arroz 5kg"), (2, "Banana Prata kg")):
        valor = c[col].replace("**", "")
        if abs(num(valor) - kpi[nome][chave]) > 0.005:
            erros.append(f"T9 {nome} {chave}: md={valor} json={kpi[nome][chave]}")
out.write(f"Tabela 9 (reposicao): conferida\n")

# ── Tabela 10: alphas ───────────────────────────────────────────────────────
al = {r["pid"]: r for r in alphas}
for l in linhas_tabela("Tabela 10 -"):
    c = [x.strip() for x in l.strip("|").split("|")]
    pid = int(c[0]); e = al[pid]
    for idx, chave in ((2, "a"), (3, "b"), (4, "g")):
        if abs(num(c[idx]) - e[chave]) > 1e-9:
            erros.append(f"T10 pid={pid} {chave}: md={c[idx]} json={e[chave]}")
out.write(f"Tabela 10 (alphas): {len(linhas_tabela('Tabela 10 -'))} linhas conferidas\n")

# ── Afirmacoes no texto corrido ─────────────────────────────────────────────
out.write("\nAfirmacoes do texto:\n")
vit = d["vitorias"]
checks = [
    ("placar 6 x 4", vit.get("holt_winters") == 6 and vit.get("prophet") == 4),
    ("supera o baseline em 10/10", d["n_supera_baseline"] == 10 and len(d["ganho_vs_baseline"]) == 10),
    ("margem < 0,7 pp em 9 de 10", sum(1 for r in d["margens"] if r["margem_pp"] < 0.7) == 9),
    ("margem < 0,06 pp em 5", sum(1 for r in d["margens"] if r["margem_pp"] < 0.06) == 5),
    ("so 1 produto com margem > 1 pp", sum(1 for r in d["margens"] if r["margem_pp"] > 1.0) == 1),
    ("7 produtos com alpha exatamente 0", sum(1 for r in alphas if r["a"] == 0.0) == 7),
]
g = sorted(r["ganho_rel_pct"] for r in d["ganho_vs_baseline"])
mediana = (g[4] + g[5]) / 2
checks.append(("mediana da reducao = 45,1%", abs(mediana - 45.1) < 0.05))
checks.append(("min 12,8% / max 69,4%", abs(g[0] - 12.8) < 0.05 and abs(g[-1] - 69.4) < 0.05))
for nome, ok in checks:
    out.write(f"  {'OK ' if ok else 'ERRO'} {nome}\n")
    if not ok:
        erros.append(f"afirmacao: {nome}")

out.write("\n" + ("TODOS OS NUMEROS CONFEREM" if not erros else f"{len(erros)} DIVERGENCIAS:"))
for e in erros:
    out.write("\n  - " + e)
Path(sys.argv[1]).write_text(out.getvalue(), encoding="utf-8")
