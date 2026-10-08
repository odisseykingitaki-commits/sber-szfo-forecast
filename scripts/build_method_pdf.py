"""Build для_жюри/TASK2_method_report.pdf from MD.

    python scripts/build_method_pdf.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JURY = ROOT / "для_жюри"
MD_REPORT = JURY / "TASK2_METHOD_REPORT.md"
OUT_REPORT = JURY / "TASK2_method_report.pdf"
FIGURES = ROOT / "figures"
REPO_URL = "https://github.com/odisseykingitaki-commits/sber-szfo-forecast"


def _find_font_paths():
    windir = Path(r"C:\Windows\Fonts")
    for reg, bold in [
        (windir / "arial.ttf", windir / "arialbd.ttf"),
        (windir / "Arial.ttf", windir / "Arialbd.ttf"),
        (windir / "calibri.ttf", windir / "calibrib.ttf"),
        (windir / "DejaVuSans.ttf", windir / "DejaVuSans-Bold.ttf"),
    ]:
        if reg.exists():
            return str(reg), str(bold if bold.exists() else reg)
    raise FileNotFoundError("Не найден TTF с кириллицей")


def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    reg, bold = _find_font_paths()
    pdfmetrics.registerFont(TTFont("Body", reg))
    pdfmetrics.registerFont(TTFont("BodyBold", bold))
    return "Body", "BodyBold"


def _strip_md(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"[рис.: \1]", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("`", "")
    text = re.sub(r"^#+\s*", "", text)
    text = text.replace("---", "")
    text = text.replace(r"\(", "").replace(r"\)", "")
    text = text.replace(r"\[", "").replace(r"\]", "")
    text = text.replace(r"\approx", "≈").replace(r"\lambda", "λ")
    text = text.replace("$", "").replace("&lt;", "<").replace("&gt;", ">")
    return text


def build_report_pdf():
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image, KeepTogether, PageBreak, Paragraph, Preformatted,
        SimpleDocTemplate, Spacer, Table, TableStyle,
    )
    from reportlab.lib import colors

    font, font_b = _register_fonts()
    JURY.mkdir(parents=True, exist_ok=True)
    md = MD_REPORT.read_text(encoding="utf-8")

    doc = SimpleDocTemplate(
        str(OUT_REPORT), pagesize=A4,
        leftMargin=1.6 * cm, rightMargin=1.6 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        title="Task 2 — Методологический отчёт",
        author="sber-szfo-forecast",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="H1R", fontName=font_b, fontSize=14, leading=18,
        spaceAfter=8, spaceBefore=12, textColor=colors.HexColor("#1e3a5f"),
    ))
    styles.add(ParagraphStyle(
        name="H2R", fontName=font_b, fontSize=12, leading=15,
        spaceAfter=6, spaceBefore=10, textColor=colors.HexColor("#2a6f6a"),
    ))
    styles.add(ParagraphStyle(
        name="H3R", fontName=font_b, fontSize=11, leading=14,
        spaceAfter=4, spaceBefore=8, textColor=colors.HexColor("#1a2332"),
    ))
    styles.add(ParagraphStyle(
        name="BodyR", fontName=font, fontSize=9.5, leading=13,
        alignment=TA_JUSTIFY, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CenterR", fontName=font_b, fontSize=11, leading=14,
        alignment=TA_CENTER, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CodeR", fontName=font, fontSize=8, leading=10,
        backColor=colors.HexColor("#f4f6f8"), spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CellR", fontName=font, fontSize=7.5, leading=9,
    ))

    story = []
    story.append(Paragraph("Задача 2. Методологический отчёт", styles["H1R"]))
    story.append(Paragraph(
        f"Прогноз расходов и структурные сдвиги · СЗФО · {REPO_URL}",
        styles["CenterR"],
    ))
    story.append(Spacer(1, 0.3 * cm))

    lines = md.splitlines()
    i = 0
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        i += 1

    buf_code, table_buf, in_code = [], [], False

    def flush_code():
        nonlocal buf_code
        if buf_code:
            story.append(Preformatted("\n".join(buf_code), styles["CodeR"]))
            buf_code = []

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        rows = []
        for raw in table_buf:
            cells = [c.strip() for c in raw.strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            rows.append([Paragraph(_strip_md(c), styles["CellR"]) for c in cells])
        if rows:
            t = Table(rows, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")),
                ("FONTNAME", (0, 0), (-1, 0), font_b),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d5dd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.25 * cm))
        table_buf = []

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_table()
                in_code = True
            i += 1
            continue
        if in_code:
            buf_code.append(line)
            i += 1
            continue
        if line.strip().startswith("|"):
            flush_code()
            table_buf.append(line)
            i += 1
            continue
        flush_table()
        if line.startswith("# "):
            story.append(Paragraph(_strip_md(line[2:]), styles["H1R"]))
        elif line.startswith("## "):
            story.append(Paragraph(_strip_md(line[3:]), styles["H2R"]))
        elif line.startswith("### "):
            story.append(Paragraph(_strip_md(line[4:]), styles["H3R"]))
        elif line.strip() and line.strip() != "---":
            story.append(Paragraph(_strip_md(line), styles["BodyR"]))
        i += 1
    flush_code()
    flush_table()

    for name in ("fig_changepoints_consensus.png", "fig_changepoints.png"):
        fp = FIGURES / name
        if fp.exists():
            if name == "fig_changepoints_consensus.png":
                story.append(PageBreak())
                story.append(Paragraph("Ключевые рисунки", styles["H2R"]))
            story.append(KeepTogether([
                Paragraph(fp.name, styles["CenterR"]),
                Image(str(fp), width=15 * cm, height=9 * cm, kind="proportional"),
                Spacer(1, 0.4 * cm),
            ]))

    def _footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(1.6 * cm, 1.0 * cm, "Task 2 · методологический отчёт")
        canvas.drawRightString(A4[0] - 1.6 * cm, 1.0 * cm, REPO_URL)
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"OK report -> {OUT_REPORT}")


if __name__ == "__main__":
    build_report_pdf()
