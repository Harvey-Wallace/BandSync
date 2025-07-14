#!/usr/bin/env python3
"""
Final Domain Verification Test
Test sending emails to multiple different email addresses
"""

import os
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.services.email_service import EmailService

def test_domain_verification():
    print("🧪 Testing Domain Verification - bandsync.co.uk")
    print("=" * 50)
    
    email_service = EmailService()
    
    print(f"✅ FROM_EMAIL: {email_service.from_email}")
    print(f"✅ FROM_NAME: {email_service.from_name}")
    print(f"✅ API_KEY: {email_service.api_key[:10]}...")
    print()
    
    # Test emails to different providers
    test_emails = [
        "rob@harvey-wallace.co.uk",  # Your primary email
        "bobbyharvey12@gmail.com",   # Gmail
    ]
    
    print("📧 Testing email delivery to different providers...")
    
    for email in test_emails:
        print(f"Sending to: {email}")
        
        success = email_service._send_email(
            to_emails=[email],
            subject="BandSync Domain Verification Test",
            html_content=f"""
            <html>
            <body>
                <h1>🎉 Domain Verification Success!</h1>
                <p>Hello from BandSync!</p>
                <p>This email was sent from <strong>noreply@bandsync.co.uk</strong></p>
                <p>✅ Your domain is verified and working correctly!</p>
                <p>✅ You can now send emails to anyone within the app!</p>
                <hr>
                <p><small>Sent to: {email}</small></p>
            </body>
            </html>
            """,
            text_content=f"""
            🎉 Domain Verification Success!
            
            Hello from BandSync!
            
            This email was sent from noreply@bandsync.co.uk
            
            ✅ Your domain is verified and working correctly!
            ✅ You can now send emails to anyone within the app!
            
            Sent to: {email}
            """
        )
        
        if success:
            print(f"  ✅ SUCCESS - Email sent to {email}")
        else:
            print(f"  ❌ FAILED - Could not send to {email}")
        print()
    
    print("🎯 Domain verification test complete!")
    print("Check your inboxes for the test emails.")

if __name__ == "__main__":
    test_domain_verification()
