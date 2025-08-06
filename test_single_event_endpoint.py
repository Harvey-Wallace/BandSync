#!/usr/bin/env python3
"""
Test script for single event endpoint with timing and RSVP statistics
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"  # Update if your server runs on different host/port
EVENT_ID = 1  # Update with a valid event ID from your database

def test_single_event_endpoint():
    """Test the enhanced single event endpoint"""
    
    print("🧪 Testing Single Event Endpoint Enhancement")
    print("=" * 50)
    
    # You'll need to add your JWT token here
    # You can get this from your browser's developer tools after logging in
    jwt_token = "YOUR_JWT_TOKEN_HERE"
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test single event endpoint
        response = requests.get(f"{BASE_URL}/events/{EVENT_ID}", headers=headers)
        
        if response.status_code == 200:
            event_data = response.json()
            
            print("✅ Single Event Endpoint Response:")
            print("-" * 30)
            
            # Check timing fields
            print("⏰ Timing Information:")
            print(f"   Arrive by Time: {event_data.get('arrive_by_time', 'Not set')}")
            print(f"   Start Time: {event_data.get('start_time', 'Not set')}")
            print(f"   End Time: {event_data.get('end_time', 'Not set')}")
            print()
            
            # Check RSVP statistics
            rsvp_stats = event_data.get('rsvp_stats', {})
            if rsvp_stats:
                print("📊 RSVP Statistics:")
                print(f"   Total Responses: {rsvp_stats.get('total_responses', 0)}")
                print(f"   Total Users: {rsvp_stats.get('total_users', 0)}")
                print(f"   Yes Count: {rsvp_stats.get('yes_count', 0)}")
                print(f"   No Count: {rsvp_stats.get('no_count', 0)}")
                print(f"   Maybe Count: {rsvp_stats.get('maybe_count', 0)}")
                print(f"   No Response Count: {rsvp_stats.get('no_response_count', 0)}")
                print()
                
                # Show the "X of Y" format
                total_responses = rsvp_stats.get('total_responses', 0)
                total_users = rsvp_stats.get('total_users', 0)
                print(f"🎯 Dashboard Display Format: {total_responses} of {total_users}")
                print(f"   (Instead of just showing individual counts)")
            else:
                print("❌ No RSVP statistics found in response")
            
            print("\n" + "=" * 50)
            print("📋 Full Response Structure:")
            print(json.dumps(event_data, indent=2))
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def frontend_integration_guide():
    """Show how to integrate the enhanced data in frontend"""
    
    print("\n" + "🎨 Frontend Integration Guide")
    print("=" * 50)
    
    print("""
1. TIMING FIELDS:
   The event now includes these timing fields:
   - arrive_by_time: "14:30" (or null)
   - start_time: "15:00" (or null) 
   - end_time: "17:00" (or null)

   Example frontend code:
   ```javascript
   if (event.arrive_by_time) {
       displayTime("Arrive by", event.arrive_by_time);
   }
   if (event.start_time) {
       displayTime("Start", event.start_time);
   }
   if (event.end_time) {
       displayTime("End", event.end_time);
   }
   ```

2. RSVP STATISTICS:
   The event now includes rsvp_stats object:
   - total_responses: Number of users who have RSVP'd
   - total_users: Total users in the organization
   - yes_count, no_count, maybe_count: Individual response counts

   Example frontend code for "X of Y" display:
   ```javascript
   const stats = event.rsvp_stats;
   const displayText = `${stats.total_responses} of ${stats.total_users}`;
   // Shows "1 of 3" instead of just "1 going"
   ```

3. REACT COMPONENT EXAMPLE:
   ```jsx
   function EventCard({ event }) {
       const { rsvp_stats } = event;
       
       return (
           <div className="event-card">
               {/* Timing section */}
               <div className="timing-info">
                   {event.arrive_by_time && (
                       <div>Arrive by: {event.arrive_by_time}</div>
                   )}
                   {event.start_time && (
                       <div>Start: {event.start_time}</div>
                   )}
                   {event.end_time && (
                       <div>End: {event.end_time}</div>
                   )}
               </div>
               
               {/* RSVP section */}
               <div className="rsvp-info">
                   <div className="total-responses">
                       {rsvp_stats.total_responses} of {rsvp_stats.total_users}
                   </div>
                   <div className="response-breakdown">
                       <span className="yes">{rsvp_stats.yes_count} going</span>
                       <span className="maybe">{rsvp_stats.maybe_count} maybe</span>
                       <span className="no">{rsvp_stats.no_count} not going</span>
                   </div>
               </div>
           </div>
       );
   }
   ```
""")

if __name__ == "__main__":
    test_single_event_endpoint()
    frontend_integration_guide()
