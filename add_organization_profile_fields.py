#!/usr/bin/env python3
"""
Migration script to add profile fields to the Organization table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def run_migration():
    """Add new profile fields to the organization table"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Create database engine
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'organization' 
                AND column_name IN ('rehearsal_address', 'contact_phone', 'contact_email', 'website', 'facebook_url', 'instagram_url', 'twitter_url', 'tiktok_url', 'created_at')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Add missing columns
            columns_to_add = [
                ('rehearsal_address', 'TEXT'),
                ('contact_phone', 'VARCHAR(20)'),
                ('contact_email', 'VARCHAR(120)'),
                ('website', 'VARCHAR(255)'),
                ('facebook_url', 'VARCHAR(255)'),
                ('instagram_url', 'VARCHAR(255)'),
                ('twitter_url', 'VARCHAR(255)'),
                ('tiktok_url', 'VARCHAR(255)'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    print(f"Adding column: {column_name}")
                    conn.execute(text(f"ALTER TABLE organization ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                else:
                    print(f"Column {column_name} already exists, skipping")
            
            print("Migration completed successfully!")
            
    except OperationalError as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
