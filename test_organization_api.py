#!/usr/bin/env python3
"""
Test script to check organization API endpoint
"""

import requests
import json
import os

def test_organization_api():
    """Test the organization API endpoint"""
    
    # You'll need to replace these with your actual values
    api_url = "https://your-railway-app.railway.app/api/admin/organization"  # Replace with your Railway URL
    token = "your-jwt-token"  # Replace with a valid admin JWT token
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test GET request
        print("Testing GET /api/admin/organization...")
        response = requests.get(api_url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("Organization data retrieved successfully!")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    print("This is a template test script.")
    print("You need to update the api_url and token variables with your actual values.")
    print("Run this script manually after updating the variables.")
