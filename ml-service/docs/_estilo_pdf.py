"""
Estilo compartilhado dos PDFs de documentação do ml-service.

Centraliza fontes, paleta, estilos de parágrafo e os construtores de bloco
(títulos, tabelas, fórmulas, figuras, caixas de destaque) usados por:
    - gerar_relatorio_pdf.py     → docs/relatorio-modelos-preditivos.pdf
    - gerar_capitulo_validacao.py → docs/capitulo-validacao.pdf

Fontes: DejaVu Sans / Sans Mono, empacotadas com o matplotlib. Necessárias
porque as fontes padrão do reportlab não têm os símbolos gregos e matemáticos
(α, β, γ, σ, √, ŷ) que as fórmulas exigem. A mono não possui o glifo ℓ (U+2113),
por isso os documentos usam L para o nível do Holt-Winters.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ── Fontes ────────────────────────────────────────────────────────────────────
_FT = Path(os.path.dirname(matplotlib.__file__)) / "mpl-data" / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DJ", _FT / "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJ-B", _FT / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJ-I", _FT / "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DJ-BI", _FT / "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DJM", _FT / "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DJM-B", _FT / "DejaVuSansMono-Bold.ttf"))
registerFontFamily("DJ", normal="DJ", bold="DJ-B", italic="DJ-I", boldItalic="DJ-BI")
registerFontFamily("DJM", normal="DJM", bold="DJM-B", italic="DJM", boldItalic="DJM-B")

# ── Paleta ────────────────────────────────────────────────────────────────────
AZUL = colors.HexColor("#1B3A5C")
AZUL_CLARO = colors.HexColor("#E8EFF6")
CINZA = colors.HexColor("#5A6572")
CINZA_CLARO = colors.HexColor("#F2F4F6")
BORDA = colors.HexColor("#C8D2DC")
VERDE = colors.HexColor("#1E6B3A")
VERDE_CLARO = colors.HexColor("#E7F3EB")
AMBAR = colors.HexColor("#8A6100")
AMBAR_CLARO = colors.HexColor("#FDF3DC")
VERMELHO = colors.HexColor("#B3261E")

MARGEM = 2.0 * cm
LARGURA_UTIL = A4[0] - 2 * MARGEM

_ss = getSampleStyleSheet()

S_TITULO = ParagraphStyle("t", parent=_ss["Title"], fontName="DJ-B", fontSize=23,
                          leading=29, textColor=AZUL, alignment=TA_CENTER, spaceAfter=6)
S_SUB = ParagraphStyle("s", parent=_ss["Normal"], fontName="DJ", fontSize=12.5,
                       leading=18, textColor=CINZA, alignment=TA_CENTER)
S_H1 = ParagraphStyle("h1", fontName="DJ-B", fontSize=15.5, leading=20, textColor=AZUL,
                      spaceBefore=16, spaceAfter=8)
S_H2 = ParagraphStyle("h2", fontName="DJ-B", fontSize=12, leading=16, textColor=AZUL,
                      spaceBefore=12, spaceAfter=5)
S_H3 = ParagraphStyle("h3", fontName="DJ-BI", fontSize=10.5, leading=14,
                      textColor=CINZA, spaceBefore=9, spaceAfter=3)
S_P = ParagraphStyle("p", fontName="DJ", fontSize=9.6, leading=14.4,
                     alignment=TA_JUSTIFY, spaceAfter=6)
S_LI = ParagraphStyle("li", parent=S_P, leftIndent=13, bulletIndent=3, spaceAfter=3.5)
S_CAP = ParagraphStyle("cap", fontName="DJ-I", fontSize=8.3, leading=11.5,
                       textColor=CINZA, alignment=TA_CENTER, spaceBefore=3, spaceAfter=11)
S_TAB = ParagraphStyle("tb", fontName="DJ", fontSize=7.9, leading=10.5)
S_TABH = ParagraphStyle("tbh", fontName="DJ-B", fontSize=7.9, leading=10.5,
                        textColor=colors.white)
S_FORM = ParagraphStyle("f", fontName="DJM", fontSize=9.2, leading=14.5,
                        textColor=colors.HexColor("#102A43"))
S_COD = ParagraphStyle("c", fontName="DJM", fontSize=8.1, leading=11.8,
                       textColor=colors.HexColor("#243B53"))


# ── Construtores de bloco ─────────────────────────────────────────────────────
def h1(t):
    return Paragraph(t, S_H1)


def h2(t):
    return Paragraph(t, S_H2)


def h3(t):
    return Paragraph(t, S_H3)


def p(t):
    return Paragraph(t, S_P)


def li(t, marca="•"):
    return Paragraph(t, S_LI, bulletText=marca)


def esp(h=5):
    return Spacer(1, h)


def caixa(conteudo, fundo, borda, largura=LARGURA_UTIL):
    t = Table([[conteudo]], colWidths=[largura])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fundo),
        ("BOX", (0, 0), (-1, -1), 0.9, borda),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def formula(txt):
    return caixa(Paragraph(txt, S_FORM), CINZA_CLARO, BORDA)


def codigo(txt):
    linhas = [Paragraph(l.replace(" ", "&nbsp;"), S_COD) for l in txt.split("\n")]
    return caixa(linhas, colors.HexColor("#F7F9FB"), BORDA)


def destaque(titulo, txt, tipo="info"):
    fundo, borda = {"info": (AZUL_CLARO, AZUL), "ok": (VERDE_CLARO, VERDE),
                    "alerta": (AMBAR_CLARO, AMBAR)}[tipo]
    cor = {"info": AZUL, "ok": VERDE, "alerta": AMBAR}[tipo]
    itens = [Paragraph(titulo, ParagraphStyle("dt", fontName="DJ-B", fontSize=9.8,
                                              leading=13, textColor=cor, spaceAfter=4))]
    for bloco in (txt if isinstance(txt, list) else [txt]):
        itens.append(Paragraph(bloco, ParagraphStyle("dp", parent=S_P, spaceAfter=3)))
    return caixa(itens, fundo, borda)


def tabela(linhas, larguras, alinha_dir=(), destaque_linhas=()):
    dados = [[Paragraph(str(c), S_TABH) for c in linhas[0]]]
    for linha in linhas[1:]:
        dados.append([Paragraph(str(c), S_TAB) for c in linha])
    t = Table(dados, colWidths=larguras, repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA_CLARO]),
    ]
    for c in alinha_dir:
        estilo.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    for r in destaque_linhas:
        estilo.append(("BACKGROUND", (0, r), (-1, r), VERDE_CLARO))
    t.setStyle(TableStyle(estilo))
    return t


def figura(caminho, legenda, largura=None):
    largura = largura or (LARGURA_UTIL * 0.92)
    with PILImage.open(caminho) as im:
        prop = im.height / im.width
    img = Image(str(caminho), width=largura, height=largura * prop)
    img.hAlign = "CENTER"
    return KeepTogether([img, Paragraph(legenda, S_CAP)])


# ── Documento ─────────────────────────────────────────────────────────────────
def montar_documento(destino, story, rodape_texto, **meta):
    """Constrói o PDF com rodapé numerado (a primeira página não recebe rodapé)."""
    def _rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont("DJ", 7.6)
        canvas.setFillColor(CINZA)
        if doc.page > 1:
            canvas.drawString(MARGEM, 1.25 * cm, rodape_texto)
            canvas.drawRightString(A4[0] - MARGEM, 1.25 * cm, f"{doc.page}")
            canvas.setStrokeColor(BORDA)
            canvas.setLineWidth(0.4)
            canvas.line(MARGEM, 1.65 * cm, A4[0] - MARGEM, 1.65 * cm)
        canvas.restoreState()

    doc = BaseDocTemplate(
        str(destino), pagesize=A4,
        leftMargin=MARGEM, rightMargin=MARGEM,
        topMargin=1.7 * cm, bottomMargin=2.1 * cm, **meta,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=_rodape)])
    doc.build(story)
    return Path(destino)
