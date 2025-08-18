#!/usr/bin/env python3
"""
Debug deployed frontend vs direct API calls
Check what's different between the two approaches
"""

import requests
import json

def check_api_endpoints():
    """Check API endpoints directly"""
    print("🔧 API Endpoint Debug Tool")
    print("=" * 50)
    
    base_url = "https://app.bandsync.co.uk"
    api_url = f"{base_url}/api"
    
    print(f"🌐 Base URL: {base_url}")
    print(f"🔗 API URL: {api_url}")
    
    # Test email
    test_email = "RobertH@Bassett-group.co.uk"
    
    print(f"\n📧 Testing with email: {test_email}")
    
    # 1. Test API endpoint directly (this works)
    print("\n1️⃣ Direct API Call (VS Code method):")
    try:
        response = requests.post(f"{api_url}/auth/magic-link-request", 
                               json={"email": test_email}, 
                               timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Direct API call SUCCESS")
        else:
            print("   ❌ Direct API call FAILED")
            
    except Exception as e:
        print(f"   ❌ Direct API call ERROR: {e}")
    
    # 2. Test with different headers (simulating frontend)
    print("\n2️⃣ Frontend-style API Call:")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': base_url,
            'Referer': f"{base_url}/login"
        }
        
        response = requests.post(f"{api_url}/auth/magic-link-request", 
                               json={"email": test_email},
                               headers=headers,
                               timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Frontend-style call SUCCESS")
        else:
            print("   ❌ Frontend-style call FAILED")
            
    except Exception as e:
        print(f"   ❌ Frontend-style call ERROR: {e}")
    
    # 3. Check if the frontend is hitting the right URL
    print("\n3️⃣ Frontend URL Check:")
    try:
        # Test what the frontend getApiUrl() function returns
        frontend_response = requests.get(f"{base_url}/static/js/main.js", timeout=5)
        if "getApiUrl" in frontend_response.text:
            print("   ✅ Frontend has getApiUrl function")
        else:
            print("   ⚠️  Frontend may have getApiUrl issues")
            
        # Check if the main HTML loads properly
        html_response = requests.get(f"{base_url}/login", timeout=5)
        if html_response.status_code == 200:
            print("   ✅ Login page loads successfully")
        else:
            print(f"   ❌ Login page error: {html_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Frontend check ERROR: {e}")
    
    # 4. Check Railway logs suggestion
    print("\n4️⃣ Debugging suggestions:")
    print("   • Check browser console for JavaScript errors")
    print("   • Check browser Network tab when requesting magic link")
    print("   • Verify the API URL in the frontend")
    print("   • Check Railway deployment logs")

def browser_debug_instructions():
    """Provide browser debugging instructions"""
    print("\n🌐 Browser Debugging Instructions:")
    print("=" * 50)
    print("1. Open https://app.bandsync.co.uk/login in your browser")
    print("2. Open Developer Tools (F12 or Cmd+Option+I)")
    print("3. Go to the Network tab")
    print("4. Try requesting a magic link")
    print("5. Look for:")
    print("   • Any failed network requests (red entries)")
    print("   • Check what URL is being called")
    print("   • Check the request payload")
    print("   • Check the response")
    print("\n6. Also check the Console tab for any JavaScript errors")
    print("\n7. If you see errors, please share them!")

if __name__ == "__main__":
    check_api_endpoints()
    browser_debug_instructions()
    
    print("\n💡 Most likely causes:")
    print("1. Frontend is calling wrong API URL")
    print("2. CORS issue (but this should work)")
    print("3. JavaScript error preventing the request")
    print("4. Network issue in browser")
    print("5. Frontend build issue (old cached files)")
