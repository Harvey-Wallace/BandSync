#!/usr/bin/env python3
"""
Test script to verify email service configuration
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/robertharvey/Documents/GitHub/BandSync/backend')

# Test the email service configuration
def test_email_service():
    print("Testing email service configuration...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv('/Users/robertharvey/Documents/GitHub/BandSync/backend/.env')
        print("✓ Environment variables loaded")
    except ImportError:
        print("⚠️  dotenv not available, using existing environment")
    
    # Check environment variables
    resend_api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('FROM_EMAIL', 'noreply@bandsync.com')
    
    print(f"RESEND_API_KEY: {'✓ Set' if resend_api_key else '✗ Not set'}")
    print(f"FROM_EMAIL: {from_email}")
    
    if not resend_api_key:
        print("❌ RESEND_API_KEY is not set in environment variables")
        return False
    
    # Test resend import
    try:
        import resend
        print("✓ Resend library imported successfully")
        
        # Test API key
        resend.api_key = resend_api_key
        print("✓ API key set in resend library")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with resend library: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_email_service()
    
    if success:
        print("\n✅ Email service appears to be configured correctly")
    else:
        print("\n❌ Email service configuration issues detected")
        
    sys.exit(0 if success else 1)
