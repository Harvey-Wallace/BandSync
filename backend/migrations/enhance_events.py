#!/usr/bin/env python3
"""
Migration script to enhance Event model with recurring events, templates, and notifications
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Event
from sqlalchemy import text

def run_migration():
    with app.app_context():
        print("Starting Event enhancement migration...")
        
        # Get current Event table columns
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('event')]
        print(f"Current Event columns: {columns}")
        
        # Add new columns if they don't exist
        new_columns = [
            ('end_date', 'TIMESTAMP NULL'),
            ('is_recurring', 'BOOLEAN DEFAULT FALSE'),
            ('recurring_pattern', 'VARCHAR(50) NULL'),
            ('recurring_interval', 'INTEGER DEFAULT 1'),
            ('recurring_end_date', 'TIMESTAMP NULL'),
            ('recurring_count', 'INTEGER NULL'),
            ('parent_event_id', 'INTEGER NULL'),
            ('is_template', 'BOOLEAN DEFAULT FALSE'),
            ('template_name', 'VARCHAR(120) NULL'),
            ('send_reminders', 'BOOLEAN DEFAULT TRUE'),
            ('reminder_days_before', 'INTEGER DEFAULT 1'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('created_by', 'INTEGER NULL')
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                try:
                    db.session.execute(text(f"ALTER TABLE event ADD COLUMN {column_name} {column_def}"))
                    db.session.commit()  # Commit each column addition separately
                    print(f"Added column: {column_name}")
                except Exception as e:
                    db.session.rollback()  # Rollback failed addition
                    print(f"Error adding column {column_name}: {e}")
        
        # Add foreign key constraints
        try:
            # Check if foreign key for parent_event_id exists
            inspector = db.inspect(db.engine)  # Refresh inspector
            fks = inspector.get_foreign_keys('event')
            parent_fk_exists = any(fk['constrained_columns'] == ['parent_event_id'] for fk in fks)
            
            if not parent_fk_exists and 'parent_event_id' in [col['name'] for col in inspector.get_columns('event')]:
                db.session.execute(text("ALTER TABLE event ADD CONSTRAINT fk_event_parent FOREIGN KEY (parent_event_id) REFERENCES event(id)"))
                db.session.commit()
                print("Added foreign key constraint for parent_event_id")
        except Exception as e:
            db.session.rollback()
            print(f"Note: Foreign key constraint for parent_event_id failed: {e}")
        
        try:
            # Check if foreign key for created_by exists  
            inspector = db.inspect(db.engine)  # Refresh inspector
            fks = inspector.get_foreign_keys('event')
            created_by_fk_exists = any(fk['constrained_columns'] == ['created_by'] for fk in fks)
            
            if not created_by_fk_exists and 'created_by' in [col['name'] for col in inspector.get_columns('event')]:
                db.session.execute(text('ALTER TABLE event ADD CONSTRAINT fk_event_creator FOREIGN KEY (created_by) REFERENCES "user"(id)'))
                db.session.commit()
                print("Added foreign key constraint for created_by")
        except Exception as e:
            db.session.rollback()
            print(f"Note: Foreign key constraint for created_by failed: {e}")
        
        print("Event enhancement migration completed successfully!")

if __name__ == '__main__':
    run_migration()
