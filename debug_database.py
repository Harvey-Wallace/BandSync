#!/usr/bin/env python3
"""
Debug database users and potentially recreate test users
"""

import os
import sys
sys.path.insert(0, 'backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.models import db, User, Organization
from backend.app import app
from werkzeug.security import generate_password_hash

def debug_database():
    """Debug database and check users"""
    print("🔍 Debugging database and users...")
    
    with app.app_context():
        try:
            # Check if database tables exist
            print("\n📊 Database connection test:")
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            print(f"✅ Database connection successful: {result}")
            
            # Check users table structure
            print("\n🗂️  Users table structure:")
            result = db.session.execute(db.text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'user'
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("Columns in user table:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            # Check if password reset columns exist
            reset_columns = [col for col in result if col[0] in ['password_reset_token', 'password_reset_expires']]
            if reset_columns:
                print(f"✅ Password reset columns found: {[col[0] for col in reset_columns]}")
            else:
                print("❌ Password reset columns missing")
            
            # Check existing users
            print("\n👥 Existing users:")
            users = User.query.all()
            if users:
                for user in users:
                    print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}")
                    print(f"    Password hash: {'SET' if user.password_hash else 'MISSING'}")
                    print(f"    Organization: {user.organization_id}")
            else:
                print("  No users found in database")
            
            # Check organizations
            print("\n🏢 Organizations:")
            orgs = Organization.query.all()
            if orgs:
                for org in orgs:
                    print(f"  - ID: {org.id}, Name: {org.name}")
            else:
                print("  No organizations found")
            
            return len(users) > 0
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

def create_test_user():
    """Create a test user for debugging"""
    print("\n🔧 Creating test user...")
    
    with app.app_context():
        try:
            # Check if test organization exists
            org = Organization.query.filter_by(name="Test Band").first()
            if not org:
                org = Organization(name="Test Band")
                db.session.add(org)
                db.session.commit()
                print(f"✅ Created test organization: {org.name}")
            
            # Check if test user exists
            existing_user = User.query.filter_by(username="testuser").first()
            if existing_user:
                print(f"⚠️  User 'testuser' already exists")
                # Update password just in case
                existing_user.password_hash = generate_password_hash("testpass")
                db.session.commit()
                print("✅ Updated password for existing user")
                return True
            
            # Create new test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                name="Test User",
                password_hash=generate_password_hash("testpass"),
                role="admin",
                organization_id=org.id,
                current_organization_id=org.id,
                primary_organization_id=org.id
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"✅ Created test user:")
            print(f"  Username: testuser")
            print(f"  Password: testpass")
            print(f"  Email: test@example.com")
            print(f"  Role: admin")
            print(f"  Organization: {org.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            db.session.rollback()
            return False

def test_login_locally():
    """Test login logic locally"""
    print("\n🧪 Testing login logic...")
    
    with app.app_context():
        try:
            # Try to find user
            user = User.query.filter_by(username="testuser").first()
            if not user:
                print("❌ Test user not found")
                return False
            
            print(f"✅ Found user: {user.username}")
            
            # Test password verification
            from werkzeug.security import check_password_hash
            password_correct = check_password_hash(user.password_hash, "testpass")
            print(f"Password verification: {'✅ CORRECT' if password_correct else '❌ INCORRECT'}")
            
            # Check user attributes
            print(f"User attributes:")
            print(f"  - ID: {user.id}")
            print(f"  - Username: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Role: {user.role}")
            print(f"  - Organization ID: {user.organization_id}")
            print(f"  - Password hash length: {len(user.password_hash) if user.password_hash else 0}")
            
            return password_correct
            
        except Exception as e:
            print(f"❌ Login test error: {e}")
            return False

if __name__ == "__main__":
    print("🔧 BandSync Database Debug Tool")
    print("=" * 50)
    
    # Debug database
    has_users = debug_database()
    
    # Create test user if needed
    if not has_users:
        print("\n🔄 No users found, creating test user...")
        create_test_user()
    else:
        response = input("\n❓ Create/update test user? (y/N): ")
        if response.lower().startswith('y'):
            create_test_user()
    
    # Test login
    test_login_locally()
    
    print("\n🎯 Next steps:")
    print("1. Try logging in with: testuser / testpass")
    print("2. If still not working, check Railway logs")
    print("3. Test password reset functionality")
