#!/usr/bin/env python3
"""
Test Flask email service integration
"""

import os
import sys
sys.path.insert(0, 'backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.services.email_service import EmailService

def test_flask_email_service():
    print("Testing Flask EmailService integration...")
    
    # Create email service instance
    email_service = EmailService()
    
    # Check if service is configured
    if not email_service.client:
        print("❌ Email service not configured")
        return False
    
    print(f"✅ Email service configured")
    print(f"API Key: {email_service.api_key[:10]}...")
    print(f"From Email: {email_service.from_email}")
    print(f"From Name: {email_service.from_name}")
    
    # Test sending email
    test_email = "rob@harvey-wallace.co.uk"  # Your verified email
    
    html_content = """
    <html>
    <body>
        <h1>BandSync Flask Integration Test</h1>
        <p>This email was sent from the Flask EmailService class.</p>
        <p>If you receive this, the integration is working correctly!</p>
    </body>
    </html>
    """
    
    text_content = "BandSync Flask Integration Test\n\nThis email was sent from the Flask EmailService class.\n\nIf you receive this, the integration is working correctly!"
    
    print(f"Sending test email to: {test_email}")
    
    success = email_service._send_email(
        to_emails=[test_email],
        subject="BandSync Flask Integration Test",
        html_content=html_content,
        text_content=text_content
    )
    
    if success:
        print("✅ Flask email service integration working!")
        return True
    else:
        print("❌ Flask email service integration failed")
        return False

if __name__ == "__main__":
    test_flask_email_service()
