#!/usr/bin/env python3
"""Generate the concise Phase 1 presentation and email PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "ecommerce_phase1_presentation_brief.pdf"
ARCHITECTURE = ROOT / "docs" / "architecture.png"

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2563A6")
GREEN = colors.HexColor("#16805B")
ORANGE = colors.HexColor("#C86422")
INK = colors.HexColor("#243444")
MUTED = colors.HexColor("#607080")
LINE = colors.HexColor("#D7DEE7")
LIGHT_BLUE = colors.HexColor("#EAF2F8")
LIGHT_GREEN = colors.HexColor("#E9F7EF")
LIGHT_ORANGE = colors.HexColor("#FFF3E8")
OFF_WHITE = colors.HexColor("#F7F9FC")


class BriefTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=18 * mm,
            bottomMargin=16 * mm,
            title="E-commerce Sales Data Pipeline - Phase 1 Presentation Brief",
            author="Ahmed Hossam Ahmed, Karim Khaled, Moaz Ahmed",
            subject="Data Engineering Phase 1 presentation and email brief",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="content",
        )
        self.addPageTemplates([PageTemplate(id="brief", frames=frame, onPage=draw_page)])


def draw_page(canvas, doc) -> None:
    page = canvas.getPageNumber()
    width, height = A4
    canvas.saveState()
    if page == 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 22 * mm, width, 22 * mm, fill=1, stroke=0)
        canvas.setFillColor(GREEN)
        canvas.rect(0, 0, width, 8 * mm, fill=1, stroke=0)
        canvas.restoreState()
        return

    canvas.setStrokeColor(LINE)
    canvas.line(16 * mm, height - 12 * mm, width - 16 * mm, height - 12 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, height - 9 * mm, "E-commerce Sales Data Pipeline")
    canvas.drawRightString(width - 16 * mm, height - 9 * mm, "Phase 1 Presentation Brief")
    canvas.line(16 * mm, 11 * mm, width - 16 * mm, 11 * mm)
    canvas.drawString(16 * mm, 6.5 * mm, "Data Engineering")
    canvas.drawRightString(width - 16 * mm, 6.5 * mm, f"Page {page} of 4")
    canvas.restoreState()


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "BriefTitle",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=29,
            leading=34,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "BriefSubtitle",
            parent=sample["Heading2"],
            fontName="Helvetica",
            fontSize=15.5,
            leading=20,
            textColor=BLUE,
            spaceAfter=12,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=INK,
        ),
        "h1": ParagraphStyle(
            "BriefH1",
            parent=sample["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=NAVY,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "BriefH2",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=BLUE,
            spaceBefore=5,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BriefBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12.3,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "BriefSmall",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.3,
            textColor=INK,
        ),
        "small_bold": ParagraphStyle(
            "BriefSmallBold",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9.3,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "BriefTableHeader",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=colors.white,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "card_body": ParagraphStyle(
            "CardBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=10.5,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "callout": ParagraphStyle(
            "BriefCallout",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.2,
            textColor=INK,
            leftIndent=5,
            rightIndent=5,
        ),
        "code": ParagraphStyle(
            "BriefCode",
            parent=sample["Code"],
            fontName="Courier",
            fontSize=7.2,
            leading=10,
            textColor=INK,
        ),
        "reference": ParagraphStyle(
            "BriefReference",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=9,
            textColor=MUTED,
        ),
    }


STYLES = make_styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def table(
    rows: list[list[str | Paragraph]],
    widths: list[float],
    *,
    header: bool = True,
    body_style: str = "small",
    row_backgrounds: tuple[colors.Color, colors.Color] = (colors.white, OFF_WHITE),
) -> Table:
    converted: list[list[Paragraph]] = []
    for row_index, row in enumerate(rows):
        style = "table_header" if header and row_index == 0 else body_style
        converted.append([cell if isinstance(cell, Paragraph) else p(str(cell), style) for cell in row])
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D2DD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), list(row_backgrounds)),
            ]
        )
    else:
        commands.append(("ROWBACKGROUNDS", (0, 0), (-1, -1), list(row_backgrounds)))
    result.setStyle(TableStyle(commands))
    return result


def callout(text: str, *, background=LIGHT_GREEN, accent=GREEN) -> Table:
    block = Table([[p(text, "callout")]], colWidths=[178 * mm])
    block.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.8, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return block


def bullets(items: list[str], *, size_style: str = "small") -> ListFlowable:
    entries = [ListItem(p(item, size_style), leftIndent=8) for item in items]
    return ListFlowable(
        entries,
        bulletType="bullet",
        leftIndent=16,
        bulletFontSize=6,
        bulletColor=GREEN,
        spaceAfter=4,
    )


def cover_story() -> list:
    team_rows = [
        ["Student", "University ID", "Phase 1 role"],
        ["Ahmed Hossam Ahmed", "692400737", "Project coordination / data engineering"],
        ["Karim Khaled", "692300126", "Database design / SQL"],
        ["Moaz Ahmed", "692300067", "Docker environment / documentation"],
    ]
    cards = [
        [
            p("VERIFIED DATASET", "card_title"),
            p("99,441 orders<br/>112,650 order items", "card_body"),
        ],
        [
            p("ANALYTICAL SCOPE", "card_title"),
            p("Revenue by category, month, and customer state", "card_body"),
        ],
        [
            p("WORKING ENVIRONMENT", "card_title"),
            p("PostgreSQL and pgAdmin healthy in Docker", "card_body"),
        ],
        [
            p("PHASE BOUNDARY", "card_title"),
            p("Planning and setup complete; pipeline implementation is later", "card_body"),
        ],
    ]
    card_cells = []
    for title, body in cards:
        cell = Table([[title], [body]], colWidths=[83 * mm])
        cell.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.7, BLUE),
                    ("TOPPADDING", (0, 0), (-1, 0), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 1), (-1, 1), 2),
                    ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
                ]
            )
        )
        card_cells.append(cell)
    card_grid = Table(
        [[card_cells[0], card_cells[1]], [card_cells[2], card_cells[3]]],
        colWidths=[87 * mm, 87 * mm],
        rowHeights=[35 * mm, 35 * mm],
        hAlign="CENTER",
    )
    card_grid.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    tag = Table([[p("EMAIL AND PRESENTATION EDITION", "small_bold")]], colWidths=[58 * mm])
    tag.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
                ("BOX", (0, 0), (-1, -1), 0.7, GREEN),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [
        Spacer(1, 26 * mm),
        tag,
        Spacer(1, 7 * mm),
        p("E-commerce Sales<br/>Data Pipeline", "title"),
        p("Phase 1: Project Proposal and Environment Setup", "subtitle"),
        p(
            "A concise university brief covering the verified Olist dataset, the three analytical questions, the proposed architecture, and the working PostgreSQL environment.",
            "cover_meta",
        ),
        Spacer(1, 8 * mm),
        p("TEAM", "h2"),
        table(team_rows, [46 * mm, 31 * mm, 101 * mm]),
        Spacer(1, 8 * mm),
        p("PHASE 1 AT A GLANCE", "h2"),
        card_grid,
        Spacer(1, 5 * mm),
        p("Course: Data Engineering &nbsp;&nbsp;|&nbsp;&nbsp; Dataset: Olist Brazilian E-Commerce &nbsp;&nbsp;|&nbsp;&nbsp; 19 November 2026", "small"),
    ]


def dataset_story() -> list:
    dataset_rows = [
        ["Source", "Rows", "Purpose"],
        ["Orders", "99,441", "Status and timestamps"],
        ["Order items", "112,650", "Product, seller, price, freight"],
        ["Customers", "99,441", "Customer identifiers and state"],
        ["Products", "32,951", "Category and attributes"],
        ["Payments", "103,886", "Payment methods and values"],
        ["Reviews", "99,224", "Scores and optional comments"],
        ["Sellers", "3,095", "Seller location"],
        ["Geolocation", "1,000,163", "Postal-prefix coordinates"],
        ["Translation", "71", "Portuguese to English categories"],
    ]
    question_rows = [
        ["#", "Analytical question", "Business value"],
        ["1", "Which product categories generate the highest sales revenue?", "Merchandising and category prioritization"],
        ["2", "How do monthly revenue and distinct order volumes change over time?", "Seasonality and performance monitoring"],
        ["3", "Which Brazilian customer states contribute the most revenue?", "Regional demand prioritization"],
    ]
    return [
        p("1. Project scope and verified dataset", "h1"),
        callout(
            "<b>Problem:</b> Olist stores related transactions across separate CSV files. Without declared grains and controlled joins, revenue can be duplicated and reports can disagree. <b>Phase 1 response:</b> verify the source, define the analytical rules, design the solution, and prove a reproducible development environment."
        ),
        Spacer(1, 4 * mm),
        p("Verified source coverage", "h2"),
        table(dataset_rows, [36 * mm, 25 * mm, 117 * mm]),
        Spacer(1, 3 * mm),
        p("Three primary analytical questions", "h2"),
        table(question_rows, [9 * mm, 101 * mm, 68 * mm]),
        Spacer(1, 3 * mm),
        p("Agreed calculation rules", "h2"),
        bullets(
            [
                "Revenue is <font name='Courier'>SUM(order_items.price)</font>; freight is excluded.",
                "Completed sales use delivered orders; order volume uses distinct <font name='Courier'>order_id</font>.",
                "Monthly grouping uses the purchase timestamp; geography uses customer state.",
                "Payments are not joined directly to item-grain revenue, preventing many-to-many duplication.",
                "Missing categories remain visible as Unknown instead of silently dropping sales.",
            ]
        ),
        callout(
            "<b>Measured quality notes:</b> 261,831 repeated geolocation rows, 610 products without a category, large optional review-text gaps, and two non-null category labels without a translation match.",
            background=LIGHT_ORANGE,
            accent=ORANGE,
        ),
    ]


def architecture_story() -> list:
    image = Image(str(ARCHITECTURE), width=166 * mm, height=108.8 * mm)
    image.hAlign = "CENTER"
    phase_rows = [
        ["Implemented in Phase 1", "Planned for later phases"],
        [
            "Repository and documentation<br/>Docker Compose<br/>PostgreSQL and pgAdmin<br/>Persistent named volumes<br/>Verified dataset profile",
            "Python ingestion and raw loading<br/>Cleaning and star schema<br/>Automated SQL quality checks<br/>Kestra orchestration<br/>Power BI dashboard",
        ],
    ]
    schema_rows = [
        ["Fact grain", "Dimensions", "Key business rule"],
        [
            "One row per order item",
            "Customer, product, seller, and date",
            "Unique source pair: (order_id, order_item_id)",
        ],
    ]
    return [
        p("2. Proposed architecture and data model", "h1"),
        p(
            "The diagram separates the working Phase 1 environment from the future processing pipeline. Solid green components are implemented configuration; dashed blue and orange components are planned.",
            "body",
        ),
        KeepTogether([image, p("Figure 1. Phase 1 environment and planned end-to-end workflow", "reference")]),
        Spacer(1, 3 * mm),
        table(phase_rows, [89 * mm, 89 * mm]),
        Spacer(1, 4 * mm),
        p("Conceptual analytical model", "h2"),
        table(schema_rows, [48 * mm, 63 * mm, 67 * mm]),
        Spacer(1, 3 * mm),
        callout(
            "<b>Why this grain matters:</b> each item has one price, product, seller, customer, and purchase date. Payments and reviews have different grains and will not be mixed into the item fact table without aggregation and reconciliation."
        ),
    ]


def validation_story() -> list:
    validation_rows = [
        ["Validation check", "Observed result", "Status"],
        ["Docker Compose", "Configuration resolved successfully", "PASS"],
        ["PostgreSQL", "17.12; container healthy", "PASS"],
        ["pgAdmin", "9.19; container healthy", "PASS"],
        ["Database", "ecommerce_db exists", "PASS"],
        ["Database login", "ecommerce_user authenticated", "PASS"],
        ["pgAdmin HTTP", "200 PING", "PASS"],
        ["Browser test", "Server connected", "PASS"],
        ["Persistent storage", "Two local named volumes", "PASS"],
    ]
    readiness_rows = [
        ["Deliverable", "Readiness"],
        ["Concise presentation PDF", "Ready for email and live presentation"],
        ["Full academic proposal", "Ready as supporting evidence"],
        ["Local Git repository", "Clean with three Phase 1 commits"],
        ["Docker demonstration", "Running on ports 5432 and 5050"],
        ["Video walkthrough", "Script ready; recording is a team action"],
        ["GitHub publication", "Remote repository must be created and pushed"],
    ]
    demo_code = (
        "docker compose ps<br/>"
        "docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db "
        "-c &quot;SELECT current_database(), current_user, version();&quot;"
    )
    return [
        p("3. Working environment and submission readiness", "h1"),
        callout(
            "<b>Environment result:</b> the complete Phase 1 Docker environment was tested, not only configured. Both services are healthy, PostgreSQL accepts queries, pgAdmin loads in a browser, and the predefined server connects successfully."
        ),
        Spacer(1, 4 * mm),
        table(validation_rows, [48 * mm, 105 * mm, 25 * mm]),
        Spacer(1, 4 * mm),
        p("60-second live demonstration", "h2"),
        table(
            [
                [p(demo_code, "code")],
                [p("Then open <b>http://localhost:5050</b>, expand Servers, and show the PostgreSQL dashboard.", "small")],
            ],
            [178 * mm],
            header=False,
            row_backgrounds=(colors.HexColor("#F3F5F7"), colors.white),
        ),
        Spacer(1, 4 * mm),
        p("Submission readiness", "h2"),
        table(readiness_rows, [61 * mm, 117 * mm]),
        Spacer(1, 4 * mm),
        callout(
            "<b>Phase 1 boundary:</b> ingestion code, populated raw tables, the physical star schema, Kestra flows, automated quality jobs, analytical views, and Power BI are future deliverables. They are designed here but not falsely presented as operational.",
            background=LIGHT_BLUE,
            accent=BLUE,
        ),
        Spacer(1, 4 * mm),
        p("Selected references", "h2"),
        p(
            "Olist dataset: kaggle.com/datasets/olistbr/brazilian-ecommerce &nbsp; | &nbsp; PostgreSQL: postgresql.org/docs &nbsp; | &nbsp; Docker Compose: docs.docker.com/compose &nbsp; | &nbsp; pgAdmin: pgadmin.org/docs",
            "reference",
        ),
    ]


def build_pdf() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    story = []
    story.extend(cover_story())
    story.append(PageBreak())
    story.extend(dataset_story())
    story.append(PageBreak())
    story.extend(architecture_story())
    story.append(PageBreak())
    story.extend(validation_story())
    BriefTemplate(str(OUTPUT)).build(story)


def main() -> None:
    build_pdf()
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
