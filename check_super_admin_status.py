#!/usr/bin/env python3
"""
Check and fix Super Admin status for Harvey258
"""

import requests
import json

# API Configuration  
API_URL = "https://bandsync-production.up.railway.app/api"

def check_super_admin_status():
    """Check Super Admin database status directly via API"""
    
    print("🔍 Checking Super Admin status...")
    print("=" * 50)
    
    # Login as Harvey258 to any organization
    login_data = {"username": "Harvey258", "password": "password"}
    
    try:
        # First login
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        login_result = login_response.json()
        
        if login_result.get('multiple_organizations'):
            # Select the first organization
            orgs = login_result['organizations']
            selected_org = orgs[0]  # Default org
            
            # Login with organization
            org_login_data = {**login_data, "organization_id": selected_org['id']}
            org_response = requests.post(f"{API_URL}/auth/login", json=org_login_data)
            
            if org_response.status_code == 200:
                token_data = org_response.json()
                token = token_data['access_token']
                
                print(f"✅ Logged in to: {selected_org['name']}")
                print(f"   Role in org: {selected_org['role']}")
                print(f"   JWT super_admin claim: {token_data.get('super_admin', 'Not present')}")
                
                # Try Super Admin endpoint
                headers = {"Authorization": f"Bearer {token}"}
                test_response = requests.get(f"{API_URL}/super-admin/overview", headers=headers)
                
                print(f"\n🔍 Super Admin endpoint test:")
                print(f"   Status: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    print("   ✅ Super Admin access working!")
                    overview = test_response.json()
                    print(f"   Found {len(overview.get('organizations', []))} organizations")
                elif test_response.status_code == 403:
                    print("   ❌ Access denied - not recognized as Super Admin")
                    print(f"   Response: {test_response.text}")
                else:
                    print(f"   ❌ Error: {test_response.status_code}")
                    print(f"   Response: {test_response.text}")
                    
            else:
                print(f"❌ Organization login failed: {org_response.status_code}")
        else:
            print("❌ Expected multiple organizations response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_super_admin_status()
