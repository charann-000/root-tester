import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, KeepTogether
)
from reportlab.platypus import Flowable

def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

DARK_BG = hex_to_rgb("#0D1117")
CARD_BG = hex_to_rgb("#161B22")
BORDER = hex_to_rgb("#30363D")
ACCENT_BLUE = hex_to_rgb("#58A6FF")
CRITICAL_RED = hex_to_rgb("#F85149")
HIGH_ORANGE = hex_to_rgb("#F0883E")
MEDIUM_YELLOW = hex_to_rgb("#D29922")
LOW_GREEN = hex_to_rgb("#3FB950")
INFO_BLUE = hex_to_rgb("#58A6FF")

def get_severity_color(severity: str) -> colors.Color:
    colors_map = {
        "Critical": colors.HexColor(*CRITICAL_RED),
        "High": colors.HexColor(*HIGH_ORANGE),
        "Medium": colors.HexColor(*MEDIUM_YELLOW),
        "Low": colors.HexColor(*LOW_GREEN),
        "Info": colors.HexColor(*INFO_BLUE)
    }
    return colors_map.get(severity, colors.HexColor(*INFO_BLUE))

def format_cvss_score(score: float) -> str:
    filled = int(score / 10)
    empty = 10 - filled
    return "★" * filled + "☆" * empty

class ColoredSpacer(Spacer):
    def __init__(self, width, height, color=None):
        super().__init__(width, height)
        self.color = color

