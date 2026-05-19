#!/usr/bin/env python3
"""
Sales Pipeline PDF Report Generator — produces professional multi-page PDF reports.
Usage: python3 generate_pdf_report.py <json_data_file> [output_pdf_file]
       python3 generate_pdf_report.py  # demo mode with sample data
"""

import json
import math
import sys
from datetime import date

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.graphics.shapes import Drawing, Circle, Wedge, String, Line, Rect
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    from reportlab.graphics import renderPDF
except ImportError:
    print("Error: reportlab is required. Run: pip install reportlab>=4.0")
    sys.exit(1)

# Color palette
PRIMARY = colors.HexColor("#1B2A4A")
ACCENT = colors.HexColor("#0EA5E9")
HIGHLIGHT = colors.HexColor("#F59E0B")
SUCCESS = colors.HexColor("#10B981")
DANGER = colors.HexColor("#EF4444")
LIGHT_GRAY = colors.HexColor("#F3F4F6")
MID_GRAY = colors.HexColor("#9CA3AF")
DARK_GRAY = colors.HexColor("#374151")
WHITE = colors.white

GRADE_COLORS = {
    "A": SUCCESS,
    "B": ACCENT,
    "C": HIGHLIGHT,
    "D": DANGER,
}

SCORE_COLORS = {
    "high": SUCCESS,    # 80+
    "medium": ACCENT,   # 60-79
    "low": HIGHLIGHT,   # 40-59
    "poor": DANGER,     # <40
}


def score_color(score):
    if score >= 80:
        return SUCCESS
    elif score >= 60:
        return ACCENT
    elif score >= 40:
        return HIGHLIGHT
    else:
        return DANGER


def grade_from_score(score):
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    else:
        return "D"


def build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("title", fontSize=28, textColor=WHITE, fontName="Helvetica-Bold", spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontSize=14, textColor=colors.HexColor("#CBD5E1"), fontName="Helvetica", spaceAfter=2),
        "h1": ParagraphStyle("h1", fontSize=18, textColor=PRIMARY, fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontSize=14, textColor=PRIMARY, fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontSize=11, textColor=DARK_GRAY, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=9, textColor=DARK_GRAY, fontName="Helvetica", spaceAfter=4, leading=14),
        "small": ParagraphStyle("small", fontSize=8, textColor=MID_GRAY, fontName="Helvetica", spaceAfter=2),
        "score_large": ParagraphStyle("score_large", fontSize=48, textColor=PRIMARY, fontName="Helvetica-Bold", alignment=1),
        "centered": ParagraphStyle("centered", fontSize=9, textColor=DARK_GRAY, fontName="Helvetica", alignment=1),
        "label": ParagraphStyle("label", fontSize=8, textColor=MID_GRAY, fontName="Helvetica-Bold", spaceAfter=2),
        "footer": ParagraphStyle("footer", fontSize=7, textColor=MID_GRAY, fontName="Helvetica", alignment=1),
    }
    return custom


def draw_score_gauge(score, size=120):
    """Draw a circular score gauge."""
    d = Drawing(size, size)
    cx, cy = size / 2, size / 2
    r_outer = size * 0.45
    r_inner = size * 0.30

    # Background ring
    for angle in range(0, 360, 5):
        wedge = Wedge(cx, cy, r_outer, angle, angle + 5, radius1=r_inner)
        wedge.fillColor = LIGHT_GRAY
        wedge.strokeColor = None
        d.add(wedge)

    # Score fill (starts at 90 degrees = top, goes clockwise)
    filled_degrees = (score / 100) * 360
    start_angle = 90
    for i in range(0, int(filled_degrees), 5):
        angle = start_angle - i
        wedge = Wedge(cx, cy, r_outer, angle - 5, angle, radius1=r_inner)
        wedge.fillColor = score_color(score)
        wedge.strokeColor = None
        d.add(wedge)

    # Center text
    score_str = String(cx, cy - 8, str(score), textAnchor="middle", fontSize=size * 0.25,
                       fontName="Helvetica-Bold", fillColor=PRIMARY)
    grade_str = String(cx, cy + size * 0.12, grade_from_score(score), textAnchor="middle",
                       fontSize=size * 0.14, fontName="Helvetica-Bold", fillColor=score_color(score))
    d.add(score_str)
    d.add(grade_str)
    return d


