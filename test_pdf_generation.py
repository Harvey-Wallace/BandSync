#!/usr/bin/env python3
"""
Simple test script for PDF RSVP report generation
"""

import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
from models import Event, User, RSVP, Organization

def test_pdf_generation():
    """Test PDF generation with existing data"""
    
    with app.app_context():
        # Get first event
        event = Event.query.first()
        if not event:
            print("❌ No events found in database")
            return
            
        print(f"✅ Found event: {event.title}")
        print(f"📅 Date: {event.date}")
        print(f"🏢 Organization ID: {event.organization_id}")
        
        # Get organization
        org = Organization.query.get(event.organization_id)
        if not org:
            print("❌ Organization not found")
            return
            
        print(f"🏢 Organization: {org.name}")
        
        # Get RSVPs
        rsvps = RSVP.query.filter_by(event_id=event.id).all()
        print(f"📝 RSVPs found: {len(rsvps)}")
        
        # Get all members
        members = User.query.filter_by(organization_id=event.organization_id).all()
        print(f"👥 Total members: {len(members)}")
        
        # Test PDF generation
        try:
            from services.pdf_service import PDFReportService
            
            print("\n🔄 Generating PDF report...")
            pdf_data = PDFReportService.generate_event_rsvp_report(event.id, event.organization_id)
            
            if pdf_data:
                print(f"✅ PDF generated successfully! Size: {len(pdf_data)} bytes")
                
                # Save to file for testing
                filename = f"test_rsvp_report_{event.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(pdf_data)
                print(f"💾 PDF saved as: {filename}")
                
                return True
            else:
                print("❌ PDF generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🧪 Testing PDF RSVP Report Generation")
    print("=" * 50)
    
    if test_pdf_generation():
        print("\n🎉 PDF generation test completed successfully!")
    else:
        print("\n❌ PDF generation test failed!")
