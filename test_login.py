#!/usr/bin/env python3
"""Test login endpoint"""
import requests
import json

# Test login data
login_data = {
    "username": "testuser2",
    "password": "testpassword123"
}

def test_login():
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
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"Error testing login: {e}")

if __name__ == "__main__":
    test_login()
