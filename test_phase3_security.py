#!/usr/bin/env python3
"""
Phase 3 Security & Compliance Testing Script
Comprehensive testing of audit trails, security events, and data privacy features.
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_phase3_security():
    """Test Phase 3 Security & Compliance endpoints"""
    
    # Base URL - use Railway deployment
    base_url = 'https://bandsync-production.up.railway.app/api'
    
    # Test credentials
    username = 'Harvey258'
    password = 'password'
    
    print("🔐 Phase 3 Security & Compliance Testing")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    
    # Step 1: Login as Super Admin
    print("\n1. Logging in as Super Admin...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json={
            'username': username,
            'password': password
        }, timeout=10)
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
            
        login_data = login_response.json()
        
        # Handle multi-organization login
        if login_data.get('multiple_organizations'):
            organizations = login_data.get('organizations', [])
            super_admin_org = None
            for org in organizations:
                if org.get('role') == 'Super Admin':
                    super_admin_org = org
                    break
            
            if super_admin_org:
                print(f"Using Super Admin organization: {super_admin_org['name']}")
                login_response = requests.post(f"{base_url}/auth/login", json={
                    'username': username,
                    'password': password,
                    'organization_id': super_admin_org['id']
                }, timeout=10)
                
                if login_response.status_code != 200:
                    print(f"Organization login failed: {login_response.text}")
                    return
                    
                login_data = login_response.json()
        
        token = login_data.get('access_token')
        if not token:
            print("No access token received")
            return
            
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Step 2: Test Audit Log Retrieval
    print("\n2. Testing Audit Log Retrieval...")
    try:
        audit_response = requests.get(
            f"{base_url}/super-admin/security/audit-log",
            headers=headers,
            params={'per_page': 10},
            timeout=10
        )
        
        print(f"Audit Log Status: {audit_response.status_code}")
        
        if audit_response.status_code == 200:
            audit_data = audit_response.json()
            total_entries = audit_data.get('summary', {}).get('total_entries', 0)
            recent_entries = audit_data.get('summary', {}).get('recent_entries_24h', 0)
            
            print("✅ Audit Log Success!")
            print(f"  - Total Audit Entries: {total_entries}")
            print(f"  - Recent Entries (24h): {recent_entries}")
            print(f"  - Returned Logs: {len(audit_data.get('audit_logs', []))}")
            
            # Show recent entries
            logs = audit_data.get('audit_logs', [])
            if logs:
                print("  Recent Actions:")
                for log in logs[:3]:
                    action = log.get('action_type', 'unknown')
                    resource = log.get('resource_type', 'unknown')
                    user = log.get('username', 'system')
                    timestamp = log.get('timestamp', '')[:19] if log.get('timestamp') else 'unknown'
                    print(f"    • {user}: {action} {resource} at {timestamp}")
        else:
            print(f"✗ Audit Log Failed: {audit_response.text}")
            
    except Exception as e:
        print(f"Audit log error: {e}")
    
    # Step 3: Test Security Events
    print("\n3. Testing Security Events...")
    try:
        security_response = requests.get(
            f"{base_url}/super-admin/security/security-events",
            headers=headers,
            params={'per_page': 10},
            timeout=10
        )
        
        print(f"Security Events Status: {security_response.status_code}")
        
        if security_response.status_code == 200:
            security_data = security_response.json()
            total_events = security_data.get('summary', {}).get('total_events', 0)
            unresolved_critical = security_data.get('summary', {}).get('unresolved_critical', 0)
            
            print("✅ Security Events Success!")
            print(f"  - Total Security Events: {total_events}")
            print(f"  - Unresolved Critical: {unresolved_critical}")
            print(f"  - Returned Events: {len(security_data.get('security_events', []))}")
            
            # Show recent events
            events = security_data.get('security_events', [])
            if events:
                print("  Recent Security Events:")
                for event in events[:3]:
                    event_type = event.get('event_type', 'unknown')
                    severity = event.get('severity', 'unknown')
                    resolved = event.get('resolved', False)
                    timestamp = event.get('timestamp', '')[:19] if event.get('timestamp') else 'unknown'
                    status = "resolved" if resolved else "unresolved"
                    print(f"    • {event_type} ({severity}) - {status} at {timestamp}")
        else:
            print(f"✗ Security Events Failed: {security_response.text}")
            
    except Exception as e:
        print(f"Security events error: {e}")
    
    # Step 4: Test Audit Summary
    print("\n4. Testing Audit Summary...")
    try:
        summary_response = requests.get(
            f"{base_url}/super-admin/security/audit-summary",
            headers=headers,
            timeout=10
        )
        
        print(f"Audit Summary Status: {summary_response.status_code}")
        
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            audit_stats = summary_data.get('audit_statistics', {})
            security_stats = summary_data.get('security_statistics', {})
            
            print("✅ Audit Summary Success!")
            print(f"  - Total Audit Entries: {audit_stats.get('total_entries', 0)}")
            print(f"  - Entries (24h): {audit_stats.get('entries_24h', 0)}")
            print(f"  - Entries (7d): {audit_stats.get('entries_7d', 0)}")
            print(f"  - Growth Rate (24h): {audit_stats.get('growth_rate_24h', 0)}%")
            print(f"  - Security Events: {security_stats.get('total_events', 0)}")
            print(f"  - Resolution Rate: {security_stats.get('resolution_rate', 0)}%")
            
            # Show recent activity
            recent_activity = summary_data.get('recent_activity', {})
            actions = recent_activity.get('actions_24h', [])
            if actions:
                print("  Recent Actions (24h):")
                for action in actions[:3]:
                    action_type = action.get('action', 'unknown')
                    count = action.get('count', 0)
                    print(f"    • {action_type}: {count} times")
        else:
            print(f"✗ Audit Summary Failed: {summary_response.text}")
            
    except Exception as e:
        print(f"Audit summary error: {e}")
    
    # Step 5: Test Audit Log Filtering
    print("\n5. Testing Audit Log Filtering...")
    try:
        # Test filtering by action type
        filter_response = requests.get(
            f"{base_url}/super-admin/security/audit-log",
            headers=headers,
            params={
                'action_type': 'view',
                'per_page': 5,
                'start_date': (datetime.utcnow() - timedelta(days=1)).isoformat()
            },
            timeout=10
        )
        
        print(f"Filtered Audit Log Status: {filter_response.status_code}")
        
        if filter_response.status_code == 200:
            filter_data = filter_response.json()
            filtered_logs = filter_data.get('audit_logs', [])
            
            print("✅ Audit Log Filtering Success!")
            print(f"  - Filtered Results: {len(filtered_logs)}")
            print(f"  - Total Pages: {filter_data.get('pagination', {}).get('pages', 0)}")
            
            # Verify all results match filter
            view_actions = [log for log in filtered_logs if log.get('action_type') == 'view']
            print(f"  - 'view' Actions: {len(view_actions)}/{len(filtered_logs)}")
        else:
            print(f"✗ Audit Log Filtering Failed: {filter_response.text}")
            
    except Exception as e:
        print(f"Audit log filtering error: {e}")
    
    # Step 6: Test Security Event Filtering
    print("\n6. Testing Security Event Filtering...")
    try:
        # Test filtering by severity
        security_filter_response = requests.get(
            f"{base_url}/super-admin/security/security-events",
            headers=headers,
            params={
                'severity': 'high',
                'resolved': False,
                'per_page': 5
            },
            timeout=10
        )
        
        print(f"Filtered Security Events Status: {security_filter_response.status_code}")
        
        if security_filter_response.status_code == 200:
            security_filter_data = security_filter_response.json()
            filtered_events = security_filter_data.get('security_events', [])
            
            print("✅ Security Event Filtering Success!")
            print(f"  - Filtered Results: {len(filtered_events)}")
            print(f"  - High Severity Unresolved: {len(filtered_events)}")
            
            # Show filtered events
            if filtered_events:
                print("  High Severity Unresolved Events:")
                for event in filtered_events:
                    event_type = event.get('event_type', 'unknown')
                    source_ip = event.get('source_ip', 'unknown')
                    print(f"    • {event_type} from {source_ip}")
        else:
            print(f"✗ Security Event Filtering Failed: {security_filter_response.text}")
            
    except Exception as e:
        print(f"Security event filtering error: {e}")
    
    print(f"\n🔐 Phase 3 Security & Compliance Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    test_phase3_security()
