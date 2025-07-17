#!/usr/bin/env python3
"""
Script to check database data for analytics debugging
Run this on Railway or with production database access
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append('/app/backend')  # Railway path
sys.path.append('./backend')     # Local path

try:
    from models import db, User, Event, RSVP, Organization
    from flask import Flask
    from config import Config
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    def check_database_data():
        """Check what data exists in the database"""
        
        with app.app_context():
            print("🔍 Checking BandSync Database Data")
            print("=" * 50)
            
            # Check organizations
            orgs = Organization.query.all()
            print(f"Organizations: {len(orgs)}")
            for org in orgs:
                print(f"  - ID: {org.id}, Name: {org.name}")
            
            # Check users
            users = User.query.all()
            print(f"\nUsers: {len(users)}")
            for user in users:
                print(f"  - ID: {user.id}, Name: {user.name}, Role: {user.role}, Org: {user.organization_id}")
            
            # Check events
            events = Event.query.all()
            print(f"\nEvents: {len(events)}")
            for event in events:
                print(f"  - ID: {event.id}, Title: {event.title}, Date: {event.date}, Org: {event.organization_id}")
            
            # Check RSVPs
            rsvps = RSVP.query.all()
            print(f"\nRSVPs: {len(rsvps)}")
            for rsvp in rsvps:
                print(f"  - User: {rsvp.user_id}, Event: {rsvp.event_id}, Response: {rsvp.response}")
            
            # Check analytics for first organization
            if orgs:
                org_id = orgs[0].id
                print(f"\n📊 Analytics for Organization {org_id}:")
                
                # Test analytics queries
                from services.analytics_service import AnalyticsService
                
                try:
                    overview = AnalyticsService.get_organization_overview(org_id, 30)
                    print(f"Overview: {overview}")
                except Exception as e:
                    print(f"Analytics error: {e}")
            
            print("\n" + "=" * 50)
    
    if __name__ == "__main__":
        check_database_data()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("This script needs to be run in the Flask application context")
    print("Try running it on Railway or with proper database access")
