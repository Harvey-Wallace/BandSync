#!/usr/bin/env python3
"""
Test script to verify Railway email service after environment variables are set
"""

import requests
import json

import requests
import time

# Railway app URL
RAILWAY_URL = "https://app.bandsync.co.uk"
API_URL = f"{RAILWAY_URL}/api"

def test_email_service():
    """Test email service functionality"""
    print("🔍 Testing Railway Email Service")
    print("=" * 40)
    
    # Test admin test notification endpoint
    print("\n📧 Testing admin test notification...")
    
    # First try to login as an admin to get token
    print("1. Attempting admin login...")
    login_data = {
        "username": "Harvey258",  # Super admin
        "password": "password"    # Use known password
    }
    
    try:
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            
            # Handle multiple organizations
            if login_result.get('multiple_organizations'):
                orgs = login_result['organizations']
                # Select first organization
                org_login_data = {**login_data, "organization_id": orgs[0]['id']}
                org_response = requests.post(f"{API_URL}/auth/login", json=org_login_data)
                
                if org_response.status_code == 200:
                    token_data = org_response.json()
                    token = token_data['access_token']
                    print(f"✅ Logged in to: {orgs[0]['name']}")
                else:
                    print(f"❌ Organization login failed: {org_response.status_code}")
                    return False
            else:
                token = login_result['access_token']
                print("✅ Direct login successful")
            
            # Test email service
            print("\n2. Testing email service...")
            headers = {"Authorization": f"Bearer {token}"}
            
            email_response = requests.post(
                f"{API_URL}/admin/send-test-notification",
                headers=headers
            )
            
            print(f"Email test status: {email_response.status_code}")
            
            if email_response.status_code == 200:
                result = email_response.json()
                print(f"✅ Email service working: {result.get('message', 'Success')}")
                return True
            else:
                try:
                    error = email_response.json()
                    print(f"❌ Email test failed: {error}")
                except:
                    print(f"❌ Email test failed: {email_response.text}")
                return False
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            try:
                error = login_response.json()
                print(f"Error: {error}")
            except:
                print(f"Error text: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_password_reset():
    """Test password reset email functionality"""
    print("\n📧 Testing password reset email...")
    
    reset_data = {
        "email": "rob@harvey-wallace.co.uk"  # Use your verified email
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/password-reset-request", json=reset_data)
        
        print(f"Password reset status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Password reset email sent: {result.get('msg', 'Success')}")
            return True
        else:
            try:
                error = response.json()
                print(f"❌ Password reset failed: {error}")
            except:
                print(f"❌ Password reset failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Password reset test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Railway Email Service Test")
    print("=" * 50)
    
    print("\n📋 This test will verify:")
    print("- Email service configuration")
    print("- Admin test notification")
    print("- Password reset emails")
    
    # Test admin email
    admin_test = test_email_service()
    
    # Test password reset
    reset_test = test_password_reset()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Admin Email Test: {'✅ PASS' if admin_test else '❌ FAIL'}")
    print(f"Password Reset Test: {'✅ PASS' if reset_test else '❌ FAIL'}")
    
    if admin_test and reset_test:
        print("\n🎉 All email tests passed! Your email service is working.")
    else:
        print("\n🚨 Some email tests failed. Check Railway environment variables:")
        print("   - RESEND_API_KEY")
        print("   - FROM_EMAIL") 
        print("   - FROM_NAME")
        print("   - BASE_URL")

if __name__ == "__main__":
    main()