def draw_horizontal_bar(label, score, width=300, height=18, max_score=100):
    """Draw a single horizontal bar for a category score."""
    d = Drawing(width + 60, height + 4)
    bar_width = (score / max_score) * width

    # Background bar
    bg = Rect(0, 2, width, height - 4, fillColor=LIGHT_GRAY, strokeColor=None)
    d.add(bg)

    # Filled bar
    if bar_width > 0:
        fill = Rect(0, 2, bar_width, height - 4, fillColor=score_color(score), strokeColor=None)
        d.add(fill)

    # Score label
    score_label = String(width + 5, height / 2 - 4, f"{score}", fontSize=9,
                         fontName="Helvetica-Bold", fillColor=DARK_GRAY)
    d.add(score_label)
    return d


def add_header_footer(canvas, doc, title="Sales Pipeline Report"):
    """Add header and footer to each page."""
    canvas.saveState()
    w, h = letter

    # Header bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, h - 0.5 * inch, w, 0.5 * inch, fill=True, stroke=False)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(0.75 * inch, h - 0.32 * inch, title)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - 0.75 * inch, h - 0.32 * inch, f"Page {doc.page}")

    # Footer line
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.setLineWidth(0.5)
    canvas.line(0.75 * inch, 0.5 * inch, w - 0.75 * inch, 0.5 * inch)
    canvas.setFillColor(MID_GRAY)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(w / 2, 0.3 * inch, "Confidential — AI Sales Team Pipeline Report")
    canvas.restoreState()


