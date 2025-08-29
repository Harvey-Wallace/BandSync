#!/usr/bin/env python3
"""
Phase 1 Feature 2: Advanced Event Types & Templates
Database Migration for Event Templates
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app
from models import db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_event_template_features():
    """Add Event Template table and related enhancements"""
    
    print("🔄 Adding Advanced Event Types & Templates features...")
    
    try:
        with app.app_context():
            # For SQLite compatibility - check if columns exist by trying to select
            try:
                # Check if event_template table exists
                db.session.execute(db.text("SELECT COUNT(*) FROM event_template LIMIT 1"))
                print("✅ 'event_template' table already exists")
                template_table_exists = True
            except Exception:
                template_table_exists = False
            
            changes_made = False
            
            # Create event_template table if it doesn't exist
            if not template_table_exists:
                logger.info("Creating 'event_template' table...")
                db.session.execute(db.text('''
                    CREATE TABLE event_template (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(120) NOT NULL,
                        description TEXT,
                        category_id INTEGER,
                        organization_id INTEGER NOT NULL,
                        
                        -- Default values for events created from this template
                        default_duration_hours INTEGER DEFAULT 2,
                        default_location_address TEXT,
                        default_location_lat REAL,
                        default_location_lng REAL,
                        default_location_place_id VARCHAR(255),
                        
                        -- Time defaults
                        default_arrive_by_time TIME,
                        default_start_time TIME,
                        default_end_time TIME,
                        
                        -- RSVP defaults
                        default_rsvp_required BOOLEAN DEFAULT TRUE,
                        default_rsvp_deadline_hours INTEGER DEFAULT 24,
                        
                        -- Notification defaults
                        default_reminder_hours INTEGER DEFAULT 24,
                        default_send_invitations BOOLEAN DEFAULT TRUE,
                        
                        -- Template metadata
                        is_active BOOLEAN DEFAULT TRUE,
                        is_organization_default BOOLEAN DEFAULT FALSE,
                        use_count INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        
                        FOREIGN KEY (category_id) REFERENCES event_category(id),
                        FOREIGN KEY (organization_id) REFERENCES organization(id)
                    )
                '''))
                db.session.commit()
                changes_made = True
                print("✅ Created 'event_template' table")
            
            # Add template_id to event table if it doesn't exist
            try:
                db.session.execute(db.text("SELECT template_id FROM event LIMIT 1"))
                print("✅ 'template_id' column already exists in event table")
                template_columns_exist = True
            except Exception:
                template_columns_exist = False
            
            if not template_columns_exist:
                logger.info("Adding 'template_id' column to event table...")
                db.session.execute(db.text('ALTER TABLE event ADD COLUMN template_id INTEGER'))
                
                # Check if is_template column exists separately
                try:
                    db.session.execute(db.text("SELECT is_template FROM event LIMIT 1"))
                    print("✅ 'is_template' column already exists")
                except Exception:
                    db.session.execute(db.text('ALTER TABLE event ADD COLUMN is_template BOOLEAN DEFAULT FALSE'))
                    print("✅ Added 'is_template' column")
                
                db.session.commit()
                changes_made = True
                print("✅ Added template columns to event table")
            
            # Add enhanced category features to event_category table
            try:
                db.session.execute(db.text("SELECT has_default_template FROM event_category LIMIT 1"))
                print("✅ Enhanced category columns already exist")
            except Exception:
                logger.info("Adding enhanced category features...")
                db.session.execute(db.text('ALTER TABLE event_category ADD COLUMN has_default_template BOOLEAN DEFAULT FALSE'))
                db.session.execute(db.text('ALTER TABLE event_category ADD COLUMN default_template_id INTEGER'))
                db.session.execute(db.text('ALTER TABLE event_category ADD COLUMN template_count INTEGER DEFAULT 0'))
                db.session.commit()
                changes_made = True
                print("✅ Added enhanced category features")
            
            if changes_made:
                print("\\n🎉 Event Templates migration completed successfully!")
                print("\\n📋 New Event Template features available:")
                print("   - Event Templates: Create reusable event templates")
                print("   - Smart Defaults: Pre-filled location, timing, and settings")
                print("   - Category Templates: Templates linked to event categories")
                print("   - Template Management: Create, edit, and track template usage")
            else:
                print("\\n✅ All Event Template features already exist - no migration needed")
                
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting Event Templates Migration...")
    success = add_event_template_features()
    
    if success:
        print("\\n✅ Migration completed successfully!")
        print("\\n🎉 Advanced Event Types & Templates features are ready!")
        print("\\nNext steps:")
        print("1. Update Event model to include template relationships")
        print("2. Create EventTemplate API endpoints") 
        print("3. Build Template Management UI")
        print("4. Create default templates for common event types")
    else:
        print("\\n❌ Migration failed!")
        sys.exit(1)
