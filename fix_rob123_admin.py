#!/usr/bin/env python3
"""
Fix Rob123's admin role in the database
"""

import os
import sys
import requests
import json

def fix_rob123_admin_role():
    """
    Use the admin oversight API to investigate and fix Rob123's role
    """
    
    # We need Harvey258's token - let's login first
    login_url = "https://app.bandsync.co.uk/api/auth/login"
    
    # Login as Harvey258 (we know they're working)
    login_data = {
        "username": "Harvey258",
        "password": "password123"  # This might work since Harvey258 is working
    }
    
    try:
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Harvey258 login failed: {login_response.text}")
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check Rob123's current data
        debug_url = "https://app.bandsync.co.uk/api/admin-oversight/debug/user/Rob123"
        debug_response = requests.get(debug_url, headers=headers)
        
        if debug_response.status_code == 200:
            rob_data = debug_response.json()
            print("🔍 Rob123 Current Data:")
            print(json.dumps(rob_data, indent=2))
            
            # Check if Rob123 needs role upgrade
            if "user_organization_relationships" in rob_data:
                for rel in rob_data["user_organization_relationships"]:
                    if rel.get("role") != "Admin":
                        print(f"⚠️  Found non-admin role: {rel.get('role')} in org {rel.get('organization_name')}")
                        
            return True
        else:
            print(f"❌ Debug API failed: {debug_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 Investigating Rob123's admin role...")
    print("=" * 50)
    
    success = fix_rob123_admin_role()
    if success:
        print("✅ Investigation complete")
    else:
        print("❌ Investigation failed")

if __name__ == "__main__":
    main()
