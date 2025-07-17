#!/usr/bin/env python3
"""
Fix admin user in second organization using direct database access
"""

import sys
import os
sys.path.append('/Users/robertharvey/Documents/GitHub/BandSync/backend')

# Set up environment
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/bandsync')

from flask import Flask
from config import Config
from models import db, User, Organization, UserOrganization

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def fix_admin_organizations():
    """Fix admin user organization memberships"""
    
    app = create_app()
    
    with app.app_context():
        print("🔄 Checking organizations and admin user...")
        
        # List all organizations
        organizations = Organization.query.all()
        print(f"📊 Found {len(organizations)} organizations:")
        for org in organizations:
            print(f"   - {org.name} (ID: {org.id})")
        
        # Find admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Found admin user: {admin_user.username} (ID: {admin_user.id})")
        print(f"   - Current org ID: {admin_user.organization_id}")
        print(f"   - Primary org ID: {admin_user.primary_organization_id}")
        print(f"   - Role: {admin_user.role}")
        
        # Show admin's current memberships
        memberships = UserOrganization.query.filter_by(user_id=admin_user.id).all()
        print(f"\n📋 Admin's current organization memberships ({len(memberships)}):")
        for membership in memberships:
            org_name = membership.organization.name if membership.organization else "Unknown"
            print(f"   - {org_name} (ID: {membership.organization_id}, Role: {membership.role}, Active: {membership.is_active})")
        
        # If there are multiple organizations, add admin to all of them
        if len(organizations) > 1:
            print(f"\n🔧 Adding admin to all organizations...")
            
            added_count = 0
            for org in organizations:
                # Check if admin is already in this organization
                existing = UserOrganization.query.filter_by(
                    user_id=admin_user.id,
                    organization_id=org.id
                ).first()
                
                if not existing:
                    try:
                        # Add admin to this organization
                        user_org = UserOrganization(
                            user_id=admin_user.id,
                            organization_id=org.id,
                            role='Admin',  # Make admin an Admin in all orgs
                            is_active=True
                        )
                        db.session.add(user_org)
                        print(f"   ✅ Added admin to '{org.name}' as Admin")
                        added_count += 1
                    except Exception as e:
                        print(f"   ❌ Error adding admin to '{org.name}': {e}")
                        db.session.rollback()
                        return False
                else:
                    print(f"   ✅ Admin already in '{org.name}' as {existing.role}")
            
            if added_count > 0:
                try:
                    db.session.commit()
                    print(f"🎉 Successfully added admin to {added_count} organizations!")
                except Exception as e:
                    print(f"❌ Error committing changes: {e}")
                    db.session.rollback()
                    return False
            
            # Show final memberships
            final_memberships = UserOrganization.query.filter_by(user_id=admin_user.id).all()
            print(f"\n📋 Admin's final organization memberships ({len(final_memberships)}):")
            for membership in final_memberships:
                org_name = membership.organization.name if membership.organization else "Unknown"
                print(f"   - {org_name} (ID: {membership.organization_id}, Role: {membership.role}, Active: {membership.is_active})")
        
        return True

if __name__ == "__main__":
    success = fix_admin_organizations()
    print(f"\n{'🎉 Success!' if success else '❌ Failed!'}")
    sys.exit(0 if success else 1)
