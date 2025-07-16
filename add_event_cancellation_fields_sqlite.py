#!/usr/bin/env python3
"""
Add event cancellation fields to the Event model
"""

import sqlite3
import os

def add_event_cancellation_fields():
    """Add new event cancellation fields to the Event table"""
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'app.db')
    
    # For production, you might need to check for PostgreSQL instead
    if not os.path.exists(db_path):
        print("Database file not found. This script is for SQLite databases.")
        print("For production PostgreSQL databases, run these SQL commands manually:")
        print("ALTER TABLE event ADD COLUMN is_cancelled BOOLEAN DEFAULT FALSE;")
        print("ALTER TABLE event ADD COLUMN cancelled_at TIMESTAMP NULL;")
        print("ALTER TABLE event ADD COLUMN cancelled_by INTEGER NULL;")
        print("ALTER TABLE event ADD COLUMN cancellation_reason TEXT NULL;")
        print("ALTER TABLE event ADD COLUMN cancellation_notification_sent BOOLEAN DEFAULT FALSE;")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if fields already exist
        print("Checking for existing cancellation fields...")
        cursor.execute("PRAGMA table_info(event)")
        existing_fields = [row[1] for row in cursor.fetchall()]
        
        fields_to_add = [
            ("is_cancelled", "BOOLEAN DEFAULT FALSE"),
            ("cancelled_at", "TIMESTAMP NULL"),
            ("cancelled_by", "INTEGER NULL"),
            ("cancellation_reason", "TEXT NULL"),
            ("cancellation_notification_sent", "BOOLEAN DEFAULT FALSE")
        ]
        
        for field_name, field_def in fields_to_add:
            if field_name not in existing_fields:
                print(f"Adding field: {field_name}")
                cursor.execute(f"ALTER TABLE event ADD COLUMN {field_name} {field_def}")
            else:
                print(f"Field {field_name} already exists, skipping...")
        
        conn.commit()
        print("✅ Event cancellation fields added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding cancellation fields: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_event_cancellation_fields()
