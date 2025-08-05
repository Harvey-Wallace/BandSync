#!/usr/bin/env python3
"""
Test script to verify RSVP endpoints are working correctly
This script tests all the RSVP endpoints you mentioned needing.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_EVENT_ID = 1  # You'll need to use a real event ID from your database

def test_rsvp_endpoints():
    """Test all RSVP endpoints"""
    
    print("🧪 BandSync RSVP Endpoints Test")
    print("=" * 50)
    
    # Test credentials - using the local test credentials
    login_data = {
        "email": "test@bandsync.com",     # Local test user
        "password": "password123"         # Local test password
    }
    
    # First, login to get auth token
    print("1. Testing Authentication...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Login successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # 2. Test GET /api/events/ (list events)
    print("\n2. Testing GET /api/events/ (list events)...")
    try:
        response = requests.get(f"{BASE_URL}/events/", headers=headers)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Events list retrieved: {len(events)} events found")
            if events:
                # Use the first event for testing
                TEST_EVENT_ID = events[0]['id']
                print(f"📌 Using Event ID {TEST_EVENT_ID} for RSVP tests")
            else:
                print("⚠️  No events found - creating test event...")
                # You might need to create a test event here
                return False
        else:
            print(f"❌ Events list failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Events list request failed: {e}")
        return False
    
    # 3. Test GET /api/events/{id}/ (single event)
    print(f"\n3. Testing GET /api/events/{TEST_EVENT_ID}/ (single event)...")
    try:
        response = requests.get(f"{BASE_URL}/events/{TEST_EVENT_ID}", headers=headers)
        if response.status_code == 200:
            event = response.json()
            print(f"✅ Single event retrieved: {event.get('title', 'Unknown')}")
        else:
            print(f"❌ Single event failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Single event request failed: {e}")
        return False
    
    # 4. Test POST /api/events/{event_id}/rsvp/ (create RSVP)
    print(f"\n4. Testing POST /api/events/{TEST_EVENT_ID}/rsvp/ (create RSVP)...")
    rsvp_data = {
        "status": "attending",
        "event_id": TEST_EVENT_ID
    }
    try:
        response = requests.post(f"{BASE_URL}/events/{TEST_EVENT_ID}/rsvp/", 
                               json=rsvp_data, headers=headers)
        if response.status_code == 201:
            rsvp = response.json()
            print(f"✅ RSVP created: {rsvp.get('status')} for event {rsvp.get('event_id')}")
        elif response.status_code == 400 and "already exists" in response.text:
            print("✅ RSVP already exists (as expected)")
        else:
            print(f"❌ Create RSVP failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create RSVP request failed: {e}")
        return False
    
    # 5. Test GET /api/events/{event_id}/rsvp/ (get RSVP status)
    print(f"\n5. Testing GET /api/events/{TEST_EVENT_ID}/rsvp/ (get RSVP status)...")
    try:
        response = requests.get(f"{BASE_URL}/events/{TEST_EVENT_ID}/rsvp/", headers=headers)
        if response.status_code == 200:
            rsvp = response.json()
            print(f"✅ RSVP status retrieved: {rsvp.get('status')} for user {rsvp.get('user_id')}")
            print(f"   Timestamp: {rsvp.get('timestamp')}")
        elif response.status_code == 404:
            print("✅ RSVP not found (as expected if none exists)")
        else:
            print(f"❌ Get RSVP failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get RSVP request failed: {e}")
        return False
    
    # 6. Test PUT /api/events/{event_id}/rsvp/ (update RSVP)
    print(f"\n6. Testing PUT /api/events/{TEST_EVENT_ID}/rsvp/ (update RSVP)...")
    update_data = {
        "status": "maybe",
        "event_id": TEST_EVENT_ID
    }
    try:
        response = requests.put(f"{BASE_URL}/events/{TEST_EVENT_ID}/rsvp/", 
                              json=update_data, headers=headers)
        if response.status_code == 200:
            rsvp = response.json()
            print(f"✅ RSVP updated: {rsvp.get('status')} for event {rsvp.get('event_id')}")
        else:
            print(f"❌ Update RSVP failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update RSVP request failed: {e}")
        return False
    
    # 7. Test DELETE /api/events/{event_id}/rsvp/ (delete RSVP)
    print(f"\n7. Testing DELETE /api/events/{TEST_EVENT_ID}/rsvp/ (delete RSVP)...")
    try:
        response = requests.delete(f"{BASE_URL}/events/{TEST_EVENT_ID}/rsvp/", headers=headers)
        if response.status_code == 204:
            print("✅ RSVP deleted successfully")
        else:
            print(f"❌ Delete RSVP failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Delete RSVP request failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All RSVP endpoints are working correctly!")
    print("\nAPI Endpoints Status:")
    print("✅ GET /api/events/ (list events)")
    print("✅ GET /api/events/{id}/ (single event)")
    print("✅ GET /api/events/{event_id}/rsvp/ (get user RSVP)")
    print("✅ POST /api/events/{event_id}/rsvp/ (create RSVP)")
    print("✅ PUT /api/events/{event_id}/rsvp/ (update RSVP)")
    print("✅ DELETE /api/events/{event_id}/rsvp/ (delete RSVP)")
    
    return True

def usage():
    """Print usage instructions"""
    print("""
Usage: python3 test_rsvp_endpoints.py

This script tests all the RSVP endpoints for your mobile app.

Prerequisites:
1. Flask server must be running on localhost:5000
2. You need valid test credentials (update login_data in the script)
3. At least one event must exist in the database

To start the server:
    cd /Users/robertharvey/Documents/GitHub/BandSync/backend
    python3 app.py

To run this test:
    python3 test_rsvp_endpoints.py
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        usage()
        sys.exit(0)
    
    print("🚀 Starting RSVP endpoints test...")
    print("⚠️  Make sure your Flask server is running on localhost:5000")
    print("⚠️  Update the login credentials in this script for your test user")
    print()
    
    success = test_rsvp_endpoints()
    sys.exit(0 if success else 1)
