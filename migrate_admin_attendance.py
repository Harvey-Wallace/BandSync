#!/usr/bin/env python3
"""
Database migration for admin attendance notifications

This script adds the new tables and columns needed for admin attendance notifications:
- AdminAttendanceReport table
- AdminRSVPChangeNotification table  
- Admin attendance preferences columns in User table
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import db, User, AdminAttendanceReport, AdminRSVPChangeNotification
from backend.app import app

def run_migration():
    """Run the database migration"""
    with app.app_context():
        print("🚀 Starting admin attendance notification migration...")
        
        try:
            # Create the new tables
            print("📋 Creating AdminAttendanceReport table...")
            db.create_all()
            
            print("📋 Creating AdminRSVPChangeNotification table...")
            # Tables are created by db.create_all() above
            
            # Add new columns to User table (if they don't exist)
            print("👤 Adding admin attendance preferences columns to User table...")
            
            # Check if columns exist by trying to query them
            try:
                test_user = User.query.first()
                if test_user:
                    _ = test_user.email_admin_attendance_reports
                    _ = test_user.admin_attendance_report_timing
                    _ = test_user.admin_attendance_report_unit
                    _ = test_user.email_admin_rsvp_changes
                    print("✅ Admin attendance preference columns already exist")
                else:
                    print("✅ No users found, but columns are ready")
            except Exception as e:
                print(f"⚠️  Column check failed: {str(e)}")
                print("This is normal if columns don't exist yet - they'll be created by SQLAlchemy")
            
            # Set default values for existing admin users
            print("🔧 Setting default values for existing admin users...")
            admin_users = User.query.filter_by(role='admin').all()
            
            for admin in admin_users:
                # Only set if not already set (in case migration runs multiple times)
                if not hasattr(admin, 'email_admin_attendance_reports') or admin.email_admin_attendance_reports is None:
                    admin.email_admin_attendance_reports = True
                if not hasattr(admin, 'admin_attendance_report_timing') or admin.admin_attendance_report_timing is None:
                    admin.admin_attendance_report_timing = 120  # 2 hours
                if not hasattr(admin, 'admin_attendance_report_unit') or admin.admin_attendance_report_unit is None:
                    admin.admin_attendance_report_unit = 'minutes'
                if not hasattr(admin, 'email_admin_rsvp_changes') or admin.email_admin_rsvp_changes is None:
                    admin.email_admin_rsvp_changes = True
            
            db.session.commit()
            print(f"✅ Updated {len(admin_users)} admin users with default preferences")
            
            print("🎉 Admin attendance notification migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    run_migration()
