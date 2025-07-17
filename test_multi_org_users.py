#!/usr/bin/env python3
"""
Test script to verify multi-organization user management
"""

import sys
import os
import requests
import json

# API Configuration
# API_URL = "http://localhost:5000/api"  # Change to your API URL
API_URL = "https://bandsync-production.up.railway.app/api"

def test_multi_org_users():
    """Test that users added to multiple organizations show up correctly"""
    
    print("🧪 Testing Multi-Organization User Management")
    print("=" * 50)
    
    # Test credentials (update as needed)
    admin_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 1. Login as admin
        print("1. Logging in as admin...")
        login_response = requests.post(f"{API_URL}/auth/login", json=admin_credentials)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            
            # Handle multi-organization login
            if login_data.get('multiple_organizations'):
                print("   Admin belongs to multiple organizations:")
                for org in login_data['organizations']:
                    print(f"     - {org['name']} (Role: {org['role']})")
                
                # Select first organization
                selected_org = login_data['organizations'][0]
                print(f"   Selecting organization: {selected_org['name']}")
                
                # Login with organization context
                org_login_response = requests.post(f"{API_URL}/auth/login", json={
                    **admin_credentials,
                    "organization_id": selected_org['id']
                })
                
                if org_login_response.status_code == 200:
                    org_data = org_login_response.json()
                    token = org_data['access_token']
                    current_org = org_data['organization']
                    print(f"   ✅ Logged in to: {current_org['name']}")
                else:
                    print(f"   ❌ Failed to login with organization context")
                    return False
            else:
                token = login_data['access_token']
                current_org = login_data.get('organization', {})
                print(f"   ✅ Logged in to: {current_org.get('name', 'Unknown')}")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
        
        # 2. Get users in current organization
        print(f"\n2. Getting users in {current_org['name']}...")
        headers = {"Authorization": f"Bearer {token}"}
        
        users_response = requests.get(f"{API_URL}/admin/users", headers=headers)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"   ✅ Found {len(users_data)} users in organization:")
            
            for user in users_data:
                print(f"     - {user['username']} ({user['email']}) - Role: {user['role']}")
                
                # Check if user has section
                if user.get('section_name'):
                    print(f"       Section: {user['section_name']}")
        else:
            print(f"   ❌ Failed to get users: {users_response.status_code}")
            return False
        
        # 3. Test switching organizations (if multiple exist)
        print(f"\n3. Testing organization switching...")
        
        # Get available organizations
        orgs_response = requests.get(f"{API_URL}/organizations/available", headers=headers)
        
        if orgs_response.status_code == 200:
            orgs_data = orgs_response.json()
            available_orgs = orgs_data.get('organizations', [])
            
            print(f"   Available organizations: {len(available_orgs)}")
            
            if len(available_orgs) > 1:
                # Switch to another organization
                other_org = next((org for org in available_orgs if org['id'] != current_org['id']), None)
                
                if other_org:
                    print(f"   Switching to: {other_org['name']}")
                    
                    switch_response = requests.post(f"{API_URL}/organizations/switch", 
                                                  json={"organization_id": other_org['id']}, 
                                                  headers=headers)
                    
                    if switch_response.status_code == 200:
                        switch_data = switch_response.json()
                        new_token = switch_data['access_token']
                        new_headers = {"Authorization": f"Bearer {new_token}"}
                        
                        print(f"   ✅ Switched to: {other_org['name']}")
                        
                        # Get users in new organization
                        new_users_response = requests.get(f"{API_URL}/admin/users", headers=new_headers)
                        
                        if new_users_response.status_code == 200:
                            new_users_data = new_users_response.json()
                            print(f"   ✅ Found {len(new_users_data)} users in {other_org['name']}:")
                            
                            for user in new_users_data:
                                print(f"     - {user['username']} ({user['email']}) - Role: {user['role']}")
                        else:
                            print(f"   ❌ Failed to get users in new org: {new_users_response.status_code}")
                    else:
                        print(f"   ❌ Failed to switch organization: {switch_response.status_code}")
                else:
                    print("   No other organization to switch to")
            else:
                print("   Only one organization available, skipping switch test")
        else:
            print(f"   ❌ Failed to get available organizations: {orgs_response.status_code}")
        
        print(f"\n🎉 Multi-organization user management test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_multi_org_users()
    sys.exit(0 if success else 1)
