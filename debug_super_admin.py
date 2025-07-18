#!/usr/bin/env python3
"""
Debug script to test Super Admin functionality and general login
"""

import requests
import json

# API Configuration
API_URL = "https://bandsync-production.up.railway.app/api"

def test_super_admin_login():
    """Test Super Admin login functionality"""
    
    print("🔍 Testing Super Admin login and functionality...")
    print("=" * 60)
    
    # Test Harvey258 credentials (should be Super Admin)
    harvey_credentials = [
        {"username": "Harvey258", "password": "password"},
        {"username": "Harvey258", "password": "admin123"},
        {"username": "Harvey258", "password": "Harvey258"},
        {"username": "Harvey258", "password": "temp_Harvey258123"},  # Temp password
    ]
    
    for creds in harvey_credentials:
        print(f"\n🔐 Trying Harvey258 credentials with password: {creds['password'][:4]}...")
        
        try:
            # Try to login
            login_response = requests.post(f"{API_URL}/auth/login", json=creds)
            
            print(f"Login response status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"✅ Login successful for Harvey258!")
                print(f"Response: {json.dumps(login_data, indent=2)}")
                
                # Check if Super Admin
                if login_data.get('super_admin'):
                    print("🔥 Harvey258 is Super Admin!")
                    
                    # Test Super Admin endpoints
                    token = login_data['access_token']
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Test overview endpoint
                    overview_response = requests.get(f"{API_URL}/super-admin/overview", headers=headers)
                    print(f"Super Admin overview status: {overview_response.status_code}")
                    
                    if overview_response.status_code == 200:
                        overview_data = overview_response.json()
                        print(f"Super Admin overview: {json.dumps(overview_data, indent=2)}")
                    else:
                        print(f"Super Admin overview failed: {overview_response.text}")
                
                break  # Stop trying other passwords
                
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {login_response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print("🔍 Testing other known credentials...")
    
    # Test other possible credentials
    other_credentials = [
        {"username": "CBBB25", "password": "admin123"},
        {"username": "admin", "password": "admin123"},
        {"username": "CBBB25", "password": "password"},
    ]
    
    for creds in other_credentials:
        print(f"\n🔐 Trying {creds['username']}...")
        
        try:
            login_response = requests.post(f"{API_URL}/auth/login", json=creds)
            print(f"Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"✅ Login successful for {creds['username']}!")
                print(f"Super Admin: {login_data.get('super_admin', False)}")
                break
            else:
                try:
                    error_data = login_response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {login_response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

def test_basic_endpoints():
    """Test basic endpoints to check if server is running"""
    
    print(f"\n" + "=" * 60)
    print("🔍 Testing basic server endpoints...")
    
    try:
        # Test root endpoint
        root_response = requests.get(f"{API_URL.replace('/api', '')}")
        print(f"Root endpoint status: {root_response.status_code}")
        
        # Test a simple endpoint
        health_response = requests.get(f"{API_URL}/organizations/current")
        print(f"Organizations endpoint status: {health_response.status_code}")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

if __name__ == "__main__":
    test_super_admin_login()
    test_basic_endpoints()
