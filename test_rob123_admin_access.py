#!/usr/bin/env python3
"""
Test Rob123's admin endpoint access
"""

import requests
import json

def test_admin_endpoints():
    """Test various admin endpoints to see what Rob123 can access"""
    
    base_url = "https://app.bandsync.co.uk/api"
    
    # We'll need to manually get Rob123's token from the browser
    print("📋 To test Rob123's admin access:")
    print("1. Login as Rob123 in browser")
    print("2. Open browser console (F12)")
    print("3. Run: localStorage.getItem('token')")
    print("4. Copy the token value (without quotes)")
    print("5. Paste it here")
    print()
    
    token = input("Rob123's JWT Token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints that the AdminDashboard tries to call
    endpoints = [
        "/admin/organization",
        "/admin/users", 
        "/admin/sections",
        "/admin/email-stats",
        "/admin/email-logs",
        "/admin/calendar-stats"
    ]
    
    print("\n🔍 Testing Rob123's access to admin endpoints:")
    print("=" * 60)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, headers=headers)
            status = "✅ Success" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{endpoint:<25} {status}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"                         Error: {error_data.get('msg', 'Unknown error')}")
                except:
                    print(f"                         Response: {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint:<25} ❌ Exception: {e}")
    
    print("\n🔍 Testing token decode:")
    try:
        import base64
        payload = json.loads(base64.b64decode(token.split('.')[1] + '=='))
        print("Token payload:")
        print(json.dumps(payload, indent=2))
    except Exception as e:
        print(f"❌ Token decode failed: {e}")

if __name__ == "__main__":
    test_admin_endpoints()
