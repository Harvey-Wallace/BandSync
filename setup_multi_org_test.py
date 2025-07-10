#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/robertharvey/Documents/BandSync/backend')

from models import db, User, Organization, UserOrganization
from app import app

def setup_multi_org_test():
    """Set up a test scenario with a user in multiple organizations"""
    
    with app.app_context():
        print("Setting up multi-organization test scenario...")
        
        # Find admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("❌ Admin user not found!")
            return
        
        print(f"✅ Found admin user: {admin_user.username}")
        
        # Create a second organization
        second_org = Organization.query.filter_by(name='Test Band Organization').first()
        if not second_org:
            second_org = Organization(
                name='Test Band Organization'
            )
            db.session.add(second_org)
            try:
                db.session.commit()
                print(f"✅ Created second organization: {second_org.name}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating organization: {e}")
                # Try to find existing org again
                second_org = Organization.query.filter_by(name='Test Band Organization').first()
                if second_org:
                    print(f"✅ Found existing organization after rollback: {second_org.name}")
                else:
                    print("❌ Could not create or find second organization")
                    return
        else:
            print(f"✅ Found existing second organization: {second_org.name}")
        
        # Check if admin is already in this organization
        existing_membership = UserOrganization.query.filter_by(
            user_id=admin_user.id,
            organization_id=second_org.id
        ).first()
        
        if not existing_membership:
            # Add admin to second organization as Member
            user_org = UserOrganization(
                user_id=admin_user.id,
                organization_id=second_org.id,
                role='Member'
            )
            db.session.add(user_org)
            db.session.commit()
            print(f"✅ Added admin to {second_org.name} as Member")
        else:
            print(f"✅ Admin already belongs to {second_org.name} as {existing_membership.role}")
        
        # Check admin's current memberships
        memberships = UserOrganization.query.filter_by(user_id=admin_user.id).all()
        print(f"\n📋 Admin's organization memberships:")
        for membership in memberships:
            print(f"   - {membership.organization.name} (Role: {membership.role})")
        
        print(f"\n✅ Multi-organization test setup complete!")
        print(f"   Admin user now belongs to {len(memberships)} organizations")

if __name__ == "__main__":
    setup_multi_org_test()
