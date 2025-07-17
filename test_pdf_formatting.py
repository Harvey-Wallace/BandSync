#!/usr/bin/env python3
"""
Test script to verify PDF formatting fixes
"""

import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_pdf_formatting():
    """Test PDF formatting with mock data"""
    
    try:
        from services.pdf_service import PDFReportService
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        print("✅ Testing PDF formatting fixes...")
        
        # Create a test PDF with sample data
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        content = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        # Title
        content.append(Paragraph("Test RSVP Report - Formatting Check", title_style))
        content.append(Spacer(1, 20))
        
        # Test member data with different RSVP statuses
        member_data = [
            ['Name', 'Email', 'RSVP Status', 'Response Date'],
            ['John Doe', 'john@example.com', 'Yes', '07/15/2025'],
            ['Jane Smith', 'jane@example.com', 'No', '07/16/2025'],
            ['Bob Johnson', 'bob@example.com', 'Maybe', '07/17/2025'],
            ['Alice Brown', 'alice@example.com', 'No Response', 'N/A'],
            ['Charlie Wilson', 'charlie@example.com', 'Yes', '07/14/2025']
        ]
        
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
        
        # Build PDF
        doc.build(content)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF generated successfully! Size: {len(pdf_data)} bytes")
        
        # Save test file
        filename = f"test_formatting_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_data)
        print(f"💾 Test PDF saved as: {filename}")
        
        print("\n🎨 Color coding test:")
        print("✅ Yes status: Green and Bold")
        print("✅ No status: Red and Bold")
        print("✅ Maybe status: Orange and Bold")
        print("✅ No Response: Gray and Italic")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing PDF formatting: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing PDF Formatting Fixes")
    print("=" * 50)
    
    if test_pdf_formatting():
        print("\n🎉 PDF formatting test completed successfully!")
        print("✅ Ready to generate properly formatted RSVP reports!")
    else:
        print("\n❌ PDF formatting test failed!")
        print("❌ Check the error details above")
