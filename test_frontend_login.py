#!/usr/bin/env python3
"""
Test frontend login functionality
"""

import requests
import json
from urllib.parse import urljoin

def test_frontend_login():
    """Test what the frontend is actually doing during login"""
    print("🔍 Frontend Login Debug Test")
    print("=" * 50)
    
    base_url = "https://app.bandsync.co.uk"
    
    # Test 1: Check if the main page loads the environment config
    print("\n📄 Testing main page JavaScript loading...")
    try:
        response = requests.get(base_url)
        html_content = response.text
        
        # Check if env-config.js is referenced
        if 'env-config.js' in html_content:
            print("✅ env-config.js referenced in HTML")
        else:
            print("❌ env-config.js not found in HTML")
        
        # Check if the main.js file is referenced
        if 'main.' in html_content and '.js' in html_content:
            print("✅ Main JavaScript file referenced")
        else:
            print("❌ Main JavaScript file not found")
            
    except Exception as e:
        print(f"❌ Error loading main page: {e}")
        return False
    
    # Test 2: Test the environment configuration
    print("\n🔧 Testing environment configuration...")
    try:
        env_response = requests.get(f"{base_url}/env-config.js")
        env_content = env_response.text
        
        print("📝 Environment config content:")
        print(env_content)
        
        # Check if the API URL is properly set
        if 'REACT_APP_API_URL' in env_content:
            print("✅ REACT_APP_API_URL found in config")
        else:
            print("❌ REACT_APP_API_URL missing from config")
            
    except Exception as e:
        print(f"❌ Error loading env config: {e}")
    
    # Test 3: Test the login API directly
    print("\n🔑 Testing login API directly...")
    try:
        login_url = f"{base_url}/api/auth/login"
        login_data = {
            "username": "Rob123",
            "password": "Rob123pass"
        }
        
        response = requests.post(login_url, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login API works correctly")
            data = response.json()
            print(f"Response contains: {list(data.keys())}")
        else:
            print(f"❌ Login API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing login API: {e}")
    
    # Test 4: Test with browser-like headers
    print("\n🌐 Testing with browser-like headers...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': base_url,
            'Referer': base_url
        }
        
        response = requests.post(login_url, json=login_data, headers=headers)
        print(f"Browser-like request Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Browser-like request works")
        else:
            print(f"❌ Browser-like request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error with browser-like request: {e}")
    
    # Test 5: Check for CORS issues
    print("\n🔒 Testing CORS configuration...")
    try:
        # Test preflight request
        options_response = requests.options(login_url, headers={
            'Origin': base_url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        print(f"CORS preflight Status Code: {options_response.status_code}")
        print("CORS headers:")
        for header, value in options_response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
                
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
    
    print("\n🔧 Debugging Recommendations:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify env-config.js loads before main.js")
    print("3. Check if axios is properly configured")
    print("4. Test with browser developer tools network tab")
    print("5. Clear browser cache and try again")
    
    return True

if __name__ == "__main__":
    test_frontend_login()
