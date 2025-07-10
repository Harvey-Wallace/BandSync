#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/robertharvey/Documents/BandSync/backend')

from models import db, User, Organization, UserOrganization
from app import app

def check_database_state():
    """Check the current database state"""
    
    with app.app_context():
        print("Current database state:")
        
        # Check organizations
        orgs = Organization.query.all()
        print(f"Organizations ({len(orgs)}):")
        for org in orgs:
            print(f"   - ID: {org.id}, Name: {org.name}")
        
        # Check users
        users = User.query.all()
        print(f"\nUsers ({len(users)}):")
        for user in users:
            print(f"   - ID: {user.id}, Username: {user.username}")
        
        # Check user-organization relationships
        user_orgs = UserOrganization.query.all()
        print(f"\nUser-Organization relationships ({len(user_orgs)}):")
        for uo in user_orgs:
            print(f"   - User: {uo.user.username}, Org: {uo.organization.name}, Role: {uo.role}")

def create_test_org():
    """Create a test organization using raw SQL to avoid sequence issues"""
    
    with app.app_context():
        try:
            # Use raw SQL to insert with a specific ID
            result = db.session.execute("""
                INSERT INTO organization (name, logo_url, theme_color) 
                VALUES ('Test Band Organization', NULL, '#007bff') 
                ON CONFLICT (name) DO NOTHING
                RETURNING id, name
            """)
            
            row = result.fetchone()
            if row:
                org_id, org_name = row
                print(f"✅ Created organization: {org_name} (ID: {org_id})")
                db.session.commit()
                return org_id
            else:
                # Organization already exists
                org = Organization.query.filter_by(name='Test Band Organization').first()
                if org:
                    print(f"✅ Found existing organization: {org.name} (ID: {org.id})")
                    return org.id
                else:
                    print("❌ Could not create or find organization")
                    return None
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return None

def add_user_to_org():
    """Add admin user to the test organization"""
    
    with app.app_context():
        # Find admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("❌ Admin user not found!")
            return
        
        # Create organization
        org_id = create_test_org()
        if not org_id:
            return
            
        # Check if admin is already in this organization
        existing = UserOrganization.query.filter_by(
            user_id=admin_user.id,
            organization_id=org_id
        ).first()
        
        if not existing:
            try:
                # Add relationship
                user_org = UserOrganization(
                    user_id=admin_user.id,
                    organization_id=org_id,
                    role='Member'
                )
                db.session.add(user_org)
                db.session.commit()
                print(f"✅ Added admin to Test Band Organization as Member")
                
            except Exception as e:
                print(f"❌ Error adding user to org: {e}")
                db.session.rollback()
        else:
            print(f"✅ Admin already belongs to Test Band Organization as {existing.role}")

if __name__ == "__main__":
    print("Database State Check and Multi-Org Setup")
    print("="*50)
    
    check_database_state()
    print("\n" + "="*50)
    add_user_to_org()
    print("\n" + "="*50)
    check_database_state()
