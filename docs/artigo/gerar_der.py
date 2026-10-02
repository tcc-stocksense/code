# -*- coding: utf-8 -*-
"""Desenha o DER a partir das migrations Flyway — fonte unica, sem redesenho manual."""
import re, sys
from pathlib import Path

MIG = Path("backend/src/main/resources/db/migration")
sql = "\n".join(p.read_text(encoding="utf-8") for p in sorted(MIG.glob("V*.sql")))

tabelas = {}
for m in re.finditer(r"CREATE TABLE (\w+)\s*\((.*?)\n\)\s*ENGINE", sql, re.S):
    nome, corpo = m.group(1), m.group(2)
    cols, pks = [], set()
    mp = re.search(r"PRIMARY KEY \(([^)]+)\)", corpo)
    if mp:
        pks = {c.strip() for c in mp.group(1).split(",")}
    for linha in corpo.splitlines():
        l = linha.strip().rstrip(",")
        if not l or l.upper().startswith(("CONSTRAINT", "PRIMARY KEY", "INDEX", "UNIQUE",
                                         "FOREIGN KEY", "ON DELETE", "ON UPDATE", ")")):
            continue
        mm = re.match(r"(\w+)\s+([A-Z]+(?:\([\d,\s]+\))?)", l)
        if mm:
            cols.append((mm.group(1), mm.group(2), "PRIMARY KEY" in l or mm.group(1) in pks))
    tabelas[nome] = cols
for m in re.finditer(r"CREATE TABLE (\w+)\s*\((.*?)\n\)\s*ENGINE", sql, re.S):
    for mm in re.finditer(r"FOREIGN KEY \((\w+)\) REFERENCES (\w+)", mm_body := m.group(2)):
        pass
# colunas adicionadas por ALTER (V3)
for m in re.finditer(r"ALTER TABLE (\w+)\s+ADD COLUMN (\w+)\s+([A-Z]+(?:\([\d,\s]+\))?)", sql):
    if m.group(1) in tabelas:
        tabelas[m.group(1)].append((m.group(2), m.group(3), False))

# Relacoes (origem, coluna, destino) lidas tabela a tabela
rels = []
for m in re.finditer(r"CREATE TABLE (\w+)\s*\((.*?)\n\)\s*ENGINE", sql, re.S):
    orig, corpo = m.group(1), m.group(2)
    for mm in re.finditer(r"FOREIGN KEY \((\w+)\) REFERENCES (\w+)", corpo):
        rels.append((orig, mm.group(1), mm.group(2)))

# ── Layout em tres blocos, como o texto da secao 3.3.2 descreve ──────────────
POS = {
    "estabelecimento":   (40,  40,  "cadastral"),
    "produto":           (40,  210, "cadastral"),
    "fornecedor":        (420, 40,  "cadastral"),
    "produto_fornecedor":(420, 180, "cadastral"),
    "venda":             (420, 400, "transacional"),
    "previsao":          (800, 40,  "analitico"),
    "metrica_modelo":    (800, 300, "analitico"),
}
COR = {"cadastral": ("#E8F0FE", "#1A5FB4"), "transacional": ("#FFF4E6", "#C64600"),
       "analitico": ("#E9F7EF", "#1E7B46")}
LH, CAB, LARG = 17, 26, 330

def caixa(nome, cols, x, y, bloco):
    fundo, borda = COR[bloco]
    h = CAB + len(cols) * LH + 6
    s = [f'<rect x="{x}" y="{y}" width="{LARG}" height="{h}" rx="6" fill="white" stroke="{borda}" stroke-width="2"/>',
         f'<rect x="{x}" y="{y}" width="{LARG}" height="{CAB}" rx="6" fill="{fundo}" stroke="{borda}" stroke-width="2"/>',
         f'<rect x="{x}" y="{y+CAB-6}" width="{LARG}" height="6" fill="{fundo}"/>',
         f'<text x="{x+10}" y="{y+18}" font-family="Arial" font-size="14" font-weight="bold" fill="{borda}">{nome}</text>']
    for i, (c, t, pk) in enumerate(cols):
        yy = y + CAB + 13 + i * LH
        peso = ' font-weight="bold"' if pk else ''
        marca = "PK " if pk else ("FK " if any(r[0] == nome and r[1] == c for r in rels) else "   ")
        s.append(f'<text x="{x+10}" y="{yy}" font-family="Consolas,monospace" font-size="11"{peso} fill="#333">{marca}{c}</text>')
        s.append(f'<text x="{x+LARG-10}" y="{yy}" text-anchor="end" font-family="Consolas,monospace" font-size="10" fill="#888">{t}</text>')
    return "".join(s), h

partes, alturas = [], {}
for nome, (x, y, bloco) in POS.items():
    if nome in tabelas:
        svg, h = caixa(nome, tabelas[nome], x, y, bloco)
        partes.append(svg); alturas[nome] = (x, y, h)

linhas = []
for orig, col, dest in rels:
    if orig not in alturas or dest not in alturas:
        continue
    xo, yo, ho = alturas[orig]; xd, yd, hd = alturas[dest]
    x1, y1 = (xo if xo > xd else xo + LARG), yo + ho / 2
    x2, y2 = (xd + LARG if xo > xd else xd), yd + hd / 2
    mx = (x1 + x2) / 2
    linhas.append(f'<path d="M {x1} {y1} C {mx} {y1}, {mx} {y2}, {x2} {y2}" fill="none" stroke="#777" stroke-width="1.6" marker-end="url(#seta)"/>')
    linhas.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-6}" text-anchor="middle" font-family="Arial" font-size="10" fill="#777">1:N</text>')

legenda = []
for i, (bloco, rot) in enumerate([("cadastral", "Cadastral"), ("transacional", "Transacional"), ("analitico", "Analítico")]):
    fundo, borda = COR[bloco]
    legenda.append(f'<rect x="{40+i*170}" y="566" width="16" height="16" fill="{fundo}" stroke="{borda}" stroke-width="2" rx="3"/>')
    legenda.append(f'<text x="{62+i*170}" y="579" font-family="Arial" font-size="13" fill="#333">{rot}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="600" viewBox="0 0 1180 600">
<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M 0 0 L 10 5 L 0 10 z" fill="#777"/></marker></defs>
<rect width="1180" height="600" fill="white"/>
{"".join(linhas)}
{"".join(partes)}
{"".join(legenda)}
</svg>'''
Path(sys.argv[1]).write_text(svg, encoding="utf-8")
print("tabelas:", len(tabelas), "| relacoes:", len(rels))
for t, c in tabelas.items():
    print("   %-20s %d colunas" % (t, len(c)))
