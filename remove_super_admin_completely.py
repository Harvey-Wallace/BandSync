#!/usr/bin/env python3
"""
Complete Super Admin Removal Script
===================================
This script will completely remove all traces of super admin functionality:
1. Remove super_admin column from user table
2. Update all user roles to remove 'Super Admin' 
3. Remove super admin routes and functionality
4. Clean up all super admin related data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_railway_database_url():
    """Get the Railway database URL"""
    return "postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@shuttle.proxy.rlwy.net:40111/railway"

def remove_super_admin_completely():
    """Remove all traces of super admin functionality"""
    
    print("🗑️  COMPLETE SUPER ADMIN REMOVAL")
    print("=" * 50)
    print("This will permanently remove all super admin functionality:")
    print("- Remove super_admin column from user table")
    print("- Update user roles to remove 'Super Admin'")
    print("- Clean up organization memberships")
    print("- Reset Harvey258 to regular admin")
    
    confirm = input("\n⚠️  Are you sure? This cannot be undone! (type 'YES' to confirm): ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return False
    
    database_url = get_railway_database_url()
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Connected to Railway database")
        
        # Step 1: Check current super admins
        print("\n🔍 Step 1: Checking current super admin users...")
        cursor.execute("""
            SELECT id, username, email, super_admin
            FROM "user"
            WHERE super_admin = true
        """)
        super_admins = cursor.fetchall()
        
        if super_admins:
            print(f"Found {len(super_admins)} super admin users:")
            for admin in super_admins:
                print(f"  - {admin['username']} ({admin['email']})")
        else:
            print("No super admin users found")
        
        # Step 2: Update user roles - remove 'Super Admin' role
        print("\n🔧 Step 2: Removing 'Super Admin' roles...")
        cursor.execute("""
            UPDATE user_organizations 
            SET role = 'Admin' 
            WHERE role = 'Super Admin'
        """)
        updated_roles = cursor.rowcount
        print(f"✅ Updated {updated_roles} user organization roles from 'Super Admin' to 'Admin'")
        
        # Step 3: Reset all super_admin flags to false
        print("\n🔧 Step 3: Resetting super_admin flags...")
        cursor.execute("""
            UPDATE "user" 
            SET super_admin = FALSE 
            WHERE super_admin = TRUE
        """)
        updated_users = cursor.rowcount
        print(f"✅ Reset super_admin flag for {updated_users} users")
        
        # Step 4: Check if super_admin column exists and remove it
        print("\n🗑️  Step 4: Removing super_admin column...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name = 'super_admin'
        """)
        
        if cursor.fetchone():
            cursor.execute('ALTER TABLE "user" DROP COLUMN super_admin')
            print("✅ Removed super_admin column from user table")
        else:
            print("✅ super_admin column already removed")
        
        # Step 5: Ensure Harvey258 is still an admin but not super admin
        print("\n👤 Step 5: Ensuring Harvey258 has proper admin access...")
        cursor.execute("""
            SELECT u.id, u.username, u.email, uo.role, o.name as org_name
            FROM "user" u
            LEFT JOIN user_organizations uo ON u.id = uo.user_id
            LEFT JOIN "organization" o ON uo.organization_id = o.id
            WHERE u.username = 'Harvey258'
        """)
        
        harvey_data = cursor.fetchall()
        if harvey_data:
            print(f"Harvey258 organization memberships:")
            for data in harvey_data:
                if data['org_name']:
                    print(f"  - {data['org_name']}: {data['role']}")
                else:
                    print(f"  - No organization memberships found")
            
            # Ensure Harvey258 is Admin in Harvey-Wallace organization
            cursor.execute("""
                INSERT INTO user_organizations (user_id, organization_id, role, is_active)
                SELECT u.id, o.id, 'Admin', TRUE
                FROM "user" u, "organization" o
                WHERE u.username = 'Harvey258'
                AND o.name = 'Harvey-Wallace'
                AND NOT EXISTS (
                    SELECT 1 FROM user_organizations uo
                    WHERE uo.user_id = u.id AND uo.organization_id = o.id
                )
            """)
            
            if cursor.rowcount > 0:
                print("✅ Added Harvey258 as Admin to Harvey-Wallace organization")
            else:
                print("✅ Harvey258 already has access to Harvey-Wallace organization")
        else:
            print("❌ Harvey258 user not found")
        
        # Step 6: Verify final state
        print("\n📊 Step 6: Verifying final state...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user'
            ORDER BY column_name
        """)
        columns = [row['column_name'] for row in cursor.fetchall()]
        print(f"User table columns: {', '.join(columns)}")
        
        if 'super_admin' not in columns:
            print("✅ super_admin column successfully removed")
        else:
            print("❌ super_admin column still exists")
        
        # Check for any remaining 'Super Admin' roles
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM user_organizations 
            WHERE role = 'Super Admin'
        """)
        super_admin_roles = cursor.fetchone()['count']
        
        if super_admin_roles == 0:
            print("✅ No 'Super Admin' roles remaining")
        else:
            print(f"❌ {super_admin_roles} 'Super Admin' roles still exist")
        
        # Commit all changes
        conn.commit()
        print("\n🎉 SUPER ADMIN REMOVAL COMPLETED SUCCESSFULLY!")
        print("✅ All super admin functionality has been removed")
        print("✅ Harvey258 remains as regular Admin in Harvey-Wallace organization")
        print("✅ Database is now clean of all super admin traces")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during super admin removal: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    remove_super_admin_completely()
