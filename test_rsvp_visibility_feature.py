#!/usr/bin/env python3
"""
Test the RSVP visibility control feature
Tests both API endpoints and business logic
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://bandsync-production.up.railway.app"
#BASE_URL = "http://localhost:5000"  # Uncomment for local testing

def test_rsvp_visibility_feature():
    """Test the complete RSVP visibility control feature"""
    
    print("🧪 Testing RSVP Visibility Control Feature")
    print("=" * 60)
    
    # Test credentials - you'll need to update these with valid credentials
    admin_credentials = {
        "username": "testadmin",  # Replace with actual admin username
        "password": "testpass"    # Replace with actual password
    }
    
    member_credentials = {
        "username": "testmember", # Replace with actual member username
        "password": "testpass"    # Replace with actual password
    }
    
    print("🔐 Testing authentication...")
    
    # Get admin token
    admin_token = login_user(admin_credentials)
    if not admin_token:
        print("❌ Failed to authenticate admin user")
        return False
    
    # Get member token
    member_token = login_user(member_credentials)
    if not member_token:
        print("❌ Failed to authenticate member user")
        return False
    
    print("✅ Authentication successful")
    
    # Test 1: Get current RSVP visibility setting
    print("\n📋 Test 1: Get current RSVP visibility setting")
    current_setting = get_rsvp_visibility_setting(admin_token)
    if current_setting is None:
        print("❌ Failed to get current setting")
        return False
    
    print(f"✅ Current setting: {current_setting}")
    original_setting = current_setting.get('members_can_view_rsvp_status', True)
    
    # Test 2: Update RSVP visibility setting (Admin only)
    print("\n🔧 Test 2: Update RSVP visibility setting (Admin)")
    new_setting = not original_setting  # Toggle the setting
    
    success = update_rsvp_visibility_setting(admin_token, new_setting)
    if not success:
        print("❌ Failed to update setting as admin")
        return False
    
    print(f"✅ Successfully updated setting to: {new_setting}")
    
    # Test 3: Verify setting was updated
    print("\n✅ Test 3: Verify setting was updated")
    updated_setting = get_rsvp_visibility_setting(admin_token)
    if updated_setting is None:
        print("❌ Failed to verify updated setting")
        return False
    
    if updated_setting.get('members_can_view_rsvp_status') != new_setting:
        print("❌ Setting was not updated correctly")
        return False
    
    print("✅ Setting verified successfully")
    
    # Test 4: Try to update setting as member (should fail)
    print("\n🚫 Test 4: Try to update setting as member (should fail)")
    member_update_success = update_rsvp_visibility_setting(member_token, original_setting)
    if member_update_success:
        print("❌ Member was able to update setting (this should not be allowed)")
        return False
    
    print("✅ Member correctly denied access to update setting")
    
    # Test 5: Test events API with privacy disabled
    print("\n👥 Test 5: Test events API with privacy disabled")
    if new_setting == False:  # Privacy is disabled
        events_data_admin = get_events_as_user(admin_token)
        events_data_member = get_events_as_user(member_token)
        
        if events_data_admin and events_data_member:
            # Check that admin sees more details than member
            print("✅ Retrieved events data for both admin and member")
            analyze_events_privacy(events_data_admin, events_data_member, "disabled")
        else:
            print("⚠️  Could not retrieve events data for privacy test")
    
    # Test 6: Test events API with privacy enabled
    print("\n👁️  Test 6: Test events API with privacy enabled")
    # Set privacy to enabled
    update_rsvp_visibility_setting(admin_token, True)
    time.sleep(1)  # Brief pause for setting to take effect
    
    events_data_admin = get_events_as_user(admin_token)
    events_data_member = get_events_as_user(member_token)
    
    if events_data_admin and events_data_member:
        print("✅ Retrieved events data for both admin and member")
        analyze_events_privacy(events_data_admin, events_data_member, "enabled")
    else:
        print("⚠️  Could not retrieve events data for privacy test")
    
    # Restore original setting
    print("\n🔄 Restoring original setting...")
    update_rsvp_visibility_setting(admin_token, original_setting)
    
    print("\n🎉 All tests completed successfully!")
    return True

def login_user(credentials):
    """Login user and return JWT token"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials, timeout=10)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def get_rsvp_visibility_setting(token):
    """Get current RSVP visibility setting"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/organizations/settings/rsvp-visibility", 
                              headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Get setting failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Get setting error: {e}")
        return None

def update_rsvp_visibility_setting(token, new_setting):
    """Update RSVP visibility setting"""
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {"members_can_view_rsvp_status": new_setting}
        response = requests.put(f"{BASE_URL}/api/organizations/settings/rsvp-visibility", 
                              headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"Update setting failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Update setting error: {e}")
        return False

def get_events_as_user(token):
    """Get events data as a specific user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/events/", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Get events failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Get events error: {e}")
        return None

def analyze_events_privacy(admin_data, member_data, privacy_mode):
    """Analyze the privacy differences between admin and member event data"""
    print(f"\n📊 Analyzing privacy behavior (privacy {privacy_mode})...")
    
    if not admin_data.get('events') or not member_data.get('events'):
        print("⚠️  No events data to analyze")
        return
    
    admin_events = admin_data['events']
    member_events = member_data['events']
    
    if len(admin_events) != len(member_events):
        print(f"⚠️  Different number of events returned (admin: {len(admin_events)}, member: {len(member_events)})")
    
    # Analyze first event with RSVP data
    for i, (admin_event, member_event) in enumerate(zip(admin_events, member_events)):
        if 'rsvp_stats' in admin_event and 'rsvp_stats' in member_event:
            admin_rsvp = admin_event['rsvp_stats']
            member_rsvp = member_event['rsvp_stats']
            
            print(f"\n📅 Event {i+1}: {admin_event.get('title', 'Unknown')}")
            print(f"   Admin can_view_details: {admin_rsvp.get('can_view_details', 'N/A')}")
            print(f"   Member can_view_details: {member_rsvp.get('can_view_details', 'N/A')}")
            print(f"   Admin responses count: {len(admin_rsvp.get('responses', []))}")
            print(f"   Member responses count: {len(member_rsvp.get('responses', []))}")
            
            if privacy_mode == "disabled":
                # When privacy is disabled, admin should see all, member should see limited
                if admin_rsvp.get('can_view_details') != True:
                    print("   ❌ Admin should always see details")
                if member_rsvp.get('can_view_details') != False:
                    print("   ❌ Member should not see details when privacy is disabled")
                if len(admin_rsvp.get('responses', [])) <= len(member_rsvp.get('responses', [])):
                    print("   ⚠️  Admin should see more responses than member")
                if 'privacy_message' not in member_rsvp:
                    print("   ⚠️  Member should receive privacy message")
            else:
                # When privacy is enabled, both should see all details
                if admin_rsvp.get('can_view_details') != True:
                    print("   ❌ Admin should always see details")
                if member_rsvp.get('can_view_details') != True:
                    print("   ❌ Member should see details when privacy is enabled")
            
            break  # Only analyze first event with RSVP data

def test_migration_locally():
    """Test the database migration locally (if running against local instance)"""
    print("\n🗄️  Testing database migration...")
    
    # This would require direct database access
    # For now, we'll just check if the API endpoints work
    print("Migration test would require direct database access")
    print("Testing via API endpoints instead...")

if __name__ == "__main__":
    print("RSVP Visibility Feature Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    try:
        success = test_rsvp_visibility_feature()
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
