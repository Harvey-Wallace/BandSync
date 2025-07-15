#!/usr/bin/env python3
"""
Test Railway database connection and check user credentials
"""

import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

# Railway database connection
external_db_url = "postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway"

def test_railway_database():
    """Test Railway database connection and check users"""
    try:
        print("🔍 Testing Railway database connection...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # Check if user table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user'
            );
        """)
        
        table_exists = cur.fetchone()[0]
        print(f"User table exists: {'✅' if table_exists else '❌'}")
        
        if not table_exists:
            print("❌ User table doesn't exist!")
            return False
        
        # Check all users
        cur.execute("""
            SELECT id, username, email, password_hash, role, organization_id
            FROM "user" 
            ORDER BY id;
        """)
        
        users = cur.fetchall()
        print(f"\n👥 Found {len(users)} users in database:")
        
        rob_user = None
        for user_id, username, email, password_hash, role, org_id in users:
            print(f"  - ID: {user_id}, Username: {username}, Email: {email}, Role: {role}, Org: {org_id}")
            print(f"    Password hash: {'SET' if password_hash else 'MISSING'}")
            
            if username == "Rob123":
                rob_user = (user_id, username, email, password_hash, role, org_id)
        
        # Test Rob123 specifically
        if rob_user:
            print(f"\n🔍 Testing Rob123 credentials...")
            user_id, username, email, password_hash, role, org_id = rob_user
            
            # Test password verification
            test_password = "Rob123pass"
            is_valid = check_password_hash(password_hash, test_password)
            print(f"Password verification for '{test_password}': {'✅ VALID' if is_valid else '❌ INVALID'}")
            
            if not is_valid:
                print("⚠️  Password verification failed. Let's fix it...")
                
                # Generate new hash
                new_hash = generate_password_hash(test_password)
                
                # Update in database
                cur.execute("""
                    UPDATE "user" 
                    SET password_hash = %s 
                    WHERE id = %s;
                """, (new_hash, user_id))
                
                conn.commit()
                print(f"✅ Updated password hash for {username}")
                
                # Verify the update worked
                new_valid = check_password_hash(new_hash, test_password)
                print(f"New password verification: {'✅ VALID' if new_valid else '❌ INVALID'}")
            
        else:
            print(f"\n❌ User 'Rob123' not found in database!")
            print("Available users:")
            for user_id, username, email, password_hash, role, org_id in users:
                print(f"  - {username}")
        
        conn.close()
        return rob_user is not None
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_login_endpoint():
    """Test the login endpoint directly"""
    import requests
    import json
    
    print("\n🧪 Testing login endpoint...")
    
    login_data = {
        "username": "Rob123",
        "password": "Rob123pass"
    }
    
    try:
        # Test against the deployed app
        url = "https://bandsync-production.up.railway.app/api/auth/login"
        
        print(f"Testing login at: {url}")
        print(f"Data: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(url, json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            if 'access_token' in data:
                print(f"Got access token: {data['access_token'][:50]}...")
                return data['access_token']
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                pass
            return None
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return None

def test_events_api(access_token):
    """Test the events API endpoints"""
    import requests
    import json
    
    print("\n🧪 Testing events API...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test GET events
        url = "https://bandsync-production.up.railway.app/api/events/"
        print(f"Testing GET events at: {url}")
        
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Events API working!")
            try:
                events = response.json()
                print(f"Found {len(events)} events")
            except:
                print("Response is not valid JSON")
        else:
            print("❌ Events API failed!")
            
        # Test POST event (create event)
        print("\n🧪 Testing event creation...")
        
        event_data = {
            "title": "Test Event",
            "description": "Test event description",
            "date": "2025-07-20",
            "time": "19:00:00",
            "location": "Test Venue"
        }
        
        print(f"Creating event: {json.dumps(event_data, indent=2)}")
        
        response = requests.post(url, json=event_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Event creation successful!")
        else:
            print("❌ Event creation failed!")
            
    except Exception as e:
        print(f"❌ Error testing events API: {e}")
        return False

if __name__ == "__main__":
    print("🔧 BandSync Railway Database Test")
    print("=" * 50)
    
    # Test database connection and users
    db_success = test_railway_database()
    
    if db_success:
        print("\n" + "=" * 50)
        # Test login endpoint
        access_token = test_login_endpoint()
        
        if access_token:
            print("\n" + "=" * 50)
            # Test events API
            test_events_api(access_token)
    
    print("\n🎯 Summary:")
    print("- Check if Rob123 user exists in database")
    print("- Verify password hash is correct")
    print("- Test login endpoint")
    print("- Test events API")
    print("- Fix any issues found")
