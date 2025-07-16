#!/usr/bin/env python3
"""
Migration script to add time fields to events table
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import db, Event
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the time fields migration"""
    app = create_app()
    
    with app.app_context():
        try:
            # Read the migration SQL
            migration_file = os.path.join(os.path.dirname(__file__), 'add_time_fields_migration.sql')
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute the migration
            logger.info("Running time fields migration...")
            db.session.execute(text(sql))
            db.session.commit()
            
            logger.info("✅ Time fields migration completed successfully!")
            
            # Verify the columns were added
            logger.info("Verifying new columns...")
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'event' 
                AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
                ORDER BY column_name
            """))
            
            columns = result.fetchall()
            for column in columns:
                logger.info(f"✅ Column '{column[0]}' exists with type '{column[1]}'")
            
            if len(columns) == 3:
                logger.info("✅ All time fields successfully added to events table!")
            else:
                logger.warning(f"⚠️  Only {len(columns)} out of 3 expected columns were found")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_migration()
