#!/usr/bin/env python3
"""
iOS-specific compatibility test for BandSync
"""

import requests
import json
import re
from urllib.parse import urljoin

def test_ios_specific_issues():
    """Test for iOS-specific JavaScript and compatibility issues"""
    print("🍎 BandSync iOS Compatibility Test")
    print("=" * 50)
    
    base_url = "https://app.bandsync.co.uk"
    
    # Test 1: Check the main JavaScript bundle for iOS-incompatible code
    print("\n🔍 Analyzing main JavaScript bundle for iOS issues...")
    try:
        js_response = requests.get(f"{base_url}/static/js/main.fdb8c274.js")
        js_content = js_response.text
        
        # Check for common iOS Safari compatibility issues
        issues_found = []
        
        # 1. Check for ES6+ features that might not be supported
        if 'async/await' in js_content or 'async ' in js_content:
            issues_found.append("⚠️  Async/await detected - may need polyfill for older iOS")
        
        # 2. Check for modern JavaScript features
        if 'const ' in js_content and js_content.count('const ') > 10:
            issues_found.append("⚠️  Heavy const usage - may cause issues on iOS < 11")
        
        if 'let ' in js_content and js_content.count('let ') > 10:
            issues_found.append("⚠️  Heavy let usage - may cause issues on iOS < 11")
        
        # 3. Check for arrow functions
        if '=>' in js_content and js_content.count('=>') > 50:
            issues_found.append("⚠️  Heavy arrow function usage - may cause issues on iOS < 10")
        
        # 4. Check for template literals
        if '`' in js_content and js_content.count('`') > 10:
            issues_found.append("⚠️  Template literals detected - may cause issues on iOS < 9")
        
        # 5. Check for fetch API
        if 'fetch(' in js_content:
            issues_found.append("⚠️  Fetch API detected - may need polyfill for iOS < 10.3")
        
        # 6. Check for Promise usage
        if 'Promise' in js_content:
            issues_found.append("⚠️  Promise usage detected - may need polyfill for iOS < 8")
        
        # 7. Check for Object.assign
        if 'Object.assign' in js_content:
            issues_found.append("⚠️  Object.assign detected - may need polyfill for iOS < 9")
        
        # 8. Check for Array.from
        if 'Array.from' in js_content:
            issues_found.append("⚠️  Array.from detected - may need polyfill for iOS < 9")
        
        # 9. Check for Map/Set
        if 'new Map' in js_content or 'new Set' in js_content:
            issues_found.append("⚠️  Map/Set detected - may need polyfill for iOS < 9")
        
        # 10. Check for Symbol
        if 'Symbol' in js_content:
            issues_found.append("⚠️  Symbol detected - may need polyfill for iOS < 9")
        
        if issues_found:
            print("🚨 Potential iOS compatibility issues found:")
            for issue in issues_found:
                print(f"   {issue}")
        else:
            print("✅ No obvious ES6+ compatibility issues detected")
            
        # Check bundle size
        bundle_size = len(js_content) / 1024
        print(f"📊 JavaScript bundle size: {bundle_size:.1f} KB")
        
        if bundle_size > 1000:
            print("⚠️  Large JavaScript bundle may cause memory issues on iOS")
        else:
            print("✅ JavaScript bundle size appropriate for iOS")
            
    except Exception as e:
        print(f"❌ Error analyzing JavaScript: {e}")
    
    # Test 2: Check env-config.js for iOS issues
    print("\n🔧 Checking environment configuration...")
    try:
        env_response = requests.get(f"{base_url}/env-config.js")
        env_content = env_response.text
        
        print("📄 Environment configuration content:")
        print(env_content)
        
        # Check for problematic configurations
        if 'localhost' in env_content:
            print("🚨 CRITICAL: localhost detected in env-config.js - will fail on iOS!")
        
        if '127.0.0.1' in env_content:
            print("🚨 CRITICAL: 127.0.0.1 detected in env-config.js - will fail on iOS!")
        
        if 'http://' in env_content:
            print("🚨 CRITICAL: HTTP URLs detected - may cause mixed content issues on iOS!")
        
        # Check for missing API endpoints
        if 'REACT_APP_API_URL' not in env_content and 'API_URL' not in env_content:
            print("⚠️  No API URL configuration found - may cause connectivity issues")
        
    except Exception as e:
        print(f"❌ Error checking environment config: {e}")
    
    # Test 3: Check for iOS-specific React issues
    print("\n⚛️  Checking for React iOS compatibility issues...")
    try:
        response = requests.get(base_url)
        html_content = response.text
        
        # Check for noscript message
        if 'You need to enable JavaScript' in html_content:
            print("✅ NoScript message present - good fallback")
        
        # Check for React root element
        if 'id="root"' in html_content:
            print("✅ React root element found")
        else:
            print("❌ React root element missing")
        
        # Check for proper charset
        if 'charset="utf-8"' in html_content:
            print("✅ UTF-8 charset specified")
        else:
            print("⚠️  UTF-8 charset not specified")
        
    except Exception as e:
        print(f"❌ Error checking React setup: {e}")
    
    # Test 4: Check for CORS issues that might affect iOS
    print("\n🌐 Checking CORS configuration...")
    try:
        # Check preflight request
        response = requests.options(base_url)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print("🔍 CORS headers:")
        for header, value in cors_headers.items():
            if value:
                print(f"   ✅ {header}: {value}")
            else:
                print(f"   ❌ {header}: Not set")
        
    except Exception as e:
        print(f"❌ Error checking CORS: {e}")
    
    # Test 5: iOS Safari specific tests
    print("\n📱 iOS Safari specific tests...")
    
    # Test with different iOS versions
    ios_versions = [
        ('iOS 13', 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1'),
        ('iOS 14', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'),
        ('iOS 15', 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'),
        ('iOS 16', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'),
        ('iOS 17', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'),
        ('iPadOS 13', 'Mozilla/5.0 (iPad; CPU OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1')
    ]
    
    for version, user_agent in ios_versions:
        try:
            response = requests.get(base_url, headers={'User-Agent': user_agent}, timeout=10)
            if response.status_code == 200:
                print(f"✅ {version}: HTTP OK")
            else:
                print(f"❌ {version}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {version}: Error - {e}")
    
    print("\n🔧 iOS Debugging Solutions:")
    print("1. 🚨 MOST LIKELY CAUSE: JavaScript compatibility issues")
    print("   - The app likely uses ES6+ features not supported by iOS Safari")
    print("   - Need to add Babel polyfills or transpile to ES5")
    print()
    print("2. 📱 To debug on actual iOS device:")
    print("   - Connect iPhone to Mac via cable")
    print("   - Open Safari on Mac → Develop → [iPhone Name] → app.bandsync.co.uk")
    print("   - Check Console for JavaScript errors")
    print()
    print("3. 🔧 Common fixes:")
    print("   - Add @babel/polyfill to your React app")
    print("   - Use react-app-polyfill for IE and older browsers")
    print("   - Configure Babel to target older iOS versions")
    print()
    print("4. 🏗️ Build configuration:")
    print("   - Add 'browserslist' to package.json targeting iOS Safari")
    print("   - Use 'not dead', 'not op_mini all', 'iOS >= 10'")
    print()
    print("5. 🧪 Quick test:")
    print("   - Try adding ?debug=true to URL on iOS")
    print("   - Check Network tab in Safari Web Inspector")
    print("   - Look for failed JavaScript downloads")

if __name__ == "__main__":
    test_ios_specific_issues()
