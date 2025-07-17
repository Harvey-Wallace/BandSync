#!/usr/bin/env python3
"""
Debug script to test password generation and email sending
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def test_password_generation():
    """Test password generation during user creation"""
    
    print("🔍 Testing password generation and email sending...")
    print("=" * 60)
    
    # Try to login as admin
    admin_creds = {"username": "CBBB25", "password": "admin123"}
    
    try:
        # Try to login
        login_response = requests.post(f"{API_URL}/auth/login", json=admin_creds)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"✅ Login successful as {admin_creds['username']}")
            
            # Select first organization
            if login_data.get('multiple_organizations'):
                org = login_data['organizations'][0]
                print(f"📍 Using organization: {org['name']}")
                
                # Login to specific organization
                org_login = requests.post(f"{API_URL}/auth/login", json={
                    **admin_creds,
                    "organization_id": org['id']
                })
                
                if org_login.status_code == 200:
                    org_data = org_login.json()
                    token = org_data['access_token']
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Test user creation WITHOUT providing password (should generate temp password)
                    test_user_data = {
                        "username": "password_test_user",
                        "email": "password_test@example.com",
                        "name": "Password Test User",
                        "role": "Member",
                        "send_invitation": True
                        # Note: NOT providing 'password' field - should generate temp password
                    }
                    
                    print(f"📧 Creating test user WITHOUT password (should generate temp password)...")
                    print(f"   Expected temp password: temp_password_test_user123")
                    
                    create_response = requests.post(f"{API_URL}/admin/users", 
                                                    json=test_user_data, 
                                                    headers=headers)
                    
                    if create_response.status_code == 200:
                        result = create_response.json()
                        print(f"✅ User created successfully")
                        print(f"📝 Response: {json.dumps(result, indent=2)}")
                        
                        # Check if temporary_password is in response
                        if 'temporary_password' in result:
                            temp_pass = result['temporary_password']
                            print(f"🔑 Temporary password in response: '{temp_pass}'")
                            if temp_pass:
                                print(f"✅ Temporary password generated successfully")
                            else:
                                print(f"❌ Temporary password is empty/null")
                        else:
                            print(f"❌ No temporary_password field in response")
                        
                        # Clean up - delete the test user
                        if 'user' in result:
                            user_id = result['user']['id']
                            delete_response = requests.delete(f"{API_URL}/admin/users/{user_id}", 
                                                             headers=headers)
                            if delete_response.status_code == 200:
                                print(f"🗑️  Test user cleaned up successfully")
                            else:
                                print(f"⚠️  Could not clean up test user: {delete_response.status_code}")
                        
                    else:
                        print(f"❌ User creation failed: {create_response.status_code}")
                        try:
                            error_data = create_response.json()
                            print(f"   Error: {error_data}")
                        except:
                            print(f"   Error: {create_response.text}")
                
                else:
                    print(f"❌ Organization login failed: {org_login.status_code}")
            
            else:
                print("❌ No multiple organizations found")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_add_existing_user():
    """Test adding existing user with password generation"""
    
    print(f"\n🔍 Testing 'Add Existing User' password generation...")
    print("=" * 60)
    
    admin_creds = {"username": "CBBB25", "password": "admin123"}
    
    try:
        # Login and get organization context
        login_response = requests.post(f"{API_URL}/auth/login", json=admin_creds)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            
            if login_data.get('multiple_organizations'):
                org = login_data['organizations'][0]
                
                # Login to specific organization
                org_login = requests.post(f"{API_URL}/auth/login", json={
                    **admin_creds,
                    "organization_id": org['id']
                })
                
                if org_login.status_code == 200:
                    org_data = org_login.json()
                    token = org_data['access_token']
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Test adding existing user Harvey258 with email invitation
                    add_user_data = {
                        "username": "Harvey258",
                        "role": "Member",
                        "send_invitation": True
                    }
                    
                    print(f"📧 Adding existing user Harvey258 with invitation...")
                    print(f"   Expected temp password: temp_Harvey258123")
                    
                    add_response = requests.post(f"{API_URL}/admin/users/add-existing", 
                                                json=add_user_data, 
                                                headers=headers)
                    
                    if add_response.status_code == 200:
                        result = add_response.json()
                        print(f"✅ User added successfully")
                        print(f"📝 Response: {json.dumps(result, indent=2)}")
                        
                    else:
                        print(f"❌ Add user failed: {add_response.status_code}")
                        try:
                            error_data = add_response.json()
                            print(f"   Error: {error_data}")
                        except:
                            print(f"   Error: {add_response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_password_generation()
    test_add_existing_user()
