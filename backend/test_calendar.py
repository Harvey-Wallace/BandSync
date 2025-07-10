"""
Test calendar feed generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models import db, Organization, Event, User
from services.calendar_service import calendar_service
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def test_calendar_generation():
    """Test calendar feed generation with sample data"""
    with app.app_context():
        # Get first organization
        org = Organization.query.first()
        if not org:
            print("No organizations found. Please create an organization first.")
            return
        
        print(f"Testing calendar generation for organization: {org.name}")
        
        # Get events for this organization
        events = Event.query.filter_by(organization_id=org.id, is_template=False).all()
        print(f"Found {len(events)} events")
        
        if events:
            # Generate calendar feed
            try:
                ical_data = calendar_service.generate_organization_calendar(org.id)
                print(f"Calendar feed generated successfully!")
                print(f"Feed size: {len(ical_data)} bytes")
                
                # Count events in feed
                event_count = ical_data.count(b'BEGIN:VEVENT')
                print(f"Events in feed: {event_count}")
                
                # Get calendar URL
                calendar_url = calendar_service.get_calendar_url('org', org.id)
                print(f"Calendar URL: {calendar_url}")
                
                # Show sample of the feed
                print("\nSample feed data:")
                print(ical_data[:500].decode('utf-8', errors='ignore'))
                
                # Test subscription info
                subscription_info = calendar_service.get_calendar_subscription_info(org.id)
                print(f"\nAvailable calendar feeds:")
                for feed_type, feed_info in subscription_info.items():
                    if isinstance(feed_info, dict):
                        print(f"  {feed_type}: {feed_info.get('name', 'Unknown')}")
                    elif isinstance(feed_info, list):
                        print(f"  {feed_type}: {len(feed_info)} items")
                
            except Exception as e:
                print(f"Error generating calendar: {e}")
                
        else:
            print("No events found. Calendar feed will be empty.")

if __name__ == '__main__':
    test_calendar_generation()
