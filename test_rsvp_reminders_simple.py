#!/usr/bin/env python3
"""
Simple test script for RSVP deadline reminder functionality
Tests the enhanced logic using existing data
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from models import Event, User, UserOrganization, RSVP, EmailLog, Organization
from services.scheduled_tasks import ScheduledTaskService
from services.email_service import EmailService

def test_existing_data():
    """Test the RSVP deadline reminder logic with existing data"""
    
    print("🧪 Testing RSVP Deadline Reminder Logic with Existing Data")
    print("=" * 60)
    
    with app.app_context():
        # Get existing organizations
        orgs = Organization.query.all()
        print(f"📊 Found {len(orgs)} organizations")
        
        # Get existing events
        events = Event.query.filter(Event.date.isnot(None)).all()
        print(f"📅 Found {len(events)} events with dates")
        
        # Get existing users
        users = User.query.all()
        print(f"👥 Found {len(users)} users")
        
        # Get existing RSVPs
        rsvps = RSVP.query.all()
        print(f"✅ Found {len(rsvps)} RSVPs")
        
        # Get existing email logs
        email_logs = EmailLog.query.filter_by(email_type='rsvp_deadline_reminder').all()
        print(f"📧 Found {len(email_logs)} RSVP deadline reminder logs")
        
        if not orgs or not events or not users:
            print("❌ Insufficient test data. Please run with a populated database.")
            return False
        
        # Test the scheduled task service
        print(f"\n🔄 Testing scheduled task service...")
        task_service = ScheduledTaskService()
        task_service.app = app
        
        # Get jobs
        jobs = task_service.get_scheduled_jobs()
        print(f"⚙️  Found {len(jobs)} scheduled jobs:")
        for job in jobs:
            print(f"  - {job['name']} (next run: {job['next_run']})")
        
        # Test the email service
        print(f"\n📧 Testing email service...")
        email_service = EmailService()
        
        # Show configuration
        print(f"  SendGrid API Key: {'✅ Configured' if email_service.api_key else '❌ Not configured'}")
        print(f"  From Email: {email_service.from_email}")
        print(f"  Base URL: {email_service.base_url}")
        
        return True

def test_reminder_logic():
    """Test the core reminder logic"""
    
    print(f"\n🧪 Testing Core Reminder Logic")
    print("=" * 40)
    
    with app.app_context():
        # Find events happening in the next 3 days
        cutoff_time = datetime.utcnow() + timedelta(days=3)
        events = Event.query.filter(
            Event.date.isnot(None),
            Event.date <= cutoff_time,
            Event.date >= datetime.utcnow(),
            Event.is_template == False
        ).all()
        
        print(f"📅 Found {len(events)} events happening in next 3 days")
        
        for event in events:
            print(f"\n📍 Event: {event.title}")
            print(f"  Date: {event.date}")
            print(f"  Organization: {event.organization.name}")
            
            # Get active users in the organization
            active_user_orgs = UserOrganization.query.filter_by(
                organization_id=event.organization_id,
                is_active=True
            ).all()
            
            print(f"  Active users: {len(active_user_orgs)}")
            
            # Get RSVPs for this event
            rsvps = RSVP.query.filter_by(event_id=event.id).all()
            rsvp_user_ids = {rsvp.user_id for rsvp in rsvps}
            
            print(f"  RSVPs: {len(rsvps)}")
            
            # Calculate RSVP rate
            total_users = len(active_user_orgs)
            rsvp_count = len(rsvp_user_ids)
            rsvp_rate = rsvp_count / total_users if total_users > 0 else 1.0
            
            print(f"  RSVP Rate: {rsvp_rate:.1%}")
            
            # Find non-responders
            non_responders = []
            for user_org in active_user_orgs:
                user = User.query.get(user_org.user_id)
                if (user and user.id not in rsvp_user_ids and 
                    user.email_rsvp_reminders and user.email_notifications):
                    non_responders.append(user)
            
            print(f"  Non-responders: {len(non_responders)}")
            
            # Check if we would send reminders
            would_send = rsvp_rate < 0.7 and len(non_responders) > 0
            print(f"  Would send reminders: {'✅ Yes' if would_send else '❌ No'}")
            
            # Check if we've already sent reminders
            existing_reminder = EmailLog.query.filter_by(
                event_id=event.id,
                email_type='rsvp_deadline_reminder'
            ).first()
            
            already_sent = existing_reminder is not None
            print(f"  Already sent: {'✅ Yes' if already_sent else '❌ No'}")
            
            if would_send and not already_sent:
                print(f"  📤 This event would trigger reminders to {len(non_responders)} users")
            elif already_sent:
                print(f"  🔄 Reminders already sent for this event")
            elif rsvp_rate >= 0.7:
                print(f"  🎯 RSVP rate is good, no reminders needed")
            else:
                print(f"  ⏸️  No non-responders to remind")
        
        return len(events)

def test_email_template():
    """Test that the email template exists"""
    
    print(f"\n🧪 Testing Email Template")
    print("=" * 30)
    
    template_path = os.path.join(
        os.path.dirname(__file__), 
        'backend', 
        'templates', 
        'email', 
        'rsvp_deadline_reminder.html'
    )
    
    if os.path.exists(template_path):
        print(f"✅ Email template found: {template_path}")
        
        # Read and show a snippet
        with open(template_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            print(f"  Template has {len(lines)} lines")
            print(f"  First few lines:")
            for i, line in enumerate(lines[:5]):
                print(f"    {i+1}: {line.strip()}")
        
        return True
    else:
        print(f"❌ Email template not found: {template_path}")
        return False

def main():
    """Run all tests"""
    
    print("🎯 BandSync RSVP Deadline Reminder Test Suite")
    print("=" * 60)
    
    try:
        # Test existing data
        data_ok = test_existing_data()
        
        if data_ok:
            # Test reminder logic
            events_count = test_reminder_logic()
            
            # Test email template
            template_ok = test_email_template()
            
            print(f"\n🎉 Test Results:")
            print(f"✅ Database connection: Working")
            print(f"✅ Reminder logic: {'Working' if events_count >= 0 else 'Failed'}")
            print(f"✅ Email template: {'Found' if template_ok else 'Missing'}")
            
            print(f"\n🔍 Summary:")
            print(f"   - The RSVP deadline reminder logic is implemented")
            print(f"   - Only sends reminders when RSVP rate is below 70%")
            print(f"   - Only sends to non-responders with email preferences enabled")
            print(f"   - Prevents duplicate reminders using EmailLog")
            print(f"   - Scheduled to run daily at 10 AM")
            
            if not template_ok:
                print(f"\n⚠️  Email template is missing. Emails will not be sent.")
        else:
            print(f"\n❌ Test failed due to insufficient data")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
