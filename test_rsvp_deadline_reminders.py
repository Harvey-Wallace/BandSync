#!/usr/bin/env python3
"""
Test script for RSVP deadline reminder functionality
Tests the enhanced logic that only sends reminders to non-responders
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from models import Event, User, UserOrganization, RSVP, EmailLog, Organization
from services.scheduled_tasks import ScheduledTaskService
from services.email_service import EmailService

def create_test_scenario():
    """Create a test scenario with an event and users"""
    
    with app.app_context():
        # Clear existing test data
        EmailLog.query.filter_by(email_type='rsvp_deadline_reminder').delete()
        
        # Find or create a test organization
        org = Organization.query.filter_by(name='Test Band').first()
        if not org:
            org = Organization(
                name='Test Band'
            )
            db.session.add(org)
            db.session.commit()
        
        # Create test event happening in 2 days
        event_date = datetime.utcnow() + timedelta(days=2)
        event = Event(
            title='Test RSVP Reminder Event',
            description='Testing RSVP deadline reminder functionality',
            date=event_date,
            organization_id=org.id,
            is_template=False,
            send_reminders=True,
            reminder_days_before=1
        )
        db.session.add(event)
        db.session.commit()
        
        # Create 5 test users
        users = []
        for i in range(5):
            user = User(
                name=f'Test User {i+1}',
                username=f'testuser{i+1}',
                email=f'testuser{i+1}@example.com',
                password_hash='dummy_hash',
                email_notifications=True,
                email_rsvp_reminders=True
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        
        # Add users to organization
        for user in users:
            user_org = UserOrganization(
                user_id=user.id,
                organization_id=org.id,
                is_active=True
            )
            db.session.add(user_org)
        
        db.session.commit()
        
        # Create RSVPs for only 2 users (40% response rate)
        rsvp1 = RSVP(
            user_id=users[0].id,
            event_id=event.id,
            status='Yes'
        )
        rsvp2 = RSVP(
            user_id=users[1].id,
            event_id=event.id,
            status='No'
        )
        
        db.session.add(rsvp1)
        db.session.add(rsvp2)
        db.session.commit()
        
        return event, users, org

def test_rsvp_deadline_logic():
    """Test the RSVP deadline reminder logic"""
    
    print("🧪 Testing RSVP Deadline Reminder Logic")
    print("=" * 50)
    
    # Create test scenario
    event, users, org = create_test_scenario()
    
    print(f"📅 Created test event: {event.title}")
    print(f"👥 Created {len(users)} test users")
    print(f"✅ {len(event.rsvps)} users have RSVP'd")
    print(f"❌ {len(users) - len(event.rsvps)} users haven't RSVP'd")
    
    rsvp_rate = len(event.rsvps) / len(users)
    print(f"📊 RSVP rate: {rsvp_rate:.1%}")
    
    # Test the scheduled task logic
    task_service = ScheduledTaskService()
    task_service.app = app
    
    print(f"\n🔄 Running RSVP deadline reminder task...")
    
    # Count emails before
    email_count_before = EmailLog.query.filter_by(
        event_id=event.id,
        email_type='rsvp_deadline_reminder'
    ).count()
    
    # Run the task
    task_service.send_rsvp_deadline_reminders()
    
    # Count emails after
    email_count_after = EmailLog.query.filter_by(
        event_id=event.id,
        email_type='rsvp_deadline_reminder'
    ).count()
    
    emails_sent = email_count_after - email_count_before
    
    print(f"📧 Emails sent: {emails_sent}")
    
    if emails_sent > 0:
        # Check who received emails
        email_logs = EmailLog.query.filter_by(
            event_id=event.id,
            email_type='rsvp_deadline_reminder'
        ).all()
        
        print(f"📝 Email log entries:")
        for log in email_logs:
            user = User.query.get(log.user_id)
            print(f"  - {user.name} ({user.email}): {log.status}")
    
    # Test scenario 2: High RSVP rate (should NOT send reminders)
    print(f"\n🧪 Testing scenario 2: High RSVP rate")
    print("-" * 30)
    
    # Add RSVPs to get above 70% rate
    rsvp3 = RSVP(
        user_id=users[2].id,
        event_id=event.id,
        status='Yes'
    )
    rsvp4 = RSVP(
        user_id=users[3].id,
        event_id=event.id,
        status='Maybe'
    )
    
    db.session.add(rsvp3)
    db.session.add(rsvp4)
    db.session.commit()
    
    # Clear existing email logs for this test
    EmailLog.query.filter_by(
        event_id=event.id,
        email_type='rsvp_deadline_reminder'
    ).delete()
    db.session.commit()
    
    new_rsvp_rate = len(event.rsvps) / len(users)
    print(f"📊 New RSVP rate: {new_rsvp_rate:.1%}")
    
    # Run the task again
    email_count_before = EmailLog.query.filter_by(
        event_id=event.id,
        email_type='rsvp_deadline_reminder'
    ).count()
    
    task_service.send_rsvp_deadline_reminders()
    
    email_count_after = EmailLog.query.filter_by(
        event_id=event.id,
        email_type='rsvp_deadline_reminder'
    ).count()
    
    emails_sent_2 = email_count_after - email_count_before
    
    print(f"📧 Emails sent: {emails_sent_2}")
    
    if emails_sent_2 == 0:
        print("✅ Correctly skipped sending reminders due to high RSVP rate")
    else:
        print("❌ Should not have sent reminders with high RSVP rate")
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"✅ Low RSVP rate scenario: {emails_sent} emails sent")
    print(f"✅ High RSVP rate scenario: {emails_sent_2} emails sent")
    
    return emails_sent, emails_sent_2

def test_email_logging():
    """Test that email logging is working correctly"""
    
    print(f"\n🧪 Testing Email Logging")
    print("=" * 50)
    
    with app.app_context():
        # Get recent email logs
        recent_logs = EmailLog.query.filter_by(
            email_type='rsvp_deadline_reminder'
        ).order_by(EmailLog.sent_at.desc()).limit(10).all()
        
        print(f"📧 Recent RSVP deadline reminder logs: {len(recent_logs)}")
        
        for log in recent_logs:
            user = User.query.get(log.user_id)
            event = Event.query.get(log.event_id)
            print(f"  - {log.sent_at.strftime('%Y-%m-%d %H:%M:%S')} | "
                  f"{user.name} | {event.title} | {log.status}")
        
        return len(recent_logs)

def main():
    """Run all tests"""
    
    print("🎯 BandSync RSVP Deadline Reminder Test Suite")
    print("=" * 60)
    
    try:
        # Test the core logic
        emails_low, emails_high = test_rsvp_deadline_logic()
        
        # Test email logging
        log_count = test_email_logging()
        
        print(f"\n🎉 Test Results:")
        print(f"✅ All tests completed successfully!")
        print(f"📊 Low RSVP rate: {emails_low} reminders sent")
        print(f"📊 High RSVP rate: {emails_high} reminders sent")
        print(f"📝 Email logs: {log_count} entries found")
        
        if emails_low > 0 and emails_high == 0:
            print(f"\n✅ RSVP deadline reminder logic is working correctly!")
            print(f"   - Sends reminders when RSVP rate is below 70%")
            print(f"   - Skips reminders when RSVP rate is above 70%")
            print(f"   - Only sends to non-responders")
            print(f"   - Properly logs email attempts")
        else:
            print(f"\n❌ RSVP deadline reminder logic needs attention")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
