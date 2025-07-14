#!/usr/bin/env python3
"""
Manual Railway Database Migration
Use this script to manually run the password reset migration on Railway
"""

import os
import sys
import subprocess
import time

def run_migration_command():
    """Run the migration via Railway CLI"""
    print("🔄 Running password reset migration on Railway...")
    
    # Create a temporary Python script to run the migration
    migration_script = """
import os
from sqlalchemy import create_engine, text

def run_migration():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns exist
            result = conn.execute(text('''
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires')
            '''))
            
            existing = [row[0] for row in result.fetchall()]
            
            # Add missing columns
            if 'password_reset_token' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL'))
                print("✅ Added password_reset_token column")
            else:
                print("ℹ️  password_reset_token column already exists")
            
            if 'password_reset_expires' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL'))
                print("✅ Added password_reset_expires column")
            else:
                print("ℹ️  password_reset_expires column already exists")
            
            conn.commit()
            print("🎉 Password reset migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
"""
    
    # Write the migration script to a temporary file
    with open('temp_migration.py', 'w') as f:
        f.write(migration_script)
    
    try:
        # Run the migration script on Railway
        print("Executing migration on Railway...")
        result = subprocess.run([
            'railway', 'run', 'python', 'temp_migration.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.stdout:
            print("📋 Migration output:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Migration stderr:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            return True
        else:
            print("❌ Migration failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Migration timed out")
        return False
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists('temp_migration.py'):
            os.remove('temp_migration.py')

def check_railway_connection():
    """Check if Railway CLI is connected"""
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI connected")
            print(result.stdout)
            return True
        else:
            print("❌ Railway CLI not connected")
            print("Run: railway login")
            return False
    except Exception as e:
        print(f"❌ Error checking Railway connection: {e}")
        return False

def main():
    """Main migration process"""
    print("🗄️  Railway Database Migration - Password Reset Fields")
    print("=" * 55)
    
    # Check Railway connection
    if not check_railway_connection():
        print("\nPlease run: railway login")
        sys.exit(1)
    
    # Confirm migration
    print("\nThis will add password_reset_token and password_reset_expires columns to the user table.")
    response = input("Continue with migration? (y/N): ")
    
    if not response.lower().startswith('y'):
        print("❌ Migration cancelled")
        sys.exit(1)
    
    # Run migration
    success = run_migration_command()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Deploy your latest code to Railway")
        print("2. Test the password reset functionality")
        print("3. Monitor Railway logs for any issues")
    else:
        print("\n❌ Migration failed!")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL environment variable")
        print("2. Verify database permissions")
        print("3. Check Railway logs for errors")
        print("4. Try running: railway logs")

if __name__ == "__main__":
    main()
