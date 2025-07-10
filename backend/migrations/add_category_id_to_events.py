#!/usr/bin/env python3
"""
Add category_id column to events table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import EventCategory
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Add the category_id column
            with db.engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE event 
                    ADD COLUMN category_id INTEGER;
                """))
                
                # Add foreign key constraint
                conn.execute(text("""
                    ALTER TABLE event 
                    ADD CONSTRAINT fk_event_category 
                    FOREIGN KEY (category_id) REFERENCES event_category(id);
                """))
                
                print("✓ Added category_id column to event table")
                
                # Set default category for existing events
                # Get the first category for each organization
                result = conn.execute(text("""
                    UPDATE event 
                    SET category_id = (
                        SELECT ec.id 
                        FROM event_category ec 
                        WHERE ec.organization_id = event.organization_id 
                        ORDER BY ec.id 
                        LIMIT 1
                    )
                    WHERE category_id IS NULL;
                """))
                
                print(f"✓ Updated {result.rowcount} existing events with default categories")
                
                conn.commit()
                print("✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            raise

if __name__ == "__main__":
    migrate()
