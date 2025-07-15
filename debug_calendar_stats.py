#!/usr/bin/env python3
"""
Debug calendar stats issue
"""

import requests
import json

def debug_calendar_stats():
    """Debug calendar stats endpoint"""
    print("🧪 Debugging calendar stats...")
    
    # Login
    login_data = {
        "username": "Rob123",
        "password": "Rob123pass"
    }
    
    try:
        # Login
        login_response = requests.post(
            "https://bandsync-production.up.railway.app/api/auth/login",
            json=login_data
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed!")
            return
        
        access_token = login_response.json()['access_token']
        print("✅ Login successful!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test calendar stats
        print("\n📊 Testing calendar stats...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/events/stats",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Calendar stats working!")
            print(f"Stats: {json.dumps(stats, indent=2)}")
        else:
            print("❌ Calendar stats failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_calendar_stats()
