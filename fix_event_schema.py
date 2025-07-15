#!/usr/bin/env python3
"""
Fix the event table schema to match the model expectations
"""

import psycopg2

# Railway database connection
external_db_url = "postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway"

def fix_event_schema():
    """Fix the event table schema to match the model"""
    try:
        print("🔧 Fixing event table schema...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # First, let's check if there are any events with data
        cur.execute("SELECT COUNT(*) FROM event;")
        event_count = cur.fetchone()[0]
        print(f"📊 Found {event_count} events in the table")
        
        # If there are events, we need to migrate the data
        if event_count > 0:
            print("⚠️  Migrating existing event data...")
            
            # First, add a temporary column for the combined datetime
            cur.execute("ALTER TABLE event ADD COLUMN temp_datetime TIMESTAMP;")
            
            # Combine date and time into the temporary column
            cur.execute("""
                UPDATE event 
                SET temp_datetime = date + time
                WHERE date IS NOT NULL AND time IS NOT NULL;
            """)
            
            # For events with only date, use midnight
            cur.execute("""
                UPDATE event 
                SET temp_datetime = date + TIME '00:00:00'
                WHERE date IS NOT NULL AND time IS NULL;
            """)
            
            print("✅ Data migrated to temporary column")
        
        # Drop the old time column
        cur.execute("ALTER TABLE event DROP COLUMN time;")
        print("✅ Dropped old 'time' column")
        
        # Change the date column to timestamp
        cur.execute("ALTER TABLE event ALTER COLUMN date TYPE TIMESTAMP USING date::timestamp;")
        print("✅ Changed 'date' column to TIMESTAMP")
        
        # If we had data, copy it back from the temporary column
        if event_count > 0:
            cur.execute("UPDATE event SET date = temp_datetime WHERE temp_datetime IS NOT NULL;")
            cur.execute("ALTER TABLE event DROP COLUMN temp_datetime;")
            print("✅ Restored data from temporary column")
        
        # Also fix the end_date column
        cur.execute("ALTER TABLE event ALTER COLUMN end_date TYPE TIMESTAMP USING end_date::timestamp;")
        print("✅ Changed 'end_date' column to TIMESTAMP")
        
        # Also fix the recurring_end_date column
        cur.execute("ALTER TABLE event ALTER COLUMN recurring_end_date TYPE TIMESTAMP USING recurring_end_date::timestamp;")
        print("✅ Changed 'recurring_end_date' column to TIMESTAMP")
        
        conn.commit()
        print("✅ Schema migration completed successfully!")
        
        # Verify the changes
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'event' AND column_name IN ('date', 'end_date', 'recurring_end_date')
            ORDER BY column_name;
        """)
        
        columns = cur.fetchall()
        print(f"\n📊 Updated column types:")
        for col_name, data_type in columns:
            print(f"  {col_name}: {data_type}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    fix_event_schema()
