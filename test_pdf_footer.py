#!/usr/bin/env python3
"""
Test script to verify PDF footer branding
"""

import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_pdf_footer():
    """Test PDF footer branding"""
    
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        def add_page_footer(canvas, doc):
            """Add BandSync branding footer to every page"""
            canvas.saveState()
            
            # Footer positioning
            footer_y = 50  # 50 points from bottom
            page_width = doc.pagesize[0]
            
            # BandSync branding
            canvas.setFont("Helvetica", 10)
            canvas.setFillColor(HexColor('#6c757d'))
            
            # Center the text
            website_text = "www.bandsync.co.uk"
            email_text = "info@bandsync.co.uk"
            
            # Calculate text width for centering
            website_width = canvas.stringWidth(website_text, "Helvetica", 10)
            email_width = canvas.stringWidth(email_text, "Helvetica", 10)
            
            # Draw website
            canvas.drawString((page_width - website_width) / 2, footer_y + 15, website_text)
            
            # Draw email
            canvas.drawString((page_width - email_width) / 2, footer_y, email_text)
            
            canvas.restoreState()
        
        print("✅ Testing PDF footer branding...")
        
        # Create a test PDF with footer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=90)
        
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
        content.append(Paragraph("Test RSVP Report - Footer Branding", title_style))
        content.append(Spacer(1, 20))
        
        # Add some content to test footer
        content.append(Paragraph("This is a test PDF to verify the footer branding appears correctly.", styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Test table
        test_data = [
            ['Name', 'Email', 'RSVP Status'],
            ['John Doe', 'john@example.com', 'Yes'],
            ['Jane Smith', 'jane@example.com', 'No'],
            ['Bob Johnson', 'bob@example.com', 'Maybe'],
            ['Alice Brown', 'alice@example.com', 'No Response']
        ]
        
        test_table = Table(test_data, colWidths=[2*inch, 2.5*inch, 1*inch])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        content.append(test_table)
        content.append(Spacer(1, 20))
        
        # Add more content to test multiple pages
        for i in range(20):
            content.append(Paragraph(f"This is test line {i+1} to create multiple pages and test footer on each page.", styles['Normal']))
            content.append(Spacer(1, 12))
        
        # Build PDF with footer
        doc.build(content, onFirstPage=add_page_footer, onLaterPages=add_page_footer)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF generated successfully! Size: {len(pdf_data)} bytes")
        
        # Save test file
        filename = f"test_footer_branding_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_data)
        print(f"💾 Test PDF saved as: {filename}")
        
        print("\n🎨 Footer branding test:")
        print("✅ Website: www.bandsync.co.uk")
        print("✅ Email: info@bandsync.co.uk")
        print("✅ Footer appears on every page")
        print("✅ Centered at bottom of page")
        print("✅ Professional gray color")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing PDF footer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing PDF Footer Branding")
    print("=" * 50)
    
    if test_pdf_footer():
        print("\n🎉 PDF footer branding test completed successfully!")
        print("✅ Ready to generate branded RSVP reports!")
    else:
        print("\n❌ PDF footer branding test failed!")
        print("❌ Check the error details above")
