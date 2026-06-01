from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
from typing import Dict, List


class PDFService:
    
    @staticmethod
    def generate_portfolio_report(portfolio_data: Dict, analysis: Dict, filepath: str):
        """Generate PDF portfolio report"""
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a202c'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("Portfolio Analysis Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Date
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        date_para = Paragraph(date_text, styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Portfolio Summary
        summary_style = ParagraphStyle(
            'SummaryHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12
        )
        
        story.append(Paragraph("Portfolio Summary", summary_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Value', f"${portfolio_data.get('total_value', 0):,.2f}"],
            ['Total Cost', f"${portfolio_data.get('total_cost', 0):,.2f}"],
            ['Total Gain/Loss', f"${portfolio_data.get('total_gain_loss', 0):,.2f}"],
            ['Return %', f"{portfolio_data.get('total_gain_loss_percent', 0):.2f}%"],
            ['Number of Holdings', str(len(portfolio_data.get('holdings', [])))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Holdings
        if portfolio_data.get('holdings'):
            story.append(Paragraph("Holdings Details", summary_style))
            story.append(Spacer(1, 0.1*inch))
            
            holdings_data = [['Symbol', 'Quantity', 'Avg Price', 'Current Price', 'Value', 'Gain/Loss']]
            
            for holding in portfolio_data['holdings']:
                holdings_data.append([
                    holding['symbol'],
                    f"{holding['quantity']:.2f}",
                    f"${holding['average_price']:.2f}",
                    f"${holding['current_price']:.2f}",
                    f"${holding['total_value']:,.2f}",
                    f"${holding['gain_loss']:,.2f} ({holding['gain_loss_percent']:.2f}%)"
                ])
            
            holdings_table = Table(holdings_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch, 1.8*inch])
            holdings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(holdings_table)
            story.append(Spacer(1, 0.3*inch))
        
        # AI Analysis
        if analysis:
            story.append(Paragraph("AI Analysis & Recommendations", summary_style))
            story.append(Spacer(1, 0.1*inch))
            
            analysis_text = analysis.get('summary', 'No analysis available')
            analysis_para = Paragraph(analysis_text, styles['Normal'])
            story.append(analysis_para)
            story.append(Spacer(1, 0.2*inch))
            
            if analysis.get('recommendations'):
                story.append(Paragraph("Recommendations:", styles['Heading3']))
                for rec in analysis['recommendations']:
                    rec_para = Paragraph(f"• {rec}", styles['Normal'])
                    story.append(rec_para)
                    story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        return filepath