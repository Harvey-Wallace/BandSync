#!/usr/bin/env python3

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import models after adding to path
from models import db, User, Organization, UserOrganization
from flask import Flask
from config import Config

def setup_super_admin():
    """Set up Super Admin functionality"""
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # First, let's check if we need to add super_admin column to users table
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            # Check if super_admin column exists
            columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"📋 Current users table columns: {columns}")
            
            if 'super_admin' not in columns:
                print("➕ Adding super_admin column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN super_admin BOOLEAN DEFAULT FALSE"))
                db.session.commit()
                print("✅ super_admin column added successfully")
            else:
                print("✅ super_admin column already exists")
            
            # Get user to make Super Admin
            super_admin_username = input("Enter the username to make Super Admin (or press Enter for 'Harvey258'): ").strip()
            if not super_admin_username:
                super_admin_username = "Harvey258"
            
            user = User.query.filter_by(username=super_admin_username).first()
            
            if not user:
                print(f"❌ User '{super_admin_username}' not found!")
                return False
            
            print(f"👤 Found user: {user.username} (ID: {user.id})")
            
            # Check if already Super Admin
            if user.super_admin:
                print(f"✅ User '{user.username}' is already a Super Admin")
            else:
                # Make user Super Admin
                user.super_admin = True
                print(f"🔐 Setting '{user.username}' as Super Admin...")
            
            # Get all organizations
            organizations = Organization.query.all()
            print(f"🏢 Found {len(organizations)} organizations")
            
            added_to_orgs = 0
            for org in organizations:
                # Check if user is already in this organization
                existing_user_org = UserOrganization.query.filter_by(
                    user_id=user.id,
                    organization_id=org.id
                ).first()
                
                if not existing_user_org:
                    # Add user to organization with Super Admin role
                    user_org = UserOrganization(
                        user_id=user.id,
                        organization_id=org.id,
                        role='Super Admin',
                        is_active=True
                    )
                    db.session.add(user_org)
                    added_to_orgs += 1
                    print(f"  ➕ Added to '{org.name}' with Super Admin role")
                else:
                    print(f"  ✅ Already in '{org.name}' with role '{existing_user_org.role}'")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n🎉 Super Admin setup complete!")
            print(f"📊 Summary:")
            print(f"   - User: {user.username}")
            print(f"   - Super Admin flag: {'✅ Set' if user.super_admin else '❌ Not set'}")
            print(f"   - Total organizations: {len(organizations)}")
            print(f"   - New organization assignments: {added_to_orgs}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Super Admin: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🚀 Setting up Super Admin functionality...")
    success = setup_super_admin()
    if success:
        print("✅ Super Admin setup completed successfully!")
    else:
        print("❌ Super Admin setup failed!")
        sys.exit(1)
