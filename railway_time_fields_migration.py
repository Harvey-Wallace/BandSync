#!/usr/bin/env python3
"""
Railway migration script to add time fields to events table
This script should be run in the Railway environment where the database URL is available
"""

import os
import sys
import logging
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_railway_migration():
    """Run the time fields migration in Railway environment"""
    logger.info("🚀 Starting Railway time fields migration...")
    
    try:
        # Import after path setup
        from app import create_app
        from models import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            logger.info("📦 Database connection established")
            
            # Read the migration SQL
            migration_file = os.path.join(os.path.dirname(__file__), 'add_time_fields_migration.sql')
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            logger.info("🔄 Executing time fields migration...")
            
            # Execute the migration
            db.session.execute(text(sql))
            db.session.commit()
            
            logger.info("✅ Time fields migration completed successfully!")
            
            # Verify the columns were added
            logger.info("🔍 Verifying new columns...")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'event' 
                AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
                ORDER BY column_name
            """))
            
            columns = result.fetchall()
            logger.info(f"📊 Found {len(columns)} time columns:")
            
            for column in columns:
                logger.info(f"  ✅ {column[0]} ({column[1]}, nullable: {column[2]})")
            
            if len(columns) == 3:
                logger.info("🎉 All time fields successfully added to events table!")
                
                # Test creating a basic event with time fields
                logger.info("🧪 Testing time fields functionality...")
                
                test_query = text("""
                    SELECT COUNT(*) as event_count 
                    FROM event 
                    WHERE arrive_by_time IS NOT NULL 
                    OR start_time IS NOT NULL 
                    OR end_time IS NOT NULL
                """)
                
                result = db.session.execute(test_query)
                count = result.scalar()
                logger.info(f"📈 Found {count} events with time fields populated")
                
                return True
            else:
                logger.warning(f"⚠️  Only {len(columns)} out of 3 expected columns were found")
                return False
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    success = run_railway_migration()
    if success:
        logger.info("🎊 Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Migration failed!")
        sys.exit(1)
