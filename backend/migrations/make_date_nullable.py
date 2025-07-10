#!/usr/bin/env python3
"""
Make event date field nullable for templates
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Make the date column nullable
            with db.engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE event 
                    ALTER COLUMN date DROP NOT NULL;
                """))
                
                conn.commit()
                print("✓ Made event.date column nullable for templates")
                print("✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            raise

if __name__ == "__main__":
    migrate()
