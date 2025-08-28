#!/usr/bin/env python3
"""
Simple Enhanced RSVP Migration for Railway
"""
import os
import sys
sys.path.insert(0, '/app')

from app import app
from models import db

print("🔄 Adding Enhanced RSVP features...")

with app.app_context():
    try:
        # Check if columns exist
        result = db.session.execute(db.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'rsvp' 
            AND column_name IN ('comments', 'likelihood', 'updated_at')
        """))
        existing = [row[0] for row in result.fetchall()]
        print(f"Existing columns: {existing}")
        
        if 'comments' not in existing:
            db.session.execute(db.text('ALTER TABLE rsvp ADD COLUMN comments TEXT'))
            print("✅ Added comments column")
        
        if 'likelihood' not in existing:
            db.session.execute(db.text('ALTER TABLE rsvp ADD COLUMN likelihood INTEGER DEFAULT NULL'))
            print("✅ Added likelihood column")
            
        if 'updated_at' not in existing:
            db.session.execute(db.text('ALTER TABLE rsvp ADD COLUMN updated_at TIMESTAMP DEFAULT NULL'))
            print("✅ Added updated_at column")
            
        db.session.commit()
        print("🎉 Enhanced RSVP migration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
