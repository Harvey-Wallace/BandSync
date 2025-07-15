#!/usr/bin/env python3
"""
Test event creation endpoint specifically
"""

import requests
import json

def test_event_creation():
    """Test the event creation endpoint"""
    print("🧪 Testing event creation endpoint...")
    
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
        
        # Test event creation
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        event_data = {
            "title": "Test Event",
            "description": "Test event description",
            "date": "2025-07-20T19:00:00",
            "type": "Rehearsal",
            "location_address": "Test Venue"
        }
        
        print(f"Creating event: {json.dumps(event_data, indent=2)}")
        
        response = requests.post(
            "https://bandsync-production.up.railway.app/api/events/",
            headers=headers,
            json=event_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Event creation successful!")
            try:
                data = response.json()
                print(f"Created event: {json.dumps(data, indent=2)}")
            except:
                print("Response is not valid JSON")
        else:
            print("❌ Event creation failed!")
            
            # Try to get more detailed error info
            if response.status_code == 500:
                print("Server error - checking logs...")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_event_creation()
