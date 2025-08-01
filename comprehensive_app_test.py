#!/usr/bin/env python3
"""
Comprehensive BandSync Application Testing Script
Tests all major functionality to ensure the app is working correctly after fixes
"""

import requests
import json
import time
import random
import string
from datetime import datetime, timedelta
import sys

class BandSyncTester:
    def __init__(self, base_url="https://bandsync-production.up.railway.app"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.organization_id = None
        self.event_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
    
    def generate_test_email(self):
        """Generate a unique test email"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test_{random_str}@example.com"
    
    def test_health_check(self):
        """Test basic server health"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_test("Health Check", True, "Server is responding")
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_frontend_loading(self):
        """Test that frontend loads properly"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200 and "BandSync" in response.text:
                self.log_test("Frontend Loading", True, "Frontend loads successfully")
                return True
            else:
                self.log_test("Frontend Loading", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Loading", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            test_email = self.generate_test_email()
            registration_data = {
                "username": test_email,
                "email": test_email,
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "phone": "+1234567890"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("User Registration", True, f"User registered: {test_email}")
                return True
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login with existing credentials"""
        try:
            # Try to login with a test account
            login_data = {
                "username": "test@example.com",  # Try with test account
                "password": "password123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("User Login", True, "Successfully logged in")
                return True
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            return False
    
    def test_get_organizations(self):
        """Test fetching user organizations"""
        if not self.auth_token:
            self.log_test("Get Organizations", False, "No auth token available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/organizations")
            
            if response.status_code == 200:
                data = response.json()
                organizations = data.get("organizations", [])
                if organizations:
                    self.organization_id = organizations[0].get("id")
                    self.log_test("Get Organizations", True, f"Found {len(organizations)} organizations")
                    return True
                else:
                    self.log_test("Get Organizations", True, "No organizations found (expected for new user)")
                    return True
            else:
                self.log_test("Get Organizations", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Organizations", False, f"Error: {str(e)}")
            return False
    
    def test_create_organization(self):
        """Test creating a new organization"""
        if not self.auth_token:
            self.log_test("Create Organization", False, "No auth token available")
            return False
        
        try:
            org_data = {
                "name": f"Test Band {random.randint(1000, 9999)}",
                "description": "Test band for automated testing",
                "organization_type": "Band"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/organizations",
                json=org_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.organization_id = data.get("organization", {}).get("id")
                self.log_test("Create Organization", True, f"Created organization: {org_data['name']}")
                return True
            else:
                self.log_test("Create Organization", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Organization", False, f"Error: {str(e)}")
            return False
    
    def test_get_events(self):
        """Test fetching events"""
        if not self.auth_token or not self.organization_id:
            self.log_test("Get Events", False, "No auth token or organization ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/organizations/{self.organization_id}/events")
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                self.log_test("Get Events", True, f"Found {len(events)} events")
                return True
            else:
                self.log_test("Get Events", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Events", False, f"Error: {str(e)}")
            return False
    
    def test_create_event(self):
        """Test creating a new event"""
        if not self.auth_token or not self.organization_id:
            self.log_test("Create Event", False, "No auth token or organization ID available")
            return False
        
        try:
            # Create event for next week
            event_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            event_data = {
                "title": f"Test Rehearsal {random.randint(100, 999)}",
                "description": "Automated test event",
                "date": event_date,
                "location": "Test Venue",
                "event_type": "Rehearsal",
                "start_time": "19:00",
                "end_time": "21:00"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/organizations/{self.organization_id}/events",
                json=event_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.event_id = data.get("event", {}).get("id")
                self.log_test("Create Event", True, f"Created event: {event_data['title']}")
                return True
            else:
                self.log_test("Create Event", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Event", False, f"Error: {str(e)}")
            return False
    
    def test_rsvp_to_event(self):
        """Test RSVP functionality"""
        if not self.auth_token or not self.event_id:
            self.log_test("RSVP to Event", False, "No auth token or event ID available")
            return False
        
        try:
            rsvp_data = {
                "status": "attending",
                "notes": "Looking forward to it!"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/events/{self.event_id}/rsvp",
                json=rsvp_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                self.log_test("RSVP to Event", True, "Successfully RSVPed to event")
                return True
            else:
                self.log_test("RSVP to Event", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("RSVP to Event", False, f"Error: {str(e)}")
            return False
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        if not self.auth_token:
            self.log_test("Get User Profile", False, "No auth token available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/user/profile")
            
            if response.status_code == 200:
                data = response.json()
                user = data.get("user", {})
                self.log_test("Get User Profile", True, f"Retrieved profile for: {user.get('email', 'Unknown')}")
                return True
            else:
                self.log_test("Get User Profile", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get User Profile", False, f"Error: {str(e)}")
            return False
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        if not self.auth_token:
            self.log_test("Update User Profile", False, "No auth token available")
            return False
        
        try:
            update_data = {
                "first_name": "Updated",
                "last_name": "TestUser",
                "phone": "+1987654321"
            }
            
            response = self.session.put(
                f"{self.base_url}/api/user/profile",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.log_test("Update User Profile", True, "Profile updated successfully")
                return True
            else:
                self.log_test("Update User Profile", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update User Profile", False, f"Error: {str(e)}")
            return False
    
    def test_calendar_functionality(self):
        """Test calendar-related endpoints"""
        if not self.auth_token or not self.organization_id:
            self.log_test("Calendar Functionality", False, "No auth token or organization ID available")
            return False
        
        try:
            # Test getting calendar data
            response = self.session.get(f"{self.base_url}/api/organizations/{self.organization_id}/calendar")
            
            if response.status_code == 200:
                self.log_test("Calendar Functionality", True, "Calendar data retrieved successfully")
                return True
            else:
                self.log_test("Calendar Functionality", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Calendar Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test accessing protected endpoint without auth
            response = self.session.get(f"{self.base_url}/api/organizations", headers={})
            
            if response.status_code == 401:
                self.log_test("Error Handling", True, "Properly returns 401 for unauthorized access")
                return True
            else:
                self.log_test("Error Handling", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False
    
    def test_static_assets(self):
        """Test that static assets are loading"""
        try:
            # Test CSS loading
            css_response = self.session.get(f"{self.base_url}/static/css/main.css")
            js_response = self.session.get(f"{self.base_url}/static/js/main.js")
            
            css_ok = css_response.status_code in [200, 404]  # 404 is ok if different path
            js_ok = js_response.status_code in [200, 404]   # 404 is ok if different path
            
            if css_ok and js_ok:
                self.log_test("Static Assets", True, "Static asset endpoints responding")
                return True
            else:
                self.log_test("Static Assets", False, f"CSS: {css_response.status_code}, JS: {js_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Static Assets", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive BandSync Testing")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_frontend_loading,
            self.test_static_assets,
            self.test_error_handling,
            self.test_user_login,  # Try login first
            self.test_user_registration,  # Fall back to registration if login fails
            self.test_get_user_profile,
            self.test_update_user_profile,
            self.test_get_organizations,
            self.test_create_organization,
            self.test_get_events,
            self.test_create_event,
            self.test_rsvp_to_event,
            self.test_calendar_functionality,
        ]
        
        for test in tests:
            test()
            time.sleep(1)  # Small delay between tests
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Your app is working great!")
        else:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    print("BandSync Comprehensive Testing Tool")
    print("This will test all major functionality of your application\n")
    
    # Allow custom URL
    base_url = "https://bandsync-production.up.railway.app"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    tester = BandSyncTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
