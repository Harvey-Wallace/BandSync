#!/usr/bin/env python3

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clear_database():
    """Clear all data from the Railway database"""
    
    # Database connection details - Railway production database
    DATABASE_URL = "postgresql://postgres:JtcWvnrKgqgvFbfDpaBhXdQivQLrFnhS@postgres.railway.internal:5432/railway"
    
    print("🗑️  Clearing BandSync Database...")
    print("⚠️  WARNING: This will delete ALL data!")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to delete ALL users and organizations? (type 'YES' to confirm): ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Disable foreign key checks temporarily
        cursor.execute("SET session_replication_role = replica;")
        
        # Clear all tables in the correct order (to avoid foreign key issues)
        tables_to_clear = [
            'user_organizations',
            'event_rsvps',
            'custom_field_responses',
            'custom_fields',
            'event_templates',
            'events',
            'email_preferences',
            'organization_profile',
            'user',
            'organization'
        ]
        
        print("\n🧹 Clearing tables...")
        
        for table in tables_to_clear:
            try:
                cursor.execute(f'DELETE FROM "{table}";')
                rows_deleted = cursor.rowcount
                print(f"   ✅ Cleared {table}: {rows_deleted} rows deleted")
            except Exception as e:
                print(f"   ⚠️  Warning clearing {table}: {e}")
        
        # Reset sequences (auto-increment counters)
        print("\n🔄 Resetting sequences...")
        sequences_to_reset = [
            'user_id_seq',
            'organization_id_seq',
            'events_id_seq',
            'event_templates_id_seq',
            'custom_fields_id_seq',
            'custom_field_responses_id_seq'
        ]
        
        for seq in sequences_to_reset:
            try:
                cursor.execute(f'ALTER SEQUENCE "{seq}" RESTART WITH 1;')
                print(f"   ✅ Reset sequence {seq}")
            except Exception as e:
                print(f"   ⚠️  Warning resetting {seq}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Database cleared successfully!")
        print("🎉 You can now start fresh with new users and organizations")
        
        # Verify the cleanup
        print("\n🔍 Verifying cleanup...")
        verification_tables = ['user', 'organization', 'events']
        for table in verification_tables:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} rows remaining")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

if __name__ == "__main__":
    success = clear_database()
    if success:
        print("\n🚀 Database is now clean and ready for fresh setup!")
        print("You can now:")
        print("1. Register new users through the web interface")
        print("2. Create new organizations")
        print("3. Set up super admin users")
    else:
        print("\n❌ Database clearing failed. Please check the error messages above.")
