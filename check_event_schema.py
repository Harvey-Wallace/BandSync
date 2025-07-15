#!/usr/bin/env python3
"""
Check database schema for event table
"""

import psycopg2

# Railway database connection
external_db_url = "postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway"

def check_event_table_schema():
    """Check the event table schema"""
    try:
        print("🔍 Checking event table schema...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # Check columns in event table
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'event'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print(f"\n📊 Event table has {len(columns)} columns:")
        
        for col_name, data_type, nullable, default in columns:
            print(f"  - {col_name}: {data_type} {'(nullable)' if nullable == 'YES' else ''} {f'default: {default}' if default else ''}")
        
        # Check if location_address column exists
        location_address_exists = any(col[0] == 'location_address' for col in columns)
        print(f"\n🔍 location_address column exists: {'✅' if location_address_exists else '❌'}")
        
        if not location_address_exists:
            print("\n⚠️  Missing location_address column. This is causing the 500 error!")
            print("Need to add missing columns to fix the issue.")
            
            # Check what location-related columns exist
            location_cols = [col for col in columns if 'location' in col[0].lower()]
            print(f"\n📍 Existing location columns: {[col[0] for col in location_cols]}")
            
            # Let's add the missing columns
            print("\n🔧 Adding missing columns...")
            
            missing_columns = [
                "location_address TEXT",
                "location_lat DOUBLE PRECISION",
                "location_lng DOUBLE PRECISION",
                "location_place_id VARCHAR(255)",
                "category_id INTEGER",
                "is_recurring BOOLEAN DEFAULT FALSE",
                "recurring_pattern VARCHAR(20)",
                "recurring_interval INTEGER",
                "recurring_end_date DATE",
                "recurring_count INTEGER",
                "parent_event_id INTEGER",
                "is_template BOOLEAN DEFAULT FALSE",
                "template_name VARCHAR(255)",
                "send_reminders BOOLEAN DEFAULT TRUE",
                "reminder_days_before INTEGER DEFAULT 1",
                "created_by INTEGER",
                "end_date DATE"
            ]
            
            for column_def in missing_columns:
                col_name = column_def.split()[0]
                # Check if column already exists
                if not any(col[0] == col_name for col in columns):
                    try:
                        cur.execute(f"ALTER TABLE event ADD COLUMN {column_def};")
                        print(f"  ✅ Added {col_name}")
                    except Exception as e:
                        print(f"  ❌ Failed to add {col_name}: {e}")
                else:
                    print(f"  ⏭️  {col_name} already exists")
            
            conn.commit()
            print("\n✅ Database schema updated!")
        
        conn.close()
        return location_address_exists
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    check_event_table_schema()