def page1_cover(data, styles):
    """Cover page: score gauge + executive summary."""
    elements = []
    w, h = letter

    # Cover background block — use a colored table as background
    score = data.get("overall_pipeline_score", 0)
    report_date = data.get("date", date.today().strftime("%B %d, %Y"))

    cover_data = [[
        Paragraph("SALES PIPELINE REPORT", styles["title"]),
    ]]
    cover_table = Table(cover_data, colWidths=[6.5 * inch])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 30),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PRIMARY]),
    ]))
    elements.append(cover_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Date and prospect count
    total = data.get("pipeline_health", {}).get("total_prospects", len(data.get("prospects", [])))
    elements.append(Paragraph(f"Date: {report_date}  |  Prospects Analyzed: {total}", styles["label"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Score gauge centered
    gauge = draw_score_gauge(score, size=140)
    gauge_table = Table([[gauge]], colWidths=[6.5 * inch])
    gauge_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    elements.append(gauge_table)
    elements.append(Paragraph("Overall Pipeline Score", styles["centered"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Pipeline health summary boxes
    health = data.get("pipeline_health", {})
    a_count = health.get("a_grade", 0)
    b_count = health.get("b_grade", 0)
    c_count = health.get("c_grade", 0)
    d_count = health.get("d_grade", 0)
    avg_score = health.get("avg_score", score)

    metrics_data = [
        [
            _metric_cell("A-Grade Leads", str(a_count), SUCCESS),
            _metric_cell("B-Grade Leads", str(b_count), ACCENT),
            _metric_cell("Avg Score", str(avg_score), score_color(avg_score)),
            _metric_cell("Total Pipeline", str(total), PRIMARY),
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[1.5 * inch] * 4)
    metrics_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Executive summary
    elements.append(Paragraph("Executive Summary", styles["h1"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    elements.append(Spacer(1, 0.1 * inch))
    summary = data.get("executive_summary", "No executive summary provided.")
    elements.append(Paragraph(summary, styles["body"]))

    return elements


def _metric_cell(label, value, color):
    inner = Table([
        [Paragraph(value, ParagraphStyle("mv", fontSize=22, fontName="Helvetica-Bold",
                                          textColor=color, alignment=1))],
        [Paragraph(label, ParagraphStyle("ml", fontSize=8, fontName="Helvetica",
                                          textColor=MID_GRAY, alignment=1))],
    ])
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.5, color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return inner


def page2_score_breakdown(data, styles):
    """Score breakdown page with horizontal bar charts."""
    elements = [PageBreak()]
    elements.append(Paragraph("Score Breakdown by Category", styles["h1"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    elements.append(Spacer(1, 0.2 * inch))

    categories = data.get("categories", {})
    if categories:
        for cat_name, cat_data in categories.items():
            score = cat_data.get("score", 0)
            bar = draw_horizontal_bar(cat_name, score, width=320, height=20)
            row = [
                Paragraph(cat_name, styles["h3"]),
                bar,
            ]
            t = Table([row], colWidths=[2.0 * inch, 4.5 * inch])
            t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
    else:
        elements.append(Paragraph("No category data available.", styles["body"]))

    elements.append(Spacer(1, 0.3 * inch))

    # Score distribution
    elements.append(Paragraph("Grade Distribution", styles["h2"]))
    health = data.get("pipeline_health", {})

    dist_data = [
        ["Grade", "Count", "Score Range", "Assessment"],
        ["A (Hot Lead)", str(health.get("a_grade", 0)), "80-100", "Immediate priority — action now"],
        ["B (Strong Fit)", str(health.get("b_grade", 0)), "60-79", "Active nurturing required"],
        ["C (Weak Fit)", str(health.get("c_grade", 0)), "40-59", "Research gaps before investing"],
        ["D (No Fit)", str(health.get("d_grade", 0)), "0-39", "Remove from active pipeline"],
    ]

    dist_table = Table(dist_data, colWidths=[1.5 * inch, 0.8 * inch, 1.2 * inch, 3.0 * inch])
    dist_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#D1FAE5")),
        ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#DBEAFE")),
        ("BACKGROUND", (0, 3), (0, 3), colors.HexColor("#FEF3C7")),
        ("BACKGROUND", (0, 4), (0, 4), colors.HexColor("#FEE2E2")),
    ]))
    elements.append(dist_table)

    return elements


def page3_top_prospects(data, styles):
    """Top 5 prospects detail cards."""
    elements = [PageBreak()]
    elements.append(Paragraph("Top Prospects", styles["h1"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    elements.append(Spacer(1, 0.1 * inch))

    prospects = sorted(data.get("prospects", []), key=lambda p: p.get("score", 0), reverse=True)[:5]

    for i, p in enumerate(prospects):
        score = p.get("score", 0)
        grade = p.get("grade", grade_from_score(score))
        color = GRADE_COLORS.get(grade, MID_GRAY)

        # Prospect card header
        header_data = [[
            Paragraph(f"#{i+1}  {p.get('name', 'Unknown')}", ParagraphStyle(
                "ph", fontSize=12, fontName="Helvetica-Bold", textColor=WHITE)),
            Paragraph(f"Score: {score}  |  Grade: {grade}", ParagraphStyle(
                "ps", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=2)),
        ]]
        header_table = Table(header_data, colWidths=[3.5 * inch, 3.0 * inch])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(header_table)

        # Details row
        details_data = [[
            Paragraph(f"Stage: {p.get('stage', 'N/A')}", styles["small"]),
            Paragraph(f"URL: {p.get('url', 'N/A')}", styles["small"]),
            Paragraph(f"Next: {p.get('next_action', 'N/A')}", styles["small"]),
        ]]
        details_table = Table(details_data, colWidths=[2.0 * inch, 2.5 * inch, 2.0 * inch])
        details_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("BOX", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 0.12 * inch))

    return elements


def page4_pipeline_table(data, styles):
    """Full pipeline summary table."""
    elements = [PageBreak()]
    elements.append(Paragraph("Pipeline Summary", styles["h1"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    elements.append(Spacer(1, 0.1 * inch))

    prospects = sorted(data.get("prospects", []), key=lambda p: p.get("score", 0), reverse=True)

    table_data = [["#", "Company", "Score", "Grade", "Stage", "Next Action"]]
    for i, p in enumerate(prospects):
        score = p.get("score", 0)
        grade = p.get("grade", grade_from_score(score))
        table_data.append([
            str(i + 1),
            p.get("name", "Unknown")[:24],
            str(score),
            grade,
            p.get("stage", "N/A")[:18],
            p.get("next_action", "N/A")[:30],
        ])

    col_widths = [0.3 * inch, 1.8 * inch, 0.6 * inch, 0.5 * inch, 1.3 * inch, 2.0 * inch]
    table = Table(table_data, colWidths=col_widths)

    style = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    # Color grade cells
    for i, p in enumerate(prospects, start=1):
        grade = p.get("grade", grade_from_score(p.get("score", 0)))
        cell_color = {
            "A": colors.HexColor("#D1FAE5"),
            "B": colors.HexColor("#DBEAFE"),
            "C": colors.HexColor("#FEF3C7"),
            "D": colors.HexColor("#FEE2E2"),
        }.get(grade, WHITE)
        style.append(("BACKGROUND", (3, i), (3, i), cell_color))

    table.setStyle(TableStyle(style))
    elements.append(table)

    return elements


def page5_action_plan(data, styles):
    """Action plan page."""
    elements = [PageBreak()]
    elements.append(Paragraph("Action Plan", styles["h1"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    elements.append(Spacer(1, 0.15 * inch))

    action_items = data.get("action_items", {})

    sections = [
        ("Quick Wins (Today)", action_items.get("quick_wins", []), SUCCESS),
        ("This Week", action_items.get("this_week", []), ACCENT),
        ("This Month", action_items.get("this_month", []), HIGHLIGHT),
    ]

    for section_title, items, color in sections:
        if not items:
            continue

        elements.append(Paragraph(section_title, styles["h2"]))

        for j, item in enumerate(items, start=1):
            item_data = [[
                Paragraph(str(j), ParagraphStyle("num", fontSize=9, fontName="Helvetica-Bold",
                                                   textColor=WHITE, alignment=1)),
                Paragraph(item, styles["body"]),
            ]]
            item_table = Table(item_data, colWidths=[0.3 * inch, 6.2 * inch])
            item_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), color),
                ("BACKGROUND", (1, 0), (1, 0), LIGHT_GRAY),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.25, MID_GRAY),
            ]))
            elements.append(item_table)
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Spacer(1, 0.1 * inch))

    return elements


def page6_methodology(data, styles):
    """Scoring methodology page."""
    elements = [PageBreak()]
    elements.append(Paragraph("Scoring Methodology", styles["h1"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph(
        "Prospects are evaluated using a weighted BANT + MEDDIC framework across five dimensions. "
        "Each dimension is scored 0-100 and combined into an overall Prospect Score.",
        styles["body"]
    ))
    elements.append(Spacer(1, 0.15 * inch))

    method_data = [
        ["Dimension", "Weight", "Key Signals"],
        ["Company Fit", "25%", "Size, industry, tech stack, growth signals, budget indicators"],
        ["Contact Access", "20%", "Decision makers identified, seniority, email availability"],
        ["Opportunity Quality", "20%", "Pain severity, BANT qualification, use case fit"],
        ["Competitive Position", "15%", "Incumbent tools, switching feasibility, our differentiation"],
        ["Outreach Readiness", "20%", "Personalization depth, channel fit, timing signals"],
    ]

    method_table = Table(method_data, colWidths=[1.8 * inch, 0.8 * inch, 4.0 * inch])
    method_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(method_table)
    elements.append(Spacer(1, 0.25 * inch))

    # Grade table
    elements.append(Paragraph("Grade Scale", styles["h2"]))
    grade_data = [
        ["Grade", "Score Range", "Status", "Recommended Action"],
        ["A", "80-100", "Hot Lead", "Immediate outreach — highest priority"],
        ["B", "60-79", "Strong Fit", "Active nurturing — schedule discovery call"],
        ["C", "40-59", "Moderate Fit", "Research phase — qualify before investing"],
        ["D", "0-39", "Poor Fit", "Long-term nurture or remove from pipeline"],
    ]
    grade_table = Table(grade_data, colWidths=[0.6 * inch, 1.1 * inch, 1.2 * inch, 3.5 * inch])
    grade_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, MID_GRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#D1FAE5")),
        ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#DBEAFE")),
        ("BACKGROUND", (0, 3), (0, 3), colors.HexColor("#FEF3C7")),
        ("BACKGROUND", (0, 4), (0, 4), colors.HexColor("#FEE2E2")),
    ]))
    elements.append(grade_table)

    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(
        "Generated by AI Sales Team  •  Confidential Pipeline Report",
        styles["footer"]
    ))

    return elements


def generate_pdf(data, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = build_styles()

    def on_page(canvas, doc):
        add_header_footer(canvas, doc, title="Sales Pipeline Report")

    elements = []
    elements += page1_cover(data, styles)
    elements += page2_score_breakdown(data, styles)
    elements += page3_top_prospects(data, styles)
    elements += page4_pipeline_table(data, styles)
    elements += page5_action_plan(data, styles)
    elements += page6_methodology(data, styles)

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)
    return output_path


SAMPLE_DATA = {
    "date": date.today().strftime("%B %d, %Y"),
    "overall_pipeline_score": 72,
    "executive_summary": (
        "Pipeline health is strong with 3 A-grade prospects ready for immediate outreach. "
        "Average score of 72 reflects a qualified, focused pipeline. "
        "Priority this week: Initiate contact with top two prospects and complete competitive research on the third."
    ),
    "prospects": [
        {"name": "Acme Corp", "url": "acmecorp.com", "score": 88, "grade": "A",
         "stage": "Research", "next_action": "Schedule discovery call with VP Sales"},
        {"name": "Beta Industries", "url": "betaindustries.com", "score": 81, "grade": "A",
         "stage": "Outreach Started", "next_action": "Follow up on initial email"},
        {"name": "Gamma Solutions", "url": "gammasolutions.io", "score": 74, "grade": "B",
         "stage": "Research", "next_action": "Identify economic buyer"},
        {"name": "Delta Tech", "url": "deltatech.com", "score": 67, "grade": "B",
         "stage": "Research", "next_action": "Complete company research"},
        {"name": "Epsilon Group", "url": "epsilongroup.com", "score": 58, "grade": "C",
         "stage": "Research", "next_action": "Qualify budget signals"},
    ],
    "categories": {
        "Company Fit": {"score": 78},
        "Contact Access": {"score": 65},
        "Opportunity Quality": {"score": 71},
        "Competitive Position": {"score": 62},
        "Outreach Readiness": {"score": 69},
    },
    "action_items": {
        "quick_wins": [
            "Email Acme Corp VP Sales — connection request ready",
            "Request LinkedIn intro to Beta Industries CRO via mutual contact",
        ],
        "this_week": [
            "Complete DECISION-MAKERS research for Gamma Solutions",
            "Build outreach sequence for top 3 prospects",
            "Research Epsilon Group budget signals from job postings",
        ],
        "this_month": [
            "Add 5 new B-grade prospects to maintain pipeline depth",
            "Create competitive battle cards for top incumbent tools",
        ],
    },
    "pipeline_health": {
        "total_prospects": 5,
        "avg_score": 72,
        "a_grade": 2,
        "b_grade": 2,
        "c_grade": 1,
        "d_grade": 0,
    },
}


def main():
    if len(sys.argv) >= 2:
        json_file = sys.argv[1]
        try:
            with open(json_file) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {json_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        output_file = sys.argv[2] if len(sys.argv) >= 3 else f"SALES-REPORT-{date.today()}.pdf"
    else:
        print("Running in demo mode with sample data...")
        data = SAMPLE_DATA
        output_file = f"SALES-REPORT-DEMO-{date.today()}.pdf"

    print(f"Generating PDF: {output_file}")
    generate_pdf(data, output_file)
    print(f"PDF generated successfully: {output_file}")


if __name__ == "__main__":
    main()
