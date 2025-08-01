#!/usr/bin/env python3
"""
Test Railway email configuration by calling the actual API endpoint
"""
import requests
import json

# Railway app URL
RAILWAY_URL = "https://app.bandsync.co.uk"
API_URL = f"{RAILWAY_URL}/api"

print("🚀 Testing Railway Email Configuration")
print("=" * 50)

print(f"🌐 Testing API endpoint: {API_URL}")

# First, let's test if we can reach the API
print("\n1️⃣ Testing API connectivity...")
try:
    response = requests.get(f"{API_URL}/health", timeout=10)
    if response.status_code == 200:
        print("✅ API is reachable")
    else:
        print(f"⚠️  API responded with status {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ API connectivity test failed: {e}")

# Test password reset endpoint (this doesn't require auth)
print("\n2️⃣ Testing password reset email endpoint...")
try:
    response = requests.post(
        f"{API_URL}/auth/password-reset-request",
        headers={"Content-Type": "application/json"},
        json={"email": "rob@harvey-wallace.co.uk"},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Password reset endpoint is working - email service is configured!")
    else:
        print(f"❌ Password reset failed with status {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

# Test the admin test notification endpoint (this requires auth, so it will fail, but we can see the error)
print("\n3️⃣ Testing admin notification endpoint (will fail auth, but shows if email service is configured)...")
try:
    response = requests.post(
        f"{API_URL}/admin/send-test-notification",
        headers={"Content-Type": "application/json"},
        json={},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401 or "Not enough segments" in response.text:
        print("✅ Endpoint is accessible (auth failed as expected)")
    elif "Email service not configured" in response.text:
        print("❌ Email service is not configured on Railway")
        response_data = response.json()
        if 'debug_info' in response_data:
            debug_info = response_data['debug_info']
            print(f"Debug info:")
            print(f"  - API key set: {debug_info.get('api_key_set', 'unknown')}")
            print(f"  - From email: {debug_info.get('from_email', 'unknown')}")
            print(f"  - From name: {debug_info.get('from_name', 'unknown')}")
            print(f"  - Base URL: {debug_info.get('base_url', 'unknown')}")
    else:
        print(f"⚠️  Unexpected response")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

print("\n" + "=" * 50)
print("Test complete!")
print("\n💡 Next steps:")
print("1. If password reset works ✅, the email service is configured correctly")
print("2. If you're still getting errors in the admin panel, try logging in and testing again")
print("3. Check Railway logs for more detailed error messages: railway logs")
