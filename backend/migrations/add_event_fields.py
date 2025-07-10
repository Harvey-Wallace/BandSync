"""
Database migration to add enhanced event fields
Run this script to add the new event fields to the database.
"""

import sqlite3
import os

def migrate_events():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'bandsync.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add new columns to the event table
        cursor.execute('ALTER TABLE event ADD COLUMN type VARCHAR(50) DEFAULT "Rehearsal"')
        print("Added 'type' column to event table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'type' already exists")
        else:
            raise
    
    try:
        cursor.execute('ALTER TABLE event ADD COLUMN location_address TEXT')
        print("Added 'location_address' column to event table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'location_address' already exists")
        else:
            raise
    
    try:
        cursor.execute('ALTER TABLE event ADD COLUMN location_lat REAL')
        print("Added 'location_lat' column to event table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'location_lat' already exists")
        else:
            raise
    
    try:
        cursor.execute('ALTER TABLE event ADD COLUMN location_lng REAL')
        print("Added 'location_lng' column to event table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'location_lng' already exists")
        else:
            raise
    
    try:
        cursor.execute('ALTER TABLE event ADD COLUMN location_place_id VARCHAR(255)')
        print("Added 'location_place_id' column to event table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'location_place_id' already exists")
        else:
            raise
    
    # Update existing events to have default type
    cursor.execute('UPDATE event SET type = "Rehearsal" WHERE type IS NULL')
    print("Updated existing events with default type")
    
    conn.commit()
    conn.close()
    print("Event fields migration completed successfully!")

if __name__ == "__main__":
    migrate_events()
