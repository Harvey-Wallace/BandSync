#!/usr/bin/env python3

import requests
import json

# Configuration
API_URL = "http://127.0.0.1:5001/api"

def test_multi_org_login():
    """Test login with a user that belongs to multiple organizations"""
    
    print("Testing multi-organization login...")
    
    # Test login with admin user (should belong to multiple orgs)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"1. Attempting login with username: {login_data['username']}")
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('multiple_organizations'):
            print("✅ User belongs to multiple organizations!")
            print("Available organizations:")
            for org in data['organizations']:
                print(f"   - {org['name']} (ID: {org['id']}, Role: {org['role']})")
            
            # Test selecting first organization
            if data['organizations']:
                selected_org = data['organizations'][0]
                print(f"\n2. Selecting organization: {selected_org['name']}")
                
                login_with_org = {
                    **login_data,
                    "organization_id": selected_org['id']
                }
                
                org_response = requests.post(f"{API_URL}/auth/login", json=login_with_org)
                
                if org_response.status_code == 200:
                    org_data = org_response.json()
                    print("✅ Successfully logged in with organization context!")
                    print(f"   - Token received: {org_data['access_token'][:50]}...")
                    print(f"   - Organization: {org_data.get('organization')}")
                    print(f"   - Role: {org_data.get('role')}")
                    
                    # Test organization switching API
                    print(f"\n3. Testing organization switching API...")
                    token = org_data['access_token']
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Get available organizations
                    available_response = requests.get(f"{API_URL}/organizations/available", headers=headers)
                    if available_response.status_code == 200:
                        available_data = available_response.json()
                        print("✅ Available organizations API works!")
                        print(f"   - Found {len(available_data['organizations'])} organizations")
                        
                        # Test switching to another org if available
                        if len(available_data['organizations']) > 1:
                            other_org = next((org for org in available_data['organizations'] 
                                            if org['id'] != selected_org['id']), None)
                            
                            if other_org:
                                print(f"\n4. Testing switch to: {other_org['name']}")
                                switch_data = {"organization_id": other_org['id']}
                                switch_response = requests.post(f"{API_URL}/organizations/switch", 
                                                              json=switch_data, headers=headers)
                                
                                if switch_response.status_code == 200:
                                    switch_result = switch_response.json()
                                    print("✅ Organization switching works!")
                                    print(f"   - New organization: {switch_result.get('organization', {}).get('name')}")
                                    print(f"   - New role: {switch_result.get('role')}")
                                    print(f"   - New token: {switch_result['access_token'][:50]}...")
                                else:
                                    print(f"❌ Organization switching failed: {switch_response.text}")
                            else:
                                print("ℹ️  No other organization to switch to")
                        else:
                            print("ℹ️  User only belongs to one organization")
                    else:
                        print(f"❌ Available organizations API failed: {available_response.text}")
                    
                else:
                    print(f"❌ Login with organization failed: {org_response.text}")
        else:
            print("ℹ️  User belongs to only one organization")
            print(f"   - Organization: {data.get('organization')}")
            print(f"   - Role: {data.get('role')}")
    else:
        print(f"❌ Login failed: {response.text}")

def test_current_organization_api():
    """Test the current organization API"""
    print("\n" + "="*50)
    print("Testing current organization API...")
    
    # Login first
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        
        # If multiple orgs, select the first one
        if data.get('multiple_organizations'):
            selected_org = data['organizations'][0]
            login_with_org = {**login_data, "organization_id": selected_org['id']}
            response = requests.post(f"{API_URL}/auth/login", json=login_with_org)
            data = response.json()
        
        if response.status_code == 200:
            token = data['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test current organization API
            current_response = requests.get(f"{API_URL}/organizations/current", headers=headers)
            if current_response.status_code == 200:
                current_data = current_response.json()
                print("✅ Current organization API works!")
                print(f"   - Current org: {current_data.get('organization', {}).get('name')}")
                print(f"   - Role: {current_data.get('role')}")
            else:
                print(f"❌ Current organization API failed: {current_response.text}")

if __name__ == "__main__":
    print("BandSync Multi-Organization Testing")
    print("="*50)
    
    try:
        test_multi_org_login()
        test_current_organization_api()
        print("\n" + "="*50)
        print("✅ Testing completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
