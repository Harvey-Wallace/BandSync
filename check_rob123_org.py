#!/usr/bin/env python3
"""
Diagnostic script to check Rob123's organization relationships
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_rob123_organizations():
    """Check Rob123's organization relationships in detail."""
    
    # Use the Railway database URL
    database_url = 'postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@postgres.railway.internal:5432/railway'
    
    try:
        print("🔍 Checking Rob123 Organization Relationships")
        print("=" * 60)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Find Rob123 user
        print("\n1. Finding Rob123 User...")
        cursor.execute("""
            SELECT id, username, name, email, organization_id, current_organization_id, primary_organization_id
            FROM users 
            WHERE username = %s
        """, ('Rob123',))
        
        rob_user = cursor.fetchone()
        
        if rob_user:
            print(f"✅ Found Rob123:")
            print(f"   ID: {rob_user['id']}")
            print(f"   Username: {rob_user['username']}")
            print(f"   Name: {rob_user['name']}")
            print(f"   Email: {rob_user['email']}")
            print(f"   Legacy organization_id: {rob_user['organization_id']}")
            print(f"   Current organization_id: {rob_user['current_organization_id']}")
            print(f"   Primary organization_id: {rob_user['primary_organization_id']}")
            
            rob_user_id = rob_user['id']
            
            # 2. Check UserOrganization relationships
            print(f"\n2. Checking UserOrganization relationships for Rob123 (ID: {rob_user_id})...")
            cursor.execute("""
                SELECT uo.id, uo.user_id, uo.organization_id, uo.role, uo.joined_at, uo.is_active,
                       o.name as org_name
                FROM user_organizations uo
                JOIN organizations o ON uo.organization_id = o.id
                WHERE uo.user_id = %s
                ORDER BY uo.joined_at DESC
            """, (rob_user_id,))
            
            user_orgs = cursor.fetchall()
            
            if user_orgs:
                print(f"✅ Found {len(user_orgs)} organization relationships:")
                for uo in user_orgs:
                    print(f"   • Organization: {uo['org_name']} (ID: {uo['organization_id']})")
                    print(f"     Role: {uo['role']}")
                    print(f"     Joined: {uo['joined_at']}")
                    print(f"     Active: {uo['is_active']}")
                    print()
            else:
                print("❌ No UserOrganization relationships found!")
            
            # 3. Check for City of Birmingham Brass Band
            print("\n3. Looking for 'City of Birmingham Brass Band'...")
            cursor.execute("""
                SELECT id, name, created_at
                FROM organizations 
                WHERE name ILIKE %s
                ORDER BY name
            """, ('%City of Birmingham%',))
            
            birmingham_orgs = cursor.fetchall()
            
            if birmingham_orgs:
                print(f"✅ Found {len(birmingham_orgs)} matching organizations:")
                for org in birmingham_orgs:
                    print(f"   • {org['name']} (ID: {org['id']}) - Created: {org['created_at']}")
                    
                    # Check if Rob123 should be in this org
                    cursor.execute("""
                        SELECT uo.role, uo.is_active, uo.joined_at
                        FROM user_organizations uo
                        WHERE uo.user_id = %s AND uo.organization_id = %s
                    """, (rob_user_id, org['id']))
                    
                    rob_in_org = cursor.fetchone()
                    if rob_in_org:
                        print(f"     → Rob123 IS in this org: {rob_in_org['role']} (Active: {rob_in_org['is_active']})")
                    else:
                        print(f"     → Rob123 is NOT in this org")
                    print()
            else:
                print("❌ No organizations found matching 'City of Birmingham'")
            
            # 4. Check all organizations to see what exists
            print("\n4. All organizations in the system:")
            cursor.execute("""
                SELECT id, name, created_at,
                       (SELECT COUNT(*) FROM user_organizations WHERE organization_id = o.id) as user_count
                FROM organizations o
                ORDER BY name
            """, )
            
            all_orgs = cursor.fetchall()
            
            for org in all_orgs:
                print(f"   • {org['name']} (ID: {org['id']}) - {org['user_count']} members")
            
            # 5. Suggest fix if needed
            if not user_orgs and birmingham_orgs:
                print(f"\n💡 SUGGESTED FIX:")
                print(f"Rob123 has no organization relationships but '{birmingham_orgs[0]['name']}' exists.")
                print(f"You may need to add Rob123 to the organization manually.")
                
        else:
            print("❌ Rob123 user not found!")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        
        # Try alternative connection for testing
        print("\n🔄 Trying to connect to production database...")
        try:
            # This might work if running from Railway environment
            import requests
            print("Cannot connect directly from local machine to Railway internal database.")
            print("The admin oversight dashboard should show the real data when accessed through the web interface.")
        except:
            pass
            
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_rob123_organizations()
