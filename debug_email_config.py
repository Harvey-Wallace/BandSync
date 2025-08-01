#!/usr/bin/env python3
"""
Debug email service configuration
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("🔍 Email Service Configuration Debug")
print("=" * 50)

# Check environment variables
print("\n📋 Environment Variables:")
resend_key = os.environ.get('RESEND_API_KEY', 'NOT SET')
from_email = os.environ.get('FROM_EMAIL', 'NOT SET')
from_name = os.environ.get('FROM_NAME', 'NOT SET')
base_url = os.environ.get('BASE_URL', 'NOT SET')

print(f"RESEND_API_KEY: {'SET (starts with ' + resend_key[:5] + ')' if resend_key != 'NOT SET' else 'NOT SET'}")
print(f"FROM_EMAIL: {from_email}")
print(f"FROM_NAME: {from_name}")
print(f"BASE_URL: {base_url}")

# Try to load .env file
print("\n📁 Checking .env file:")
env_file = os.path.join(os.path.dirname(__file__), 'backend', '.env')
if os.path.exists(env_file):
    print(f"✅ .env file found at: {env_file}")
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ .env file loaded")
        
        # Re-check environment variables after loading .env
        print("\n📋 Environment Variables (after .env):")
        resend_key = os.environ.get('RESEND_API_KEY', 'NOT SET')
        from_email = os.environ.get('FROM_EMAIL', 'NOT SET')
        from_name = os.environ.get('FROM_NAME', 'NOT SET')
        base_url = os.environ.get('BASE_URL', 'NOT SET')
        
        print(f"RESEND_API_KEY: {'SET (starts with ' + resend_key[:5] + ')' if resend_key != 'NOT SET' else 'NOT SET'}")
        print(f"FROM_EMAIL: {from_email}")
        print(f"FROM_NAME: {from_name}")
        print(f"BASE_URL: {base_url}")
        
    except ImportError:
        print("⚠️  python-dotenv not available")
else:
    print(f"❌ .env file not found at: {env_file}")

# Test EmailService initialization
print("\n🔧 Testing EmailService:")
try:
    from services.email_service import EmailService
    email_service = EmailService()
    
    print(f"✅ EmailService created")
    print(f"Has client: {bool(email_service.client)}")
    print(f"API Key configured: {bool(email_service.api_key)}")
    print(f"From email: {email_service.from_email}")
    print(f"From name: {email_service.from_name}")
    print(f"Base URL: {email_service.base_url}")
    
    if not email_service.client:
        print("❌ EmailService client is not initialized - missing API key")
    else:
        print("✅ EmailService is properly configured")
        
        # Test resend library
        print("\n🧪 Testing Resend library:")
        try:
            import resend
            print(f"✅ Resend library imported")
            print(f"Resend API key set: {bool(resend.api_key)}")
            
            # Try to make a simple API call to test the key
            if resend.api_key:
                try:
                    # This should work with a valid API key
                    response = resend.Emails.send({
                        "from": "test@test.com",
                        "to": "test@test.com",
                        "subject": "Test",
                        "html": "<p>Test</p>"
                    })
                    print("📧 Resend API test: Response received (may be error due to invalid emails, but API key works)")
                except Exception as e:
                    error_msg = str(e)
                    if "API key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                        print(f"❌ Resend API key is invalid: {error_msg}")
                    else:
                        print(f"✅ Resend API key is valid (got expected error: {error_msg})")
            
        except ImportError:
            print("❌ Resend library not available")
        except Exception as e:
            print(f"❌ Error testing Resend: {e}")
    
except Exception as e:
    print(f"❌ Error creating EmailService: {e}")

print("\n" + "=" * 50)
print("Debug complete!")
