#!/usr/bin/env python3
"""
Test script to verify Harvey258 login behavior and debug the temporary password loop issue
"""

import requests
import json

# Railway API endpoint
BASE_URL = "https://app.bandsync.co.uk/api"

def test_harvey258_login():
    """Test Harvey258 login with temporary password"""
    
    print("🔍 Testing Harvey258 login with temporary password...")
    
    # First attempt - login with temp password (should show multiple orgs or force password reset)
    login_data = {
        "username": "Harvey258",
        "password": "temp_Harvey258123"
    }
    
    print(f"\n1️⃣ Attempting login with: {login_data}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('multiple_organizations'):
                print("\n📋 Multiple organizations found:")
                for org in data.get('organizations', []):
                    print(f"  - {org['name']} (ID: {org['id']}, Role: {org['role']})")
                
                # Test login with first organization
                first_org_id = data['organizations'][0]['id']
                print(f"\n2️⃣ Testing login with organization {first_org_id}...")
                
                login_data_with_org = {
                    "username": "Harvey258",
                    "password": "temp_Harvey258123",
                    "organization_id": first_org_id
                }
                
                response2 = requests.post(f"{BASE_URL}/auth/login", 
                                        json=login_data_with_org,
                                        headers={'Content-Type': 'application/json'})
                
                print(f"Status Code: {response2.status_code}")
                print(f"Response: {response2.text}")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"\n✅ Login successful!")
                    print(f"Requires password change: {data2.get('requires_password_change', 'Not specified')}")
                    print(f"Access token received: {'✅' if data2.get('access_token') else '❌'}")
                    print(f"Organization: {data2.get('organization')}")
                    print(f"Role: {data2.get('role')}")
                else:
                    print(f"\n❌ Login with organization failed")
                    
            elif data.get('requires_password_change'):
                print(f"\n✅ Login successful - requires password change!")
                print(f"Organization: {data.get('organization')}")
                print(f"Role: {data.get('role')}")
            else:
                print(f"\n✅ Normal login successful")
                print(f"Requires password change: {data.get('requires_password_change', 'Not specified')}")
                
        else:
            print(f"\n❌ Login failed")
            
    except Exception as e:
        print(f"\n💥 Error during test: {str(e)}")

if __name__ == "__main__":
    test_harvey258_login()
