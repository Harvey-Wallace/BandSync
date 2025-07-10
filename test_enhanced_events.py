#!/usr/bin/env python3
"""
Test script for enhanced event features
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_login():
    """Test login and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
        return token
    else:
        print("❌ Login failed")
        return None

def test_categories(token):
    """Test event categories endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/events/categories", headers=headers)
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ Categories loaded: {len(categories)} categories found")
        for cat in categories:
            print(f"  - {cat['name']} ({cat['color']})")
        return categories
    else:
        print("❌ Failed to load categories")
        return []

def test_events(token):
    """Test enhanced events endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/events/", headers=headers)
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Events loaded: {len(events)} events found")
        for event in events[:3]:  # Show first 3 events
            print(f"  - {event['title']} (Category: {event.get('category', 'None')})")
        return events
    else:
        print("❌ Failed to load events")
        return []

def test_create_recurring_event(token, categories):
    """Test creating a recurring event"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use first category if available
    category_id = categories[0]['id'] if categories else None
    
    event_data = {
        "title": "Weekly Rehearsal Test",
        "type": "Rehearsal",
        "description": "Test recurring weekly rehearsal",
        "date": "2025-07-15T19:00:00",
        "end_date": "2025-07-15T21:00:00",
        "category_id": category_id,
        "is_recurring": True,
        "recurring_pattern": "weekly",
        "recurring_interval": 1,
        "recurring_end_date": "2025-08-15",
        "send_reminders": True,
        "reminder_days_before": 2
    }
    
    response = requests.post(f"{BASE_URL}/api/events/", headers=headers, json=event_data)
    if response.status_code == 200:
        print("✅ Recurring event created successfully")
        return response.json()
    else:
        print(f"❌ Failed to create recurring event: {response.text}")
        return None

def test_templates(token):
    """Test event templates endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/events/templates", headers=headers)
    if response.status_code == 200:
        templates = response.json()
        print(f"✅ Templates loaded: {len(templates)} templates found")
        return templates
    else:
        print("❌ Failed to load templates")
        return []

def main():
    print("🧪 Testing Enhanced Event Features")
    print("=" * 40)
    
    # Test login
    token = test_login()
    if not token:
        return
    
    # Test categories
    print("\n📂 Testing Event Categories")
    categories = test_categories(token)
    
    # Test events
    print("\n📅 Testing Enhanced Events")
    events = test_events(token)
    
    # Test templates
    print("\n📋 Testing Event Templates")
    templates = test_templates(token)
    
    # Test creating recurring event
    print("\n🔄 Testing Recurring Event Creation")
    test_create_recurring_event(token, categories)
    
    print("\n✨ Enhanced Event Features Test Complete!")

if __name__ == "__main__":
    main()
