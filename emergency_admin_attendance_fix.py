#!/usr/bin/env python3
"""
Emergency fix for admin attendance columns
This will add the missing columns to the production database
"""

import psycopg2
import os

def fix_admin_attendance_columns():
    """Add missing admin attendance columns to user table"""
    
    # Use Railway database URL
    db_url = 'postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway'
    
    try:
        print("🔧 Connecting to Railway database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("✅ Connected to database")
        
        # Check which columns exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name LIKE '%admin%'
        """)
        
        existing_cols = [row[0] for row in cur.fetchall()]
        print(f"Existing admin columns: {existing_cols}")
        
        # Add missing columns
        columns_to_add = [
            ('email_admin_attendance_reports', 'BOOLEAN DEFAULT TRUE'),
            ('admin_attendance_report_timing', 'INTEGER DEFAULT 120'),
            ('admin_attendance_report_unit', 'VARCHAR(20) DEFAULT \'minutes\''),
            ('email_admin_rsvp_changes', 'BOOLEAN DEFAULT TRUE')
        ]
        
        for col_name, col_def in columns_to_add:
            if col_name not in existing_cols:
                try:
                    cur.execute(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_def}')
                    print(f'✅ Added column: {col_name}')
                except Exception as e:
                    print(f'❌ Error adding {col_name}: {e}')
            else:
                print(f'⚠️  Column {col_name} already exists')
        
        # Create admin attendance tables
        print("\n🔧 Creating admin attendance tables...")
        
        # AdminAttendanceReport table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS admin_attendance_report (
                id SERIAL PRIMARY KEY,
                event_id INTEGER REFERENCES event(id),
                organization_id INTEGER REFERENCES organization(id),
                report_data JSONB,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print('✅ Created/verified admin_attendance_report table')
        
        # AdminRSVPChangeNotification table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS admin_rsvp_change_notification (
                id SERIAL PRIMARY KEY,
                event_id INTEGER REFERENCES event(id),
                user_id INTEGER REFERENCES "user"(id),
                organization_id INTEGER REFERENCES organization(id),
                old_status VARCHAR(20),
                new_status VARCHAR(20),
                change_reason VARCHAR(255),
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print('✅ Created/verified admin_rsvp_change_notification table')
        
        conn.commit()
        print('\n🎉 Admin attendance migration completed successfully!')
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        return False

if __name__ == "__main__":
    print("🚨 Emergency Admin Attendance Database Fix")
    print("=" * 50)
    
    success = fix_admin_attendance_columns()
    
    if success:
        print("\n✅ Database migration completed!")
        print("The login should now work properly.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")
