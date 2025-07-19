#!/usr/bin/env python3

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/Users/robertharvey/Documents/GitHub/BandSync/backend')

def test_impersonation():
    # Base URL - use Railway deployment
    base_url = 'https://bandsync-production.up.railway.app/api'
    
    # Test credentials
    username = 'Harvey258'
    password = 'password'
    
    print("=== Testing Super Admin Impersonation ===")
    print(f"Base URL: {base_url}")
    
    # Step 1: Login as Super Admin
    print("\n1. Logging in as Super Admin...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json={
            'username': username,
            'password': password
        }, timeout=10)
        
        print(f"Login Status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
            
        login_data = login_response.json()
        print(f"Login response: {login_data}")
        
        # Handle multi-organization login
        if login_data.get('multiple_organizations'):
            organizations = login_data.get('organizations', [])
            print(f"Found {len(organizations)} organizations")
            
            # Find Super Admin organization
            super_admin_org = None
            for org in organizations:
                if org.get('role') == 'Super Admin':
                    super_admin_org = org
                    break
            
            if not super_admin_org:
                print("No Super Admin organization found")
                return
                
            print(f"Using Super Admin organization: {super_admin_org['name']}")
            
            # Login with organization
            login_response = requests.post(f"{base_url}/auth/login", json={
                'username': username,
                'password': password,
                'organization_id': super_admin_org['id']
            }, timeout=10)
            
            if login_response.status_code != 200:
                print(f"Organization login failed: {login_response.text}")
                return
                
            login_data = login_response.json()
        
        # Handle different token field names
        token = login_data.get('access_token') or login_data.get('token')
        if not token:
            print(f"No token found in response. Available keys: {list(login_data.keys())}")
            return
            
        print(f"✓ Login successful, got token")
        
    except Exception as e:
        print(f"✗ Login error: {e}")
        return
    
    # Step 2: Search for a user to impersonate
    print("\n2. Searching for users to impersonate...")
    try:
        search_response = requests.get(f"{base_url}/super-admin/users/search?q=user", headers={
            'Authorization': f'Bearer {token}'
        }, timeout=10)
        
        print(f"Search Status: {search_response.status_code}")
        if search_response.status_code != 200:
            print(f"Search failed: {search_response.text}")
            return
            
        search_data = search_response.json()
        print(f"Search response: {search_data}")
        users = search_data.get('users', [])
        
        if not users:
            print("No users found to impersonate")
            print("Let's try searching for any user...")
            # Try a broader search
            search_response2 = requests.get(f"{base_url}/super-admin/users/search?q=", headers={
                'Authorization': f'Bearer {token}'
            }, timeout=10)
            if search_response2.status_code == 200:
                search_data2 = search_response2.json()
                print(f"Broader search response: {search_data2}")
                users = search_data2.get('users', [])
            
            if not users:
                return
            
        # Find a non-super-admin user to impersonate
        target_user = None
        for user in users:
            # Skip the super admin himself
            if user['username'] != 'Harvey258':
                target_user = user
                break
        
        if not target_user:
            print("No suitable target user found")
            return
            
        print(f"✓ Found target user: {target_user['username']} (ID: {target_user['id']})")
        print(f"  User organizations: {[org['name'] for org in target_user.get('organizations', [])]}")
        
    except Exception as e:
        print(f"✗ Search error: {e}")
        return
    
    # Step 3: Attempt impersonation
    print(f"\n3. Attempting to impersonate user {target_user['username']}...")
    try:
        impersonate_response = requests.post(
            f"{base_url}/super-admin/user/{target_user['id']}/impersonate",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={},  # Empty body, let backend choose organization
            timeout=10
        )
        
        print(f"Impersonation Status: {impersonate_response.status_code}")
        
        if impersonate_response.status_code == 200:
            impersonate_data = impersonate_response.json()
            print("✓ Impersonation successful!")
            print(f"  Impersonation token received")
            print(f"  Target user: {impersonate_data['user']['username']}")
            print(f"  Organization: {impersonate_data['organization']['name']}")
            print(f"  Role: {impersonate_data['role']}")
        else:
            print(f"✗ Impersonation failed: {impersonate_response.text}")
            
            # Try to parse the error as JSON
            try:
                error_data = impersonate_response.json()
                print(f"  Error message: {error_data.get('msg', 'Unknown error')}")
            except:
                pass
        
    except Exception as e:
        print(f"✗ Impersonation error: {e}")
        
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_impersonation()
