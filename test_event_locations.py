#!/usr/bin/env python3
"""
Test event data to check if lat/lng coordinates are available
"""

import requests
import json

def test_event_location_data():
    """Test if events have location data for maps"""
    print("🧪 Testing event location data...")
    
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
        
        # Get events
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/events/",
            headers=headers
        )
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Found {len(events)} events")
            
            for i, event in enumerate(events):
                print(f"\n📍 Event {i+1}: {event.get('title', 'Untitled')}")
                print(f"  Location Address: {event.get('location_address', 'None')}")
                print(f"  Latitude: {event.get('lat', 'None')}")
                print(f"  Longitude: {event.get('lng', 'None')}")
                print(f"  Location (legacy): {event.get('location', 'None')}")
                
                # Check if this event has coordinates for maps
                if event.get('lat') and event.get('lng'):
                    print(f"  ✅ Has coordinates - map should work")
                else:
                    print(f"  ❌ Missing coordinates - map won't work")
                    
        else:
            print(f"❌ Failed to get events: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_event_location_data()
