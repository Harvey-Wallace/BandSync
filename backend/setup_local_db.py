#!/usr/bin/env python3
"""
Local development setup script for BandSync RSVP testing
This script sets up a local SQLite database for testing RSVP endpoints
"""

import os
import sys
from datetime import datetime

def setup_local_database():
    """Set up local SQLite database for testing"""
    
    print("🔧 Setting up local BandSync database for RSVP testing...")
    
    # Set environment to use SQLite instead of PostgreSQL
    os.environ['DATABASE_URL'] = 'sqlite:///bandsync_local.db'
    os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing'
    os.environ['JWT_SECRET_KEY'] = 'jwt-dev-secret-key-for-testing'
    
    try:
        # Import Flask app and models
        from app import app
        from models import db, User, Organization, Event, RSVP, EventCategory
        
        with app.app_context():
            print("📦 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we have any organizations
            org_count = Organization.query.count()
            user_count = User.query.count()
            event_count = Event.query.count()
            
            print(f"📊 Current database state:")
            print(f"   Organizations: {org_count}")
            print(f"   Users: {user_count}")
            print(f"   Events: {event_count}")
            
            if org_count == 0:
                print("\n🏗️  Creating test data...")
                create_test_data(db)
            
            print("\n🎉 Local database setup complete!")
            print(f"🗄️  Database file: {os.path.abspath('bandsync_local.db')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_test_data(db):
    """Create minimal test data for RSVP testing"""
    try:
        # Create test organization
        org = Organization(name="Test Band")
        db.session.add(org)
        db.session.flush()  # Get org ID
        
        # Create event category
        category = EventCategory(
            name="Rehearsal",
            organization_id=org.id,
            is_default=True
        )
        db.session.add(category)
        db.session.flush()  # Get category ID
        
        # Create test user
        user = User(
            username="testuser",
            email="test@bandsync.com",
            name="Test User",
            role="Member",
            organization_id=org.id
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@bandsync.com",
            name="Admin User",
            role="Admin",
            organization_id=org.id
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()  # Get admin ID
        
        # Create test event
        event = Event(
            title="Test Rehearsal",
            type="Rehearsal",
            description="Test event for RSVP testing",
            date=datetime.now(),
            location_address="Test Location",
            category_id=category.id,
            organization_id=org.id,
            created_by=admin.id
        )
        db.session.add(event)
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Created test organization: {org.name} (ID: {org.id})")
        print(f"✅ Created test user: {user.email} (password: password123)")
        print(f"✅ Created admin user: {admin.email} (password: admin123)")
        print(f"✅ Created test event: {event.title} (ID: {event.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        db.session.rollback()
        return False

def print_usage():
    """Print usage information"""
    print("""
🚀 BandSync Local Development Setup

This script sets up a local SQLite database for testing RSVP endpoints.

Usage:
    python3 setup_local_db.py

After setup:
1. Start the Flask server:
   python3 app.py

2. Test the RSVP endpoints:
   python3 test_rsvp_endpoints.py

3. Login credentials:
   Regular user: test@bandsync.com / password123
   Admin user:   admin@bandsync.com / admin123

The script creates:
- Local SQLite database (bandsync_local.db)
- Test organization
- Test users (regular and admin)
- Test event for RSVP testing
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(0)
    
    print("🔧 BandSync Local Development Setup")
    print("=" * 50)
    
    success = setup_local_database()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the Flask server: python3 app.py")
        print("2. Test RSVP endpoints: python3 test_rsvp_endpoints.py")
        print("3. Login with: test@bandsync.com / password123")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)
