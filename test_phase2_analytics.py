#!/usr/bin/env python3

import requests
import json
import sys

def test_phase2_analytics():
    """Test Phase 2 Super Admin Analytics endpoints"""
    
    # Base URL - use Railway deployment
    base_url = 'https://bandsync-production.up.railway.app/api'
    
    # Test credentials
    username = 'Harvey258'
    password = 'password'
    
    print("=== Phase 2 Analytics Testing ===")
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
            else:
                print("No Super Admin organization found")
                return
        
        token = login_data.get('access_token') or login_data.get('token')
        if not token:
            print(f"No token found. Response: {login_data}")
            return
            
        print(f"✅ Login successful")
        
    except Exception as e:
        print(f"✗ Login error: {e}")
        return
    
    # Step 2: Test Analytics Overview
    print("\n2. Testing Analytics Overview...")
    try:
        analytics_response = requests.get(f"{base_url}/super-admin/analytics/overview", headers={
            'Authorization': f'Bearer {token}'
        }, timeout=10)
        
        print(f"Analytics Overview Status: {analytics_response.status_code}")
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print("✅ Analytics Overview Success!")
            print(f"  - Total Users: {analytics_data['overview']['users']['total']}")
            print(f"  - New Users (30d): {analytics_data['overview']['users']['new_30d']}")
            print(f"  - Active Users (30d): {analytics_data['overview']['users']['active_30d']}")
            print(f"  - Total Organizations: {analytics_data['overview']['organizations']['total']}")
            print(f"  - Total Events: {analytics_data['overview']['events']['total']}")
            print(f"  - Growth Rate: {analytics_data['overview']['users']['growth_rate_30d']}%")
        else:
            print(f"✗ Analytics Overview Failed: {analytics_response.text}")
    except Exception as e:
        print(f"✗ Analytics Overview Error: {e}")
    
    # Step 3: Test Organization Performance
    print("\n3. Testing Organization Performance...")
    try:
        perf_response = requests.get(f"{base_url}/super-admin/analytics/organizations/performance", headers={
            'Authorization': f'Bearer {token}'
        }, timeout=10)
        
        print(f"Organization Performance Status: {perf_response.status_code}")
        if perf_response.status_code == 200:
            perf_data = perf_response.json()
            print("✅ Organization Performance Success!")
            print(f"  - Organizations Analyzed: {len(perf_data['organizations'])}")
            print(f"  - Excellent Health: {perf_data['summary']['excellent_health']}")
            print(f"  - Good Health: {perf_data['summary']['good_health']}")
            print(f"  - Needs Attention: {perf_data['summary']['needs_attention']}")
            print(f"  - Average Engagement Score: {perf_data['summary']['avg_engagement_score']}")
            
            # Show top 3 organizations
            print("\n  Top Organizations:")
            for i, org in enumerate(perf_data['organizations'][:3]):
                print(f"    {i+1}. {org['name']}: {org['metrics']['engagement_score']} score")
        else:
            print(f"✗ Organization Performance Failed: {perf_response.text}")
    except Exception as e:
        print(f"✗ Organization Performance Error: {e}")
    
    # Step 4: Test Trends
    print("\n4. Testing Trends Data...")
    try:
        trends_response = requests.get(f"{base_url}/super-admin/analytics/trends?period=30d&metric=users", headers={
            'Authorization': f'Bearer {token}'
        }, timeout=10)
        
        print(f"Trends Status: {trends_response.status_code}")
        if trends_response.status_code == 200:
            trends_data = trends_response.json()
            print("✅ Trends Success!")
            print(f"  - Period: {trends_data['period']}")
            print(f"  - Metric: {trends_data['metric']}")
            print(f"  - Data Points: {len(trends_data['trends'])}")
            if trends_data['trends']:
                print(f"  - Latest Entry: {trends_data['trends'][-1]}")
        else:
            print(f"✗ Trends Failed: {trends_response.text}")
    except Exception as e:
        print(f"✗ Trends Error: {e}")
    
    # Step 5: Test Export
    print("\n5. Testing Export Functionality...")
    try:
        export_response = requests.get(f"{base_url}/super-admin/analytics/export/system_overview", headers={
            'Authorization': f'Bearer {token}'
        }, timeout=10)
        
        print(f"Export Status: {export_response.status_code}")
        if export_response.status_code == 200:
            export_data = export_response.json()
            print("✅ Export Success!")
            print(f"  - Report Type: {export_data['report_type']}")
            print(f"  - Generated At: {export_data['generated_at']}")
            print(f"  - Date Range: {export_data['date_range']['start']} to {export_data['date_range']['end']}")
        else:
            print(f"✗ Export Failed: {export_response.text}")
    except Exception as e:
        print(f"✗ Export Error: {e}")
    
    print("\n=== Phase 2 Analytics Test Complete ===")

if __name__ == "__main__":
    test_phase2_analytics()
