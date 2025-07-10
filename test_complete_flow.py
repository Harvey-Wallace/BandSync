#!/usr/bin/env python3

import requests
import json
import time

# Configuration
API_URL = "http://127.0.0.1:5001/api"

def test_complete_multi_org_flow():
    """Test the complete multi-organization flow"""
    
    print("Testing Complete Multi-Organization Flow")
    print("="*60)
    
    # Step 1: Initial login (should return multiple organizations)
    print("1. Testing initial login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('multiple_organizations'):
            print("✅ Login returned multiple organizations")
            orgs = data['organizations']
            for org in orgs:
                print(f"   - {org['name']} (Role: {org['role']})")
            
            # Step 2: Login with specific organization
            print(f"\n2. Logging in with specific organization: {orgs[0]['name']}")
            login_with_org = {
                **login_data,
                "organization_id": orgs[0]['id']
            }
            
            org_response = requests.post(f"{API_URL}/auth/login", json=login_with_org)
            
            if org_response.status_code == 200:
                org_data = org_response.json()
                token = org_data['access_token']
                headers = {"Authorization": f"Bearer {token}"}
                
                print("✅ Successfully logged in with organization")
                print(f"   - Organization: {org_data.get('organization')}")
                print(f"   - Role: {org_data.get('role')}")
                
                # Step 3: Test current organization API
                print(f"\n3. Testing current organization API...")
                current_response = requests.get(f"{API_URL}/organizations/current", headers=headers)
                
                if current_response.status_code == 200:
                    current_data = current_response.json()
                    print("✅ Current organization API works")
                    print(f"   - Current org: {current_data.get('organization', {}).get('name')}")
                    print(f"   - Role: {current_data.get('role')}")
                
                # Step 4: Test available organizations API
                print(f"\n4. Testing available organizations API...")
                available_response = requests.get(f"{API_URL}/organizations/available", headers=headers)
                
                if available_response.status_code == 200:
                    available_data = available_response.json()
                    available_orgs = available_data['organizations']
                    print("✅ Available organizations API works")
                    print(f"   - Found {len(available_orgs)} organizations")
                    
                    # Step 5: Test organization switching
                    if len(available_orgs) > 1:
                        other_org = next((org for org in available_orgs 
                                        if org['id'] != orgs[0]['id']), None)
                        
                        if other_org:
                            print(f"\n5. Testing organization switch to: {other_org['name']}")
                            switch_data = {"organization_id": other_org['id']}
                            switch_response = requests.post(f"{API_URL}/organizations/switch", 
                                                          json=switch_data, headers=headers)
                            
                            if switch_response.status_code == 200:
                                switch_result = switch_response.json()
                                new_token = switch_result['access_token']
                                new_headers = {"Authorization": f"Bearer {new_token}"}
                                
                                print("✅ Organization switch successful")
                                print(f"   - New organization: {switch_result.get('organization', {}).get('name')}")
                                print(f"   - New role: {switch_result.get('role')}")
                                
                                # Step 6: Verify new context
                                print(f"\n6. Verifying new organization context...")
                                verify_response = requests.get(f"{API_URL}/organizations/current", headers=new_headers)
                                
                                if verify_response.status_code == 200:
                                    verify_data = verify_response.json()
                                    print("✅ New organization context verified")
                                    print(f"   - Current org: {verify_data.get('organization', {}).get('name')}")
                                    print(f"   - Role: {verify_data.get('role')}")
                                
                                # Step 7: Test that events API respects organization context
                                print(f"\n7. Testing events API with new organization context...")
                                events_response = requests.get(f"{API_URL}/events", headers=new_headers)
                                
                                if events_response.status_code == 200:
                                    events_data = events_response.json()
                                    print("✅ Events API works with new organization context")
                                    print(f"   - Found {len(events_data)} events for {verify_data.get('organization', {}).get('name')}")
                                else:
                                    print(f"⚠️  Events API returned: {events_response.status_code}")
                            else:
                                print(f"❌ Organization switch failed: {switch_response.text}")
                    else:
                        print("ℹ️  Only one organization available, skipping switch test")
                else:
                    print(f"❌ Available organizations API failed: {available_response.text}")
            else:
                print(f"❌ Login with organization failed: {org_response.text}")
        else:
            print("ℹ️  User only belongs to one organization")
    else:
        print(f"❌ Initial login failed: {response.text}")

def print_frontend_test_instructions():
    """Print instructions for manual frontend testing"""
    
    print("\n" + "="*60)
    print("Frontend Testing Instructions")
    print("="*60)
    print("1. Open browser to: http://localhost:3000")
    print("2. Login with username: admin, password: admin123")
    print("3. You should see an organization selection screen with:")
    print("   - Demo Organization (Admin)")
    print("   - Second Band (Member)")
    print("4. Select 'Demo Organization' and continue")
    print("5. Once logged in, look for organization switcher in navbar")
    print("6. Click on the organization name in navbar to switch")
    print("7. Select 'Second Band' to switch organizations")
    print("8. Verify that:")
    print("   - Page refreshes with new organization context")
    print("   - Organization name updates in navbar")
    print("   - User role may change based on organization")
    print("   - Events and other data reflect the new organization")
    print("\nExpected behavior:")
    print("- Organization switcher should appear as a clickable badge")
    print("- Dropdown should show available organizations")
    print("- Current organization should be highlighted")
    print("- Switching should refresh the page with new context")

if __name__ == "__main__":
    test_complete_multi_org_flow()
    print_frontend_test_instructions()
