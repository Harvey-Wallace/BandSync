#!/usr/bin/env python3
"""
Test the new email and magic link authentication features
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
API_URL = "http://localhost:5000/api"  # Local backend for testing

def test_email_login():
    """Test email-based login functionality"""
    print("\n📧 Testing Email Login...")
    print("=" * 50)
    
    # Test data - you can modify these
    test_credentials = [
        {"email": "rob@harvey-wallace.co.uk", "password": "password"},
        {"username": "Harvey258", "password": "password"}  # Fallback to username
    ]
    
    for creds in test_credentials:
        print(f"\n🔐 Testing login with: {list(creds.keys())[0]} = {list(creds.values())[0]}")
        
        try:
            response = requests.post(f"{API_URL}/auth/login", json=creds, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Login successful!")
                print(f"  - Role: {result.get('role', 'Unknown')}")
                print(f"  - Organization: {result.get('organization', 'Unknown')}")
                print(f"  - Token received: {'Yes' if result.get('access_token') else 'No'}")
                return True
            else:
                try:
                    error = response.json()
                    print(f"❌ Login failed: {error.get('msg', 'Unknown error')}")
                except:
                    print(f"❌ Login failed: HTTP {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - is the backend running on {API_URL}?")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def test_magic_link_request():
    """Test magic link request functionality"""
    print("\n🪄 Testing Magic Link Request...")
    print("=" * 50)
    
    test_email = "rob@harvey-wallace.co.uk"  # Use your verified email
    
    try:
        response = requests.post(f"{API_URL}/auth/magic-link-request", 
                               json={"email": test_email}, 
                               timeout=10)
        
        print(f"Magic link request status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Magic link request successful: {result.get('msg', 'Success')}")
            print("📧 Check your email for the magic login link!")
            return True
        else:
            try:
                error = response.json()
                print(f"❌ Magic link request failed: {error}")
            except:
                print(f"❌ Magic link request failed: HTTP {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - is the backend running on {API_URL}?")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def test_backend_health():
    """Test if the backend is running and accessible"""
    print("\n🏥 Testing Backend Health...")
    print("=" * 50)
    
    try:
        # Try to hit a simple endpoint
        response = requests.get(f"http://localhost:5000/", timeout=5)
        print(f"✅ Backend is accessible at {API_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Backend is not accessible at {API_URL}")
        print("💡 Make sure to start the backend with: cd backend && flask run")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🎵 BandSync Email & Magic Link Authentication Test")
    print("=" * 60)
    
    # Test backend availability first
    if not test_backend_health():
        print("\n🚨 Please start the backend server first:")
        print("   cd backend && flask run")
        sys.exit(1)
    
    # Test email login
    email_success = test_email_login()
    
    # Test magic link request
    magic_success = test_magic_link_request()
    
    print("\n🎯 Test Summary:")
    print("=" * 30)
    print(f"📧 Email Login: {'✅ PASS' if email_success else '❌ FAIL'}")
    print(f"🪄 Magic Link: {'✅ PASS' if magic_success else '❌ FAIL'}")
    
    if email_success or magic_success:
        print("\n🎉 At least one authentication method is working!")
        print("\n📝 Next steps:")
        print("1. If magic link worked, check your email")
        print("2. Test the frontend at http://localhost:3000/login")
        print("3. Try both username/email login and magic link options")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the backend is running: cd backend && flask run")
        print("2. Check database connectivity")
        print("3. Verify email service configuration")
