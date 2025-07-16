#!/usr/bin/env python3
"""
Migration script to create UserOrganization entries for existing users
This fixes the issue where cancellation notifications weren't being sent 
because users weren't properly linked to organizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, User, UserOrganization, Organization
from config import Config

def migrate_user_organizations():
    """Create UserOrganization entries for users who don't have them"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        db.init_app(app)
        
        print("🔄 Starting UserOrganization migration...")
        
        # Get all users who have an organization_id but no UserOrganization entry
        users_without_org_entry = db.session.query(User).filter(
            User.organization_id.isnot(None)
        ).all()
        
        print(f"📊 Found {len(users_without_org_entry)} users to process")
        
        created_count = 0
        updated_count = 0
        
        for user in users_without_org_entry:
            # Check if UserOrganization entry already exists
            existing_org = UserOrganization.query.filter_by(
                user_id=user.id,
                organization_id=user.organization_id
            ).first()
            
            if not existing_org:
                # Create new UserOrganization entry
                user_org = UserOrganization(
                    user_id=user.id,
                    organization_id=user.organization_id,
                    role=user.role,
                    section_id=user.section_id,
                    is_active=True
                )
                
                db.session.add(user_org)
                created_count += 1
                
                print(f"✅ Created UserOrganization for {user.username} ({user.email})")
                
                # Update user's current and primary organization
                user.current_organization_id = user.organization_id
                user.primary_organization_id = user.organization_id
                updated_count += 1
                
            else:
                # Update existing entry to be active
                if not existing_org.is_active:
                    existing_org.is_active = True
                    updated_count += 1
                    print(f"✅ Activated UserOrganization for {user.username}")
        
        try:
            db.session.commit()
            print(f"🎉 Migration completed successfully!")
            print(f"   - Created {created_count} UserOrganization entries")
            print(f"   - Updated {updated_count} user records")
            
            # Verify the migration
            total_user_orgs = UserOrganization.query.filter_by(is_active=True).count()
            print(f"   - Total active UserOrganizations: {total_user_orgs}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            return False
        
        return True

if __name__ == "__main__":
    success = migrate_user_organizations()
    sys.exit(0 if success else 1)
