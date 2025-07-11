#!/usr/bin/env python3
"""Test registration endpoint locally"""
import requests
import json

# Test data
test_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "organization": "Test Band"
}

def test_registration():
    try:
        # Test against the deployed app
        url = "https://bandsync-production.up.railway.app/api/auth/register"
        
        print(f"Testing registration at: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            
    except Exception as e:
        print(f"Error testing registration: {e}")

if __name__ == "__main__":
    test_registration()
