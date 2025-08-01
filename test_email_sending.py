#!/usr/bin/env python3
"""
Test the actual email sending functionality
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("📧 Testing Email Sending")
print("=" * 40)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))
    print("✅ Environment variables loaded")
except ImportError:
    print("⚠️  python-dotenv not available")

try:
    from services.email_service import email_service
    
    print(f"📋 Email Service Status:")
    print(f"  - Client configured: {bool(email_service.client)}")
    print(f"  - From email: {email_service.from_email}")
    print(f"  - From name: {email_service.from_name}")
    print(f"  - Base URL: {email_service.base_url}")
    
    if not email_service.client:
        print("❌ Email service not configured - cannot test sending")
        sys.exit(1)
    
    # Test sending a simple email
    test_email = "rob@harvey-wallace.co.uk"  # Your email
    
    print(f"\n🧪 Sending test email to {test_email}...")
    
    success = email_service._send_email(
        to_emails=[test_email],
        subject="BandSync Email Test - Local Testing",
        html_content="""
        <h2>Email Test</h2>
        <p>This is a test email from the BandSync email service.</p>
        <p>If you receive this, the email service is working correctly!</p>
        <p><strong>Timestamp:</strong> """ + str(os.popen('date').read().strip()) + """</p>
        """,
        text_content="BandSync email test - if you receive this, the service is working!"
    )
    
    if success:
        print("✅ Email sent successfully!")
        print("Check your inbox for the test email.")
    else:
        print("❌ Email sending failed.")
        print("This could be due to:")
        print("  - Invalid API key")
        print("  - Network issues")
        print("  - Resend service issues")
        print("  - Email domain not verified")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThis could be due to:")
    print("  - Missing dependencies (run: pip install resend)")
    print("  - Missing environment variables")
    print("  - Import path issues")

print("\n" + "=" * 40)
