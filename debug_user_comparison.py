#!/usr/bin/env python3
"""
Debug script to investigate Rob123 vs Harvey258 data differences
This will help us understand why Rob123 gets React error #130
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
import json

def get_database_connection():
    """Get database connection from Railway environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ No DATABASE_URL found")
        return None
    
    try:
        # Parse the DATABASE_URL
        parsed = urlparse(database_url)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def debug_user_data(username):
    """Get comprehensive user data for debugging"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Get user basic info
        cursor.execute("""
            SELECT id, name, email, role, created_at 
            FROM "user" 
            WHERE name = %s
        """, (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return {"error": f"User {username} not found"}
        
        user_id, name, email, role, created_at = user_data
        result = {
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "role": role,
                "created_at": str(created_at) if created_at else None
            }
        }
        
        # Get organization relationships
        cursor.execute("""
            SELECT o.id, o.name, o.description, uo.role, uo.created_at
            FROM organization o
            JOIN user_organization uo ON o.id = uo.organization_id
            WHERE uo.user_id = %s
        """, (user_id,))
        
        orgs = []
        for org_data in cursor.fetchall():
            org_id, org_name, org_desc, user_role, join_date = org_data
            orgs.append({
                "id": org_id,
                "name": org_name,
                "description": org_desc,
                "user_role": user_role,
                "joined_at": str(join_date) if join_date else None
            })
        
        result["organizations"] = orgs
        
        # Check for any null/problematic fields in organization data
        cursor.execute("""
            SELECT o.*, uo.role as user_role
            FROM organization o
            JOIN user_organization uo ON o.id = uo.organization_id
            WHERE uo.user_id = %s
        """, (user_id,))
        
        detailed_orgs = []
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            org_dict = dict(zip(columns, row))
            # Convert any datetime objects to strings
            for key, value in org_dict.items():
                if hasattr(value, 'isoformat'):
                    org_dict[key] = value.isoformat()
                elif value is None:
                    org_dict[key] = None
            detailed_orgs.append(org_dict)
        
        result["detailed_organizations"] = detailed_orgs
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        return {"error": f"Database query failed: {e}"}

def main():
    print("🔍 Debugging Rob123 vs Harvey258 data differences...")
    print("=" * 60)
    
    # Debug both users
    for username in ["Rob123", "Harvey258"]:
        print(f"\n📊 User: {username}")
        print("-" * 40)
        
        data = debug_user_data(username)
        if data:
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ No data found for {username}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
