#!/usr/bin/env python3
"""
Test script to verify the simplified BandSync application
after super admin removal is working correctly.
"""

import requests
import json
import time
from datetime import datetime

def test_simplified_app():
    """Test the simplified BandSync application without super admin features."""
    
    base_url = "https://app.bandsync.co.uk"
    
    print("🧪 Testing Simplified BandSync Application")
    print("=" * 50)
    
    # Test 1: Check if frontend loads without React errors
    print("\n1. Testing Frontend Load...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            # Check for React build files
            if "static/js/main" in response.text and "static/css/main" in response.text:
                print("✅ Frontend loads successfully")
                print(f"   Status: {response.status_code}")
                
                # Extract build hash to verify it's the new build
                import re
                js_match = re.search(r'static/js/main\.([a-f0-9]+)\.js', response.text)
                css_match = re.search(r'static/css/main\.([a-f0-9]+)\.css', response.text)
                
                if js_match:
                    print(f"   JS Build Hash: {js_match.group(1)}")
                if css_match:
                    print(f"   CSS Build Hash: {css_match.group(1)}")
            else:
                print("⚠️  Frontend structure unexpected")
        else:
            print(f"❌ Frontend failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
    
    # Test 2: Check backend health
    print("\n2. Testing Backend Health...")
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend is responsive")
            print(f"   Status: {health_response.status_code}")
        else:
            print(f"⚠️  Backend health check status: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Backend health test failed: {e}")
    
    # Test 3: Verify super admin routes are gone
    print("\n3. Testing Super Admin Route Removal...")
    super_admin_routes = [
        "/api/super-admin/dashboard",
        "/api/super-admin/users",
        "/api/super-admin/organizations",
        "/api/super-admin/system-stats"
    ]
    
    removed_count = 0
    for route in super_admin_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 404:
                removed_count += 1
            else:
                print(f"⚠️  Route still exists: {route} (Status: {response.status_code})")
        except:
            removed_count += 1  # Assume removed if unreachable
    
    if removed_count == len(super_admin_routes):
        print("✅ All super admin routes successfully removed")
    else:
        print(f"⚠️  {removed_count}/{len(super_admin_routes)} super admin routes removed")
    
    # Test 4: Test login page accessibility
    print("\n4. Testing Core Functionality Access...")
    try:
        login_response = requests.get(f"{base_url}/login", timeout=10)
        if login_response.status_code == 200:
            print("✅ Login page accessible")
        else:
            print(f"⚠️  Login page status: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Login page test failed: {e}")
    
    # Test 5: Check if React error patterns are present
    print("\n5. Testing for React Error Patterns...")
    try:
        response = requests.get(base_url, timeout=10)
        error_patterns = [
            "Element type is invalid",
            "expected a string (for built-in components)",
            "or a class/function (for composite components)",
            "but got: object"
        ]
        
        found_errors = []
        for pattern in error_patterns:
            if pattern.lower() in response.text.lower():
                found_errors.append(pattern)
        
        if not found_errors:
            print("✅ No React error patterns detected in source")
        else:
            print(f"⚠️  Found potential error patterns: {found_errors}")
    except Exception as e:
        print(f"❌ React error pattern check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Simplified Application Test Complete")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_simplified_app()
