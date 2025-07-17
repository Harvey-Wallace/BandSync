#!/usr/bin/env python3
"""
Simple test script for PDF generation functionality
"""

import sys
import os
from datetime import datetime

# Test basic reportlab functionality
def test_reportlab():
    """Test if reportlab is working"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from io import BytesIO
        
        print("✅ Reportlab imports successful")
        
        # Create a simple test PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        
        # Content
        content = []
        content.append(Paragraph("Test RSVP Report", title_style))
        content.append(Spacer(1, 20))
        content.append(Paragraph("This is a test of the PDF generation system.", styles['Normal']))
        
        # Sample table
        data = [
            ['Name', 'Email', 'RSVP Status'],
            ['John Doe', 'john@example.com', 'Yes'],
            ['Jane Smith', 'jane@example.com', 'No'],
            ['Bob Johnson', 'bob@example.com', 'Maybe']
        ]
        
        table = Table(data, colWidths=[2*inch, 2.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        content.append(table)
        
        # Build PDF
        doc.build(content)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF generated successfully! Size: {len(pdf_data)} bytes")
        
        # Save test file
        filename = f"test_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_data)
        print(f"💾 Test PDF saved as: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing reportlab: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing PDF Generation System")
    print("=" * 50)
    
    if test_reportlab():
        print("\n🎉 PDF generation test completed successfully!")
        print("✅ Ready to generate RSVP reports!")
    else:
        print("\n❌ PDF generation test failed!")
        print("❌ Check reportlab installation")
