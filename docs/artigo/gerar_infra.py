#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Desenha o diagrama de implantação a partir dos arquivos Terraform.

Mesma lógica do gerar_der.py: o diagrama é derivado da fonte, não redesenhado à
mão. Lê os defaults de variables.tf e as regras do security group em network.tf,
de modo que uma mudança na infraestrutura se reflita na figura do artigo.

Uso, a partir da raiz do repositório:
    ml-service/venv/Scripts/python.exe docs/artigo/gerar_infra.py saida.svg
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TF = Path(__file__).resolve().parents[2] / "infra" / "terraform"


def defaults() -> dict[str, str]:
    """Extrai o valor padrão de cada variable do Terraform."""
    txt = (TF / "variables.tf").read_text(encoding="utf-8")
    achados = {}
    for m in re.finditer(r'variable\s+"(\w+)"\s*\{(.*?)\n\}', txt, re.S):
        d = re.search(r'default\s*=\s*"?([^"\n]+)"?', m.group(2))
        if d:
            achados[m.group(1)] = d.group(1).strip()
    return achados


def portas() -> list[tuple[str, str]]:
    """Lê as regras de entrada do security group: (porta, origem)."""
    txt = (TF / "network.tf").read_text(encoding="utf-8")
    sg = txt[txt.index('resource "aws_security_group"'):]
    regras = []
    for bloco in re.findall(r"ingress\s*\{(.*?)\n  \}", sg, re.S):
        p = re.search(r"from_port\s*=\s*(\d+)", bloco)
        c = re.search(r"cidr_blocks\s*=\s*\[([^\]]+)\]", bloco)
        if p and c:
            origem = "internet" if "0.0.0.0/0" in c.group(1) else "IP do desenvolvedor"
            regras.append((p.group(1), origem))
    return regras


v, regras = defaults(), portas()
AZUL, CINZA, VERDE, LARANJA = "#1A5FB4", "#5E5C64", "#1E7B46", "#C64600"
W, H = 1100, 615


def caixa(x, y, w, h, titulo, sub, cor, tracejado=False, fill="white"):
    dash = ' stroke-dasharray="7 5"' if tracejado else ""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{cor}" stroke-width="2"{dash}/>',
         f'<text x="{x+14}" y="{y+24}" font-family="Arial" font-size="14" font-weight="bold" fill="{cor}">{titulo}</text>']
    if sub:
        s.append(f'<text x="{x+14}" y="{y+42}" font-family="Consolas,monospace" font-size="11" fill="#666">{sub}</text>')
    return "".join(s)


def servico(x, y, nome, porta, cor):
    return (f'<rect x="{x}" y="{y}" width="190" height="52" rx="6" fill="#F6F8FA" stroke="{cor}" stroke-width="1.6"/>'
            f'<text x="{x+95}" y="{y+22}" text-anchor="middle" font-family="Arial" font-size="12.5" font-weight="bold" fill="#333">{nome}</text>'
            f'<text x="{x+95}" y="{y+39}" text-anchor="middle" font-family="Consolas,monospace" font-size="10.5" fill="#777">{porta}</text>')


partes = [f'<rect width="{W}" height="{H}" fill="white"/>']
partes.append(caixa(40, 70, 1020, 515, f'AWS · {v.get("region","us-east-1")}', "", CINZA, fill="#FAFAFA"))
partes.append(caixa(70, 120, 960, 435, f'VPC  {v.get("vpc_cidr","10.0.0.0/16")}', "internet gateway · route table", AZUL))
partes.append(caixa(100, 190, 900, 335, f'Sub-rede pública  {v.get("subnet_cidr","10.0.1.0/24")}',
                    "pública por decisão: sub-rede privada exigiria NAT Gateway", AZUL, tracejado=True))
partes.append(caixa(140, 265, 820, 230, f'EC2  {v.get("instance_type","t3.medium")}',
                    f'Ubuntu 24.04 · EBS gp3 {v.get("root_volume_gb","30")} GB · Elastic IP', VERDE))
partes.append('<text x="170" y="345" font-family="Arial" font-size="12" font-weight="bold" fill="#555">docker compose</text>')
for i, (nome, porta, cor) in enumerate((("Aplicação web", "nginx · 80", VERDE),
                                        ("API", "Spring Boot · 8080", VERDE),
                                        ("Motor preditivo", "FastAPI · 8000", VERDE),
                                        ("Banco de dados", "MySQL 8.0 · 3306", LARANJA))):
    partes.append(servico(170 + (i % 2) * 400, 360 + (i // 2) * 68, nome, porta, cor))

partes.append('<circle cx="80" cy="40" r="16" fill="#E8F0FE" stroke="' + AZUL + '" stroke-width="2"/>')
partes.append(f'<text x="80" y="45" text-anchor="middle" font-family="Arial" font-size="13">\U0001F464</text>')
partes.append(f'<text x="105" y="45" font-family="Arial" font-size="13" fill="#333">Lojista</text>')
rotulo = " · ".join(f"{p}/tcp ({o})" for p, o in regras)
partes.append(f'<text x="175" y="45" font-family="Consolas,monospace" font-size="10.5" fill="#777">security group: {rotulo}</text>')
partes.append(f'<path d="M 80 58 L 80 268" fill="none" stroke="{CINZA}" stroke-width="1.8" marker-end="url(#s)"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<defs><marker id="s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
       f'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{CINZA}"/></marker></defs>'
       + "".join(partes) + "</svg>")

Path(sys.argv[1]).write_text(svg, encoding="utf-8")
print("lido de variables.tf:", {k: v[k] for k in ("region", "instance_type", "vpc_cidr", "subnet_cidr", "root_volume_gb") if k in v})
print("regras de entrada:", regras)
