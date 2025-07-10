#!/usr/bin/env python3
"""
BandSync Phase 2 Frontend Testing Script
Automated testing of frontend components and user flows
"""

import requests
import time
import json
from datetime import datetime

class FrontendTester:
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:5001"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.token = None
        self.results = []
        
    def log_test(self, test_name, status, message="", details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
    def setup_authentication(self):
        """Get authentication token for API testing"""
        print("🔧 Setting up authentication...")
        
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        try:
            response = requests.post(f"{self.backend_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                
                # Handle multi-organization login
                if data.get('multiple_organizations'):
                    login_data['organization_id'] = 1
                    response = requests.post(f"{self.backend_url}/api/auth/login", json=login_data)
                    data = response.json()
                
                self.token = data.get('access_token')
                self.log_test("Authentication", "PASS", "Successfully authenticated")
                return True
            else:
                self.log_test("Authentication", "FAIL", f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Authentication error: {str(e)}")
            return False
    
    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        print("\n🌐 Testing Frontend Accessibility...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_test("Frontend Access", "PASS", "Frontend is accessible")
                
                # Check for React app
                if "root" in response.text and ("react" in response.text.lower() or "React" in response.text):
                    self.log_test("React App", "PASS", "React app detected")
                else:
                    self.log_test("React App", "WARN", "React app not clearly detected")
                    
                return True
            else:
                self.log_test("Frontend Access", "FAIL", f"Frontend returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Access", "FAIL", f"Cannot access frontend: {str(e)}")
            return False
    
    def test_api_endpoints_from_frontend(self):
        """Test that API endpoints work for frontend consumption"""
        print("\n🔌 Testing API Endpoints for Frontend...")
        
        if not self.token:
            self.log_test("API Token", "FAIL", "No authentication token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test key endpoints that frontend needs
        endpoints = [
            ("/api/email-management/aliases", "Email Aliases"),
            ("/api/messages/", "Message Threads"),
            ("/api/substitutes/requests", "Substitute Requests"),
            ("/api/bulk-ops/import-template", "Bulk Operations"),
            ("/api/quick-polls/", "Quick Polls"),
            ("/api/events/", "Events")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", headers=headers)
                if response.status_code == 200:
                    self.log_test(f"API: {name}", "PASS", "Endpoint accessible")
                else:
                    self.log_test(f"API: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API: {name}", "FAIL", f"Error: {str(e)}")
    
    def test_phase2_component_paths(self):
        """Test if Phase 2 component paths are accessible"""
        print("\n📱 Testing Phase 2 Component Routes...")
        
        routes = [
            "/messaging",
            "/substitution", 
            "/bulk-operations",
            "/polls",
            "/admin"
        ]
        
        for route in routes:
            try:
                response = requests.get(f"{self.frontend_url}{route}", timeout=5)
                # Frontend routes typically return the same HTML (SPA)
                if response.status_code == 200:
                    self.log_test(f"Route: {route}", "PASS", "Route accessible")
                else:
                    self.log_test(f"Route: {route}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Route: {route}", "FAIL", f"Error: {str(e)}")
    
    def check_console_errors(self):
        """Note: This would require browser automation to check for console errors"""
        print("\n⚠️  Console Error Check:")
        print("   Manual check required - open browser DevTools to check for:")
        print("   - JavaScript errors")
        print("   - Failed network requests")
        print("   - React warnings")
        print("   - CORS errors")
        self.log_test("Console Errors", "WARN", "Manual browser check required")
    
    def test_mobile_responsiveness_indicators(self):
        """Check for mobile responsiveness indicators in the HTML"""
        print("\n📱 Testing Mobile Responsiveness Indicators...")
        
        try:
            response = requests.get(self.frontend_url)
            html = response.text
            
            # Check for viewport meta tag
            if 'viewport' in html and 'width=device-width' in html:
                self.log_test("Viewport Meta", "PASS", "Mobile viewport meta tag found")
            else:
                self.log_test("Viewport Meta", "FAIL", "Mobile viewport meta tag missing")
            
            # Check for responsive CSS framework indicators
            if 'bootstrap' in html.lower() or 'reactstrap' in html.lower():
                self.log_test("Responsive Framework", "PASS", "Bootstrap/Reactstrap detected")
            else:
                self.log_test("Responsive Framework", "WARN", "No obvious responsive framework")
                
        except Exception as e:
            self.log_test("Mobile Check", "FAIL", f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📊 FRONTEND TESTING REPORT")
        print("="*60)
        
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.results if r['status'] == 'WARN'])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Warnings: {warnings} ⚠️")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['message']}")
        
        if warnings > 0:
            print(f"\n⚠️  WARNINGS:")
            for result in self.results:
                if result['status'] == 'WARN':
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save detailed report
        with open('frontend_test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"\n📄 Detailed report saved to: frontend_test_report.json")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        return success_rate
    
    def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 Starting BandSync Phase 2 Frontend Testing")
        print("="*60)
        
        # Run tests in order
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
            
        self.test_frontend_accessibility()
        self.test_api_endpoints_from_frontend()
        self.test_phase2_component_paths()
        self.test_mobile_responsiveness_indicators()
        self.check_console_errors()
        
        # Generate report
        success_rate = self.generate_report()
        
        if success_rate >= 80:
            print("\n🎉 Frontend testing looks good! Ready for manual testing.")
        else:
            print("\n⚠️  Some issues found. Review failed tests before proceeding.")

if __name__ == "__main__":
    tester = FrontendTester()
    tester.run_all_tests()
