#!/usr/bin/env python3
"""
BandSync Phase 2 Component Integration Test
Test individual components with backend APIs
"""

import requests
import json
import time
from datetime import datetime

class ComponentTester:
    def __init__(self, backend_url="http://localhost:5001"):
        self.backend_url = backend_url
        self.token = None
        self.user_id = None
        self.org_id = None
        
    def setup_auth(self):
        """Setup authentication"""
        login_data = {'username': 'admin', 'password': 'admin123'}
        
        response = requests.post(f"{self.backend_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('multiple_organizations'):
                login_data['organization_id'] = 1
                response = requests.post(f"{self.backend_url}/api/auth/login", json=login_data)
                data = response.json()
            
            self.token = data.get('access_token')
            self.user_id = data.get('user_id', 1)
            self.org_id = data.get('organization_id', 1)
            return True
        return False
    
    def test_messaging_component_data(self):
        """Test if messaging component has proper data"""
        print("🧪 Testing Messaging Component Data...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test threads endpoint
        response = requests.get(f"{self.backend_url}/api/messages/", headers=headers)
        if response.status_code == 200:
            threads = response.json()
            print(f"✅ Message threads: {len(threads)} found")
            
            # Create a test message if no threads exist
            if len(threads) == 0:
                print("📝 Creating test message thread...")
                message_data = {
                    'subject': 'Frontend Test Message',
                    'content': 'This is a test message for frontend testing',
                    'recipients': {'all_members': True}
                }
                
                response = requests.post(f"{self.backend_url}/api/messages/send", 
                                       json=message_data, headers=headers)
                if response.status_code == 201:
                    print("✅ Test message created successfully")
                else:
                    print(f"❌ Failed to create test message: {response.status_code}")
        else:
            print(f"❌ Failed to fetch message threads: {response.status_code}")
    
    def test_email_component_data(self):
        """Test email component data"""
        print("🧪 Testing Email Component Data...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test email aliases
        response = requests.get(f"{self.backend_url}/api/email-management/aliases", headers=headers)
        if response.status_code == 200:
            aliases = response.json()
            print(f"✅ Email aliases: {len(aliases)} found")
            
            # Create a test alias if none exist
            if len(aliases) == 0:
                print("📧 Creating test email alias...")
                alias_data = {
                    'alias_name': 'frontend-test',
                    'alias_type': 'organization'
                }
                
                response = requests.post(f"{self.backend_url}/api/email-management/aliases", 
                                       json=alias_data, headers=headers)
                if response.status_code == 201:
                    print("✅ Test email alias created successfully")
                else:
                    print(f"❌ Failed to create test alias: {response.status_code}")
        else:
            print(f"❌ Failed to fetch email aliases: {response.status_code}")
    
    def test_substitution_component_data(self):
        """Test substitution component data"""
        print("🧪 Testing Substitution Component Data...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test substitute requests
        response = requests.get(f"{self.backend_url}/api/substitutes/requests", headers=headers)
        if response.status_code == 200:
            requests_data = response.json()
            print(f"✅ Substitute requests: {len(requests_data)} found")
        else:
            print(f"❌ Failed to fetch substitute requests: {response.status_code}")
    
    def test_polls_component_data(self):
        """Test quick polls component data"""
        print("🧪 Testing Quick Polls Component Data...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test polls
        response = requests.get(f"{self.backend_url}/api/quick-polls/", headers=headers)
        if response.status_code == 200:
            polls = response.json()
            print(f"✅ Quick polls: {len(polls)} found")
            
            # Create a test poll if none exist
            if len(polls) == 0:
                print("📊 Creating test poll...")
                poll_data = {
                    'question': 'Frontend Test Poll - What do you think?',
                    'options': ['Option 1', 'Option 2', 'Option 3'],
                    'anonymous': True
                }
                
                response = requests.post(f"{self.backend_url}/api/quick-polls/", 
                                       json=poll_data, headers=headers)
                if response.status_code == 201:
                    print("✅ Test poll created successfully")
                else:
                    print(f"❌ Failed to create test poll: {response.status_code}")
        else:
            print(f"❌ Failed to fetch polls: {response.status_code}")
    
    def test_bulk_ops_component_data(self):
        """Test bulk operations component data"""
        print("🧪 Testing Bulk Operations Component Data...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test import template
        response = requests.get(f"{self.backend_url}/api/bulk-ops/import-template", headers=headers)
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Import template available with {len(template.get('headers', []))} columns")
        else:
            print(f"❌ Failed to fetch import template: {response.status_code}")
        
        # Test export
        response = requests.get(f"{self.backend_url}/api/bulk-ops/export", headers=headers)
        if response.status_code == 200:
            export_data = response.json()
            member_count = len(export_data.get('members', []))
            event_count = len(export_data.get('events', []))
            print(f"✅ Export data available: {member_count} members, {event_count} events")
        else:
            print(f"❌ Failed to fetch export data: {response.status_code}")
    
    def create_test_data_for_frontend(self):
        """Create comprehensive test data for frontend testing"""
        print("🔧 Creating test data for frontend components...")
        
        if not self.setup_auth():
            print("❌ Authentication failed")
            return
        
        self.test_messaging_component_data()
        self.test_email_component_data()
        self.test_substitution_component_data()
        self.test_polls_component_data()
        self.test_bulk_ops_component_data()
        
        print("\n✅ Test data creation complete!")
        print("🌐 You can now test the frontend components with real data:")
        print("   - http://localhost:3000/messaging")
        print("   - http://localhost:3000/admin (Email Management)")
        print("   - http://localhost:3000/substitution")
        print("   - http://localhost:3000/polls")
        print("   - http://localhost:3000/bulk-operations")

if __name__ == "__main__":
    tester = ComponentTester()
    tester.create_test_data_for_frontend()
