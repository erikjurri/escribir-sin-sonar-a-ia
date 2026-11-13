# -*- coding: utf-8 -*-
"""Markdown -> PDF con reportlab. Uso: python md2pdf.py entrada.md salida.pdf "Título de pie de página"
Soporta: # ## ### , párrafos, **negrita**, *cursiva*, `código`, [enlaces](url), listas, casillas, tablas y reglas.
"""
import os, re, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

src, dst = sys.argv[1], sys.argv[2]
running = sys.argv[3] if len(sys.argv) > 3 else ""

F = r"C:\Windows\Fonts"
BASE, BOLD, ITAL, BOIT = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"
try:
    for name, file in (("Body", "segoeui.ttf"), ("Body-B", "segoeuib.ttf"), ("Body-I", "segoeuii.ttf"), ("Body-BI", "segoeuiz.ttf")):
        pdfmetrics.registerFont(TTFont(name, os.path.join(F, file)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")
    BASE, BOLD, ITAL, BOIT = "Body", "Body-B", "Body-I", "Body-BI"
except Exception as e:
    print("aviso: sin Segoe UI, uso Helvetica:", e)

INK = colors.HexColor("#1b1b1b"); ACC = colors.HexColor("#8a3b12"); GRID = colors.HexColor("#c9c4bc"); HEAD = colors.HexColor("#efeae2")
st = {
 "h1": ParagraphStyle("h1", fontName=BOLD, fontSize=25, leading=30, textColor=INK, spaceAfter=10),
 "h2": ParagraphStyle("h2", fontName=BOLD, fontSize=16.5, leading=21, textColor=ACC, spaceBefore=16, spaceAfter=7),
 "h3": ParagraphStyle("h3", fontName=BOLD, fontSize=12, leading=16, textColor=INK, spaceBefore=11, spaceAfter=4),
 "h4": ParagraphStyle("h4", fontName=BOLD, fontSize=10.4, leading=14, textColor=ACC, spaceBefore=8, spaceAfter=3),
 "code": ParagraphStyle("code", fontName=BASE, fontSize=9.4, leading=13.2, textColor=INK, spaceAfter=0),
 "p": ParagraphStyle("p", fontName=BASE, fontSize=10.2, leading=15, textColor=INK, spaceAfter=6.5, alignment=TA_LEFT),
 "li": ParagraphStyle("li", fontName=BASE, fontSize=10.2, leading=14.6, textColor=INK, leftIndent=15, bulletIndent=3, spaceAfter=3.2),
 "cell": ParagraphStyle("cell", fontName=BASE, fontSize=8.6, leading=11.4, textColor=INK),
 "cellh": ParagraphStyle("cellh", fontName=BOLD, fontSize=8.6, leading=11.4, textColor=INK),
 "quote": ParagraphStyle("quote", fontName=BASE, fontSize=9.8, leading=13.6, textColor=INK, spaceAfter=1.5),
}

def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: f'<link href="{m.group(2)}" color="#1a4f8a">{m.group(1)}</link>', t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r'<font face="Courier" size="9">\1</font>', t)
    return t

def table(rows):
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    width = A4[0] - 4 * cm
    w = []
    for c in range(ncol):
        lens = [len(re.sub(r"[*`\[\]()]", "", r[c])) for r in rows]
        w.append(min(max(max(lens) * 0.45 + sum(lens) / len(lens) * 0.55, 7), 60))
    tot = sum(w); cw = [width * x / tot for x in w]
    # ninguna columna más estrecha que su palabra más larga (evita partir palabras)
    from reportlab.pdfbase.pdfmetrics import stringWidth
    mins = []
    for c in range(ncol):
        words = [wd for r in rows for wd in re.sub(r"[*`]|\[|\]|\(https?://[^)]*\)", " ", r[c]).split()]
        longest = max([stringWidth(wd, BOLD, 8.6) for wd in words] or [20])
        mins.append(min(longest + 10, width * 0.45))
    for _ in range(4):
        deficit = sum(max(0, mins[c] - cw[c]) for c in range(ncol))
        if deficit < 0.5: break
        spare = [max(0, cw[c] - mins[c]) for c in range(ncol)]; tsp = sum(spare) or 1
        cw = [max(cw[c], mins[c]) - (spare[c] / tsp) * deficit if cw[c] > mins[c] else mins[c] for c in range(ncol)]
    data = [[Paragraph(inline(c), st["cellh"] if i == 0 else st["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD), ("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]))
    return t

lines = open(src, encoding="utf-8").read().splitlines()
story, para, i = [], [], 0
def flush():
    global para
    if para:
        story.append(Paragraph(inline(" ".join(para)), st["p"])); para = []
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln.strip():
        flush(); i += 1; continue
    if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|?$", lines[i + 1].strip()):
        flush(); rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            row = lines[i].strip()
            if not re.match(r"^\|[\s:\-|]+\|?$", row):
                rows.append([c.strip() for c in row.strip("|").split("|")])
            i += 1
        story.append(Spacer(1, 3)); story.append(table(rows)); story.append(Spacer(1, 8)); continue
    if ln.lstrip().startswith(">"):
        flush(); qlines = []
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            qlines.append(re.sub(r"^\s*>\s?", "", lines[i].rstrip())); i += 1
        cell = []
        for q in qlines:
            if not q.strip():
                cell.append(Spacer(1, 4))
            else:
                cell.append(Paragraph(inline(q), st["quote"]))
        box = Table([[cell]], colWidths=[A4[0] - 4.6 * cm])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f6f2ea")), ("LINEBEFORE", (0, 0), (0, -1), 2, ACC),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story.append(Spacer(1, 2)); story.append(box); story.append(Spacer(1, 8)); continue
    if ln.strip().startswith("```"):
        flush(); i += 1; code = []
        while i < len(lines) and not lines[i].strip().startswith("```"):
            code.append(lines[i].rstrip()); i += 1
        i += 1
        # cada párrafo del bloque es una fila, para que el recuadro pueda partirse entre páginas
        paras, cur = [], []
        for c in code:
            if c.strip():
                cur.append(c.strip())
            elif cur:
                paras.append(cur); cur = []
        if cur: paras.append(cur)
        rows = []
        for pr in paras:
            if all(re.match(r"^\s*[-*]\s+", x) for x in pr):
                for x in pr:
                    rows.append([Paragraph(inline(re.sub(r"^\s*[-*]\s+", "", x)), st["code"], bulletText="•")])
            else:
                rows.append([Paragraph(inline(" ".join(pr)), st["code"])])
        box = Table(rows or [[Paragraph("&nbsp;", st["code"])]], colWidths=[A4[0] - 4.4 * cm])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f1ec")), ("BOX", (0, 0), (-1, -1), 0.6, GRID),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                                 ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(Spacer(1, 2)); story.append(box); story.append(Spacer(1, 8)); continue
    m = re.match(r"^(#{1,4})\s+(.*)", ln)
    if m:
        flush(); lvl = len(m.group(1)); txt = inline(m.group(2))
        story.append(Paragraph(txt, st["h1"] if lvl == 1 else st["h2"] if lvl == 2 else st["h3"] if lvl == 3 else st["h4"])); i += 1; continue
    if re.match(r"^-{3,}$", ln.strip()):
        flush(); story.append(Spacer(1, 4)); story.append(HRFlowable(width="100%", thickness=0.6, color=GRID)); story.append(Spacer(1, 6)); i += 1; continue
    m = re.match(r"^\s*[-*]\s+\[( |x)\]\s+(.*)", ln)
    if m:
        flush(); story.append(Paragraph(inline(m.group(2)), st["li"], bulletText="☐" if BASE == "Body" else "[ ]")); i += 1; continue
    m = re.match(r"^\s*[-*]\s+(.*)", ln)
    if m:
        flush(); story.append(Paragraph(inline(m.group(1)), st["li"], bulletText="•")); i += 1; continue
    m = re.match(r"^\s*(\d+)[.)]\s+(.*)", ln)
    if m:
        flush(); story.append(Paragraph(inline(m.group(2)), st["li"], bulletText=m.group(1) + ".")); i += 1; continue
    para.append(ln.strip()); i += 1
flush()

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont(BASE, 8); canvas.setFillColor(colors.HexColor("#6b655c"))
    canvas.drawString(2 * cm, 1.2 * cm, running); canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page)); canvas.restoreState()

doc = SimpleDocTemplate(dst, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm, title=running, author="Erik Jurri")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("PDF:", dst, "| páginas:", doc.page)
