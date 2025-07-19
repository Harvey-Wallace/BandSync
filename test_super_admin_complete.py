#!/usr/bin/env python3
"""
Test Super Admin functionality after successful login
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def test_super_admin_functionality():
    """Test Super Admin functionality"""
    
    print("🔍 Testing Super Admin functionality...")
    print("=" * 60)
    
    # Login as Harvey258 to Test Band (org id 1)
    login_data = {
        "username": "Harvey258",
        "password": "password",
        "organization_id": 1  # Test Band where Harvey258 is Super Admin
    }
    
    try:
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"✅ Login successful to Test Band!")
            print(f"Role: {data.get('role')}")
            print(f"Super Admin: {data.get('super_admin')}")
            print(f"Organization: {data.get('organization')}")
            
            token = data['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test Super Admin overview endpoint
            print(f"\n🔍 Testing Super Admin overview...")
            overview_response = requests.get(f"{API_URL}/super-admin/overview", headers=headers)
            print(f"Overview status: {overview_response.status_code}")
            
            if overview_response.status_code == 200:
                overview_data = overview_response.json()
                print(f"✅ Super Admin overview successful!")
                print(f"Total organizations: {overview_data['stats']['total_organizations']}")
                print(f"Total users: {overview_data['stats']['total_users']}")
                print(f"Total events: {overview_data['stats']['total_events']}")
                
                print(f"\nOrganizations:")
                for org in overview_data['organizations']:
                    print(f"  - {org['name']} (ID: {org['id']}) - {org['user_count']} users, {org['event_count']} events")
            else:
                print(f"❌ Super Admin overview failed: {overview_response.status_code}")
                print(f"Error: {overview_response.text}")
            
            # Test regular admin endpoints
            print(f"\n🔍 Testing regular admin endpoints...")
            users_response = requests.get(f"{API_URL}/admin/users", headers=headers)
            print(f"Admin users status: {users_response.status_code}")
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"✅ Admin users successful! Found {len(users_data)} users")
                for user in users_data:
                    print(f"  - {user['username']} ({user['email']}) - {user['role']}")
            else:
                print(f"❌ Admin users failed: {users_response.status_code}")
                print(f"Error: {users_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Error: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_cbbb25_login():
    """Test CBBB25 login"""
    
    print(f"\n" + "=" * 60)
    print("🔍 Testing CBBB25 login...")
    
    login_data = {
        "username": "CBBB25", 
        "password": "password"
    }
    
    try:
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"✅ CBBB25 login successful!")
            print(f"Role: {data.get('role')}")
            print(f"Super Admin: {data.get('super_admin')}")
            print(f"Organization: {data.get('organization')}")
            
            # Check if multiple organizations
            if data.get('multiple_organizations'):
                print(f"Multiple organizations available:")
                for org in data['organizations']:
                    print(f"  - {org['name']} (ID: {org['id']}, Role: {org['role']})")
                    
        else:
            print(f"❌ CBBB25 login failed: {login_response.status_code}")
            print(f"Error: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_super_admin_functionality()
    test_cbbb25_login()
