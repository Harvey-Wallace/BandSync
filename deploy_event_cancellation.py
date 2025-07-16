#!/usr/bin/env python3
"""
Deploy event cancellation features to Railway
"""

import os
import subprocess
import sys

def run_railway_migration():
    """Run the database migration on Railway"""
    print("🚀 Deploying event cancellation features to Railway...")
    
    # Run the migration using Railway's environment
    migration_commands = [
        "ALTER TABLE event ADD COLUMN is_cancelled BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE event ADD COLUMN cancelled_at TIMESTAMP NULL;", 
        "ALTER TABLE event ADD COLUMN cancelled_by INTEGER NULL;",
        "ALTER TABLE event ADD COLUMN cancellation_reason TEXT NULL;",
        "ALTER TABLE event ADD COLUMN cancellation_notification_sent BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE event ADD CONSTRAINT fk_event_cancelled_by FOREIGN KEY (cancelled_by) REFERENCES \"user\"(id);"
    ]
    
    print("📋 Migration commands to run on Railway:")
    for cmd in migration_commands:
        print(f"  {cmd}")
    
    print("\n✅ Migration script prepared!")
    print("🔧 To apply these changes:")
    print("1. Connect to your Railway PostgreSQL database")
    print("2. Run each SQL command above")
    print("3. Or use the Railway CLI to run the migration")
    
    # Also deploy the code changes
    print("\n🚀 Deploying code changes...")
    try:
        # Git add all changes
        subprocess.run(["git", "add", "."], check=True)
        
        # Git commit
        subprocess.run([
            "git", "commit", "-m", 
            "Implement comprehensive event cancellation system\n\n" +
            "✨ Features:\n" +
            "- Event cancellation with reason and timestamp\n" +
            "- Optional email notifications to RSVP'd members\n" +
            "- Cancellation display on dashboard and events page\n" +
            "- Disabled RSVP for cancelled events\n" +
            "- Admin cancel button with modal interface\n" +
            "- Database migration for cancellation fields\n" +
            "- Email template for cancellation notifications\n\n" +
            "🗄️ Database changes:\n" +
            "- Added is_cancelled, cancelled_at, cancelled_by fields\n" +
            "- Added cancellation_reason, cancellation_notification_sent\n" +
            "- Added foreign key constraint for cancelled_by\n\n" +
            "🎨 UI improvements:\n" +
            "- Red 'CANCELLED' badge on event cards\n" +
            "- Cancellation details in expanded view\n" +
            "- Disabled RSVP buttons for cancelled events\n" +
            "- Cancel event modal with reason input\n" +
            "- Notification email option checkbox"
        ], check=True)
        
        # Git push
        subprocess.run(["git", "push"], check=True)
        
        print("✅ Code changes deployed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error deploying code changes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_railway_migration()
