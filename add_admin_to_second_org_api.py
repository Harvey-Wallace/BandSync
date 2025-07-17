#!/usr/bin/env python3
"""
Quick fix to add admin user to second organization
"""

import requests
import json

# Configuration
API_URL = "https://bandsync-production.up.railway.app/api"
admin_credentials = {
    "username": "admin",
    "password": "admin123"  # Update if different
}

def add_admin_to_second_org():
    """Add admin user to second organization using the API"""
    
    print("🔄 Adding admin user to second organization...")
    
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
                    print(f"     - {org['name']} (ID: {org['id']}, Role: {org['role']})")
                
                # Find the first organization (likely the main one)
                first_org = login_data['organizations'][0]
                print(f"   Logging into first organization: {first_org['name']}")
                
                # Login with organization context
                org_login_response = requests.post(f"{API_URL}/auth/login", json={
                    **admin_credentials,
                    "organization_id": first_org['id']
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
        
        # 2. Get available organizations
        print("\n2. Getting available organizations...")
        headers = {"Authorization": f"Bearer {token}"}
        
        orgs_response = requests.get(f"{API_URL}/organizations/available", headers=headers)
        
        if orgs_response.status_code == 200:
            orgs_data = orgs_response.json()
            available_orgs = orgs_data.get('organizations', [])
            
            print(f"   Found {len(available_orgs)} organizations:")
            for org in available_orgs:
                print(f"     - {org['name']} (ID: {org['id']}, Role: {org['role']})")
            
            # Find the second organization (not the current one)
            second_org = None
            for org in available_orgs:
                if org['id'] != current_org['id']:
                    second_org = org
                    break
            
            if second_org:
                print(f"\n3. Switching to second organization: {second_org['name']}")
                
                # Switch to second organization
                switch_response = requests.post(f"{API_URL}/organizations/switch", 
                                              json={"organization_id": second_org['id']}, 
                                              headers=headers)
                
                if switch_response.status_code == 200:
                    switch_data = switch_response.json()
                    new_token = switch_data['access_token']
                    new_headers = {"Authorization": f"Bearer {new_token}"}
                    
                    print(f"   ✅ Switched to: {second_org['name']}")
                    
                    # 4. Check users in second organization
                    print(f"\n4. Checking users in {second_org['name']}...")
                    
                    users_response = requests.get(f"{API_URL}/admin/users", headers=new_headers)
                    
                    if users_response.status_code == 200:
                        users_data = users_response.json()
                        print(f"   ✅ Found {len(users_data)} users in {second_org['name']}:")
                        
                        admin_found = False
                        for user in users_data:
                            print(f"     - {user['username']} ({user['email']}) - Role: {user['role']}")
                            if user['username'] == 'admin':
                                admin_found = True
                        
                        if admin_found:
                            print("   ✅ Admin user is already in the second organization!")
                        else:
                            print("   ❌ Admin user is missing from the second organization")
                            
                            # Try to add admin user using the "Add Existing User" feature
                            print("\n5. Adding admin user to second organization...")
                            
                            add_user_data = {
                                "username": "admin",
                                "role": "Admin",
                                "send_invitation": False
                            }
                            
                            add_response = requests.post(f"{API_URL}/admin/users/add-existing", 
                                                       json=add_user_data, 
                                                       headers=new_headers)
                            
                            if add_response.status_code == 201:
                                print("   ✅ Successfully added admin user to second organization!")
                                
                                # Verify by checking users again
                                verify_response = requests.get(f"{API_URL}/admin/users", headers=new_headers)
                                if verify_response.status_code == 200:
                                    verify_data = verify_response.json()
                                    print(f"   ✅ Verified: Now showing {len(verify_data)} users in {second_org['name']}:")
                                    for user in verify_data:
                                        print(f"     - {user['username']} ({user['email']}) - Role: {user['role']}")
                                        
                            else:
                                print(f"   ❌ Failed to add admin user: {add_response.status_code}")
                                try:
                                    error_data = add_response.json()
                                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                                except:
                                    print(f"   Error: {add_response.text}")
                    else:
                        print(f"   ❌ Failed to get users: {users_response.status_code}")
                else:
                    print(f"   ❌ Failed to switch organization: {switch_response.status_code}")
            else:
                print("   ❌ No second organization found")
        else:
            print(f"   ❌ Failed to get available organizations: {orgs_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_admin_to_second_org()
    print(f"\n{'🎉 Success!' if success else '❌ Failed!'}")
