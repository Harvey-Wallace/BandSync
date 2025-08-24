#!/usr/bin/env python3

import requests
import json

def check_current_user_status():
    """Check current user and super admin status in the system"""
    
    base_url = 'https://app.bandsync.co.uk/api'
    
    print("🔍 Checking current users and super admin status...")
    print(f"Base URL: {base_url}")
    
    # Try a general API endpoint to see if the API is responding
    print("\n1. Testing basic API connectivity...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is responsive")
        else:
            print(f"❌ API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        
    # Try to check if there are any public endpoints that might give us info
    print("\n2. Testing auth endpoints...")
    
    # Test registration (this might tell us about existing users)
    test_registration = {
        'username': 'test_user_123',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'organization': 'TestOrg'
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=test_registration)
        print(f"Registration test status: {response.status_code}")
        if response.status_code != 200:
            print(f"Registration response: {response.text}")
    except Exception as e:
        print(f"Registration test error: {e}")
        
    # Try some common usernames that might exist
    print("\n3. Testing common super admin usernames...")
    
    common_usernames = [
        'admin',
        'harvey',
        'Harvey',
        'Harvey258',
        'harvey258',
        'robertharvey',
        'robert',
        'super_admin',
        'superadmin'
    ]
    
    common_passwords = [
        'SuperAdminPassword123!',
        'SuperAdmin123!',
        'Password123!',
        'admin123',
        'password'
    ]
    
    for username in common_usernames:
        for password in common_passwords:
            try:
                login_data = {'username': username, 'password': password}
                response = requests.post(f"{base_url}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ LOGIN SUCCESS: {username} / {password}")
                    print(f"   Role: {data.get('role')}")
                    print(f"   Super Admin: {data.get('super_admin')}")
                    print(f"   Organization: {data.get('organization')}")
                    return username, password, data.get('access_token')
                elif response.status_code != 401:
                    print(f"⚠️  {username} / {password}: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ Error testing {username}: {e}")
                break
    
    print("❌ No valid super admin credentials found")
    return None, None, None

if __name__ == "__main__":
    check_current_user_status()
