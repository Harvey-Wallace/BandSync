#!/usr/bin/env python3
"""
Test production database connection and query users
"""

import psycopg2
import os
from urllib.parse import urlparse

# Railway database URL from environment variables
db_url = "postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@postgres.railway.internal:5432/railway"

# For external connections, we need to use the external host
# Let's try to connect using the external host if available
external_db_url = "postgresql://postgres:ERmHVseNucyFyenNPtsLCjnxzNKrqycx@caboose.proxy.rlwy.net:46206/railway"

def test_db_connection():
    """Test database connection and query users"""
    try:
        print("🔍 Attempting to connect to production database...")
        
        # Try external connection first
        try:
            conn = psycopg2.connect(external_db_url)
            print("✅ Connected to external database")
        except:
            print("❌ External connection failed, trying internal...")
            conn = psycopg2.connect(db_url)
            print("✅ Connected to internal database")
        
        cur = conn.cursor()
        
        # Check if users table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'user'
            );
        """)
        table_exists = cur.fetchone()[0]
        print(f"User table exists: {table_exists}")
        
        if table_exists:
            # Query users
            cur.execute("""
                SELECT id, username, email, role, organization_id, 
                       password_hash IS NOT NULL as has_password,
                       length(password_hash) as password_length
                FROM "user" 
                ORDER BY id;
            """)
            
            users = cur.fetchall()
            print(f"\n👥 Found {len(users)} users:")
            
            for user in users:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
                print(f"    Role: {user[3]}, Org ID: {user[4]}")
                print(f"    Has password: {user[5]}, Password length: {user[6]}")
                print()
        
        # Check organizations
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'organization'
            );
        """)
        org_table_exists = cur.fetchone()[0]
        print(f"Organization table exists: {org_table_exists}")
        
        if org_table_exists:
            cur.execute('SELECT id, name FROM organization ORDER BY id;')
            orgs = cur.fetchall()
            print(f"\n🏢 Found {len(orgs)} organizations:")
            for org in orgs:
                print(f"  - ID: {org[0]}, Name: {org[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 BandSync Production Database Test")
    print("=" * 50)
    test_db_connection()
