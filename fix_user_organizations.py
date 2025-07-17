#!/usr/bin/env python3
"""
Fix UserOrganization relationships for existing users
"""

import sys
import os
sys.path.append('/Users/robertharvey/Documents/GitHub/BandSync/backend')

from app import app
from models import db, User, UserOrganization, Organization

def fix_user_organizations():
    """Ensure all users have proper UserOrganization records"""
    
    with app.app_context():
        print("🔄 Checking UserOrganization relationships...")
        
        # Get all users
        users = User.query.all()
        print(f"📊 Found {len(users)} total users")
        
        fixed_count = 0
        
        for user in users:
            if user.organization_id:
                # Check if UserOrganization record exists
                existing_org = UserOrganization.query.filter_by(
                    user_id=user.id,
                    organization_id=user.organization_id
                ).first()
                
                if not existing_org:
                    print(f"🔧 Creating UserOrganization for {user.username} in org {user.organization_id}")
                    
                    # Create UserOrganization record
                    user_org = UserOrganization(
                        user_id=user.id,
                        organization_id=user.organization_id,
                        role=user.role or 'Member',
                        section_id=user.section_id,
                        is_active=True
                    )
                    
                    db.session.add(user_org)
                    fixed_count += 1
                    
                    # Set current and primary organization
                    if not user.current_organization_id:
                        user.current_organization_id = user.organization_id
                    if not user.primary_organization_id:
                        user.primary_organization_id = user.organization_id
                else:
                    print(f"✅ UserOrganization already exists for {user.username}")
        
        try:
            db.session.commit()
            print(f"🎉 Fixed {fixed_count} UserOrganization relationships")
            
            # Show summary
            print("\n📋 Current UserOrganization relationships:")
            user_orgs = UserOrganization.query.filter_by(is_active=True).all()
            
            for user_org in user_orgs:
                org_name = user_org.organization.name
                user_name = user_org.user.username
                role = user_org.role
                print(f"   - {user_name} → {org_name} ({role})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = fix_user_organizations()
    sys.exit(0 if success else 1)
