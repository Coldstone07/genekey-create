"""PDF report generator for Gene Keys hologenetic profile."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from genekey_data import GENE_KEYS
from calculator import SEQUENCES


# Color palette
COLORS = {
    "activation": HexColor("#8B0000"),   # dark red
    "venus": HexColor("#C71585"),        # medium violet red
    "pearl": HexColor("#DAA520"),        # goldenrod
    "header_bg": HexColor("#2C2C2C"),    # dark gray
    "shadow": HexColor("#8B4513"),       # saddle brown
    "gift": HexColor("#2E8B57"),         # sea green
    "siddhi": HexColor("#4B0082"),       # indigo
    "light_bg": HexColor("#F5F5F5"),     # white smoke
    "text": HexColor("#333333"),         # dark text
}

SEQUENCE_COLORS = {
    "Activation Sequence": COLORS["activation"],
    "Venus Sequence": COLORS["venus"],
    "Pearl Sequence": COLORS["pearl"],
}


def build_styles():
    """Create all paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=COLORS["header_bg"],
        spaceAfter=6,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=COLORS["text"],
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        'SequenceTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=COLORS["activation"],
        spaceBefore=16,
        spaceAfter=10,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        'SphereTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLORS["header_bg"],
        spaceBefore=12,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        'GateInfo',
        parent=styles['Normal'],
        fontSize=12,
        textColor=COLORS["text"],
        spaceBefore=2,
        spaceAfter=6,
        leftIndent=10,
    ))

    styles.add(ParagraphStyle(
        'KeywordLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLORS["text"],
        spaceBefore=1,
        spaceAfter=1,
        leftIndent=20,
    ))

    styles.add(ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor("#555555"),
        spaceBefore=0,
        spaceAfter=4,
        leftIndent=30,
    ))

    return styles


def generate_report(profile, name, date_str, time_str, location_str, output_path):
    """Generate a styled PDF report for the given profile.

    Args:
        profile: dict from calculate_profile() with sphere -> {gate, line}
        name: person's name
        date_str: birth date string
        time_str: birth time string
        location_str: birth location string
        output_path: path for output PDF
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = build_styles()
    story = []

    # Title
    story.append(Paragraph("Gene Keys Hologenetic Profile", styles['ReportTitle']))
    story.append(Spacer(1, 4))

    # Birth info
    info_text = f"<b>{name}</b><br/>{date_str} at {time_str} — {location_str}"
    story.append(Paragraph(info_text, styles['ReportSubtitle']))
    story.append(Spacer(1, 8))

    # Horizontal rule
    rule_table = Table([['']],
                       colWidths=[doc.width],
                       rowHeights=[2])
    rule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS["header_bg"]),
        ('LINEBELOW', (0, 0), (-1, -1), 0, COLORS["header_bg"]),
    ]))
    story.append(rule_table)
    story.append(Spacer(1, 12))

    # Overview table
    story.append(Paragraph("<b>Profile Overview</b>", styles['SphereTitle']))
    story.append(Spacer(1, 6))

    overview_data = [['Sphere', 'Gene Key', 'Line', 'Shadow', 'Gift', 'Siddhi']]
    for seq_name, sphere_names in SEQUENCES.items():
        for sphere_name in sphere_names:
            info = profile[sphere_name]
            gk = GENE_KEYS[info['gate']]
            overview_data.append([
                sphere_name,
                str(info['gate']),
                str(info['line']),
                gk['shadow']['keyword'],
                gk['gift']['keyword'],
                gk['siddhi']['keyword'],
            ])

    overview_table = Table(overview_data,
                           colWidths=[1.3*inch, 0.7*inch, 0.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    overview_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), COLORS["header_bg"]),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#FFFFFF"), COLORS["light_bg"]]),
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(overview_table)
    story.append(PageBreak())

    # Detailed sections for each sequence
    for seq_name, sphere_names in SEQUENCES.items():
        seq_color = SEQUENCE_COLORS[seq_name]

        # Sequence header
        seq_style = ParagraphStyle(
            f'Seq_{seq_name}',
            parent=styles['SequenceTitle'],
            textColor=seq_color,
        )
        story.append(Paragraph(seq_name, seq_style))

        # Sequence divider
        seq_rule = Table([['']],
                         colWidths=[doc.width],
                         rowHeights=[2])
        seq_rule.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), seq_color),
        ]))
        story.append(seq_rule)
        story.append(Spacer(1, 8))

        for sphere_name in sphere_names:
            info = profile[sphere_name]
            gate = info['gate']
            line = info['line']
            gk = GENE_KEYS[gate]

            # Sphere name and Gene Key
            story.append(Paragraph(
                f"{sphere_name}",
                styles['SphereTitle']
            ))
            story.append(Paragraph(
                f"Gene Key <b>{gate}</b> — Line <b>{line}</b>",
                styles['GateInfo']
            ))

            # Shadow
            story.append(Paragraph(
                f'<font color="{COLORS["shadow"]}"><b>Shadow:</b></font> '
                f'<b>{gk["shadow"]["keyword"]}</b>',
                styles['KeywordLabel']
            ))
            story.append(Paragraph(
                gk["shadow"]["description"],
                styles['Description']
            ))

            # Gift
            story.append(Paragraph(
                f'<font color="{COLORS["gift"]}"><b>Gift:</b></font> '
                f'<b>{gk["gift"]["keyword"]}</b>',
                styles['KeywordLabel']
            ))
            story.append(Paragraph(
                gk["gift"]["description"],
                styles['Description']
            ))

            # Siddhi
            story.append(Paragraph(
                f'<font color="{COLORS["siddhi"]}"><b>Siddhi:</b></font> '
                f'<b>{gk["siddhi"]["keyword"]}</b>',
                styles['KeywordLabel']
            ))
            story.append(Paragraph(
                gk["siddhi"]["description"],
                styles['Description']
            ))

            story.append(Spacer(1, 6))

        if seq_name != "Pearl Sequence":
            story.append(PageBreak())

    doc.build(story)
    return output_path
