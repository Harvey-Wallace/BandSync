#!/usr/bin/env python3
"""
Railway Magic Link Feature Verification
Test the new authentication features on your Railway deployment
"""

import requests
import sys

def test_railway_deployment(railway_url):
    """Test the new authentication features on Railway"""
    
    print(f"🚀 Testing BandSync authentication features on Railway")
    print(f"🔗 Railway URL: {railway_url}")
    print("=" * 60)
    
    api_url = f"{railway_url}/api"
    
    # Test 1: Check if magic link endpoint exists
    print("\n1️⃣ Testing Magic Link Request Endpoint...")
    try:
        response = requests.post(f"{api_url}/auth/magic-link-request", 
                               json={"email": "test@example.com"}, 
                               timeout=10)
        
        if response.status_code == 200:
            print("✅ Magic link endpoint is working!")
            print("   (Response: 'If an account with that email exists...')")
        elif response.status_code == 404:
            print("❌ Magic link endpoint not found - code may not be deployed yet")
        else:
            print(f"⚠️  Magic link endpoint returned: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {railway_url}")
        return False
    except Exception as e:
        print(f"❌ Error testing magic link: {e}")
    
    # Test 2: Check if login endpoint supports email
    print("\n2️⃣ Testing Email Login Support...")
    try:
        # Try with a fake email (should fail with "Invalid credentials", not "Email required")
        response = requests.post(f"{api_url}/auth/login", 
                               json={"email": "fake@test.com", "password": "fakepass"}, 
                               timeout=10)
        
        if response.status_code == 401:
            result = response.json()
            if "Invalid credentials" in result.get('msg', ''):
                print("✅ Email login is supported!")
                print("   (Login endpoint accepts email parameter)")
            else:
                print(f"⚠️  Unexpected response: {result}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing email login: {e}")
    
    # Test 3: Check frontend for magic link button
    print("\n3️⃣ Testing Frontend Magic Link Button...")
    try:
        response = requests.get(railway_url, timeout=10)
        
        if response.status_code == 200:
            if "Login with email link" in response.text:
                print("✅ Frontend has magic link button!")
            else:
                print("⚠️  Frontend may not have magic link button yet")
                print("   (Check if frontend build completed)")
        else:
            print(f"⚠️  Frontend returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
    
    return True

def main():
    # Get Railway URL from user
    railway_url = input("\n🔗 Enter your Railway app URL (e.g., https://your-app.railway.app): ").strip()
    
    if not railway_url:
        print("❌ No URL provided")
        return
    
    if not railway_url.startswith(('http://', 'https://')):
        railway_url = f"https://{railway_url}"
    
    # Remove trailing slash
    railway_url = railway_url.rstrip('/')
    
    success = test_railway_deployment(railway_url)
    
    if success:
        print("\n🎯 Test Summary:")
        print("=" * 30)
        print("✅ Basic connectivity: WORKING")
        print("🔧 Manual tests needed:")
        print("   1. Run SQL migration in Railway dashboard")
        print("   2. Test email login on live site")
        print("   3. Test magic link functionality")
        print(f"\n🌐 Visit: {railway_url}/login")
        
    print("\n📋 Next Steps:")
    print("1. Run the SQL migration in Railway dashboard (if not done)")
    print("2. Test both authentication methods on your live site")
    print("3. Check Railway logs if anything doesn't work")

if __name__ == "__main__":
    main()
