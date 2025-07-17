"""
PDF Report Service for BandSync
Generates downloadable PDF reports for events and analytics
"""

from datetime import datetime
from io import BytesIO
from flask import current_app
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors
from models import Event, RSVP, User, Organization, Section

class PDFReportService:
    
    @staticmethod
    def generate_event_rsvp_report(event_id, org_id):
        """Generate PDF report for event RSVP status"""
        
        # Get event data
        event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
        if not event:
            return None
            
        organization = Organization.query.get(org_id)
        
        # Get all organization members
        members = User.query.filter_by(organization_id=org_id).all()
        
        # Get RSVP data
        rsvps = {rsvp.user_id: rsvp for rsvp in RSVP.query.filter_by(event_id=event_id).all()}
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for PDF content
        content = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=HexColor('#34495e')
        )
        
        # Title
        title = Paragraph(f"RSVP Status Report", title_style)
        content.append(title)
        
        # Event details
        event_info = [
            f"<b>Event:</b> {event.title}",
            f"<b>Date:</b> {event.date.strftime('%A, %B %d, %Y at %I:%M %p') if event.date else 'TBD'}",
            f"<b>Location:</b> {event.location_address or 'TBD'}",
            f"<b>Organization:</b> {organization.name}",
            f"<b>Report Generated:</b> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}"
        ]
        
        for info in event_info:
            content.append(Paragraph(info, styles['Normal']))
            content.append(Spacer(1, 6))
        
        content.append(Spacer(1, 20))
        
        # RSVP Summary
        yes_count = sum(1 for rsvp in rsvps.values() if rsvp.status == 'Yes')
        no_count = sum(1 for rsvp in rsvps.values() if rsvp.status == 'No')
        maybe_count = sum(1 for rsvp in rsvps.values() if rsvp.status == 'Maybe')
        no_response_count = len(members) - len(rsvps)
        
        content.append(Paragraph("RSVP Summary", heading_style))
        
        summary_data = [
            ['Status', 'Count', 'Percentage'],
            ['Yes', str(yes_count), f"{(yes_count/len(members)*100):.1f}%"],
            ['No', str(no_count), f"{(no_count/len(members)*100):.1f}%"],
            ['Maybe', str(maybe_count), f"{(maybe_count/len(members)*100):.1f}%"],
            ['No Response', str(no_response_count), f"{(no_response_count/len(members)*100):.1f}%"],
            ['Total Members', str(len(members)), '100.0%']
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), HexColor('#ecf0f1')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#bdc3c7')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        content.append(summary_table)
        content.append(Spacer(1, 30))
        
        # Detailed Member List
        content.append(Paragraph("Detailed Member RSVP Status", heading_style))
        
        # Group members by section if sections exist
        sections = {}
        for member in members:
            section_name = member.section.name if member.section else "No Section"
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(member)
        
        for section_name, section_members in sections.items():
            if len(sections) > 1:  # Only show section headers if there are multiple sections
                content.append(Paragraph(f"<b>{section_name}</b>", styles['Heading3']))
                content.append(Spacer(1, 6))
            
            # Create member table
            member_data = [['Name', 'Email', 'RSVP Status', 'Response Date']]
            
            for member in sorted(section_members, key=lambda x: x.name or x.username):
                rsvp = rsvps.get(member.id)
                if rsvp:
                    status = rsvp.status
                    response_date = rsvp.created_at.strftime('%m/%d/%Y') if rsvp.created_at else 'N/A'
                    
                    # Simple text status (no HTML)
                    status_display = status
                else:
                    status_display = 'No Response'
                    response_date = 'N/A'
                
                member_data.append([
                    member.name or member.username,
                    member.email,
                    status_display,
                    response_date
                ])
            
            member_table = Table(member_data, colWidths=[2*inch, 2.5*inch, 1*inch, 1*inch])
            
            # Base table style
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
            ]
            
            # Add color coding for RSVP status column (column 2)
            for row_idx, row in enumerate(member_data[1:], 1):  # Skip header row
                status = row[2]  # RSVP Status column
                if status == 'Yes':
                    table_style.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#28a745')))
                    table_style.append(('FONTNAME', (2, row_idx), (2, row_idx), 'Helvetica-Bold'))
                elif status == 'No':
                    table_style.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#dc3545')))
                    table_style.append(('FONTNAME', (2, row_idx), (2, row_idx), 'Helvetica-Bold'))
                elif status == 'Maybe':
                    table_style.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#ffc107')))
                    table_style.append(('FONTNAME', (2, row_idx), (2, row_idx), 'Helvetica-Bold'))
                elif status == 'No Response':
                    table_style.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), HexColor('#6c757d')))
                    table_style.append(('FONTNAME', (2, row_idx), (2, row_idx), 'Helvetica-Oblique'))
            
            member_table.setStyle(TableStyle(table_style))
            
            content.append(member_table)
            content.append(Spacer(1, 20))
        
        # Footer
        content.append(Spacer(1, 30))
        footer_text = f"Generated by BandSync on {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}"
        content.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(content)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    @staticmethod
    def generate_organization_analytics_report(org_id, days=30):
        """Generate PDF report for organization analytics"""
        
        from services.analytics_service import AnalyticsService
        
        organization = Organization.query.get(org_id)
        if not organization:
            return None
        
        # Get analytics data
        overview = AnalyticsService.get_organization_overview(org_id, days)
        member_analytics = AnalyticsService.get_member_analytics(org_id, days)
        event_analytics = AnalyticsService.get_event_analytics(org_id, days)
        comm_analytics = AnalyticsService.get_communication_analytics(org_id, days)
        health_score = AnalyticsService.get_organization_health_score(org_id)
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for PDF content
        content = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=HexColor('#34495e')
        )
        
        # Title
        title = Paragraph(f"Organization Analytics Report", title_style)
        content.append(title)
        
        # Organization info
        org_info = [
            f"<b>Organization:</b> {organization.name}",
            f"<b>Report Period:</b> Last {days} days",
            f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}"
        ]
        
        for info in org_info:
            content.append(Paragraph(info, styles['Normal']))
            content.append(Spacer(1, 6))
        
        content.append(Spacer(1, 20))
        
        # Health Score
        content.append(Paragraph("Organization Health Score", heading_style))
        health_color = "green" if health_score['health_score'] >= 80 else "orange" if health_score['health_score'] >= 60 else "red"
        content.append(Paragraph(f'<font color="{health_color}"><b>{health_score["health_score"]}/100 - {health_score["health_level"]}</b></font>', styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Overview metrics
        content.append(Paragraph("Overview Metrics", heading_style))
        
        overview_data = [
            ['Metric', 'Value'],
            ['Total Members', str(overview['total_members'])],
            ['Total Events', str(overview['total_events'])],
            ['Recent Events', str(overview['recent_events'])],
            ['Recent RSVPs', str(overview['recent_rsvps'])],
            ['Engagement Rate', f"{overview['engagement_rate']}%"]
        ]
        
        overview_table = Table(overview_data, colWidths=[3*inch, 2*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        content.append(overview_table)
        content.append(Spacer(1, 20))
        
        # Recommendations
        if health_score['recommendations']:
            content.append(Paragraph("Recommendations", heading_style))
            for rec in health_score['recommendations']:
                priority_color = "red" if rec['priority'] == 'high' else "orange" if rec['priority'] == 'medium' else "green"
                content.append(Paragraph(f'<font color="{priority_color}"><b>{rec["title"]}</b></font>', styles['Normal']))
                content.append(Paragraph(rec['description'], styles['Normal']))
                content.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(content)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
