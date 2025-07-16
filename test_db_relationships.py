#!/usr/bin/env python3
"""
Quick database connection test to identify SQLAlchemy relationship issues
"""
import os
import sys
sys.path.append('/Users/robertharvey/Documents/GitHub/BandSync/backend')

from flask import Flask
from models import db, User, Organization, Event, UserOrganization
from config import Config

def test_db_relationships():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        db.init_app(app)
        
        try:
            # Test basic queries
            print("Testing database relationships...")
            
            # Test organization query
            org_count = Organization.query.count()
            print(f"✅ Organizations: {org_count}")
            
            # Test user query  
            user_count = User.query.count()
            print(f"✅ Users: {user_count}")
            
            # Test event query
            event_count = Event.query.count()
            print(f"✅ Events: {event_count}")
            
            # Test user organization relationships
            user_org_count = UserOrganization.query.count()
            print(f"✅ User Organizations: {user_org_count}")
            
            # Test a specific relationship that might be causing issues
            try:
                orgs = Organization.query.all()
                for org in orgs:
                    print(f"✅ Organization: {org.name}")
                    # Test accessing user relationships
                    user_orgs = UserOrganization.query.filter_by(organization_id=org.id).all()
                    print(f"   - User memberships: {len(user_orgs)}")
                    
            except Exception as e:
                print(f"❌ Error testing organization relationships: {e}")
                
            print("\n✅ Database relationships test completed successfully!")
            
        except Exception as e:
            print(f"❌ Database relationship error: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            
if __name__ == "__main__":
    test_db_relationships()
