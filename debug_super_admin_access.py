#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_super_admin_access():
    """Test super admin API endpoints to debug the issue"""
    
    # Get base URL
    base_url = 'https://app.bandsync.co.uk/api'
    
    print("🔍 Testing Super Admin Access...")
    print(f"Base URL: {base_url}")
    
    # Step 1: Try to login as super admin
    print("\n1. Testing super admin login...")
    
    login_data = {
        'username': 'Harvey258',
        'password': 'SuperAdminPassword123!'
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Role: {data.get('role')}")
            print(f"Super Admin: {data.get('super_admin')}")
            print(f"Organization: {data.get('organization')}")
            
            token = data.get('access_token')
            if not token:
                print("❌ No access token received!")
                return
                
            # Step 2: Test super admin endpoints
            print("\n2. Testing super admin endpoints...")
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test system health
            print("Testing /super-admin/system/health...")
            health_response = requests.get(f"{base_url}/super-admin/system/health", headers=headers)
            print(f"Health endpoint status: {health_response.status_code}")
            if health_response.status_code == 200:
                print("✅ System health endpoint accessible")
            else:
                print(f"❌ System health failed: {health_response.text}")
            
            # Test overview
            print("Testing /super-admin/overview...")
            overview_response = requests.get(f"{base_url}/super-admin/overview", headers=headers)
            print(f"Overview endpoint status: {overview_response.status_code}")
            if overview_response.status_code == 200:
                print("✅ Overview endpoint accessible")
            else:
                print(f"❌ Overview failed: {overview_response.text}")
                
            # Test analytics
            print("Testing /super-admin/analytics/overview...")
            analytics_response = requests.get(f"{base_url}/super-admin/analytics/overview", headers=headers)
            print(f"Analytics endpoint status: {analytics_response.status_code}")
            if analytics_response.status_code == 200:
                print("✅ Analytics endpoint accessible")
            else:
                print(f"❌ Analytics failed: {analytics_response.text}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_super_admin_access()
