#!/usr/bin/env python3
"""
Script to promote a user to Super Admin role in BandSync database
"""
import os
import psycopg2
from urllib.parse import urlparse

def promote_user_to_super_admin(username, database_url=None):
    """
    Promote a user to Super Admin role
    """
    if not database_url:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("Error: DATABASE_URL environment variable not set")
            print("Please provide database URL as argument or set DATABASE_URL env var")
            return False
    
    try:
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Error: User '{username}' not found")
            return False
        
        current_username, current_role = user
        print(f"Found user: {current_username} (current role: {current_role})")
        
        # Update user role to Super Admin
        cursor.execute("UPDATE users SET role = 'Super Admin' WHERE username = %s", (username,))
        
        # Commit changes
        conn.commit()
        
        print(f"✅ Successfully promoted '{username}' to Super Admin!")
        
        # Verify the change
        cursor.execute("SELECT username, role FROM users WHERE username = %s", (username,))
        updated_user = cursor.fetchone()
        print(f"Verified: {updated_user[0]} is now {updated_user[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python promote_user_to_super_admin.py <username> [database_url]")
        print("Example: python promote_user_to_super_admin.py john_doe")
        sys.exit(1)
    
    username = sys.argv[1]
    database_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    promote_user_to_super_admin(username, database_url)
