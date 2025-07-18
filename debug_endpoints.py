#!/usr/bin/env python3
"""
Debug script to compare different user endpoints
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def debug_endpoints():
    """Debug different user endpoints"""
    
    print("🔍 Debugging user endpoints...")
    print("=" * 60)
    
    # You'll need to get a valid token by logging in through the browser
    # Go to Network tab, login, and copy the Authorization header
    token = input("Please paste your authorization token (from browser network tab): ")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n1. Testing /admin/users endpoint...")
    try:
        response = requests.get(f"{API_URL}/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ /admin/users returned {len(users)} users:")
            for user in users:
                print(f"     - {user['username']} ({user.get('name', 'No name')}) - {user['role']}")
        else:
            print(f"   ❌ /admin/users failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n2. Testing /admin/users/all endpoint...")
    try:
        response = requests.get(f"{API_URL}/admin/users/all", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ /admin/users/all returned {len(users)} users:")
            for user in users:
                print(f"     - {user['username']} ({user.get('name', 'No name')}) - ID: {user['id']}")
        else:
            print(f"   ❌ /admin/users/all failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n3. Testing /events/1/rsvps endpoint (if event exists)...")
    try:
        response = requests.get(f"{API_URL}/events/1/rsvps", headers=headers)
        if response.status_code == 200:
            rsvps = response.json()
            print(f"   ✅ /events/1/rsvps returned:")
            for status, users in rsvps.items():
                print(f"     {status}: {len(users)} users")
                for user in users:
                    print(f"       - {user['username']} ({user.get('name', 'No name')})")
        else:
            print(f"   ❌ /events/1/rsvps failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_endpoints()
