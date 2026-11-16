#!/usr/bin/env python3
"""Render docs/architecture.png and docs/proposal.pdf.

Requires Pillow and ReportLab. The proposal PDF is generated from proposal.md so the
Markdown remains the editable source of truth.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARCHITECTURE_PNG = DOCS / "architecture.png"
PROPOSAL_MD = DOCS / "proposal.md"
PROPOSAL_PDF = DOCS / "proposal.pdf"

NAVY = "#17324D"
BLUE = "#2563A6"
LIGHT_BLUE = "#EAF2F8"
GREEN = "#16805B"
LIGHT_GREEN = "#E9F7EF"
ORANGE = "#C86422"
LIGHT_ORANGE = "#FFF3E8"
INK = "#243444"
MUTED = "#607080"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def center_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, *, size: int = 24, bold: bool = False, fill: str = INK) -> None:
    face = font(size, bold)
    lines = text.split("\n")
    line_boxes = [draw.textbbox((0, 0), line, font=face) for line in lines]
    heights = [b[3] - b[1] for b in line_boxes]
    total_height = sum(heights) + (len(lines) - 1) * 7
    y = box[1] + (box[3] - box[1] - total_height) / 2
    for line, bounds, height in zip(lines, line_boxes, heights):
        width = bounds[2] - bounds[0]
        x = box[0] + (box[2] - box[0] - width) / 2
        draw.text((x, y), line, font=face, fill=fill)
        y += height + 7


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill: str, outline: str, *, dash: bool = False) -> None:
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=4)
    if dash:
        x1, y1, x2, y2 = box
        for x in range(x1 + 15, x2 - 10, 24):
            draw.line((x, y1, min(x + 12, x2), y1), fill=outline, width=4)
            draw.line((x, y2, min(x + 12, x2), y2), fill=outline, width=4)
        for y in range(y1 + 15, y2 - 10, 24):
            draw.line((x1, y, x1, min(y + 12, y2)), fill=outline, width=4)
            draw.line((x2, y, x2, min(y + 12, y2)), fill=outline, width=4)
    center_text(draw, box, text, size=22, bold=True)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = MUTED, width: int = 5) -> None:
    draw.line((*start, *end), fill=color, width=width)
    x2, y2 = end
    x1, y1 = start
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        points = [(x2, y2), (x2 - direction * 16, y2 - 10), (x2 - direction * 16, y2 + 10)]
    else:
        direction = 1 if y2 > y1 else -1
        points = [(x2, y2), (x2 - 10, y2 - direction * 16), (x2 + 10, y2 - direction * 16)]
    draw.polygon(points, fill=color)


def generate_architecture() -> None:
    image = Image.new("RGB", (1800, 1180), "#F7F9FC")
    draw = ImageDraw.Draw(image)
    draw.text((70, 35), "E-commerce Sales Data Pipeline", font=font(42, True), fill=NAVY)
    draw.text((70, 87), "Phase 1 environment and planned end-to-end workflow", font=font(24), fill=MUTED)

    draw.rounded_rectangle((45, 140, 1755, 405), radius=24, fill="#F3FBF7", outline=GREEN, width=4)
    draw.text((75, 160), "PHASE 1 - IMPLEMENTED CONFIGURATION", font=font(25, True), fill=GREEN)
    implemented = [
        ((85, 235, 400, 350), "Git Repository\nand Documentation"),
        ((500, 235, 815, 350), "Docker Compose\nLocal Environment"),
        ((915, 235, 1230, 350), "PostgreSQL\nPersistent Volume"),
        ((1330, 235, 1645, 350), "pgAdmin\nPersistent Volume"),
    ]
    for box, label in implemented:
        rounded_box(draw, box, label, LIGHT_GREEN, GREEN)
    arrow(draw, (400, 292), (500, 292), GREEN)
    arrow(draw, (815, 275), (915, 275), GREEN)
    arrow(draw, (815, 320), (1330, 320), GREEN)

    draw.rounded_rectangle((45, 445, 1755, 1090), radius=24, fill="#F4F6FF", outline=BLUE, width=4)
    draw.text((75, 465), "FUTURE PHASES - PLANNED, NOT YET OPERATIONAL", font=font(25, True), fill=BLUE)

    top_labels = [
        "Olist CSV\nDataset",
        "Python\nIngestion",
        "PostgreSQL\nRaw Storage",
        "Python Cleaning\nand Transformation",
    ]
    bottom_labels = [
        "PostgreSQL\nAnalytical Tables",
        "SQL Data Quality\nValidation",
        "SQL Analytical\nViews",
        "Power BI\nDashboard",
    ]
    xs = [85, 500, 915, 1330]
    top_boxes = []
    bottom_boxes = []
    for x, label in zip(xs, top_labels):
        box = (x, 555, x + 315, 685)
        top_boxes.append(box)
        rounded_box(draw, box, label, LIGHT_BLUE, BLUE, dash=True)
    for x, label in zip(xs, bottom_labels):
        box = (x, 795, x + 315, 925)
        bottom_boxes.append(box)
        rounded_box(draw, box, label, LIGHT_BLUE, BLUE, dash=True)
    for left, right in zip(top_boxes, top_boxes[1:]):
        arrow(draw, (left[2], 620), (right[0], 620), BLUE)
    arrow(draw, (top_boxes[-1][2] - 25, 685), (top_boxes[-1][2] - 25, 745), BLUE)
    arrow(draw, (top_boxes[-1][2] - 25, 745), (bottom_boxes[0][0] + 25, 745), BLUE)
    arrow(draw, (bottom_boxes[0][0] + 25, 745), (bottom_boxes[0][0] + 25, 795), BLUE)
    for left, right in zip(bottom_boxes, bottom_boxes[1:]):
        arrow(draw, (left[2], 860), (right[0], 860), BLUE)

    kestra = (550, 970, 1250, 1050)
    rounded_box(draw, kestra, "Kestra orchestration - schedules and monitors future processing", LIGHT_ORANGE, ORANGE, dash=True)
    draw.line((900, 970, 900, 930), fill=ORANGE, width=4)
    draw.polygon([(900, 930), (890, 946), (910, 946)], fill=ORANGE)

    draw.text((70, 1120), "Solid green = Phase 1 implemented configuration    |    Dashed blue/orange = future phases planned", font=font(21, True), fill=INK)
    image.save(ARCHITECTURE_PNG, "PNG", optimize=True)


class ProposalDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="E-commerce Sales Data Pipeline - Phase 1 Proposal",
            author="Student Team",
            subject="Data Engineering Phase 1 Proposal",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=draw_page)])


def draw_page(canvas, doc) -> None:
    page = canvas.getPageNumber()
    width, height = A4
    if page == 1:
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(NAVY))
        canvas.rect(0, height - 24 * mm, width, 24 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor(GREEN))
        canvas.rect(0, 0, width, 10 * mm, fill=1, stroke=0)
        canvas.restoreState()
        return
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7DEE7"))
    canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.drawString(18 * mm, height - 10 * mm, "E-commerce Sales Data Pipeline - Phase 1 Proposal")
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.drawString(18 * mm, 8 * mm, "Data Engineering")
    canvas.drawRightString(width - 18 * mm, 8 * mm, f"Page {page}")
    canvas.restoreState()


def styles():
    sample = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("CoverTitle", parent=sample["Title"], fontName="Helvetica-Bold", fontSize=28, leading=33, textColor=colors.HexColor(NAVY), alignment=TA_LEFT, spaceAfter=12),
        "cover_subtitle": ParagraphStyle("CoverSubtitle", parent=sample["Heading2"], fontName="Helvetica", fontSize=16, leading=21, textColor=colors.HexColor(BLUE), spaceAfter=20),
        "h1": ParagraphStyle("H1", parent=sample["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor(NAVY), spaceBefore=9, spaceAfter=7, keepWithNext=True),
        "h2": ParagraphStyle("H2", parent=sample["Heading2"], fontName="Helvetica-Bold", fontSize=13.5, leading=17, textColor=colors.HexColor(BLUE), spaceBefore=8, spaceAfter=5, keepWithNext=True),
        "h3": ParagraphStyle("H3", parent=sample["Heading3"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=colors.HexColor(GREEN), spaceBefore=7, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=sample["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=colors.HexColor(INK), alignment=TA_LEFT, spaceAfter=5),
        "small": ParagraphStyle("Small", parent=sample["BodyText"], fontName="Helvetica", fontSize=7.5, leading=10, textColor=colors.HexColor(INK)),
        "table_header": ParagraphStyle("TableHeader", parent=sample["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=colors.white),
        "quote": ParagraphStyle("Quote", parent=sample["BodyText"], fontName="Helvetica-Oblique", fontSize=9, leading=13, leftIndent=10, rightIndent=10, borderColor=colors.HexColor(GREEN), borderWidth=0, borderPadding=6, backColor=colors.HexColor(LIGHT_GREEN), spaceAfter=6),
        "code": ParagraphStyle("Code", parent=sample["Code"], fontName="Courier", fontSize=7.2, leading=9.5, leftIndent=5, rightIndent=5, backColor=colors.HexColor("#F3F5F7"), borderPadding=6, spaceAfter=6),
    }


def inline_markup(text: str) -> str:
    escaped = html.escape(text.strip())
    escaped = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#2563A6">\1</link>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", escaped)
    escaped = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8">\1</font>', escaped)
    escaped = escaped.replace("  ", "<br/>")
    return escaped


def parse_table(lines: list[str], style_map: dict[str, ParagraphStyle]) -> Table:
    rows = []
    for index, line in enumerate(lines):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if index == 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        cell_style = style_map["table_header"] if index == 0 else style_map["small"]
        rows.append([Paragraph(inline_markup(cell), cell_style) for cell in cells])
    count = len(rows[0]) if rows else 1
    available = A4[0] - 36 * mm
    col_widths = [available / count] * count
    table = Table(rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D2DD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FA")]),
            ]
        )
    )
    return table


def paragraph_block(buffer: list[str], story: list, style_map: dict[str, ParagraphStyle]) -> None:
    if buffer:
        story.append(Paragraph(inline_markup(" ".join(part.strip() for part in buffer)), style_map["body"]))
        buffer.clear()


def markdown_story(markdown_text: str) -> list:
    style_map = styles()
    lines = markdown_text.splitlines()
    story = []
    paragraph: list[str] = []
    bullets: list[str] = []
    in_code = False
    code_lines: list[str] = []
    seen_first_rule = False
    i = 0

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            items = [ListItem(Paragraph(inline_markup(item), style_map["body"]), leftIndent=8) for item in bullets]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=17, bulletFontSize=7, spaceAfter=5))
            bullets = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if stripped.startswith("```"):
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), style_map["code"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(raw)
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            story.append(parse_table(table_lines, style_map))
            story.append(Spacer(1, 6))
            continue
        if stripped.startswith("!["):
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            match = re.match(r"!\[([^]]*)\]\(([^)]+)\)", stripped)
            if match:
                path = DOCS / match.group(2)
                image = RLImage(str(path), width=170 * mm, height=111.5 * mm)
                story.append(KeepTogether([image, Paragraph(f"Figure 1. {html.escape(match.group(1))}", style_map["small"])]))
                story.append(Spacer(1, 6))
            i += 1
            continue
        if stripped == "---":
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            if not seen_first_rule:
                story.append(PageBreak())
                seen_first_rule = True
            else:
                story.append(Spacer(1, 8))
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            level = len(heading.group(1))
            title = heading.group(2)
            if level == 1 and not story:
                story.append(Spacer(1, 50 * mm))
                story.append(Paragraph(inline_markup(title), style_map["cover_title"]))
            elif level == 2 and len(story) <= 2:
                story.append(Paragraph(inline_markup(title), style_map["cover_subtitle"]))
            else:
                story.append(Paragraph(inline_markup(title), style_map[f"h{level}"]))
            i += 1
            continue
        if stripped.startswith("> "):
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            story.append(Paragraph(inline_markup(stripped[2:]), style_map["quote"]))
            i += 1
            continue
        if stripped.startswith("- "):
            paragraph_block(paragraph, story, style_map)
            bullets.append(stripped[2:])
            i += 1
            continue
        if not stripped:
            paragraph_block(paragraph, story, style_map)
            flush_bullets()
            i += 1
            continue
        if bullets:
            flush_bullets()
        paragraph.append(stripped)
        i += 1

    paragraph_block(paragraph, story, style_map)
    flush_bullets()
    return story


def generate_pdf() -> None:
    markdown_text = PROPOSAL_MD.read_text(encoding="utf-8")
    doc = ProposalDocTemplate(str(PROPOSAL_PDF))
    doc.build(markdown_story(markdown_text))


def main() -> None:
    generate_architecture()
    generate_pdf()
    print(f"Wrote {ARCHITECTURE_PNG}")
    print(f"Wrote {PROPOSAL_PDF}")


if __name__ == "__main__":
    main()
