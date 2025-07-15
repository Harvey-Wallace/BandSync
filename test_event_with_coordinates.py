#!/usr/bin/env python3
"""
Test event creation with coordinates
"""

import requests
import json

def test_event_creation_with_coordinates():
    """Test creating an event with lat/lng coordinates"""
    print("🧪 Testing event creation with coordinates...")
    
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
        
        # Create event with coordinates
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # London coordinates for testing
        event_data = {
            "title": "Test Event with Map",
            "description": "Testing event with coordinates for map display",
            "date": "2025-08-01T19:00:00",
            "type": "Rehearsal",
            "location_address": "London Eye, London, UK",
            "lat": 51.5033,
            "lng": -0.1196
        }
        
        print(f"Creating event with coordinates: {json.dumps(event_data, indent=2)}")
        
        response = requests.post(
            "https://bandsync-production.up.railway.app/api/events/",
            headers=headers,
            json=event_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Event created successfully! ID: {data['id']}")
            
            # Now fetch the event to verify coordinates were saved
            print("\n🧪 Verifying event coordinates...")
            
            events_response = requests.get(
                "https://bandsync-production.up.railway.app/api/events/",
                headers=headers
            )
            
            if events_response.status_code == 200:
                events = events_response.json()
                
                # Find our newly created event
                new_event = None
                for event in events:
                    if event.get('id') == data['id']:
                        new_event = event
                        break
                
                if new_event:
                    print(f"📍 Event: {new_event.get('title')}")
                    print(f"  Location Address: {new_event.get('location_address')}")
                    print(f"  Latitude: {new_event.get('lat')}")
                    print(f"  Longitude: {new_event.get('lng')}")
                    
                    if new_event.get('lat') and new_event.get('lng'):
                        print("✅ Coordinates saved successfully - map should work!")
                        
                        # Test the map URL
                        api_key = "AIzaSyC11N3v1N5Gl14LJ2Cl9TjasJNzE5wVkEc"
                        map_url = f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={new_event['lat']},{new_event['lng']}&zoom=14"
                        print(f"🗺️  Map URL: {map_url}")
                        
                        # Test if the map URL works
                        map_response = requests.get(map_url)
                        if map_response.status_code == 200:
                            print("✅ Map URL is accessible!")
                        else:
                            print(f"❌ Map URL failed: {map_response.status_code}")
                    else:
                        print("❌ Coordinates not saved properly")
                else:
                    print("❌ Could not find newly created event")
            else:
                print(f"❌ Failed to fetch events: {events_response.status_code}")
                
        else:
            print(f"❌ Event creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_event_creation_with_coordinates()
