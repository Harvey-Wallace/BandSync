#!/usr/bin/env python3
"""
Test script for advanced RSVP features
Tests custom fields, attachments, and surveys
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:5001"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def login(credentials):
    """Login and return JWT token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)
    if response.status_code == 200:
        data = response.json()
        # Handle multi-organization login
        if data.get("multiple_organizations"):
            # Select first organization and login again
            org_id = data["organizations"][0]["id"]
            credentials_with_org = {**credentials, "organization_id": org_id}
            response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials_with_org)
            if response.status_code == 200:
                return response.json()["access_token"]
        else:
            return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_custom_fields(token, event_id):
    """Test custom fields functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔧 Testing Custom Fields...")
    
    # Create a custom field
    field_data = {
        "field_name": "Uniform Size",
        "field_type": "select",
        "field_description": "Please select your uniform size",
        "required": True,
        "field_options": ["XS", "S", "M", "L", "XL", "XXL"]
    }
    
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/custom-fields", 
                           json=field_data, headers=headers)
    if response.status_code == 201:
        field_id = response.json()["id"]
        print(f"✅ Created custom field: {field_id}")
    else:
        print(f"❌ Failed to create custom field: {response.text}")
        return False
    
    # Create another field
    field_data2 = {
        "field_name": "Dietary Restrictions",
        "field_type": "textarea",
        "field_description": "Please list any dietary restrictions or allergies",
        "required": False
    }
    
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/custom-fields", 
                           json=field_data2, headers=headers)
    if response.status_code == 201:
        field_id2 = response.json()["id"]
        print(f"✅ Created second custom field: {field_id2}")
    else:
        print(f"❌ Failed to create second custom field: {response.text}")
        return False
    
    # Get all fields
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/custom-fields", headers=headers)
    if response.status_code == 200:
        fields = response.json()
        print(f"✅ Retrieved {len(fields)} custom fields")
        for field in fields:
            print(f"   - {field['field_name']} ({field['field_type']})")
    else:
        print(f"❌ Failed to get custom fields: {response.text}")
        return False
    
    # Submit responses
    responses_data = {
        "responses": {
            str(field_id): "L",
            str(field_id2): "No nuts, lactose intolerant"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/field-responses", 
                           json=responses_data, headers=headers)
    if response.status_code == 200:
        print("✅ Submitted field responses")
    else:
        print(f"❌ Failed to submit responses: {response.text}")
        return False
    
    # Get responses summary
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/field-responses/summary", headers=headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ Retrieved responses summary with {len(summary)} fields")
        for field_id, field_summary in summary.items():
            print(f"   - {field_summary['field_name']}: {field_summary['total_responses']} responses")
    else:
        print(f"❌ Failed to get responses summary: {response.text}")
        return False
    
    return True

def test_attachments(token, event_id):
    """Test file attachments functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📎 Testing File Attachments...")
    
    # Create a test file
    test_file_content = "This is a test document for BandSync event attachments."
    test_file_name = "test_document.txt"
    
    with open(test_file_name, 'w') as f:
        f.write(test_file_content)
    
    try:
        # Upload file
        files = {'file': (test_file_name, open(test_file_name, 'rb'), 'text/plain')}
        data = {
            'description': 'Test document for event',
            'is_public': 'true'
        }
        
        response = requests.post(f"{BASE_URL}/api/events/{event_id}/attachments", 
                               files=files, data=data, headers=headers)
        
        if response.status_code == 201:
            attachment_id = response.json()["id"]
            print(f"✅ Uploaded attachment: {attachment_id}")
        else:
            print(f"❌ Failed to upload attachment: {response.text}")
            return False
        
        # Get attachments
        response = requests.get(f"{BASE_URL}/api/events/{event_id}/attachments", headers=headers)
        if response.status_code == 200:
            attachments = response.json()
            print(f"✅ Retrieved {len(attachments)} attachments")
            for attachment in attachments:
                print(f"   - {attachment['original_filename']} ({attachment['file_size']} bytes)")
        else:
            print(f"❌ Failed to get attachments: {response.text}")
            return False
        
        # Update attachment
        update_data = {
            "description": "Updated test document description"
        }
        response = requests.put(f"{BASE_URL}/api/events/{event_id}/attachments/{attachment_id}", 
                              json=update_data, headers=headers)
        if response.status_code == 200:
            print("✅ Updated attachment metadata")
        else:
            print(f"❌ Failed to update attachment: {response.text}")
            return False
        
        # Test download (just check if endpoint exists)
        response = requests.get(f"{BASE_URL}/api/events/{event_id}/attachments/{attachment_id}/download", 
                              headers=headers)
        if response.status_code == 200:
            print("✅ Download endpoint works")
        else:
            print(f"❌ Download failed: {response.text}")
            return False
        
        return True
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_name):
            os.remove(test_file_name)

