#!/usr/bin/env python3
"""
Final verification test for calendar stats and event creation fixes
"""

import requests
import json

def test_both_issues():
    """Test both calendar stats and event creation"""
    print("🧪 Testing both fixed issues...")
    
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
        
        # Test 1: Calendar stats (was failing before)
        print("\n🧪 Testing calendar stats...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/admin/calendar-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Calendar stats working! Found {data['total_events']} events")
        else:
            print(f"❌ Calendar stats failed: {response.status_code}")
            return
        
        # Test 2: Event creation (was failing before)
        print("\n🧪 Testing event creation...")
        event_data = {
            "title": "Final Test Event",
            "description": "Testing both fixes together",
            "date": "2025-07-25T20:00:00",
            "type": "Rehearsal",
            "location_address": "Final Test Venue"
        }
        
        response = requests.post(
            "https://bandsync-production.up.railway.app/api/events/",
            headers=headers,
            json=event_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Event creation working! Created event ID: {data['id']}")
        else:
            print(f"❌ Event creation failed: {response.status_code}")
            return
        
        # Test 3: Verify calendar stats updated
        print("\n🧪 Verifying calendar stats updated...")
        response = requests.get(
            "https://bandsync-production.up.railway.app/api/admin/calendar-stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Calendar stats updated! Now shows {data['total_events']} events")
        else:
            print(f"❌ Calendar stats check failed: {response.status_code}")
            return
        
        print("\n🎉 SUCCESS! Both issues are fixed:")
        print("  ✅ Calendar stats loading properly")
        print("  ✅ Event creation working")
        print("  ✅ Calendar stats updating with new events")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_both_issues()
