#!/usr/bin/env python3
"""
Production Migration: Enhanced RSVP Features
Adds comments, likelihood, and updated_at fields to RSVP table for PostgreSQL
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, '/opt/render/project/src/backend')

from app import app
from models import db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_rsvp_enhancements():
    """Add comments and likelihood fields to RSVP table for PostgreSQL"""
    
    print("🔄 Adding Enhanced RSVP features to production database...")
    
    try:
        with app.app_context():
            # For PostgreSQL, check if columns exist using information_schema
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # Check for existing columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'rsvp' 
                AND column_name IN ('comments', 'likelihood', 'updated_at')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            changes_made = False
            
            # Add comments field if it doesn't exist
            if 'comments' not in existing_columns:
                logger.info("Adding 'comments' column to RSVP table...")
                cursor.execute('ALTER TABLE rsvp ADD COLUMN comments TEXT')
                connection.commit()
                changes_made = True
                print("✅ Added 'comments' column")
            else:
                print("✅ 'comments' column already exists")
            
            # Add likelihood field if it doesn't exist
            if 'likelihood' not in existing_columns:
                logger.info("Adding 'likelihood' column to RSVP table...")
                cursor.execute('ALTER TABLE rsvp ADD COLUMN likelihood INTEGER DEFAULT NULL')
                connection.commit()
                changes_made = True
                print("✅ Added 'likelihood' column")
            else:
                print("✅ 'likelihood' column already exists")
            
            # Add updated_at field if it doesn't exist
            if 'updated_at' not in existing_columns:
                logger.info("Adding 'updated_at' column to RSVP table...")
                cursor.execute('ALTER TABLE rsvp ADD COLUMN updated_at TIMESTAMP DEFAULT NULL')
                connection.commit()
                changes_made = True
                print("✅ Added 'updated_at' column")
            else:
                print("✅ 'updated_at' column already exists")
            
            cursor.close()
            connection.close()
            
            if changes_made:
                print("\n🎉 Enhanced RSVP migration completed successfully!")
                print("\n📋 New RSVP features available:")
                print("   - Comments: Users can add optional comments with their RSVP")
                print("   - Likelihood: 'Maybe' responses can include 1-100% likelihood")
                print("   - Updated tracking: Better timestamp management")
            else:
                print("\n✅ All Enhanced RSVP features already exist - no migration needed")
                
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting Enhanced RSVP Production Migration...")
    success = add_rsvp_enhancements()
    
    if success:
        print("\n✅ Production migration completed successfully!")
        print("\n🎉 Enhanced RSVP features are now live!")
        print("\nNew features:")
        print("   📝 Response Comments")
        print("   📊 Maybe Likelihood Slider (1-100%)")
        print("   ⏰ Enhanced Timestamp Tracking")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
