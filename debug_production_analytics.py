#!/usr/bin/env python3
"""
Debug script to test analytics data on production
"""

import requests
import json
import sys

# Production URL
BASE_URL = "https://app.bandsync.co.uk"

def test_analytics_with_auth():
    """Test analytics with proper authentication"""
    
    print("🔍 Testing BandSync Analytics on Production")
    print("=" * 50)
    
    # You'll need to get a real JWT token from the production site
    # This is just a template - you'll need to login and get the token
    
    print("To test analytics on production:")
    print("1. Go to https://app.bandsync.co.uk")
    print("2. Login as an admin user")
    print("3. Open browser developer tools (F12)")
    print("4. Go to Application/Storage tab")
    print("5. Find 'token' in localStorage")
    print("6. Copy the JWT token value")
    print("7. Replace 'YOUR_JWT_TOKEN_HERE' below with the actual token")
    print()
    
    # Example of how to test with real token
    token = "YOUR_JWT_TOKEN_HERE"  # Replace with actual token
    
    if token == "YOUR_JWT_TOKEN_HERE":
        print("❌ Please set a real JWT token to test analytics")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test organization overview
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard?days=30", headers=headers)
        print(f"Dashboard API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Dashboard Data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing analytics: {e}")

def check_general_endpoints():
    """Test general endpoints that don't require auth"""
    
    print("\n🔍 Testing General Endpoints")
    print("-" * 30)
    
    try:
        # Test if site is accessible
        response = requests.get(BASE_URL, timeout=10)
        print(f"✅ Site accessible: {response.status_code}")
        
        # Test if API is accessible
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"Health check: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    check_general_endpoints()
    test_analytics_with_auth()
    
    print("\n" + "=" * 50)
    print("💡 Debug Steps:")
    print("1. Check if you can login to the admin dashboard")
    print("2. Verify the Analytics tab appears in the admin navigation")
    print("3. Check browser console for any JavaScript errors")
    print("4. Verify the backend logs for any database errors")
    print("5. Confirm the organization_id is properly set for your user")
