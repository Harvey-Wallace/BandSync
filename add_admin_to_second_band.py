#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/robertharvey/Documents/BandSync/backend')

from models import db, User, Organization, UserOrganization
from app import app

def add_admin_to_second_band():
    """Add admin user to the existing Second Band organization"""
    
    with app.app_context():
        # Find admin user and Second Band org
        admin_user = User.query.filter_by(username='admin').first()
        second_band_org = Organization.query.filter_by(name='Second Band').first()
        
        if not admin_user or not second_band_org:
            print("❌ Admin user or Second Band organization not found!")
            return
        
        print(f"✅ Found admin user: {admin_user.username}")
        print(f"✅ Found Second Band organization: {second_band_org.name}")
        
        # Check if admin is already in this organization
        existing = UserOrganization.query.filter_by(
            user_id=admin_user.id,
            organization_id=second_band_org.id
        ).first()
        
        if not existing:
            try:
                # Add relationship
                user_org = UserOrganization(
                    user_id=admin_user.id,
                    organization_id=second_band_org.id,
                    role='Member'
                )
                db.session.add(user_org)
                db.session.commit()
                print(f"✅ Added admin to Second Band as Member")
                
            except Exception as e:
                print(f"❌ Error adding user to org: {e}")
                db.session.rollback()
        else:
            print(f"✅ Admin already belongs to Second Band as {existing.role}")
        
        # Show admin's memberships
        memberships = UserOrganization.query.filter_by(user_id=admin_user.id).all()
        print(f"\n📋 Admin's organization memberships:")
        for membership in memberships:
            print(f"   - {membership.organization.name} (Role: {membership.role})")

if __name__ == "__main__":
    add_admin_to_second_band()
