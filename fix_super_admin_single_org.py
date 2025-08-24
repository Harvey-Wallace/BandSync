#!/usr/bin/env python3
"""
Fix Super Admin Multi-Tenant Issue
Removes super admin from extra organizations to make single-tenant
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os

def main():
    # Railway database connection
    try:
        conn = psycopg2.connect(
            host='shuttle.proxy.rlwy.net',
            port=40111,
            database='railway',
            user='postgres',
            password='JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS'
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Connected to Railway database")
        
        # Find super admin user
        cursor.execute("""
            SELECT id, username, email, super_admin
            FROM "user"
            WHERE super_admin = true
        """)
        
        super_admins = cursor.fetchall()
        
        if not super_admins:
            print("❌ No super admin users found")
            return
        
        for admin in super_admins:
            print(f"\n🔍 Analyzing Super Admin: {admin['username']} (ID: {admin['id']})")
            
            # Check current organization memberships
            cursor.execute("""
                SELECT uo.organization_id, o.name, uo.joined_at
                FROM user_organizations uo
                JOIN organization o ON uo.organization_id = o.id
                WHERE uo.user_id = %s
                ORDER BY o.created_at
            """, (admin['id'],))
            
            memberships = cursor.fetchall()
            
            if len(memberships) <= 1:
                print(f"✅ {admin['username']} is already single-tenant (has {len(memberships)} organization)")
                continue
                
            print(f"🔸 Current organizations for {admin['username']}:")
            for i, membership in enumerate(memberships, 1):
                print(f"  {i}. Org ID: {membership['organization_id']}, Name: '{membership['name']}'")
            
            # Ask which organization to keep
            print(f"\n❓ Which organization should {admin['username']} remain in?")
            while True:
                try:
                    choice = input(f"Enter number (1-{len(memberships)}): ").strip()
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(memberships):
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(memberships)}")
                except ValueError:
                    print("Please enter a valid number")
            
            keep_org = memberships[choice_idx]
            remove_orgs = [m for i, m in enumerate(memberships) if i != choice_idx]
            
            print(f"\n✅ Will keep: '{keep_org['name']}' (ID: {keep_org['organization_id']})")
            print(f"🗑️  Will remove memberships from:")
            for org in remove_orgs:
                print(f"   - '{org['name']}' (ID: {org['organization_id']})")
            
            # Confirm action
            confirm = input("\n⚠️  Proceed with removing these memberships? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("❌ Operation cancelled")
                return
            
            # Remove the unwanted memberships
            for org in remove_orgs:
                cursor.execute("""
                    DELETE FROM user_organizations
                    WHERE user_id = %s AND organization_id = %s
                """, (admin['id'], org['organization_id']))
                
                print(f"🗑️  Removed membership from '{org['name']}'")
            
            # Commit changes
            conn.commit()
            print(f"✅ {admin['username']} is now single-tenant in '{keep_org['name']}'")
            
            # Verify the fix
            cursor.execute("""
                SELECT uo.organization_id, o.name
                FROM user_organizations uo
                JOIN organization o ON uo.organization_id = o.id
                WHERE uo.user_id = %s
            """, (admin['id'],))
            
            final_memberships = cursor.fetchall()
            print(f"\n🔍 Final verification: {admin['username']} is now member of {len(final_memberships)} organization(s)")
            for membership in final_memberships:
                print(f"   ✅ '{membership['name']}'")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
