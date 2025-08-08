#!/usr/bin/env python3
"""
Test script to verify mobile API endpoints are working in production
Usage: python3 test_live_mobile_api.py <base_url> <jwt_token>
Example: python3 test_live_mobile_api.py https://your-app.railway.app eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
"""

import requests
import json
import sys

def test_organization_endpoint(base_url, token):
    """Test GET /api/organization endpoint"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🏢 Testing Organization Details Endpoint...")
    print(f"   URL: {base_url}/api/organization")
    
    try:
        response = requests.get(f"{base_url}/api/organization", headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Success! Response:")
            print(f"      - ID: {data.get('id')}")
            print(f"      - Name: {data.get('name')}")
            print(f"      - Logo URL: {data.get('logo_url', 'None')}")
            print(f"      - Theme: {data.get('settings', {}).get('theme_color', 'None')}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_members_endpoint(base_url, token):
    """Test GET /api/organization/members/ endpoint"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n👥 Testing Organization Members Endpoint...")
    print(f"   URL: {base_url}/api/organization/members/")
    
    try:
        response = requests.get(f"{base_url}/api/organization/members/", headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            members = data.get('members', [])
            print(f"   ✅ Success! Found {len(members)} members:")
            
            for member in members[:3]:  # Show first 3 members
                print(f"      - {member.get('name')} ({member.get('section', 'No section')}) - {member.get('role', 'No role')}")
            
            if len(members) > 3:
                print(f"      ... and {len(members) - 3} more members")
                
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 test_live_mobile_api.py <base_url> <jwt_token>")
        print("Example: python3 test_live_mobile_api.py https://your-app.railway.app eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    token = sys.argv[2]
    
    print("🧪 Testing BandSync Mobile API Endpoints")
    print("=" * 50)
    
    # Test organization endpoint
    org_success = test_organization_endpoint(base_url, token)
    
    # Test members endpoint
    members_success = test_members_endpoint(base_url, token)
    
    print("\n" + "=" * 50)
    if org_success and members_success:
        print("🎉 All mobile API endpoints are working correctly!")
        print("\n📱 Your React Native app should now be able to:")
        print("   - Display organization logos instead of placeholder initials")
        print("   - Show complete organization member lists")
        print("   - Access organization settings and contact information")
    else:
        print("❌ Some endpoints failed. Check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
