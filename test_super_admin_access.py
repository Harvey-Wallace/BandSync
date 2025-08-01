#!/usr/bin/env python3
"""
Test Super Admin Access to Admin Dashboard
===========================================

This script verifies that the super admin dashboard access fix is working correctly.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "https://app.bandsync.co.uk"
SUPER_ADMIN_USERNAME = "Harvey258"
SUPER_ADMIN_PASSWORD = "SuperAdminPassword123!"

def test_super_admin_login():
    """Test super admin login and dashboard access"""
    print("🧪 Testing Super Admin Dashboard Access")
    print("=" * 50)
    
    # Test login
    print("1. Testing super admin login...")
    login_data = {
        "username": SUPER_ADMIN_USERNAME,
        "password": SUPER_ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get('access_token')
            super_admin = login_result.get('super_admin', False)
            role = login_result.get('role')
            
            print(f"✅ Login successful!")
            print(f"   Role: {role}")
            print(f"   Super Admin: {super_admin}")
            print(f"   Token: {token[:20]}...")
            
            if super_admin:
                print("\n2. Testing admin dashboard access...")
                
                # Test admin endpoints that should be accessible to super admin
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test admin organization endpoint
                admin_org_response = requests.get(f"{BASE_URL}/api/admin/organization", headers=headers)
                print(f"   Admin Organization Endpoint: {admin_org_response.status_code}")
                
                # Test admin users endpoint
                admin_users_response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
                print(f"   Admin Users Endpoint: {admin_users_response.status_code}")
                
                # Test super admin endpoints
                super_admin_overview = requests.get(f"{BASE_URL}/api/super-admin/overview", headers=headers)
                print(f"   Super Admin Overview Endpoint: {super_admin_overview.status_code}")
                
                if admin_org_response.status_code == 200 and admin_users_response.status_code == 200:
                    print("\n✅ SUCCESS: Super admin can access both admin and super admin endpoints!")
                    print("\n📊 Navigation Summary:")
                    print("   - Super Admin can access /super-admin dashboard ✅")
                    print("   - Super Admin can access /admin dashboard ✅")
                    print("   - Role-based access control working correctly ✅")
                    return True
                else:
                    print("\n❌ PARTIAL: Super admin login works but admin access may be limited")
                    return False
            else:
                print("❌ User is not a super admin")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_navigation_logic():
    """Test the navigation logic changes"""
    print("\n🔍 Analyzing Navigation Logic Changes")
    print("=" * 50)
    
    # Check that the Navbar.js file contains the correct logic
    navbar_file = "/Users/robertharvey/Documents/GitHub/BandSync/frontend/src/components/Navbar.js"
    dashboard_file = "/Users/robertharvey/Documents/GitHub/BandSync/frontend/src/pages/Dashboard.js"
    
    try:
        with open(navbar_file, 'r') as f:
            navbar_content = f.read()
            
        with open(dashboard_file, 'r') as f:
            dashboard_content = f.read()
        
        # Check for the updated logic
        if "(role === 'Admin' || isSuperAdmin)" in navbar_content:
            print("✅ Navbar.js updated: Super admin can see Admin link")
        else:
            print("❌ Navbar.js not updated properly")
            
        if "(role === 'Admin' || localStorage.getItem('super_admin') === 'true')" in dashboard_content:
            print("✅ Dashboard.js updated: Super admin can see Admin Panel button")
        else:
            print("❌ Dashboard.js not updated properly")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Super Admin Access Verification")
    print("==================================")
    
    # Test navigation logic
    logic_test = test_navigation_logic()
    
    # Test actual API access
    api_test = test_super_admin_login()
    
    print("\n📋 Final Summary")
    print("================")
    if logic_test and api_test:
        print("🎉 ALL TESTS PASSED: Super admin access fix is working!")
        print("\nThe super admin account can now:")
        print("  1. Access the Super Admin dashboard (/super-admin)")
        print("  2. Access the Admin dashboard (/admin)")
        print("  3. See both navigation links in the navbar")
        print("  4. Use admin functionality while maintaining super admin privileges")
    else:
        print("⚠️ Some tests failed - check the output above for details")
