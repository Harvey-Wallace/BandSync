#!/usr/bin/env python3
"""
Check Harvey258 account status and prepare for clean admin oversight features
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_harvey_account():
    """Check Harvey258 account status in the database."""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@postgres.railway.internal:5432/railway')
    
    try:
        print("🔍 Checking Harvey258 Account Status")
        print("=" * 50)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check user account
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, created_at
            FROM users 
            WHERE username = %s
        """, ('Harvey258',))
        
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Found Harvey258 Account:")
            print(f"   ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Name: {user['first_name']} {user['last_name']}")
            print(f"   Created: {user['created_at']}")
            
            # Check organization memberships
            cursor.execute("""
                SELECT o.id, o.name, o.created_at, uo.role
                FROM organizations o
                JOIN user_organizations uo ON o.id = uo.organization_id
                WHERE uo.user_id = %s
                ORDER BY o.created_at
            """, (user['id'],))
            
            orgs = cursor.fetchall()
            print(f"\n📊 Organization Memberships ({len(orgs)}):")
            for org in orgs:
                print(f"   • {org['name']} (Role: {org['role']}) - Created: {org['created_at']}")
            
            # Get total organization count
            cursor.execute("SELECT COUNT(*) as total FROM organizations")
            total_orgs = cursor.fetchone()['total']
            print(f"\n🏢 Total Organizations in System: {total_orgs}")
            
            # Get total user count
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            print(f"👥 Total Users in System: {total_users}")
            
            return user['id']
            
        else:
            print("❌ Harvey258 account not found!")
            return None
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_harvey_account()
