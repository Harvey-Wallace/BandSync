#!/usr/bin/env python3
"""
Mobile responsiveness and connectivity diagnostic test
"""

import requests
import json
from urllib.parse import urljoin

def test_mobile_compatibility():
    """Test mobile-specific functionality and responsiveness"""
    print("📱 BandSync Mobile Compatibility Test")
    print("=" * 50)
    
    base_url = "https://bandsync-production.up.railway.app"
    
    # Test 1: Check if main page loads
    print("\n🌐 Testing main page load...")
    try:
        response = requests.get(base_url, headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        })
        
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            
            # Check for mobile viewport meta tag
            if 'viewport' in response.text:
                print("✅ Mobile viewport meta tag found")
            else:
                print("❌ Mobile viewport meta tag missing")
                
            # Check for responsive CSS
            if 'max-width' in response.text or 'mobile' in response.text:
                print("✅ Responsive CSS detected")
            else:
                print("⚠️  Limited responsive CSS detected")
                
        else:
            print(f"❌ Main page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading main page: {e}")
        return False
    
    # Test 2: Check static assets
    print("\n📦 Testing static assets...")
    static_assets = [
        "/static/css/main.6823e305.css",
        "/static/js/main.fdb8c274.js", 
        "/env-config.js",
        "/favicon.ico"
    ]
    
    for asset in static_assets:
        try:
            asset_url = urljoin(base_url, asset)
            response = requests.head(asset_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {asset} - Available")
            else:
                print(f"❌ {asset} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  {asset} - Error: {e}")
    
    # Test 3: API connectivity
    print("\n🔗 Testing API connectivity...")
    api_endpoints = [
        "/api/auth/login",
        "/api/events/", 
        "/api/admin/calendar-stats"
    ]
    
    for endpoint in api_endpoints:
        try:
            endpoint_url = urljoin(base_url, endpoint)
            
            if endpoint == "/api/auth/login":
                # Test POST endpoint
                response = requests.post(endpoint_url, json={
                    "username": "test", 
                    "password": "test"
                }, timeout=10)
                
                if response.status_code in [200, 401, 400]:  # Expected responses
                    print(f"✅ {endpoint} - Responding (Status: {response.status_code})")
                else:
                    print(f"❌ {endpoint} - Unexpected status: {response.status_code}")
            else:
                # Test GET endpoint (will fail without auth, but should respond)
                response = requests.get(endpoint_url, timeout=10)
                
                if response.status_code in [200, 401, 403]:  # Expected responses
                    print(f"✅ {endpoint} - Responding (Status: {response.status_code})")
                else:
                    print(f"❌ {endpoint} - Unexpected status: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    # Test 4: Check for common mobile issues
    print("\n🔍 Checking for common mobile issues...")
    
    # Check SSL certificate
    try:
        response = requests.get(base_url, verify=True)
        print("✅ SSL certificate valid")
    except requests.exceptions.SSLError:
        print("❌ SSL certificate issue")
    except Exception as e:
        print(f"⚠️  SSL check error: {e}")
    
    # Check response size (large responses can cause mobile issues)
    try:
        response = requests.get(base_url)
        size_kb = len(response.content) / 1024
        print(f"📊 Main page size: {size_kb:.1f} KB")
        
        if size_kb > 500:
            print("⚠️  Large page size may cause mobile loading issues")
        else:
            print("✅ Page size appropriate for mobile")
            
    except Exception as e:
        print(f"❌ Could not check page size: {e}")
    
    print("\n📝 Mobile Testing Recommendations:")
    print("1. Test login flow on mobile device")
    print("2. Check touch interactions and button sizes")
    print("3. Verify responsive layout on different screen sizes")
    print("4. Test network connectivity on mobile data")
    print("5. Check for JavaScript errors in mobile browser console")
    
    return True

if __name__ == "__main__":
    test_mobile_compatibility()
