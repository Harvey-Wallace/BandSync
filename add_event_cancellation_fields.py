#!/usr/bin/env python3
"""
Add event cancellation fields to the Event model
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from backend.models import db
from backend.app import create_app

def add_event_cancellation_fields():
    """Add new event cancellation fields to the Event table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if fields already exist
            print("Checking for existing cancellation fields...")
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='event' AND column_name IN ('is_cancelled', 'cancelled_at', 'cancelled_by', 'cancellation_reason', 'cancellation_notification_sent')"))
            existing_fields = [row[0] for row in result.fetchall()]
            
            fields_to_add = [
                ("is_cancelled", "BOOLEAN DEFAULT FALSE"),
                ("cancelled_at", "TIMESTAMP NULL"),
                ("cancelled_by", "INTEGER NULL"),
                ("cancellation_reason", "TEXT NULL"),
                ("cancellation_notification_sent", "BOOLEAN DEFAULT FALSE")
            ]
            
            for field_name, field_def in fields_to_add:
                if field_name not in existing_fields:
                    print(f"Adding field: {field_name}")
                    db.session.execute(text(f"ALTER TABLE event ADD COLUMN {field_name} {field_def}"))
                else:
                    print(f"Field {field_name} already exists, skipping...")
            
            # Add foreign key constraint for cancelled_by if field was added
            if "cancelled_by" not in existing_fields:
                try:
                    print("Adding foreign key constraint for cancelled_by...")
                    db.session.execute(text("ALTER TABLE event ADD CONSTRAINT fk_event_cancelled_by FOREIGN KEY (cancelled_by) REFERENCES user(id)"))
                except Exception as e:
                    print(f"Foreign key constraint may already exist or failed: {e}")
            
            db.session.commit()
            print("✅ Event cancellation fields added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding cancellation fields: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_event_cancellation_fields()
