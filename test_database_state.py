#!/usr/bin/env python3

import requests
import json

def test_database_state():
    """Test if the database is actually cleared by trying to register the same user twice"""
    
    base_url = 'https://app.bandsync.co.uk/api'
    
    print("🔍 Testing Database State...")
    
    # Try to register a test user
    test_user = {
        'username': 'TestUser123',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'organization': 'TestOrg'
    }
    
    print("1. Attempting first registration...")
    try:
        response1 = requests.post(f"{base_url}/auth/register", json=test_user)
        print(f"First registration status: {response1.status_code}")
        print(f"Response: {response1.text}")
        
        if response1.status_code == 200:
            print("✅ First registration successful - user created")
            
            # Try to register the same user again
            print("\n2. Attempting duplicate registration...")
            response2 = requests.post(f"{base_url}/auth/register", json=test_user)
            print(f"Duplicate registration status: {response2.status_code}")
            print(f"Response: {response2.text}")
            
            if response2.status_code == 400:
                print("✅ Duplicate registration correctly rejected - database has data")
                print("❌ Database was NOT cleared successfully")
                return False
            else:
                print("⚠️  Unexpected response to duplicate registration")
                
        elif response1.status_code == 400 and "already exists" in response1.text.lower():
            print("❌ User already exists - database was NOT cleared")
            return False
        else:
            print(f"⚠️  Unexpected registration response: {response1.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing database state: {e}")
        return False
    
    return True

def verify_empty_database():
    """Try to verify database is empty by checking if we can create the same org twice"""
    
    base_url = 'https://app.bandsync.co.uk/api'
    
    print("\n3. Testing organization uniqueness...")
    
    # Create two users with the same organization name
    users = [
        {
            'username': 'User1',
            'email': 'user1@example.com', 
            'password': 'Password123!',
            'organization': 'SameOrgName'
        },
        {
            'username': 'User2',
            'email': 'user2@example.com',
            'password': 'Password123!', 
            'organization': 'SameOrgName'
        }
    ]
    
    for i, user in enumerate(users, 1):
        try:
            response = requests.post(f"{base_url}/auth/register", json=user)
            print(f"User {i} registration: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error registering user {i}: {e}")

if __name__ == "__main__":
    print("🧪 Database State Verification Test")
    print("="*50)
    
    is_empty = test_database_state()
    verify_empty_database()
    
    if is_empty:
        print("\n✅ Database appears to be cleared successfully!")
    else:
        print("\n❌ Database still contains data - clearing was not successful")
        print("\nYou may need to:")
        print("1. Re-run the SQL commands in the Railway database")
        print("2. Check for any foreign key constraints preventing deletion")
        print("3. Manually verify table contents with SELECT COUNT(*) queries")
