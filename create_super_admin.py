#!/usr/bin/env python3

import requests
import json

def create_super_admin():
    """Create a super admin user"""
    
    base_url = 'https://app.bandsync.co.uk/api'
    
    print("🔧 Creating Super Admin User...")
    print(f"Base URL: {base_url}")
    
    # Step 1: Register a new super admin user
    super_admin_data = {
        'username': 'SuperAdmin',
        'email': 'super@bandsync.co.uk',
        'password': 'SuperAdmin123!',
        'organization': 'BandSync Admin'
    }
    
    print("\n1. Registering super admin user...")
    try:
        response = requests.post(f"{base_url}/auth/register", json=super_admin_data)
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Super admin user registered successfully!")
            
            # Step 2: Login to get token
            login_data = {
                'username': 'SuperAdmin',
                'password': 'SuperAdmin123!'
            }
            
            print("\n2. Testing login...")
            login_response = requests.post(f"{base_url}/auth/login", json=login_data)
            print(f"Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Login successful!")
                print(f"   Role: {login_result.get('role')}")
                print(f"   Super Admin: {login_result.get('super_admin')}")
                print(f"   Organization: {login_result.get('organization')}")
                
                token = login_result.get('access_token')
                
                # Test super admin endpoints
                print("\n3. Testing super admin access...")
                headers = {'Authorization': f'Bearer {token}'}
                
                # Test system health
                try:
                    health_response = requests.get(f"{base_url}/super-admin/system/health", headers=headers)
                    print(f"System health endpoint: {health_response.status_code}")
                    if health_response.status_code != 200:
                        print(f"   Response: {health_response.text}")
                except Exception as e:
                    print(f"   Error: {e}")
                
                return True
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_super_admin()
