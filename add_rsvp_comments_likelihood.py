#!/usr/bin/env python3
"""
Migration: Add comments and likelihood fields to RSVP table
"""

import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

from app import app, db
from models import RSVP
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_rsvp_enhancements():
    """Add comments and likelihood fields to RSVP table"""
    
    print("🔄 Adding RSVP enhancements (comments and likelihood)...")
    
    try:
        with app.app_context():
            # For SQLite, we need to check columns differently
            try:
                # Try to select from the column - if it fails, column doesn't exist
                db.session.execute(db.text("SELECT comments FROM rsvp LIMIT 1"))
                print("✅ 'comments' column already exists")
                comments_exists = True
            except Exception:
                comments_exists = False
            
            try:
                db.session.execute(db.text("SELECT likelihood FROM rsvp LIMIT 1"))
                print("✅ 'likelihood' column already exists")
                likelihood_exists = True
            except Exception:
                likelihood_exists = False
            
            try:
                db.session.execute(db.text("SELECT updated_at FROM rsvp LIMIT 1"))
                print("✅ 'updated_at' column already exists")
                updated_at_exists = True
            except Exception:
                updated_at_exists = False
            
            changes_made = False
            
            # Add comments field if it doesn't exist
            if not comments_exists:
                logger.info("Adding 'comments' column to RSVP table...")
                db.session.execute(db.text('ALTER TABLE rsvp ADD COLUMN comments TEXT'))
                db.session.commit()
                changes_made = True
                print("✅ Added 'comments' column")
            
            # Add likelihood field if it doesn't exist
            if not likelihood_exists:
                logger.info("Adding 'likelihood' column to RSVP table...")
                # likelihood is 1-100 for "Maybe" responses (percentage likelihood of attending)
                db.session.execute(db.text('ALTER TABLE rsvp ADD COLUMN likelihood INTEGER DEFAULT NULL'))
                db.session.commit()
                changes_made = True
                print("✅ Added 'likelihood' column")
            
            # Add updated_at field if it doesn't exist
            if not updated_at_exists:
                logger.info("Adding 'updated_at' column to RSVP table...")
                db.session.execute(db.text('ALTER TABLE rsvp ADD COLUMN updated_at DATETIME DEFAULT NULL'))
                db.session.commit()
                changes_made = True
                print("✅ Added 'updated_at' column")
            
            if changes_made:
                print("\n🎉 RSVP enhancement migration completed successfully!")
                print("\n📋 New RSVP features available:")
                print("   - Comments: Users can add optional comments with their RSVP")
                print("   - Likelihood: 'Maybe' responses can include 1-100% likelihood")
                print("   - Updated tracking: Better timestamp management")
            else:
                print("\n✅ All RSVP enhancements already exist - no migration needed")
                
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = add_rsvp_enhancements()
    if success:
        print("\n🚀 Ready to implement enhanced RSVP features!")
        print("\nNext steps:")
        print("1. Update RSVP model in models.py")
        print("2. Update RSVP API endpoints")
        print("3. Update frontend RSVP components")
    else:
        print("\n❌ Migration failed - please check logs")
        sys.exit(1)
