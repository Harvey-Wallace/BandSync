#!/usr/bin/env python3
"""
Add RSVP visibility setting to Organization model
This migration adds the members_can_view_rsvp_status field to the organization table
"""

import os
import sys
import sqlite3
from datetime import datetime

def run_migration():
    """Add the members_can_view_rsvp_status column to the organization table"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Looking for alternative database locations...")
        
        # Try alternative paths
        alt_paths = [
            os.path.join(os.path.dirname(__file__), 'instance', 'app.db'),
            os.path.join(os.path.dirname(__file__), 'app.db'),
            'instance/app.db',
            'backend/instance/app.db'
        ]
        
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                db_path = alt_path
                print(f"Found database at: {db_path}")
                break
        else:
            print("Database file not found in any expected location")
            return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking current organization table structure...")
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(organization)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'members_can_view_rsvp_status' in columns:
            print("✓ Column 'members_can_view_rsvp_status' already exists in organization table")
            conn.close()
            return True
        
        print("Adding 'members_can_view_rsvp_status' column to organization table...")
        
        # Add the new column with default value True (existing behavior)
        cursor.execute("""
            ALTER TABLE organization 
            ADD COLUMN members_can_view_rsvp_status BOOLEAN DEFAULT 1
        """)
        
        # Update existing organizations to have the default value
        cursor.execute("""
            UPDATE organization 
            SET members_can_view_rsvp_status = 1 
            WHERE members_can_view_rsvp_status IS NULL
        """)
        
        # Commit changes
        conn.commit()
        
        print("✓ Successfully added 'members_can_view_rsvp_status' column to organization table")
        print("✓ All existing organizations set to allow member RSVP visibility (default behavior)")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(organization)")
        columns = cursor.fetchall()
        
        print("\nUpdated organization table structure:")
        for col in columns:
            if col[1] == 'members_can_view_rsvp_status':
                print(f"  ✓ {col[1]} - {col[2]} (default: {col[4]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def verify_migration():
    """Verify that the migration was successful"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        # Try alternative paths
        alt_paths = [
            os.path.join(os.path.dirname(__file__), 'instance', 'app.db'),
            os.path.join(os.path.dirname(__file__), 'app.db'),
            'instance/app.db',
            'backend/instance/app.db'
        ]
        
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                db_path = alt_path
                break
        else:
            print("Database file not found for verification")
            return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists and has correct values
        cursor.execute("""
            SELECT COUNT(*) as org_count,
                   SUM(CASE WHEN members_can_view_rsvp_status = 1 THEN 1 ELSE 0 END) as visible_count
            FROM organization
        """)
        
        result = cursor.fetchone()
        org_count, visible_count = result
        
        print(f"\nMigration Verification:")
        print(f"  Total organizations: {org_count}")
        print(f"  Organizations with RSVP visibility enabled: {visible_count}")
        print(f"  Organizations with RSVP visibility disabled: {org_count - visible_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("RSVP Visibility Setting Migration")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Run migration
    success = run_migration()
    
    if success:
        print()
        # Verify migration
        verify_migration()
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)
        sys.exit(1)
