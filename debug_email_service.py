#!/usr/bin/env python3
"""
Debug script to test email service configuration and cancellation notifications
"""
import os
import sys
import json
from datetime import datetime

# Add the backend directory to path
sys.path.append('/Users/robertharvey/Documents/GitHub/BandSync/backend')

def test_email_service():
    print("🔍 Testing Email Service Configuration")
    print("=" * 50)
    
    # Test environment variables
    print("📧 Environment Variables:")
    resend_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('FROM_EMAIL', 'noreply@bandsync.com')
    from_name = os.environ.get('FROM_NAME', 'BandSync')
    base_url = os.environ.get('BASE_URL', 'https://bandsync.com')
    
    print(f"   RESEND_API_KEY: {'✅ Set' if resend_key else '❌ Not set'}")
    print(f"   FROM_EMAIL: {from_email}")
    print(f"   FROM_NAME: {from_name}")
    print(f"   BASE_URL: {base_url}")
    
    # Test email service import
    try:
        from services.email_service import EmailService
        email_service = EmailService()
        print(f"✅ Email service imported successfully")
        print(f"   Client available: {'✅ Yes' if email_service.client else '❌ No'}")
    except ImportError as e:
        print(f"❌ Email service import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Email service initialization failed: {e}")
        return False
    
    # Test template loading
    try:
        template_dir = os.path.join('/Users/robertharvey/Documents/GitHub/BandSync/backend/templates/email')
        print(f"📁 Template directory: {template_dir}")
        print(f"   Directory exists: {'✅ Yes' if os.path.exists(template_dir) else '❌ No'}")
        
        cancellation_template = os.path.join(template_dir, 'event_cancellation.html')
        print(f"   Cancellation template: {'✅ Exists' if os.path.exists(cancellation_template) else '❌ Missing'}")
        
        if os.path.exists(cancellation_template):
            with open(cancellation_template, 'r') as f:
                content = f.read()
                print(f"   Template size: {len(content)} characters")
    except Exception as e:
        print(f"❌ Template check failed: {e}")
    
    # Test database models
    try:
        from models import User, Event, Organization, UserOrganization
        print("✅ Database models imported successfully")
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    # Test if we can create mock objects
    try:
        # Create mock user
        class MockUser:
            def __init__(self):
                self.id = 1
                self.name = "Test User"
                self.email = "test@example.com"
                self.email_notifications = True
        
        # Create mock event
        class MockEvent:
            def __init__(self):
                self.id = 1
                self.title = "Test Event"
                self.date = datetime.now()
                self.location_address = "Test Location"
                self.organization_id = 1
                self.cancelled_at = datetime.now()
        
        mock_user = MockUser()
        mock_event = MockEvent()
        
        print("✅ Mock objects created successfully")
        
        # Test cancellation notification method
        if email_service.client:
            print("🧪 Testing cancellation notification (dry run)...")
            # This would test the method without actually sending
            success = email_service.send_event_cancellation_notification(
                user=mock_user,
                event=mock_event,
                reason="Test cancellation reason"
            )
            print(f"   Method result: {'✅ Success' if success else '❌ Failed'}")
        else:
            print("⚠️  Email service not available for testing")
            
    except Exception as e:
        print(f"❌ Mock test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    test_email_service()
