#!/usr/bin/env python3
"""
Test calendar stats endpoint specifically
"""

import requests
import json

def test_calendar_stats():
    """Test the calendar stats endpoint"""
    print("🧪 Testing calendar stats endpoint...")
    
    # First login
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
        
        # Test calendar stats
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/admin/calendar-stats",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Calendar stats endpoint working!")
            try:
                data = response.json()
                print(f"Data: {json.dumps(data, indent=2)}")
            except:
                print("Response is not valid JSON")
        else:
            print("❌ Calendar stats endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_calendar_stats()
