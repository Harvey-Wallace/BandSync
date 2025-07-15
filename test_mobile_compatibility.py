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
    
    base_url = "https://app.bandsync.co.uk"
    
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
        "/static/css/main.e1988db2.css",
        "/static/js/main.11d382e4.js", 
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
    
    # Test 5: iPhone-specific diagnostics
    print("\n📱 iPhone-specific diagnostics...")
    
    # Check for iOS-specific issues
    try:
        # Test with different iOS user agents
        ios_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        
        for i, user_agent in enumerate(ios_user_agents):
            try:
                response = requests.get(base_url, headers={'User-Agent': user_agent}, timeout=15)
                ios_version = f"iOS {15 + i}"
                if response.status_code == 200:
                    print(f"✅ {ios_version} compatibility - OK")
                else:
                    print(f"❌ {ios_version} compatibility - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {ios_version} compatibility - Error: {e}")
                
    except Exception as e:
        print(f"❌ iOS compatibility test failed: {e}")
    
    # Check for mixed content issues (http resources on https)
    print("\n🔒 Checking for mixed content issues...")
    try:
        response = requests.get(base_url)
        content = response.text.lower()
        
        # Look for http:// resources that might cause mixed content warnings
        if 'http://' in content and 'https://' in content:
            print("⚠️  Mixed content detected - may cause iOS loading issues")
        else:
            print("✅ No mixed content issues detected")
            
        # Check for common iOS-problematic patterns
        if 'document.write' in content:
            print("⚠️  document.write detected - may cause iOS issues")
        else:
            print("✅ No document.write usage detected")
            
    except Exception as e:
        print(f"❌ Mixed content check failed: {e}")
    
    # Test connection speed simulation
    print("\n🌐 Testing connection speed simulation...")
    try:
        import time
        start_time = time.time()
        response = requests.get(base_url, timeout=30)
        load_time = time.time() - start_time
        
        print(f"📊 Page load time: {load_time:.2f} seconds")
        
        if load_time > 10:
            print("⚠️  Slow loading - may timeout on mobile connections")
        elif load_time > 5:
            print("⚠️  Moderate loading speed - may be slow on mobile")
        else:
            print("✅ Good loading speed for mobile")
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - likely cause of iPhone loading issues")
    except Exception as e:
        print(f"❌ Speed test failed: {e}")
    
    # Check for JavaScript errors that might prevent loading
    print("\n🔧 Checking for potential JavaScript issues...")
    try:
        response = requests.get(base_url)
        content = response.text
        
        # Look for common JavaScript patterns that might cause issues
        if 'console.log' in content:
            print("⚠️  Console.log statements found - may cause performance issues")
        
        if 'debugger' in content:
            print("⚠️  Debugger statements found - may cause loading issues")
        
        if 'localhost' in content:
            print("⚠️  Localhost references found - will fail on mobile")
        
        if '127.0.0.1' in content:
            print("⚠️  127.0.0.1 references found - will fail on mobile")
            
        print("✅ JavaScript diagnostic complete")
        
    except Exception as e:
        print(f"❌ JavaScript check failed: {e}")
    
    # Test specific mobile browser compatibility
    print("\n📱 Mobile browser compatibility test...")
    mobile_browsers = {
        'Safari iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Chrome iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/91.0.4472.80 Mobile/15E148 Safari/604.1',
        'Firefox iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/35.0.0 Mobile/15E148 Safari/605.1.15'
    }
    
    for browser, user_agent in mobile_browsers.items():
        try:
            response = requests.get(base_url, headers={'User-Agent': user_agent}, timeout=10)
            if response.status_code == 200:
                print(f"✅ {browser} - Compatible")
            else:
                print(f"❌ {browser} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {browser} - Error: {e}")
    
    print("\n🔍 iPhone Troubleshooting Steps:")
    print("1. Check iPhone Safari settings - ensure JavaScript is enabled")
    print("2. Clear Safari cache and cookies")
    print("3. Try accessing in private/incognito mode")
    print("4. Check if you're on WiFi vs cellular data")
    print("5. Try force-closing Safari and reopening")
    print("6. Check iOS version compatibility")
    print("7. Try accessing from different network (mobile hotspot)")
    print("8. Check if any content blockers are interfering")
    
    print("\n📝 Mobile Testing Recommendations:")
    print("1. Test login flow on mobile device")
    print("2. Check touch interactions and button sizes")
    print("3. Verify responsive layout on different screen sizes")
    print("4. Test network connectivity on mobile data")
    print("5. Check for JavaScript errors in mobile browser console")
    
    return True

if __name__ == "__main__":
    test_mobile_compatibility()
