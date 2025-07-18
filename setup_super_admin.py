#!/usr/bin/env python3
"""
Super Admin Setup Script
Creates Super Admin functionality and assigns it to a specific user
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/Users/robertharvey/Documents/GitHub/BandSync/backend')

from models import db, User, Organization, UserOrganization
from app import create_app

def setup_super_admin():
    """Set up Super Admin functionality"""
    
    print("🔧 Setting up Super Admin functionality...")
    print("=" * 60)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # First, let's check if we need to add super_admin column to users table
            print("📊 Checking database schema...")
            
            # Check if super_admin column exists
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'super_admin' not in columns:
                print("➕ Adding super_admin column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN super_admin BOOLEAN DEFAULT FALSE"))
                db.session.commit()
                print("✅ super_admin column added successfully")
            else:
                print("✅ super_admin column already exists")
            
            # Now let's find the user to make Super Admin
            # You can specify your username here
            super_admin_username = input("Enter the username to make Super Admin (or press Enter for 'Harvey258'): ").strip()
            if not super_admin_username:
                super_admin_username = "Harvey258"
            
            user = User.query.filter_by(username=super_admin_username).first()
            
            if not user:
                print(f"❌ User '{super_admin_username}' not found!")
                print("Available users:")
                all_users = User.query.all()
                for u in all_users:
                    print(f"   - {u.username} ({u.email})")
                return
            
            # Set user as Super Admin
            print(f"👑 Setting {user.username} as Super Admin...")
            user.super_admin = True
            user.role = 'Super Admin'  # Update role as well
            db.session.commit()
            
            # Get all organizations
            organizations = Organization.query.all()
            print(f"🏢 Found {len(organizations)} organizations")
            
            # Add Super Admin to all organizations
            for org in organizations:
                # Check if user is already in this organization
                existing = UserOrganization.query.filter_by(
                    user_id=user.id,
                    organization_id=org.id
                ).first()
                
                if not existing:
                    print(f"   ➕ Adding to '{org.name}'...")
                    user_org = UserOrganization(
                        user_id=user.id,
                        organization_id=org.id,
                        role='Super Admin',
                        is_active=True
                    )
                    db.session.add(user_org)
                else:
                    print(f"   ✅ Already in '{org.name}' - updating role to Super Admin...")
                    existing.role = 'Super Admin'
                    existing.is_active = True
            
            db.session.commit()
            
            print(f"\n🎉 Super Admin setup complete!")
            print(f"👑 {user.username} is now a Super Admin with access to all organizations")
            print(f"📧 Email: {user.email}")
            print(f"🏢 Access to {len(organizations)} organizations")
            
            # Show organizations
            print(f"\n📋 Organizations with Super Admin access:")
            for org in organizations:
                print(f"   - {org.name}")
            
        except Exception as e:
            print(f"❌ Error setting up Super Admin: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    setup_super_admin()
