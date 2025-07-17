#!/usr/bin/env python3
"""
Debug script to check admin user organization memberships
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def debug_admin_user():
    """Debug admin user organization memberships"""
    
    print("🔍 Debugging admin user organization memberships...")
    print("=" * 60)
    
    # Test different possible admin credentials
    possible_credentials = [
        {"username": "CBBB25", "password": "admin123"},
        {"username": "admin", "password": "admin123"},
        {"username": "CBBB25", "password": "password"},
        {"username": "admin", "password": "password"},
    ]
    
    for creds in possible_credentials:
        print(f"\n🔐 Trying credentials: {creds['username']}...")
        
        try:
            # Try to login
            login_response = requests.post(f"{API_URL}/auth/login", json=creds)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"✅ Login successful for {creds['username']}")
                
                # Check if multiple organizations
                if login_data.get('multiple_organizations'):
                    print(f"👥 User belongs to {len(login_data['organizations'])} organizations:")
                    for org in login_data['organizations']:
                        print(f"   - {org['name']} (ID: {org['id']}, Role: {org['role']})")
                    
                    # Check each organization
                    for org in login_data['organizations']:
                        print(f"\n📊 Checking users in '{org['name']}'...")
                        
                        # Login to specific organization
                        org_login = requests.post(f"{API_URL}/auth/login", json={
                            **creds,
                            "organization_id": org['id']
                        })
                        
                        if org_login.status_code == 200:
                            org_data = org_login.json()
                            token = org_data['access_token']
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            # Get users in this organization
                            users_response = requests.get(f"{API_URL}/admin/users", headers=headers)
                            
                            if users_response.status_code == 200:
                                users_data = users_response.json()
                                print(f"   Users in {org['name']} ({len(users_data)}):")
                                
                                admin_found = False
                                for user in users_data:
                                    print(f"     - {user['username']} ({user['email']}) - {user['role']}")
                                    if user['username'] == creds['username']:
                                        admin_found = True
                                
                                if not admin_found:
                                    print(f"   ❌ Admin user {creds['username']} NOT found in {org['name']} user list")
                                else:
                                    print(f"   ✅ Admin user {creds['username']} found in {org['name']} user list")
                            else:
                                print(f"   ❌ Failed to get users: {users_response.status_code}")
                else:
                    print("📍 Single organization login")
                    # Handle single organization
                    token = login_data['access_token']
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Get users
                    users_response = requests.get(f"{API_URL}/admin/users", headers=headers)
                    
                    if users_response.status_code == 200:
                        users_data = users_response.json()
                        print(f"   Users ({len(users_data)}):")
                        
                        admin_found = False
                        for user in users_data:
                            print(f"     - {user['username']} ({user['email']}) - {user['role']}")
                            if user['username'] == creds['username']:
                                admin_found = True
                        
                        if not admin_found:
                            print(f"   ❌ Admin user {creds['username']} NOT found in user list")
                        else:
                            print(f"   ✅ Admin user {creds['username']} found in user list")
                    else:
                        print(f"   ❌ Failed to get users: {users_response.status_code}")
                
                break  # Stop trying other credentials
                
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n💡 **Solution**: Use the 'Add Existing User' feature to add the admin user to the organization")
    print(f"   1. Click 'Add Existing User' (blue button)")
    print(f"   2. Enter admin username")
    print(f"   3. Select Role: Admin")
    print(f"   4. Click 'Add User'")

if __name__ == "__main__":
    debug_admin_user()
