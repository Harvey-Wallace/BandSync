#!/usr/bin/env python3
"""
Test script to verify email template time display fixes
"""

import os
import sys
from datetime import datetime, time
from jinja2 import Environment, FileSystemLoader

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

def test_email_templates():
    """Test the email templates with sample data"""
    
    # Set up Jinja2 environment
    template_dir = os.path.join(backend_dir, 'templates', 'email')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Create sample event data
    class MockEvent:
        def __init__(self):
            self.title = "CBBB: Rehearsal"
            self.date = datetime(2025, 8, 31, 12, 0, 0)  # Sunday, August 31, 2025 at 12:00 PM
            self.start_time = time(14, 30, 0)  # 2:30 PM
            self.end_time = time(16, 30, 0)    # 4:30 PM
            self.arrive_by_time = time(14, 15, 0)  # 2:15 PM
            self.location_address = "Selly Park Tavern, 592 Pershore Rd, Birmingham B29 7HQ, UK"
            self.type = "Rehearsal"
            self.description = "CBBB: Rehearsal"
            
    class MockUser:
        def __init__(self):
            self.name = "Test User"
            self.email = "test@example.com"
            
    class MockOrganization:
        def __init__(self):
            self.name = "Test Band"
    
    # Create mock objects
    event = MockEvent()
    user = MockUser()
    organization = MockOrganization()
    
    templates_to_test = [
        'event_reminder.html',
        'new_event_notification.html', 
        'rsvp_deadline_reminder.html'
    ]
    
    print("Testing email template time display fixes...\n")
    
    for template_name in templates_to_test:
        try:
            template = env.get_template(template_name)
            
            # Render template with sample data
            html_content = template.render(
                event=event,
                user=user,
                organization=organization,
                days_before=1,
                rsvp_url="https://example.com/events/1",
                base_url="https://example.com"
            )
            
            print(f"✅ {template_name} rendered successfully")
            
            # Check if proper time fields are being used
            if "2:30 PM" in html_content and "4:30 PM" in html_content:
                print(f"   ✅ Correct start/end times displayed (2:30 PM - 4:30 PM)")
            elif "12:00 AM" in html_content:
                print(f"   ❌ Still showing 12:00 AM - old date.time format detected")
            else:
                print(f"   ⚠️  Time format may need verification")
                
            if "2:15 PM" in html_content:
                print(f"   ✅ Arrive by time displayed correctly (2:15 PM)")
                
        except Exception as e:
            print(f"❌ {template_name} failed to render: {str(e)}")
        
        print()
    
    print("Test complete!")

if __name__ == "__main__":
    test_email_templates()