def test_surveys(token, event_id):
    """Test surveys functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📋 Testing Surveys...")
    
    # Create a survey
    survey_data = {
        "title": "Post-Event Feedback",
        "description": "Please provide your feedback about the event",
        "is_active": True,
        "is_anonymous": False,
        "questions": [
            {
                "question_text": "How would you rate the overall event?",
                "question_type": "rating",
                "required": True
            },
            {
                "question_text": "What did you like most about the event?",
                "question_type": "text",
                "required": False
            },
            {
                "question_text": "Which aspects need improvement?",
                "question_type": "multiple_choice",
                "question_options": ["Sound quality", "Venue", "Organization", "Communication", "Other"],
                "required": False
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/surveys", 
                           json=survey_data, headers=headers)
    if response.status_code == 201:
        survey_id = response.json()["id"]
        print(f"✅ Created survey: {survey_id}")
    else:
        print(f"❌ Failed to create survey: {response.text}")
        return False
    
    # Get surveys
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/surveys", headers=headers)
    if response.status_code == 200:
        surveys = response.json()
        print(f"✅ Retrieved {len(surveys)} surveys")
        for survey in surveys:
            print(f"   - {survey['title']} ({survey['question_count']} questions)")
    else:
        print(f"❌ Failed to get surveys: {response.text}")
        return False
    
    # Get survey details
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/surveys/{survey_id}", headers=headers)
    if response.status_code == 200:
        survey_details = response.json()
        print(f"✅ Retrieved survey details with {len(survey_details['questions'])} questions")
    else:
        print(f"❌ Failed to get survey details: {response.text}")
        return False
    
    # Submit survey responses
    responses_data = {
        "responses": {
            str(survey_details['questions'][0]['id']): "5",  # Rating
            str(survey_details['questions'][1]['id']): "Great performance and good venue",  # Text
            str(survey_details['questions'][2]['id']): "Communication"  # Multiple choice
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/events/{event_id}/surveys/{survey_id}/responses", 
                           json=responses_data, headers=headers)
    if response.status_code == 200:
        print("✅ Submitted survey responses")
    else:
        print(f"❌ Failed to submit survey responses: {response.text}")
        return False
    
    # Get survey results
    response = requests.get(f"{BASE_URL}/api/events/{event_id}/surveys/{survey_id}/results", headers=headers)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Retrieved survey results with {results['survey']['total_responses']} responses")
        for question in results['questions']:
            print(f"   - {question['question_text']}: {question['total_responses']} responses")
    else:
        print(f"❌ Failed to get survey results: {response.text}")
        return False
    
    return True

def create_test_event(token):
    """Create a test event for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    
    event_data = {
        "title": "Advanced RSVP Test Event",
        "description": "Test event for advanced RSVP features",
        "date": "2024-12-25T19:00:00",
        "location_address": "Test Venue, 123 Test St"
    }
    
    response = requests.post(f"{BASE_URL}/api/events/", json=event_data, headers=headers)
    
    if response.status_code in [200, 201]:
        response_data = response.json()
        event_id = response_data.get("id")
        if event_id:
            print(f"✅ Created test event: {event_id}")
            return event_id
        else:
            print(f"❌ Event created but no ID returned: {response_data}")
            return None
    else:
        print(f"❌ Failed to create test event: {response.text}")
        return None

def main():
    print("🚀 Testing Advanced RSVP Features...")
    
    # Login as admin
    admin_token = login(ADMIN_CREDENTIALS)
    if not admin_token:
        print("❌ Failed to login as admin")
        return False
    
    print("✅ Logged in as admin")
    
    # Create test event
    event_id = create_test_event(admin_token)
    if not event_id:
        return False
    
    # Test all features
    success = True
    
    if not test_custom_fields(admin_token, event_id):
        success = False
    
    if not test_attachments(admin_token, event_id):
        success = False
    
    if not test_surveys(admin_token, event_id):
        success = False
    
    if success:
        print("\n✅ All advanced RSVP features tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
