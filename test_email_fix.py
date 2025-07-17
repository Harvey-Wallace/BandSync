#!/usr/bin/env python3
"""
Test email invitation fix for multi-organization support
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def test_email_invitation():
    """Test email invitation functionality"""
    
    print("🔍 Testing email invitation functionality...")
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
                    
                    # Test user creation with email invitation
                    test_user_data = {
                        "username": "test_email_user",
                        "email": "test@example.com",
                        "name": "Test Email User",
                        "role": "Member",
                        "send_invitation": True
                    }
                    
                    print(f"📧 Creating test user with email invitation...")
                    create_response = requests.post(f"{API_URL}/admin/users", 
                                                    json=test_user_data, 
                                                    headers=headers)
                    
                    if create_response.status_code == 200:
                        result = create_response.json()
                        print(f"✅ User created successfully: {result.get('msg', 'No message')}")
                        
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

if __name__ == "__main__":
    test_email_invitation()
