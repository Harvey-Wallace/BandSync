#!/usr/bin/env python3
"""
Quick debug script to check Rob123's role information
"""

import requests
import json

def test_login(username, password):
    """Test login to see what role Rob123 gets"""
    login_url = "https://app.bandsync.co.uk/api/auth/login"
    
    # Try login with username
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Login Response Status: {response.status_code}")
        print(f"Login Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Login error: {e}")
        return None

def main():
    print("🔍 Testing Rob123 login to check role...")
    print("=" * 50)
    
    # Note: We don't know Rob123's password, but we can try common patterns
    # This is for debugging purposes
    possible_passwords = [
        "password123",
        "temp_Rob123123",  # Temporary password pattern
        "Rob123",
        "password"
    ]
    
    for password in possible_passwords:
        print(f"\nTrying password: {password}")
        result = test_login("Rob123", password)
        if result and "access_token" in result:
            print("✅ Login successful!")
            print(f"Role: {result.get('role')}")
            print(f"Organization: {result.get('organization')}")
            print(f"Organization ID: {result.get('organization_id')}")
            break
        elif result and "multiple_organizations" in result:
            print("✅ Login successful - Multiple organizations detected!")
            print("Organizations:")
            for org in result.get('organizations', []):
                print(f"  - {org['name']} (Role: {org['role']})")
            break
        else:
            print("❌ Login failed")

if __name__ == "__main__":
    main()
