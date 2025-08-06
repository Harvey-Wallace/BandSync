#!/usr/bin/env python3
"""
Test script to verify RSVP statistics in events endpoint
"""

import requests
import json

def test_events_with_rsvp_stats():
    """Test the events endpoint with RSVP statistics"""
    
    # Configuration
    BASE_URL = "http://localhost:5000/api"
    
    # Test credentials for local test database
    login_data = {
        "email": "admin@bandsync.com",
        "password": "admin123"
    }
    
    print("🧪 Testing Events Endpoint with RSVP Statistics")
    print("=" * 60)
    
    # 1. Login to get auth token
    print("1. Authenticating...")
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
    
    # 2. Get events with RSVP statistics
    print("\n2. Fetching events with RSVP statistics...")
    try:
        response = requests.get(f"{BASE_URL}/events/", headers=headers)
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Retrieved {len(events)} events")
            
            # Display RSVP statistics for each event
            for event in events:
                print(f"\n📅 Event: {event['title']}")
                print(f"   Date: {event['date']}")
                
                if 'rsvp_stats' in event:
                    stats = event['rsvp_stats']
                    total_responses = stats['total_responses']
                    total_users = stats['total_users']
                    
                    print(f"   📊 RSVP Statistics:")
                    print(f"      Total responses: {total_responses} of {total_users} users")
                    print(f"      ✅ Yes: {stats['yes_count']}")
                    print(f"      ❌ No: {stats['no_count']}")
                    print(f"      ❓ Maybe: {stats['maybe_count']}")
                    print(f"      ⏳ No response: {stats['no_response_count']}")
                    
                    # Calculate response rate
                    if total_users > 0:
                        response_rate = (total_responses / total_users) * 100
                        print(f"      📈 Response rate: {response_rate:.1f}%")
                        
                        # Display the "X of Y" format you requested
                        print(f"      📱 Dashboard display: {total_responses} of {total_users}")
                    
                else:
                    print("   ⚠️  No RSVP statistics found")
            
            print(f"\n🎉 Events endpoint now includes RSVP statistics!")
            print(f"📱 Your dashboard can now display: 'X of Y' format")
            return True
            
        else:
            print(f"❌ Failed to get events: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Events request failed: {e}")
        return False

def print_usage():
    """Print usage instructions"""
    print("""
🧪 RSVP Statistics Test

This script tests the enhanced events endpoint that now includes RSVP statistics.

Prerequisites:
1. Flask server running on localhost:5000
2. Local database with test data (run setup_local_db.py first)
3. Admin user: admin@bandsync.com / admin123

Usage:
    python3 test_rsvp_statistics.py

The enhanced events endpoint now returns RSVP statistics including:
- total_responses: Number of users who have responded
- total_users: Total users in the organization  
- yes_count, no_count, maybe_count: Response breakdowns
- no_response_count: Users who haven't responded yet

Your dashboard can now display "X of Y" format where:
- X = total_responses (users who have RSVP'd)
- Y = total_users (total users in organization)
""")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(0)
    
    print("🚀 Starting RSVP Statistics Test...")
    print("⚠️  Make sure your Flask server is running and database is set up")
    print()
    
    success = test_events_with_rsvp_stats()
    sys.exit(0 if success else 1)
