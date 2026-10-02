#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audita as referências cruzadas do artigo: figuras, tabelas, equações e subseções.

Existe porque renumerar figuras com uma substituição simples quebra o plural —
"as Figuras 7 e 8" não casa com o padrão `Figura N`, e a referência fica
apontando para o número antigo. Esse erro já aconteceu e passou despercebido.

Rodar a partir da raiz do repositório, sempre que algo for renumerado:
    ml-service/venv/Scripts/python.exe docs/artigo/verificar_referencias.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ARTIGO = Path(__file__).resolve().parent
ORDEM = ["00-frontmatter.md", "01-introducao.md", "02-fundamentacao.md",
         "03-metodologia.md", "04-resultados.md", "05-consideracoes.md",
         "referencias.md"]


def main() -> int:
    texto, rotulos, equacoes, subsecoes = "", {"Figura": set(), "Tabela": set()}, set(), set()

    for nome in ORDEM:
        caminho = ARTIGO / nome
        if not caminho.is_file():
            continue
        conteudo = caminho.read_text(encoding="utf-8")
        texto += "\n" + conteudo
        for m in re.finditer(r"^\*\*(Figura|Tabela) (\d+) - ", conteudo, re.M):
            rotulos[m.group(1)].add(int(m.group(2)))
        for m in re.finditer(r"^\s{4,}.*?\((\d+)\)\s*$", conteudo, re.M):
            equacoes.add(int(m.group(1)))
        for m in re.finditer(r"^#{2,3} (\d+(?:\.\d+)*)\s", conteudo, re.M):
            subsecoes.add(m.group(1))

    problemas = []

    # Numeração contígua a partir de 1
    for tipo, nums in rotulos.items():
        if nums:
            faltando = sorted(set(range(1, max(nums) + 1)) - nums)
            if faltando:
                problemas.append("%s: buraco na numeração — falta %s"
                                 % (tipo, ", ".join(map(str, faltando))))
    if equacoes:
        faltando = sorted(set(range(1, max(equacoes) + 1)) - equacoes)
        if faltando:
            problemas.append("Equação: buraco na numeração — falta %s"
                             % ", ".join(map(str, faltando)))

    # Referências no corpo (singular e plural) apontam para rótulo existente
    for tipo in ("Figura", "Tabela"):
        padrao = r"\b%ss?\s+((?:\d+)(?:\s*(?:,|e)\s*\d+)*)" % tipo
        for m in re.finditer(padrao, texto):
            if re.match(r"^\*\*", texto[max(0, m.start() - 2):m.start()]):
                continue  # é o próprio rótulo
            for num in re.findall(r"\d+", m.group(1)):
                if int(num) not in rotulos[tipo]:
                    problemas.append("referência a %s %s, que não existe" % (tipo, num))

    for m in re.finditer(r"\bEquaç(?:ão|ões)\s+\((\d+)\)(?:\s*e\s*\((\d+)\))?", texto):
        for num in filter(None, m.groups()):
            if int(num) not in equacoes:
                problemas.append("referência à Equação (%s), que não existe" % num)

    for m in re.finditer(r"\bsubseç(?:ão|ões)\s+(\d+(?:\.\d+)+)", texto):
        if m.group(1) not in subsecoes:
            problemas.append("referência à subseção %s, que não existe" % m.group(1))

    print("Figuras: %s" % (sorted(rotulos["Figura"]) or "nenhuma"))
    print("Tabelas: %s" % (sorted(rotulos["Tabela"]) or "nenhuma"))
    print("Equações: %s" % (sorted(equacoes) or "nenhuma"))
    print()
    if problemas:
        print("%d PROBLEMA(S):" % len(dict.fromkeys(problemas)))
        for p in dict.fromkeys(problemas):
            print("  -", p)
        return 1
    print("TODAS AS REFERÊNCIAS CRUZADAS CONFEREM")
    return 0


if __name__ == "__main__":
    sys.exit(main())
