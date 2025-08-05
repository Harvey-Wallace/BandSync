#!/usr/bin/env python3
"""
Test script for RSVP endpoints
Tests the new mobile-compatible RSVP API endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5001"
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def login(credentials):
    """Login and return JWT token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)
    if response.status_code == 200:
        data = response.json()
        # Handle multi-organization login
        if data.get("multiple_organizations"):
            # Select first organization and login again
            org_id = data["organizations"][0]["id"]
            credentials_with_org = {**credentials, "organization_id": org_id}
            response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials_with_org)
            if response.status_code == 200:
                return response.json()["access_token"]
        else:
            return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_endpoints(token):
    """Test all RSVP endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing RSVP endpoints...")
    
    # First, get events to find an event ID
    print("\n1. Getting events list...")
    response = requests.get(f"{BASE_URL}/api/events/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get events: {response.status_code} - {response.text}")
        return False
    
    events = response.json()
    if not events:
        print("❌ No events found. Please create an event first.")
        return False
    
    event_id = events[0]['id']
    print(f"✅ Found event ID: {event_id}")
    
    # Test 1: Get single event (should work now)
    print(f"\n2. Testing GET /api/events/{event_id}/")
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/", headers=headers)
    if response.status_code == 200:
        print("✅ Single event endpoint works")
    else:
        print(f"❌ Single event endpoint failed: {response.status_code} - {response.text}")
    
    # Test 2: Get RSVP status (should return 404 if no RSVP exists)
    print(f"\n3. Testing GET /api/events/{event_id}/rsvp/")
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/rsvp/", headers=headers)
    if response.status_code == 404:
        print("✅ Get RSVP returns 404 for non-existent RSVP (expected)")
    elif response.status_code == 200:
        print(f"✅ Get RSVP returns existing RSVP: {response.json()}")
        # If RSVP exists, we'll delete it first to test creation
        print(f"   Deleting existing RSVP to test creation...")
        delete_response = requests.delete(f"{BASE_URL}/api/events/{event_id}/rsvp/", headers=headers)
        if delete_response.status_code == 204:
            print("✅ Deleted existing RSVP")
        else:
            print(f"❌ Failed to delete RSVP: {delete_response.status_code}")
    else:
        print(f"❌ Get RSVP failed: {response.status_code} - {response.text}")
    
    # Test 3: Create new RSVP
    print(f"\n4. Testing POST /api/events/{event_id}/rsvp/")
    rsvp_data = {"status": "attending", "event_id": event_id}
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/rsvp/", 
                           json=rsvp_data, headers=headers)
    if response.status_code == 201:
        created_rsvp = response.json()
        print(f"✅ Created RSVP: {created_rsvp}")
        
        # Verify it has the expected format
        expected_fields = ['status', 'event_id', 'user_id', 'timestamp']
        if all(field in created_rsvp for field in expected_fields):
            print("✅ RSVP response has all expected fields")
        else:
            print(f"❌ RSVP response missing fields. Got: {list(created_rsvp.keys())}")
            
        if created_rsvp['status'] == 'attending':
            print("✅ Status correctly returned as 'attending'")
        else:
            print(f"❌ Status incorrect. Expected 'attending', got '{created_rsvp['status']}'")
    else:
        print(f"❌ Create RSVP failed: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Try to create duplicate RSVP (should fail)
    print(f"\n5. Testing duplicate RSVP creation (should fail)")
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/rsvp/", 
                           json=rsvp_data, headers=headers)
    if response.status_code == 400:
        print("✅ Duplicate RSVP creation correctly rejected")
    else:
        print(f"❌ Duplicate RSVP creation should fail with 400, got: {response.status_code}")
    
    # Test 5: Get RSVP status (should work now)
    print(f"\n6. Testing GET /api/events/{event_id}/rsvp/ (should find RSVP)")
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/rsvp/", headers=headers)
    if response.status_code == 200:
        rsvp_data = response.json()
        print(f"✅ Get RSVP works: {rsvp_data}")
        if rsvp_data['status'] == 'attending':
            print("✅ Status correctly returned as 'attending'")
        else:
            print(f"❌ Status incorrect. Expected 'attending', got '{rsvp_data['status']}'")
    else:
        print(f"❌ Get RSVP failed: {response.status_code} - {response.text}")
    
    # Test 6: Update RSVP
    print(f"\n7. Testing PUT /api/events/{event_id}/rsvp/")
    update_data = {"status": "maybe", "event_id": event_id}
    response = requests.put(f"{BASE_URL}/api/events/{event_id}/rsvp/", 
                          json=update_data, headers=headers)
    if response.status_code == 200:
        updated_rsvp = response.json()
        print(f"✅ Updated RSVP: {updated_rsvp}")
        if updated_rsvp['status'] == 'maybe':
            print("✅ Status correctly updated to 'maybe'")
        else:
            print(f"❌ Status incorrect. Expected 'maybe', got '{updated_rsvp['status']}'")
    else:
        print(f"❌ Update RSVP failed: {response.status_code} - {response.text}")
    
    # Test 7: Test invalid status
    print(f"\n8. Testing invalid status (should fail)")
    invalid_data = {"status": "invalid_status", "event_id": event_id}
    response = requests.put(f"{BASE_URL}/api/events/{event_id}/rsvp/", 
                          json=invalid_data, headers=headers)
    if response.status_code == 400:
        print("✅ Invalid status correctly rejected")
    else:
        print(f"❌ Invalid status should fail with 400, got: {response.status_code}")
    
    # Test 8: Delete RSVP
    print(f"\n9. Testing DELETE /api/events/{event_id}/rsvp/")
    response = requests.delete(f"{BASE_URL}/api/events/{event_id}/rsvp/", headers=headers)
    if response.status_code == 204:
        print("✅ Delete RSVP works")
    else:
        print(f"❌ Delete RSVP failed: {response.status_code} - {response.text}")
    
    # Test 9: Verify RSVP is deleted
    print(f"\n10. Verifying RSVP deletion")
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/rsvp/", headers=headers)
    if response.status_code == 404:
        print("✅ RSVP correctly deleted (returns 404)")
    else:
        print(f"❌ RSVP should be deleted, but get returned: {response.status_code}")
    
    # Test 10: Test backward compatibility with old format
    print(f"\n11. Testing backward compatibility with web format")
    old_format_data = {"status": "Yes"}
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/rsvp", 
                           json=old_format_data, headers=headers)
    if response.status_code == 200:
        print("✅ Backward compatibility with old format works")
    else:
        print(f"❌ Backward compatibility failed: {response.status_code} - {response.text}")
    
    return True

def main():
    print("🚀 Testing RSVP endpoints for mobile app compatibility...")
    
    # Login
    print("🔐 Logging in...")
    token = login(TEST_CREDENTIALS)
    if not token:
        print("❌ Failed to login")
        return False
    
    print(f"✅ Login successful")
    
    # Test endpoints
    success = test_endpoints(token)
    
    if success:
        print("\n🎉 All RSVP endpoint tests completed!")
        print("\n📱 Mobile app endpoints are ready:")
        print(f"   - GET /api/events/{{event_id}}/rsvp/ - Get user's RSVP status")
        print(f"   - POST /api/events/{{event_id}}/rsvp/ - Create new RSVP")
        print(f"   - PUT /api/events/{{event_id}}/rsvp/ - Update existing RSVP")
        print(f"   - DELETE /api/events/{{event_id}}/rsvp/ - Delete RSVP")
        print(f"   - Status format: attending/maybe/not_attending")
        return True
    else:
        print("\n❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
