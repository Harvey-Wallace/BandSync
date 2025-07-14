#!/usr/bin/env python3
"""
Test script for Resend email service
Run this to test email functionality after setting up Resend API key
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up environment variables
os.environ['RESEND_API_KEY'] = 're_F2Q9H9qQ_G5EMpEAXRWCKKZGfG5pJvPbn'  # Your actual API key
os.environ['FROM_EMAIL'] = 'noreply@bandsync.co.uk'  # Your verified domain
os.environ['FROM_NAME'] = 'BandSync Test'
os.environ['BASE_URL'] = 'https://bandsync-production.up.railway.app'

try:
    from services.email_service import EmailService
    
    # Initialize email service
    email_service = EmailService()
    
    # Test basic email sending
    print("Testing Resend email service...")
    
    # Simple HTML email
    html_content = """
    <html>
    <body>
        <h1>BandSync Email Test</h1>
        <p>This is a test email sent from BandSync using Resend.</p>
        <p>Time: {}</p>
        <p>If you receive this, the email service is working correctly!</p>
    </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    text_content = """
    BandSync Email Test
    
    This is a test email sent from BandSync using Resend.
    Time: {}
    
    If you receive this, the email service is working correctly!
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Replace with your test email
    test_email = input("Enter your test email address: ").strip()
    
    if not test_email:
        print("No email address provided. Exiting.")
        sys.exit(1)
    
    print(f"Sending test email to: {test_email}")
    
    # Send test email
    success = email_service._send_email(
        to_emails=[test_email],
        subject="BandSync Email Test - Resend Integration",
        html_content=html_content,
        text_content=text_content
    )
    
    if success:
        print("✅ Email sent successfully!")
        print("Check your inbox for the test email.")
    else:
        print("❌ Email sending failed.")
        print("Check your Resend API key and from email configuration.")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory.")
    print("Also ensure the resend package is installed: pip install resend")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your Resend API key is set correctly.")
