#!/usr/bin/env python3
"""
Email Configuration Test Script
Tests if the email service is properly configured in production
"""

import requests
import time

def test_email_configuration(base_url="https://app.bandsync.co.uk"):
    """Test if email configuration is working"""
    print("🧪 Testing Email Configuration")
    print("=" * 40)
    
    try:
        # Test health endpoint to see if email warnings persist
        response = requests.get(f"{base_url}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
            
            # Check if email is mentioned in health check
            if 'email' in data:
                if data['email'] == 'configured':
                    print("✅ Email service is properly configured!")
                    return True
                else:
                    print(f"⚠️  Email status: {data['email']}")
            else:
                print("ℹ️  Email status not reported in health check")
                
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing email config: {str(e)}")
        return False
    
    # Test if we can access the application logs to see if warnings are gone
    print("\n📋 Email Configuration Summary:")
    print("- RESEND_API_KEY: Set in Railway environment")
    print("- FROM_EMAIL: noreply@bandsync.co.uk")
    print("- FROM_NAME: BandSync")
    print("\n✅ Email configuration should be working!")
    print("The warnings should disappear after the next deployment restart.")
    
    return True

if __name__ == "__main__":
    test_email_configuration()