def generate_report(analysis: dict, output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor(*ACCENT_BLUE),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(*ACCENT_BLUE),
        spaceBefore=20,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        spaceAfter=8
    )
    
    monospace_style = ParagraphStyle(
        'Monospace',
        parent=styles['Code'],
        fontSize=9,
        textColor=colors.HexColor(*LOW_GREEN),
        backgroundColor=colors.HexColor(*DARK_BG),
        spaceAfter=8
    )
    
    target = analysis.get("target", "Unknown")
    scan_timestamp = analysis.get("scan_timestamp", datetime.utcnow().isoformat())
    risk_level = analysis.get("overall_risk_level", "Unknown")
    vuln_count = len(analysis.get("vulnerabilities", []))
    
    risk_color = get_severity_color(risk_level)
    
    story.append(Paragraph("METATRON", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Penetration Test Report", title_style))
    story.append(Spacer(1, 40))
    
    summary_data = [
        ["Target:", target],
        ["Scan Date:", scan_timestamp[:19]],
        ["Risk Level:", risk_level],
        ["Vulnerabilities:", str(vuln_count)]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(*CARD_BG),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white,
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (1, 2), (1, 2), risk_color),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(*BORDER)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    exec_summary = analysis.get("executive_summary", "No summary available.")
    story.append(Paragraph("Executive Summary", heading_style))
    exec_box = Paragraph(f"<b>{exec_summary}</b>", normal_style)
    exec_table = Table([[exec_box]], colWidths=[6*inch])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(*CARD_BG),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(*ACCENT_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(exec_table)
    story.append(PageBreak())
    
    story.append(Paragraph("Findings Overview", heading_style))
    
    vulnerabilities = analysis.get("vulnerabilities", [])
    if vulnerabilities:
        vuln_headers = [["ID", "Name", "Severity", "CVSS", "Port/Service", "Exploitability"]]
        vuln_rows = []
        
        for vuln in vulnerabilities:
            vuln_id = vuln.get("vuln_id", "")
            name = vuln.get("name", "")[:30]
            severity = vuln.get("severity", "Info")
            cvss = vuln.get("cvss_score", 0.0)
            port = vuln.get("affected_port", "N/A")
            exploitability = vuln.get("exploitability", "N/A")
            
            vuln_rows.append([
                vuln_id,
                name,
                severity,
                str(cvss),
                port,
                exploitability
            ])
        
        vuln_table = Table(vuln_headers + vuln_rows, colWidths=[0.6*inch, 2*inch, 0.8*inch, 0.5*inch, 1*inch, 1.1*inch])
        vuln_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(*ACCENT_BLUE)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(*CARD_BG)),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(*BORDER)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        for i, row in enumerate(vuln_rows):
            severity = row[2]
            if severity == "Critical":
                bg_color = colors.HexColor(*CRITICAL_RED)
            elif severity == "High":
                bg_color = colors.HexColor(*HIGH_ORANGE)
            elif severity == "Medium":
                bg_color = colors.HexColor(*MEDIUM_YELLOW)
            elif severity == "Low":
                bg_color = colors.HexColor(*LOW_GREEN)
            else:
                bg_color = colors.HexColor(*INFO_BLUE)
            vuln_table.setStyle(TableStyle([
                ('BACKGROUND', (2, i+1), (2, i+1), bg_color),
            ]))
        
        story.append(vuln_table)
    else:
        story.append(Paragraph("No vulnerabilities found.", normal_style))
    
    story.append(PageBreak())
    
    attack_surface = analysis.get("attack_surface", {})
    
    story.append(Paragraph("Attack Surface", heading_style))
    
    open_ports = attack_surface.get("open_ports", [])
    if open_ports:
        port_headers = [["Port", "Protocol", "Service"]]
        port_rows = [[p.get("port", ""), p.get("protocol", ""), p.get("service", "")] for p in open_ports]
        
        port_table = Table(port_headers + port_rows, colWidths=[1*inch, 1*inch, 2*inch])
        port_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(*ACCENT_BLUE)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(*CARD_BG)),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(*BORDER)),
        ]))
        story.append(port_table)
        story.append(Spacer(1, 15))
    
    technologies = attack_surface.get("technologies", [])
    if technologies:
        tech_text = ", ".join(technologies)
        story.append(Paragraph(f"<b>Technologies:</b> {tech_text}", normal_style))
        story.append(Spacer(1, 10))
    
    security_headers = attack_surface.get("security_headers", {})
    if security_headers:
        story.append(Paragraph("<b>Security Headers:</b>", normal_style))
        for header, present in security_headers.items():
            status = "✓ Present" if present else "✗ Missing"
            color = colors.HexColor(*LOW_GREEN) if present else colors.HexColor(*CRITICAL_RED)
            story.append(Paragraph(f"  {header}: <font color='{color}'>{status}</font>", normal_style))
    
    story.append(PageBreak())
    
    fixes = analysis.get("fixes", [])
    if fixes:
        story.append(Paragraph("Remediations", heading_style))
        
        for fix in fixes:
            vuln_id = fix.get("vuln_id", "")
            summary = fix.get("fix_summary", "")
            detail = fix.get("fix_detail", "")
            priority = fix.get("priority", "Long-term")
            patch = fix.get("patch_ref", "")
            
            priority_color = get_severity_color(priority)
            
            fix_data = [
                [f"[{priority}] {summary}"],
                [detail],
                [f"Reference: {patch}" if patch else ""]
            ]
            fix_table = Table(fix_data, colWidths=[6*inch])
            fix_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(*CARD_BG)),
                ('TEXTCOLOR', (0, 0), (-0, -1), colors.white),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, priority_color),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(fix_table)
            story.append(Spacer(1, 15))
    
    additional_recon = analysis.get("additional_recon_suggested", [])
    if additional_recon:
        story.append(PageBreak())
        story.append(Paragraph("Additional Reconnaissance", heading_style))
        
        for recon in additional_recon:
            tool = recon.get("tool", "")
            command = recon.get("command", "")
            reason = recon.get("reason", "")
            
            recon_text = f"<b>{tool}</b>: {reason}"
            story.append(Paragraph(recon_text, normal_style))
            story.append(Paragraph(f"Command: <code>{command}</code>", monospace_style))
            story.append(Spacer(1, 10))
    
    notes = analysis.get("pentest_notes", "")
    if notes:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Analyst Notes", heading_style))
        notes_box = Paragraph(notes, normal_style)
        notes_table = Table([[notes_box]], colWidths=[6*inch])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(*CARD_BG)),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(*MEDIUM_YELLOW)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(notes_table)
    
    story.append(PageBreak())
    story.append(Paragraph("Disclaimer", heading_style))
    story.append(Paragraph(
        "This report is for authorized penetration testing purposes only. "
        "The findings contained herein should be used to improve the security posture "
        "of the target systems. Unauthorized scanning or testing of systems you do not "
        "own or have explicit written permission to test is illegal.",
        normal_style
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Generated by METATRON - AI-Powered Penetration Testing Platform",
        normal_style
    ))
    
    doc.build(story)