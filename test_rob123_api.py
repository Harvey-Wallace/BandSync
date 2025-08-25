#!/usr/bin/env python3
"""
Test Rob123's organization relationships via the debug API
"""

import requests

def check_rob123_via_api():
    """Check Rob123's organization relationships through the web API."""
    
    base_url = "https://app.bandsync.co.uk"
    
    print("🔍 Checking Rob123 Organization Status via API")
    print("=" * 60)
    
    # Test debug endpoint (without auth - will show error but confirm endpoint exists)
    print("\n1. Testing debug endpoint accessibility...")
    try:
        response = requests.get(f"{base_url}/api/admin-oversight/debug/user/Rob123", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Endpoint exists but requires authentication (expected)")
        elif response.status_code == 404:
            print("❌ Endpoint not found - deployment may not be complete")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error accessing endpoint: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps for Harvey258:")
    print("1. Login to https://app.bandsync.co.uk as Harvey258")
    print("2. Open browser dev tools (F12)")
    print("3. Go to Console tab")
    print("4. Run this command to check Rob123:")
    print()
    print("   fetch('/api/admin-oversight/debug/user/Rob123', {")
    print("     headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }")
    print("   }).then(r => r.json()).then(console.log)")
    print()
    print("5. This will show Rob123's organization relationships")
    print("6. If Rob123 is missing from 'City of Birmingham Brass Band',")
    print("   we can use the fix endpoint to add them")

if __name__ == "__main__":
    check_rob123_via_api()
