#!/usr/bin/env python3
"""
Make User Super Admin Script
============================
This script will make a specific user a super admin in the Railway database.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_railway_database_url():
    """Get the Railway database URL"""
    # Current external Railway URL
    return "postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@shuttle.proxy.rlwy.net:40111/railway"

def list_users():
    """List all users in the database"""
    database_url = get_railway_database_url()
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, super_admin, name
            FROM "user"
            ORDER BY id;
        """)
        
        users = cursor.fetchall()
        
        print("\n👥 Current Users:")
        print("ID | Username | Email | Role | Super Admin | Name")
        print("-" * 80)
        
        for user in users:
            user_id, username, email, role, super_admin, name = user
            super_status = "✅ YES" if super_admin else "❌ NO"
            name_display = name if name else "(no name)"
            print(f"{user_id:2} | {username:12} | {email:25} | {role:8} | {super_status:7} | {name_display}")
        
        cursor.close()
        conn.close()
        
        return users
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []

def make_super_admin(user_identifier):
    """Make a user a super admin by username, email, or ID"""
    database_url = get_railway_database_url()
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Try to find user by different identifiers
        if user_identifier.isdigit():
            # Search by ID
            cursor.execute("""
                SELECT id, username, email, super_admin
                FROM "user"
                WHERE id = %s;
            """, (int(user_identifier),))
        elif "@" in user_identifier:
            # Search by email
            cursor.execute("""
                SELECT id, username, email, super_admin
                FROM "user"
                WHERE email = %s;
            """, (user_identifier,))
        else:
            # Search by username
            cursor.execute("""
                SELECT id, username, email, super_admin
                FROM "user"
                WHERE username = %s;
            """, (user_identifier,))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{user_identifier}' not found!")
            return False
        
        user_id, username, email, is_super_admin = user
        
        if is_super_admin:
            print(f"✅ User '{username}' ({email}) is already a super admin!")
            return True
        
        # Update user to be super admin
        cursor.execute("""
            UPDATE "user"
            SET super_admin = TRUE
            WHERE id = %s;
        """, (user_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"🎉 SUCCESS: User '{username}' ({email}) is now a super admin!")
            return True
        else:
            print(f"❌ Failed to update user '{username}'")
            return False
        
    except Exception as e:
        print(f"❌ Error making user super admin: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    print("👑 BandSync Super Admin Creator")
    print("=" * 50)
    
    # List current users
    users = list_users()
    
    if not users:
        print("❌ No users found in the database!")
        print("💡 Please create a user through the web interface first.")
        return
    
    print(f"\n🎯 Found {len(users)} user(s) in the database.")
    
    # Ask which user to make super admin
    print("\n💡 You can identify the user by:")
    print("   - User ID (number)")
    print("   - Username")
    print("   - Email address")
    
    user_identifier = input("\n👑 Enter the user to make super admin: ").strip()
    
    if not user_identifier:
        print("❌ No user specified!")
        return
    
    # Confirm action
    confirm = input(f"\n⚠️  Make '{user_identifier}' a super admin? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Operation cancelled")
        return
    
    # Make the user super admin
    success = make_super_admin(user_identifier)
    
    if success:
        print(f"\n✅ Super admin status granted!")
        print(f"🔑 The user now has full admin access to:")
        print(f"   - All organizations")
        print(f"   - All users")
        print(f"   - System settings")
        print(f"   - Admin dashboard")
        
        # Show updated user list
        print(f"\n📋 Updated user list:")
        list_users()
    else:
        print(f"\n❌ Failed to grant super admin status")

if __name__ == "__main__":
    main()
