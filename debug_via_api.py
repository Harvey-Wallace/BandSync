#!/usr/bin/env python3
"""
Debug script to check user organization relationships via API
"""

import requests
import json

def debug_via_api():
    """Debug using the production API endpoints"""
    
    base_url = "https://app.bandsync.co.uk"
    
    # We'll need to simulate a login as Harvey258 to get a JWT token
    print("🔍 Debugging user organization relationships via API...")
    
    try:
        # Try to login as Harvey258 (you might need to provide credentials)
        print("\n1. Testing login endpoint...")
        login_response = requests.post(f"{base_url}/auth/login", json={
            "username": "Harvey258", 
            "password": "your_password_here"  # You'll need to replace this
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get oversight dashboard data
            print("\n2. Getting oversight dashboard data...")
            dashboard_response = requests.get(f"{base_url}/admin-oversight/dashboard", headers=headers)
            
            if dashboard_response.status_code == 200:
                data = dashboard_response.json()
                print(f"Dashboard data: {json.dumps(data, indent=2)}")
            else:
                print(f"Dashboard request failed: {dashboard_response.status_code}")
                
            # Get organizations
            print("\n3. Getting organizations...")
            orgs_response = requests.get(f"{base_url}/admin-oversight/organizations", headers=headers)
            
            if orgs_response.status_code == 200:
                orgs = orgs_response.json()
                print(f"Organizations: {json.dumps(orgs, indent=2)}")
            else:
                print(f"Organizations request failed: {orgs_response.status_code}")
                
            # Get users
            print("\n4. Getting users...")
            users_response = requests.get(f"{base_url}/admin-oversight/users", headers=headers)
            
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"Users: {json.dumps(users, indent=2)}")
            else:
                print(f"Users request failed: {users_response.status_code}")
                
        else:
            print(f"Login failed: {login_response.status_code}")
            print("Response:", login_response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("⚠️  Note: You'll need to update the password in this script")
    print("Or we can use the admin oversight debug endpoints...")
    
    # Let's try the debug endpoint instead
    base_url = "https://app.bandsync.co.uk"
    
    print("\n🔍 Trying debug endpoint (if available)...")
    try:
        # Try accessing without auth first to see what we get
        response = requests.get(f"{base_url}/admin-oversight/debug/all-users")
        print(f"Debug endpoint response: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
        else:
            print("Debug endpoint not accessible without auth")
    except Exception as e:
        print(f"Error accessing debug endpoint: {e}")
