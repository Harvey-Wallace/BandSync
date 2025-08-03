#!/usr/bin/env python3
"""
Quick test to check if the super admin impersonate endpoint is accessible
"""

import requests
import time

# Test the impersonate endpoint
BASE_URL = "https://app.bandsync.co.uk/api"

def test_impersonate_endpoint():
    """Test if the impersonate endpoint exists and responds"""
    
    print("🔍 Testing Super Admin Impersonate Endpoint...")
    
    # Test without auth (should get 401, not 404)
    print("\n1️⃣ Testing endpoint accessibility without auth...")
    
    try:
        response = requests.post(f"{BASE_URL}/super-admin/user/1/impersonate", 
                               json={},
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("❌ ISSUE: Endpoint returns 404 - route not found!")
            print("   This suggests the super admin blueprint route is not registered correctly")
        elif response.status_code == 401:
            print("✅ GOOD: Endpoint exists but requires authentication (expected)")
        else:
            print(f"ℹ️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

    # Test the actual frontend call pattern
    print("\n2️⃣ Testing exact frontend call pattern...")
    
    # Simulate the exact call the frontend would make (with a fake token)
    headers = {
        'Authorization': 'Bearer fake_token_for_testing',
        'Content-Type': 'application/json'
    }
    
    try:
        # This should return 401/422 (invalid token) not 404
        response = requests.post(f"{BASE_URL}/super-admin/user/1/impersonate", 
                               json={},
                               headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("❌ ISSUE: Frontend pattern also returns 404!")
            print("   Route might not be registered or there's a path mismatch")
        elif response.status_code in [401, 422]:
            print("✅ GOOD: Endpoint exists, authentication error (expected with fake token)")
        else:
            print(f"ℹ️  Response: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

    # Test if super-admin routes in general work
    print("\n3️⃣ Testing other super-admin endpoints...")
    
    test_routes = [
        "/super-admin/overview",
        "/super-admin/system/health", 
        "/super-admin/users/search"
    ]
    
    for route in test_routes:
        try:
            response = requests.get(f"{BASE_URL}{route}", headers=headers)
            status = "✅ EXISTS" if response.status_code != 404 else "❌ 404"
            print(f"   {route}: {status} ({response.status_code})")
        except Exception as e:
            print(f"   {route}: ❌ ERROR ({str(e)})")

if __name__ == "__main__":
    print("🔧 Super Admin Impersonate Endpoint Test")
    print("🎯 Checking if 'Failed to load impersonate: HTTP 404' is endpoint issue")
    test_impersonate_endpoint()
    
    print("\n📋 Diagnosis:")
    print("   - If all endpoints return 404: Blueprint registration issue")
    print("   - If only impersonate returns 404: Route definition issue") 
    print("   - If endpoints return 401/422: Normal behavior, frontend auth issue")
    print("   - Check browser dev tools Network tab for exact failing URL")
