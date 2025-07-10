"""
Database migration for PostgreSQL to add enhanced event fields
Run this script to add the new event fields to the database.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_events():
    # Get database connection info
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/bandsync')
    
    # Parse the DATABASE_URL to get connection parameters
    if database_url.startswith('postgresql://'):
        parts = database_url.replace('postgresql://', '').split('/')
        host_port = parts[0]
        dbname = parts[1] if len(parts) > 1 else 'bandsync'
        
        if '@' in host_port:
            user_pass, host_port = host_port.split('@')
            if ':' in user_pass:
                user, password = user_pass.split(':')
            else:
                user = user_pass
                password = None
        else:
            user = None
            password = None
            
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port or 'localhost'
            port = '5432'
    else:
        # Simple case for localhost
        host = 'localhost'
        port = '5432'
        dbname = 'bandsync'
        user = None
        password = None
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        print(f"Connected to PostgreSQL database: {dbname}")
        
        # Add new columns to the event table
        try:
            cursor.execute('ALTER TABLE event ADD COLUMN type VARCHAR(50) DEFAULT \'Rehearsal\'')
            print("Added 'type' column to event table")
        except psycopg2.errors.DuplicateColumn:
            print("Column 'type' already exists")
        
        try:
            cursor.execute('ALTER TABLE event ADD COLUMN location_address TEXT')
            print("Added 'location_address' column to event table")
        except psycopg2.errors.DuplicateColumn:
            print("Column 'location_address' already exists")
        
        try:
            cursor.execute('ALTER TABLE event ADD COLUMN location_lat REAL')
            print("Added 'location_lat' column to event table")
        except psycopg2.errors.DuplicateColumn:
            print("Column 'location_lat' already exists")
        
        try:
            cursor.execute('ALTER TABLE event ADD COLUMN location_lng REAL')
            print("Added 'location_lng' column to event table")
        except psycopg2.errors.DuplicateColumn:
            print("Column 'location_lng' already exists")
        
        try:
            cursor.execute('ALTER TABLE event ADD COLUMN location_place_id VARCHAR(255)')
            print("Added 'location_place_id' column to event table")
        except psycopg2.errors.DuplicateColumn:
            print("Column 'location_place_id' already exists")
        
        # Update existing events to have default type
        cursor.execute('UPDATE event SET type = \'Rehearsal\' WHERE type IS NULL')
        print("Updated existing events with default type")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Event fields migration completed successfully!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate_events()
