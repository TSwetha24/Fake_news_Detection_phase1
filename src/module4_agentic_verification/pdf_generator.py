import io
import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

import io
import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def generate_pdf_report_bytes(verification_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a clean, accessible, and user-friendly Fact-Check PDF Report.
    Designed so everyday end users can easily understand the verdict, reasons,
    and directly click to view verified evidence sources.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Color Palette: Clean Editorial
    primary_emerald = colors.HexColor("#00845a")
    dark_slate = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    bg_light = colors.HexColor("#f8fafc")
    card_border = colors.HexColor("#cbd5e1")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_emerald,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=12
    )

    heading2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=dark_slate,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=dark_slate
    )

    claim_style = ParagraphStyle(
        'ClaimText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10.5,
        leading=14,
        textColor=dark_slate
    )

    link_style = ParagraphStyle(
        'LinkText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=primary_emerald
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("FACT-CHECK VERIFICATION REPORT", title_style))
    story.append(Paragraph("TruthChain AI &bull; Automated Media Authenticity & Evidence Audit Summary", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_emerald, spaceBefore=2, spaceAfter=10))

    # 2. Key Verdict Box (Clear & Non-Technical)
    claim_text = verification_data.get("claim", "N/A")
    final_verdict = verification_data.get("final_verdict", "Unverified").upper()
    trust_score = verification_data.get("preliminary_trust_score", 0.0)
    exec_time = verification_data.get("execution_time_seconds", 0.0)
    timestamp_str = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")

    verdict_color = primary_emerald if final_verdict == "REAL" else (colors.HexColor("#dc2626") if final_verdict == "FAKE" else colors.HexColor("#d97706"))
    verdict_desc = "Confirmed by authentic news reports" if final_verdict == "REAL" else ("Contradicted or unsupported by verified facts" if final_verdict == "FAKE" else "Unconfirmed or conflicting evidence")

    meta_data = [
        [
            Paragraph("<b>Claim Investigated:</b>", body_style),
            Paragraph(f'"{claim_text}"', claim_style)
        ],
        [
            Paragraph("<b>Official Verdict:</b>", body_style),
            Paragraph(f'<font size=12 color="{verdict_color.hexval()}"><b>{final_verdict}</b></font> &nbsp;—&nbsp; <i>{verdict_desc}</i>', body_style)
        ],
        [
            Paragraph("<b>Overall Trust Rating:</b>", body_style),
            Paragraph(f"<b>{trust_score}%</b> (Based on 5 combined verification checks)", body_style)
        ],
        [
            Paragraph("<b>Date of Verification:</b>", body_style),
            Paragraph(f"{timestamp_str} (Completed in {exec_time} seconds)", body_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[130, 400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 1, card_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, card_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Simple Summary for the Reader (Why this verdict was reached)
    story.append(Paragraph("1. WHAT THIS VERDICT MEANS FOR YOU", heading2_style))
    rationale_text = verification_data.get("verdict_rationale", "Verification completed across live news sources.")
    story.append(Paragraph(f"<b>Summary:</b> {rationale_text}", body_style))
    story.append(Spacer(1, 5))

    # Findings from Agent
    mod4 = verification_data.get("module4_agentic", {})
    report_findings = mod4.get("explainable_report", {}).get("findings_list", [])
    if report_findings:
        story.append(Paragraph("<b>Key Findings:</b>", body_style))
        for finding in report_findings[:4]:
            clean_finding = finding.replace("**", "")
            story.append(Paragraph(f"&bull; {clean_finding}", body_style))
    story.append(Spacer(1, 8))

    # 4. How the 5 Verification Checks Scored (Easy-to-Read Table)
    story.append(Paragraph("2. HOW THE CLAIM WAS CHECKED (5 VERIFICATION CHECKS)", heading2_style))
    scores = verification_data.get("module_confidence_scores", {})
    c1 = round(scores.get("module1_content_confidence", 0.0) * 100)
    c2 = round(scores.get("module2_evidence_confidence", 0.0) * 100)
    c3 = round(scores.get("module3_independence_confidence", 0.0) * 100)
    c4 = round(scores.get("module4_agentic_confidence", 0.0) * 100)
    c5 = round(scores.get("module5_credibility_confidence", 0.0) * 100)

    checks_data = [
        [
            Paragraph("<b>Verification Check</b>", body_style),
            Paragraph("<b>What We Examined</b>", body_style),
            Paragraph("<b>Score</b>", body_style),
            Paragraph("<b>Status</b>", body_style)
        ],
        [
            Paragraph("<b>1. Wording & Style</b>", body_style),
            Paragraph("Checked whether wording sounds like normal news or clickbait rumors", body_style),
            Paragraph(f"<b>{c1}%</b>", body_style),
            Paragraph("Plausible" if c1 >= 60 else "Suspicious", body_style)
        ],
        [
            Paragraph("<b>2. Live News Search</b>", body_style),
            Paragraph("Searched real-time news portals, Google News, and encyclopedias", body_style),
            Paragraph(f"<b>{c2}%</b>", body_style),
            Paragraph("Supported" if c2 >= 60 else "Not Found", body_style)
        ],
        [
            Paragraph("<b>3. Source Diversity</b>", body_style),
            Paragraph("Ensured reports come from multiple distinct newsrooms, not just copies", body_style),
            Paragraph(f"<b>{c3}%</b>", body_style),
            Paragraph("Diverse" if c3 >= 50 else "High Copying", body_style)
        ],
        [
            Paragraph("<b>4. Fact-Checking Agent</b>", body_style),
            Paragraph("Investigated dates, authority claims, and scientific accuracy", body_style),
            Paragraph(f"<b>{c4}%</b>", body_style),
            Paragraph("Verified" if c4 >= 60 else "Questionable", body_style)
        ],
        [
            Paragraph("<b>5. Publisher Reputation</b>", body_style),
            Paragraph("Evaluated the track record and credibility of the reporting sources", body_style),
            Paragraph(f"<b>{c5}%</b>", body_style),
            Paragraph("High Trust" if c5 >= 75 else "Moderate", body_style)
        ]
    ]

    checks_table = Table(checks_data, colWidths=[120, 260, 60, 90])
    checks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_emerald),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, card_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, card_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(checks_table)
    story.append(Spacer(1, 10))

    # 5. Verified Sources Table (Top Evidence with Clickable Links)
    story.append(Paragraph("3. VERIFIED EVIDENCE SOURCES (CLICK TO VIEW ARTICLES)", heading2_style))
    story.append(Paragraph("Click any of the links below to read the original news coverage directly in your browser:", subtitle_style))

    raw_evidence = verification_data.get("module2_retrieval", {}).get("evidence_items", [])
    top_evidence = raw_evidence[:6]  # Select top 6 sources

    evidence_table_data = [
        [
            Paragraph("<b>#</b>", body_style),
            Paragraph("<b>Publisher</b>", body_style),
            Paragraph("<b>Article Headline</b>", body_style),
            Paragraph("<b>Clickable Source Link</b>", body_style)
        ]
    ]

    for idx, art in enumerate(top_evidence, 1):
        domain = art.get("source") or art.get("domain", "News Source")
        title = art.get("title", "News article")
        url = art.get("url", "https://google.com")

        # Clickable Hyperlink formatting for ReportLab
        clickable_link = f'<a href="{url}" color="#00845a"><u>Open Source Article &rarr;</u></a>'

        evidence_table_data.append([
            Paragraph(f"<b>{idx}</b>", body_style),
            Paragraph(f"<b>{domain}</b>", body_style),
            Paragraph(title[:95] + ("..." if len(title) > 95 else ""), body_style),
            Paragraph(clickable_link, link_style)
        ])

    if len(evidence_table_data) > 1:
        ev_table = Table(evidence_table_data, colWidths=[20, 115, 275, 120])
        ev_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, card_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, card_border),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(ev_table)
    else:
        story.append(Paragraph("<i>No live media articles found directly matching this statement.</i>", body_style))

    story.append(Spacer(1, 12))

    # 6. Recommendation for the Reader & Footer
    story.append(HRFlowable(width="100%", thickness=1, color=card_border, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "<b>Important Note:</b> This automated verification report was compiled by TruthChain AI using real-time search, "
        "reputation checking, and multi-agent reasoning. Always verify critical health or legal news with official public authorities before sharing.",
        subtitle_style
    ))

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer
