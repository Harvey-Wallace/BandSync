#!/usr/bin/env python3
"""
Debug script to check user organization relationships in Railway production database
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_user_organizations():
    """Debug user organization relationships in Railway database"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    print(f"🔗 Connecting to Railway database...")
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            print("\n=== USER ORGANIZATION DEBUG ===")
            
            # Check all users
            result = conn.execute(text("""
                SELECT id, username, email, primary_organization_id, current_organization_id, organization_id
                FROM "user" 
                ORDER BY username
            """))
            users = result.fetchall()
            
            print(f"\n👥 Found {len(users)} users:")
            for user in users:
                print(f"  - {user.username} (ID: {user.id})")
                print(f"    Email: {user.email}")
                print(f"    Primary Org: {user.primary_organization_id}")
                print(f"    Current Org: {user.current_organization_id}")
                print(f"    Legacy Org: {user.organization_id}")
            
            # Check all organizations
            result = conn.execute(text("""
                SELECT id, name, created_at
                FROM organization 
                ORDER BY name
            """))
            orgs = result.fetchall()
            
            print(f"\n🏢 Found {len(orgs)} organizations:")
            for org in orgs:
                print(f"  - {org.name} (ID: {org.id})")
            
            # Check all user-organization relationships
            result = conn.execute(text("""
                SELECT uo.user_id, uo.organization_id, uo.role, u.username, o.name
                FROM user_organization uo
                JOIN "user" u ON uo.user_id = u.id
                JOIN organization o ON uo.organization_id = o.id
                ORDER BY u.username, o.name
            """))
            user_orgs = result.fetchall()
            
            print(f"\n🔗 Found {len(user_orgs)} user-organization relationships:")
            for uo in user_orgs:
                print(f"  - {uo.username} -> {uo.name} ({uo.role})")
            
            # Check Rob321 specifically
            result = conn.execute(text("""
                SELECT id, username, email, primary_organization_id, current_organization_id, organization_id
                FROM "user" 
                WHERE username = 'Rob321'
            """))
            rob_user = result.fetchone()
            
            if rob_user:
                print(f"\n🔍 ROB321 DETAILS:")
                print(f"  User ID: {rob_user.id}")
                print(f"  Email: {rob_user.email}")
                print(f"  Primary Org ID: {rob_user.primary_organization_id}")
                print(f"  Current Org ID: {rob_user.current_organization_id}")
                print(f"  Legacy Org ID: {rob_user.organization_id}")
                
                # Check Rob321's organization relationships
                result = conn.execute(text("""
                    SELECT uo.organization_id, uo.role, o.name
                    FROM user_organization uo
                    JOIN organization o ON uo.organization_id = o.id
                    WHERE uo.user_id = :user_id
                """), {"user_id": rob_user.id})
                rob_orgs = result.fetchall()
                
                print(f"  Organization memberships: {len(rob_orgs)}")
                for uo in rob_orgs:
                    print(f"    - {uo.name} ({uo.role})")
            else:
                print("\n❌ Rob321 user not found!")
            
            # Check City of Birmingham Brass Band organization
            result = conn.execute(text("""
                SELECT id, name
                FROM organization 
                WHERE name = 'City of Birmingham Brass Band'
            """))
            birmingham_org = result.fetchone()
            
            if birmingham_org:
                print(f"\n🎺 CITY OF BIRMINGHAM BRASS BAND DETAILS:")
                print(f"  Organization ID: {birmingham_org.id}")
                print(f"  Name: {birmingham_org.name}")
                
                # Check members
                result = conn.execute(text("""
                    SELECT uo.user_id, uo.role, u.username
                    FROM user_organization uo
                    JOIN "user" u ON uo.user_id = u.id
                    WHERE uo.organization_id = :org_id
                """), {"org_id": birmingham_org.id})
                members = result.fetchall()
                
                print(f"  Members: {len(members)}")
                for member in members:
                    print(f"    - {member.username} ({member.role})")
            else:
                print("\n❌ City of Birmingham Brass Band organization not found!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_organizations()
