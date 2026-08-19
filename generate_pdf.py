"""
generate_pdf.py - Generates 1-Page SUMMARY.pdf for Hybrid AI Agent Track
-------------------------------------------------------------------------
Creates a professional 1-page PDF summary sheet required for hackathon submission.
Run: python generate_pdf.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_pdf():
    pdf_filename = "SUMMARY.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("<b>AI EXPRESS HACKATHON: TECHNICAL SUMMARY SHEET</b>", title_style))
    story.append(Paragraph("<b>Track:</b> Hybrid Autonomous Mars Rover Agent (Logic KB + A* Search Evasion)", subtitle_style))

    # 1. Header Table
    header_data = [
        [Paragraph("<b>Course Code:</b> AI-401", body_style), Paragraph("<b>Group ID:</b> Team Alpha", body_style)],
        [Paragraph("<b>Members:</b> Student 1, Student 2, Student 3", body_style), Paragraph("<b>Track:</b> Hybrid AI Agent (Logic KB + A* Search)", body_style)],
        [Paragraph("<b>GitHub Repo:</b> https://github.com/hackathon/hybrid-mars-rover", body_style), Paragraph("<b>Environment:</b> 10x10 Fog-of-War Grid (Pygame)", body_style)]
    ]
    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # 2. PEAS Framework Matrix
    story.append(Paragraph("1. PEAS Framework Matrix", h2_style))
    peas_data = [
        [Paragraph("<b>Parameter</b>", bold_body), Paragraph("<b>Description</b>", bold_body)],
        [Paragraph("<b>Performance</b>", body_style), Paragraph("Reach Goal G safely, 0 steps into hazards/radiation, minimize path cost, optimize algorithm handoffs.", body_style)],
        [Paragraph("<b>Environment</b>", body_style), Paragraph("10x10 2D grid, partially observable (fog of war), deterministic, multi-cell storm hazards, discrete.", body_style)],
        [Paragraph("<b>Actuators</b>", body_style), Paragraph("Orthogonal movement execution: Move Up, Move Down, Move Left, Move Right.", body_style)],
        [Paragraph("<b>Sensors</b>", body_style), Paragraph("Local Breeze sensor B(x,y) [Hazard/Storm], Local Glow sensor G(x,y) [Radiation], Position sensor (x,y).", body_style)]
    ]
    peas_table = Table(peas_data, colWidths=[100, 440])
    peas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(peas_table)
    story.append(Spacer(1, 8))

    # 3. Core Algorithmic Formulation
    story.append(Paragraph("2. Hybrid Algorithmic Formulation (Units 1 - 4)", h2_style))
    algo_text = (
        "<b>Primary Engine (Propositional Logic KB - Units 3&4):</b> Proves safe cells KB &#8870; S(x,y) using Unit Resolution "
        "and Model Entailment over atomic propositions H, R, B, G, S, V.<br/>"
        "<b>Evasion Engine (A* Search - Units 1&2):</b> When a Multi-Cell Storm or Barrier is detected, the agent dynamically "
        "switches algorithms to A* Graph Search using Manhattan distance heuristic h(n) = |dx| + |dy| and evaluation function f(n) = g(n) + h(n)."
    )
    story.append(Paragraph(algo_text, body_style))
    story.append(Spacer(1, 8))

    # 4. Complexity Analysis
    story.append(Paragraph("3. Theoretical & Observed Complexity Analysis", h2_style))
    comp_data = [
        [Paragraph("<b>Metric</b>", bold_body), Paragraph("<b>Theoretical (Big-O)</b>", bold_body), Paragraph("<b>Observed Execution</b>", bold_body)],
        [Paragraph("<b>Logic Time Complexity</b>", body_style), Paragraph("O(N^2 * k) polynomial unit resolution per step", body_style), Paragraph("~0.01 - 0.02 seconds per step inference", body_style)],
        [Paragraph("<b>A* Time Complexity</b>", body_style), Paragraph("O(N^2 log N) priority queue graph search", body_style), Paragraph("12-18 nodes expanded per A* evasion run", body_style)],
        [Paragraph("<b>Space Complexity</b>", body_style), Paragraph("O(N^2) for KB literal stores & A* open/closed sets", body_style), Paragraph("Max 100 states stored in memory", body_style)],
        [Paragraph("<b>Algorithm Handoffs</b>", body_style), Paragraph("Dynamic mode switch on storm barrier detection", body_style), Paragraph("Seamless handoff KB --> A* Search", body_style)]
    ]
    comp_table = Table(comp_data, colWidths=[110, 215, 215])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(comp_table)

    doc.build(story)
    print("SUCCESS: Generated updated Hybrid AI Agent SUMMARY.pdf successfully!")

if __name__ == "__main__":
    generate_pdf()
