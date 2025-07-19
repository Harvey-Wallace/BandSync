#!/usr/bin/env python3
"""
Test Super Admin API endpoints to diagnose issues
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def test_super_admin_apis():
    """Test Super Admin API endpoints"""
    
    print("🔍 Testing Super Admin API endpoints...")
    print("=" * 60)
    
    # Login as Super Admin
    login_data = {"username": "Harvey258", "password": "password"}
    
    try:
        print("\n🔐 Logging in as Super Admin...")
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        login_result = login_response.json()
        print(f"🔍 Login response: {json.dumps(login_result, indent=2)}")
        
        if 'access_token' in login_result:
            token = login_result['access_token']
        elif login_result.get('multiple_organizations'):
            # Super Admin with multiple orgs - need to select one
            print("🔍 Multiple organizations detected, selecting first one...")
            orgs = login_result.get('organizations', [])
            if not orgs:
                print("❌ No organizations available")
                return
            
            # Try to login with a specific organization (use first one)
            selected_org = orgs[0]
            print(f"   Selecting organization: {selected_org['name']} (ID: {selected_org['id']})")
            
            # Login again with organization_id
            org_login_data = {**login_data, "organization_id": selected_org['id']}
            org_login_response = requests.post(f"{API_URL}/auth/login", json=org_login_data)
            
            if org_login_response.status_code != 200:
                print(f"❌ Organization login failed: {org_login_response.status_code}")
                print(org_login_response.text)
                return
            
            org_login_result = org_login_response.json()
            if 'access_token' not in org_login_result:
                print("❌ No access_token in organization login response")
                return
                
            token = org_login_result['access_token']
        else:
            print("❌ No access_token and not multiple organizations")
            return
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"✅ Login successful!")
        print(f"   Super Admin: {login_result.get('super_admin', False)}")
        
        # Test 1: Overview endpoint
        print("\n📊 Testing /super-admin/overview...")
        overview_response = requests.get(f"{API_URL}/super-admin/overview", headers=headers)
        print(f"   Status: {overview_response.status_code}")
        
        if overview_response.status_code == 200:
            overview_data = overview_response.json()
            print(f"   ✅ Organizations: {len(overview_data.get('organizations', []))}")
            print(f"   ✅ Total Users: {overview_data.get('stats', {}).get('total_users', 0)}")
            print(f"   ✅ Total Events: {overview_data.get('stats', {}).get('total_events', 0)}")
            
            # Test organization details for first org
            if overview_data.get('organizations'):
                first_org = overview_data['organizations'][0]
                org_id = first_org['id']
                
                print(f"\n🏢 Testing organization details for '{first_org['name']}'...")
                org_response = requests.get(f"{API_URL}/super-admin/organization/{org_id}/details", headers=headers)
                print(f"   Status: {org_response.status_code}")
                
                if org_response.status_code == 200:
                    org_data = org_response.json()
                    print(f"   ✅ Users: {len(org_data.get('users', []))}")
                    print(f"   ✅ Events: {len(org_data.get('events', []))}")
                    
                    # Show some user details
                    if org_data.get('users'):
                        print("   👥 Sample users:")
                        for user in org_data['users'][:3]:
                            print(f"      - {user['username']} ({user['role']}) - {user['email']}")
                else:
                    print(f"   ❌ Error: {org_response.text}")
        else:
            print(f"   ❌ Error: {overview_response.text}")
        
        # Test 2: User search
        print("\n🔍 Testing user search...")
        search_response = requests.get(f"{API_URL}/super-admin/users/search?q=Harvey", headers=headers)
        print(f"   Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            users = search_data.get('users', [])
            print(f"   ✅ Found {len(users)} users matching 'Harvey'")
            
            for user in users:
                print(f"      - {user['username']} - {user['email']}")
                if user.get('organizations'):
                    print(f"        Organizations: {[org['name'] for org in user['organizations']]}")
        else:
            print(f"   ❌ Error: {search_response.text}")
        
        # Test 3: System health
        print("\n⚡ Testing system health...")
        health_response = requests.get(f"{API_URL}/super-admin/system/health", headers=headers)
        print(f"   Status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Overall status: {health_data.get('status')}")
            print(f"   ✅ Database: {health_data.get('database', {}).get('status')}")
            
            if health_data.get('system'):
                system = health_data['system']
                print(f"   ✅ CPU: {system.get('cpu_percent')}%")
                print(f"   ✅ Memory: {system.get('memory_percent')}%")
                
            if health_data.get('activity'):
                activity = health_data['activity']
                print(f"   ✅ Recent logins: {activity.get('recent_logins_24h')}")
                print(f"   ✅ Recent events: {activity.get('recent_events_24h')}")
        else:
            print(f"   ❌ Error: {health_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_super_admin_apis()
