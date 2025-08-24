#!/usr/bin/env python3

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def connect_to_railway_db():
    try:
        connection = psycopg2.connect(
            host="shuttle.proxy.rlwy.net",
            port=40111,
            database="railway",
            user="postgres",
            password="JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS"
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def debug_super_admin_organizations():
    conn = connect_to_railway_db()
    if not conn:
        return
        
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # First check what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print("=== AVAILABLE TABLES ===")
        for table in tables:
            print(f"  {table['table_name']}")
        
        # Check if user table exists
        if not any(table['table_name'] == 'user' for table in tables):
            print("\n❌ 'user' table not found in database")
            return
            
        # Find super admin users
        cursor.execute("""
            SELECT id, username, email, super_admin 
            FROM "user" 
            WHERE super_admin = TRUE
        """)
        super_admins = cursor.fetchall()
        
        print("\n=== SUPER ADMIN USERS ===")
        for admin in super_admins:
            print(f"ID: {admin['id']}, Username: {admin['username']}, Email: {admin['email']}")
            
            # First, let's see the organization table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'organization'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print(f"\n--- Organization table columns ---")
            for col in columns:
                print(f"  {col['column_name']}: {col['data_type']}")
            
            # Check what organizations exist and their structure
            cursor.execute("""
                SELECT id, name, created_at
                FROM organization
                ORDER BY created_at
            """)
            
            orgs = cursor.fetchall()
            print(f"\n--- All Organizations ---")
            
            if not orgs:
                print("  No organizations found")
            else:
                for org in orgs:
                    print(f"  Org ID: {org['id']}, Name: '{org['name']}', Created: {org['created_at']}")
                    
            # Check direct user_organizations entries for this user
            cursor.execute("""
                SELECT uo.organization_id, o.name, uo.joined_at
                FROM user_organizations uo
                JOIN organization o ON uo.organization_id = o.id
                WHERE uo.user_id = %s
            """, (admin['id'],))
            
            member_entries = cursor.fetchall()
            if member_entries:
                print(f"\n--- Organization Memberships for {admin['username']} ---")
                for entry in member_entries:
                    print(f"  Member of Org ID: {entry['organization_id']}, Name: '{entry['name']}', Joined: {entry['joined_at']}")
            else:
                print(f"\n--- No organization memberships found for {admin['username']} ---")
            
            print("-" * 50)
            
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_super_admin_organizations()
