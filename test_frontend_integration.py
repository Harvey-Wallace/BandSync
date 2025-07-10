#!/usr/bin/env python3
"""
BandSync Phase 2 Frontend Integration Test
Tests all new frontend features and integrations
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

class BandSyncFrontendTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.org_id = None
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {message}")
        
    def setup_test_environment(self):
        """Setup test environment and authentication"""
        print("🔧 Setting up test environment...")
        
        # Test admin login
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                
                # Check if multiple organizations
                if data.get('multiple_organizations'):
                    # Login with specific organization
                    login_data['organization_id'] = data['organizations'][0]['id']
                    
                    response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
                    if response.status_code == 200:
                        auth_data = response.json()
                        self.token = auth_data['access_token']
                        self.user_id = "1"  # Admin user ID
                        self.org_id = auth_data['organization_id']
                        self.log_test("Authentication Setup", "PASS", "Admin login successful")
                        return True
                    else:
                        self.log_test("Authentication Setup", "FAIL", f"Org login failed: {response.status_code}")
                        return False
                else:
                    # Single organization login
                    self.token = data['access_token']
                    self.user_id = "1"  # Admin user ID
                    self.org_id = data['organization_id']
                    self.log_test("Authentication Setup", "PASS", "Admin login successful")
                    return True
            else:
                self.log_test("Authentication Setup", "FAIL", f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication Setup", "FAIL", f"Login error: {str(e)}")
            return False
    
    def test_group_email_api(self):
        """Test Group Email API endpoints"""
        print("\n📧 Testing Group Email API...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test get email aliases
        try:
            response = requests.get(f"{self.base_url}/api/email-management/aliases", headers=headers)
            if response.status_code == 200:
                self.log_test("Group Email - Get Aliases", "PASS", "Retrieved email aliases")
            else:
                self.log_test("Group Email - Get Aliases", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Group Email - Get Aliases", "FAIL", f"Error: {str(e)}")
        
        # Test create email alias
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        alias_data = {
            'alias_name': f'test-{unique_id}',
            'alias_type': 'organization'
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/email-management/aliases", 
                                   json=alias_data, headers=headers)
            if response.status_code == 201:
                self.log_test("Group Email - Create Alias", "PASS", "Created test email alias")
            else:
                self.log_test("Group Email - Create Alias", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Group Email - Create Alias", "FAIL", f"Error: {str(e)}")
    
    def test_messaging_api(self):
        """Test Internal Messaging API endpoints"""
        print("\n💬 Testing Internal Messaging API...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test get messages
        try:
            response = requests.get(f"{self.base_url}/api/messages/", headers=headers)
            if response.status_code == 200:
                self.log_test("Messaging - Get Messages", "PASS", "Retrieved messages")
            else:
                self.log_test("Messaging - Get Messages", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Messaging - Get Messages", "FAIL", f"Error: {str(e)}")
        
        # Test send message
        message_data = {
            'subject': 'Frontend Test Message',
            'content': 'This is a test message from the frontend integration test.',
            'recipient_type': 'organization'
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/messages/send", 
                                   json=message_data, headers=headers)
            if response.status_code == 201:
                self.log_test("Messaging - Send Message", "PASS", "Sent test message")
            else:
                self.log_test("Messaging - Send Message", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Messaging - Send Message", "FAIL", f"Error: {str(e)}")
    
    def test_substitution_api(self):
        """Test Substitution Management API endpoints"""
        print("\n👥 Testing Substitution Management API...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test get substitute requests
        try:
            response = requests.get(f"{self.base_url}/api/substitutes/requests", headers=headers)
            if response.status_code == 200:
                self.log_test("Substitution - Get Requests", "PASS", "Retrieved substitute requests")
            else:
                self.log_test("Substitution - Get Requests", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Substitution - Get Requests", "FAIL", f"Error: {str(e)}")
        
        # Create a test event first
        event_data = {
            'name': 'Frontend Test Event',
            'description': 'Test event for substitute testing',
            'date': (datetime.now() + timedelta(days=7)).isoformat(),
            'location': 'Test Location'
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/events/", 
                                   json=event_data, headers=headers)
            if response.status_code in [200, 201]:  # Accept both 200 and 201
                event_id = response.json()['id']
                self.log_test("Substitution - Create Test Event", "PASS", "Created test event for substitution")
                
                # Create RSVP first (required for substitute request)
                rsvp_data = {'status': 'yes'}
                rsvp_response = requests.post(f"{self.base_url}/api/events/{event_id}/rsvp", 
                                           json=rsvp_data, headers=headers)
                
                # Test create substitute request
                sub_data = {
                    'event_id': event_id,
                    'reason': 'Frontend testing substitute request'
                }
                
                response = requests.post(f"{self.base_url}/api/substitutes/request", 
                                       json=sub_data, headers=headers)
                if response.status_code == 201:
                    self.log_test("Substitution - Create Request", "PASS", "Created substitute request")
                else:
                    self.log_test("Substitution - Create Request", "FAIL", f"Status: {response.status_code}")
            else:
                self.log_test("Substitution - Create Test Event", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Substitution - Create Request", "FAIL", f"Error: {str(e)}")
    
    def test_bulk_operations_api(self):
        """Test Bulk Operations API endpoints"""
        print("\n📦 Testing Bulk Operations API...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test get import templates
        try:
            response = requests.get(f"{self.base_url}/api/bulk-ops/import-template", headers=headers)
            if response.status_code == 200:
                self.log_test("Bulk Ops - Get Import Template", "PASS", "Retrieved import template")
            else:
                self.log_test("Bulk Ops - Get Import Template", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Bulk Ops - Get Import Template", "FAIL", f"Error: {str(e)}")
        
        # Test export data
        try:
            response = requests.get(f"{self.base_url}/api/bulk-ops/export", headers=headers)
            if response.status_code == 200:
                self.log_test("Bulk Ops - Export Data", "PASS", "Exported organization data")
            else:
                self.log_test("Bulk Ops - Export Data", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Bulk Ops - Export Data", "FAIL", f"Error: {str(e)}")
    
    def test_quick_polls_api(self):
        """Test Quick Polls API endpoints"""
        print("\n📊 Testing Quick Polls API...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test get polls
        try:
            response = requests.get(f"{self.base_url}/api/quick-polls/", headers=headers)
            if response.status_code == 200:
                self.log_test("Quick Polls - Get Polls", "PASS", "Retrieved polls")
            else:
                self.log_test("Quick Polls - Get Polls", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Quick Polls - Get Polls", "FAIL", f"Error: {str(e)}")
        
        # Test create poll
        poll_data = {
            'question': 'Frontend Test Poll - Do you like the new features?',
            'options': ['Yes', 'No', 'Maybe'],
            'anonymous': True,
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/quick-polls/", 
                                   json=poll_data, headers=headers)
            if response.status_code == 201:
                self.log_test("Quick Polls - Create Poll", "PASS", "Created test poll")
            else:
                self.log_test("Quick Polls - Create Poll", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Quick Polls - Create Poll", "FAIL", f"Error: {str(e)}")
    
    def test_enhanced_events_api(self):
        """Test Enhanced Events API with substitute integration"""
        print("\n🎭 Testing Enhanced Events API...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test get events (should work with existing API)
        try:
            response = requests.get(f"{self.base_url}/api/events/", headers=headers)
            if response.status_code == 200:
                events = response.json()
                if events:
                    event_id = events[0]['id']
                    
                    # Test RSVP functionality
                    rsvp_data = {'status': 'No'}
                    response = requests.post(f"{self.base_url}/api/events/{event_id}/rsvp", 
                                           json=rsvp_data, headers=headers)
                    if response.status_code == 200:
                        self.log_test("Enhanced Events - RSVP", "PASS", "RSVP functionality working")
                    else:
                        self.log_test("Enhanced Events - RSVP", "FAIL", f"Status: {response.status_code}")
                else:
                    self.log_test("Enhanced Events - Get Events", "PASS", "No events found (expected)")
            else:
                self.log_test("Enhanced Events - Get Events", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Events - Get Events", "FAIL", f"Error: {str(e)}")
    
    def test_frontend_routes(self):
        """Test frontend route accessibility"""
        print("\n🌐 Testing Frontend Routes...")
        
        # Test if frontend server is running
        try:
            response = requests.get("http://localhost:3000")
            if response.status_code == 200:
                self.log_test("Frontend Server", "PASS", "Frontend server is running")
            else:
                self.log_test("Frontend Server", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Server", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all frontend integration tests"""
        print("🚀 Starting BandSync Phase 2 Frontend Integration Tests")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test environment setup failed. Exiting.")
            return False
        
        # Run all tests
        self.test_group_email_api()
        self.test_messaging_api()
        self.test_substitution_api()
        self.test_bulk_operations_api()
        self.test_quick_polls_api()
        self.test_enhanced_events_api()
        self.test_frontend_routes()
        
        # Generate report
        self.generate_report()
        
        return True
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'results': self.test_results
        }
        
        with open('frontend_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: frontend_test_report.json")
        
        if failed_tests == 0:
            print("\n🎉 All tests passed! Frontend integration is ready.")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Please review before deployment.")

if __name__ == "__main__":
    tester = BandSyncFrontendTester()
    tester.run_all_tests()
