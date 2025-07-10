#!/usr/bin/env python3
"""
Quick test to verify Phase 2 endpoints are working
"""

import requests
import json

def test_endpoints():
    base_url = "http://localhost:5001"
    
    # Test login first
    print("🔐 Testing login...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('multiple_organizations'):
                login_data['organization_id'] = 1
                response = requests.post(f"{base_url}/api/auth/login", json=login_data)
                data = response.json()
            
            token = data.get('access_token')
            print(f"✅ Login successful! Token: {token[:20]}...")
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test Phase 2 endpoints
            endpoints = [
                ('/api/messages/', 'Messages'),
                ('/api/substitutes/requests', 'Substitutes'),
                ('/api/quick-polls/', 'Quick Polls'),
                ('/api/bulk-ops/stats', 'Bulk Operations'),
                ('/api/email-management/aliases', 'Email Management')
            ]
            
            print("\n🧪 Testing Phase 2 endpoints...")
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", headers=headers)
                    status = "✅" if response.status_code == 200 else "❌"
                    print(f"{status} {name}: {response.status_code}")
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the backend is running on http://localhost:5001")

if __name__ == "__main__":
    test_endpoints()
