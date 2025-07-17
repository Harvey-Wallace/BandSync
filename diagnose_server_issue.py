#!/usr/bin/env python3
"""
Diagnose server issues by checking the health endpoint
"""

import requests
import json

def check_server_health():
    """Check if the server is responding"""
    
    base_url = "https://bandsync-production.up.railway.app"
    
    # Test endpoints
    endpoints = [
        "/",
        "/api/auth/status",
        "/api/auth/test",
        "/api/health"
    ]
    
    print("🔍 Server Diagnostic Check")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 Testing: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Endpoint is working")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"Response: {response.text[:200]}...")
                else:
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Endpoint failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
    
    # Test a simple login
    print(f"\n🔑 Testing login endpoint...")
    try:
        login_url = f"{base_url}/api/auth/login"
        login_data = {
            "username": "Rob123",
            "password": "Rob123pass"
        }
        
        response = requests.post(login_url, json=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text[:500]}...")
        
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    check_server_health()
