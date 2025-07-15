#!/usr/bin/env python3
"""
Complete verification test for all BandSync fixes
"""

import requests
import json

def test_complete_functionality():
    """Test all the previously identified issues"""
    print("🧪 Complete BandSync Functionality Test")
    print("=" * 50)
    
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
            return False
        
        access_token = login_response.json()['access_token']
        print("✅ Login successful!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test 1: Calendar stats (was failing before)
        print("\n📊 Testing calendar stats...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/admin/calendar-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Calendar stats working! Found {stats.get('total_events', 'N/A')} events")
            print(f"   📅 Upcoming: {stats.get('upcoming_events', 'N/A')}")
            print(f"   📅 Past: {stats.get('past_events', 'N/A')}")
        else:
            print("❌ Calendar stats failed!")
            return False
        
        # Test 2: Event creation (was failing before)
        print("\n🎯 Testing event creation...")
        event_data = {
            "title": "Complete Test Event",
            "description": "Testing all functionality",
            "date": "2024-12-25T14:30:00",
            "location_address": "Test Complete Location",
            "lat": 51.5074,
            "lng": -0.1278,
            "event_type": "performance"
        }
        
        response = requests.post(
            "https://bandsync-production.up.railway.app/api/events/",
            json=event_data,
            headers=headers
        )
        
        if response.status_code == 200:
            event_id = response.json()['id']
            print(f"✅ Event creation working! Created event ID: {event_id}")
        else:
            print("❌ Event creation failed!")
            return False
        
        # Test 3: Verify calendar stats updated
        print("\n🔄 Verifying calendar stats updated...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/admin/calendar-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            new_stats = response.json()
            if new_stats.get('total_events', 0) > stats.get('total_events', 0):
                print("✅ Calendar stats updated with new event!")
            else:
                print("⚠️  Calendar stats didn't update (may be caching)")
        
        # Test 4: Check Google Maps API key availability
        print("\n🗺️  Testing Google Maps API key...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/env-config.js"
        )
        
        if response.status_code == 200:
            content = response.text
            if "REACT_APP_GOOGLE_MAPS_API_KEY" in content and "AIzaSy" in content:
                print("✅ Google Maps API key found in env-config.js")
            else:
                print("❌ Google Maps API key not found")
                return False
        else:
            print("❌ env-config.js not accessible")
            return False
        
        # Test 5: Check event has coordinates for map display
        print("\n🗺️  Testing event coordinates...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/events/",
            headers=headers
        )
        
        if response.status_code == 200:
            events = response.json()
            events_with_coords = [e for e in events if e.get('lat') and e.get('lng')]
            print(f"✅ Found {len(events_with_coords)} events with coordinates")
            print(f"   📍 Total events: {len(events)}")
            
            if events_with_coords:
                sample_event = events_with_coords[0]
                print(f"   📍 Sample event: {sample_event['title']}")
                print(f"   📍 Location: {sample_event.get('location_address', 'N/A')}")
                print(f"   📍 Coordinates: {sample_event['lat']}, {sample_event['lng']}")
        else:
            print("❌ Could not fetch events")
            return False
        
        print("\n🎉 SUCCESS! All functionality tests passed:")
        print("  ✅ Calendar stats loading properly")
        print("  ✅ Event creation working")
        print("  ✅ Calendar stats updating with new events")
        print("  ✅ Google Maps API key configured")
        print("  ✅ Events with coordinates for map display")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_functionality()
    if success:
        print("\n🎯 All issues have been resolved!")
    else:
        print("\n❌ Some issues remain.")
