#!/usr/bin/env python3
"""
Deploy Enhanced RSVP Features to Railway
This script deploys Phase 1 Feature 1: Response Comments & Maybe Slider
"""

import os
import subprocess
import sys
import time
import json
from datetime import datetime

def run_command(cmd, description="", check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        
        if result.stdout:
            print(f"✅ Output: {result.stdout}")
        
        if result.stderr and result.stderr.strip():
            print(f"⚠️  Stderr: {result.stderr}")
            
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return e

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI installed and working")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed. Please install: https://docs.railway.app/develop/cli")
        return False

def check_git_status():
    """Check git status and ensure we're ready to deploy"""
    print(f"\n📋 Checking git status...")
    
    # Check for uncommitted changes
    result = run_command("git status --porcelain", "Checking for uncommitted changes", check=False)
    if result.stdout.strip():
        print(f"📝 Uncommitted changes found:")
        print(result.stdout)
        return False
    
    print(f"✅ Working directory clean")
    return True

def commit_and_push_changes():
    """Commit and push our enhanced RSVP features"""
    print(f"\n📤 Committing Enhanced RSVP Features...")
    
    # Add all changes
    run_command("git add .", "Adding all changes")
    
    # Commit with descriptive message
    commit_msg = "feat: Implement Phase 1 Feature 1 - Enhanced RSVP with Comments & Maybe Likelihood Slider\n\n- Add comments, likelihood, and updated_at fields to RSVP model\n- Create EnhancedRSVPModal component with likelihood slider\n- Update RSVP API endpoints to handle new fields\n- Maintain backward compatibility with simple RSVP buttons\n- Add database migration for new RSVP fields"
    
    run_command(f'git commit -m "{commit_msg}"', "Committing enhanced RSVP features")
    
    # Push to main branch
    run_command("git push origin main", "Pushing to remote repository")

def create_production_migration():
    """Create a production-safe migration script for Railway PostgreSQL"""
    migration_content = '''#!/usr/bin/env python3
"""
Production Migration: Enhanced RSVP Features
Adds comments, likelihood, and updated_at fields to RSVP table for PostgreSQL
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, '/opt/render/project/src/backend')

from app import app
from models import db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_rsvp_enhancements():
    """Add comments and likelihood fields to RSVP table for PostgreSQL"""
    
    print("🔄 Adding Enhanced RSVP features to production database...")
    
    try:
        with app.app_context():
            # For PostgreSQL, check if columns exist using information_schema
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # Check for existing columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'rsvp' 
                AND column_name IN ('comments', 'likelihood', 'updated_at')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            changes_made = False
            
            # Add comments field if it doesn't exist
            if 'comments' not in existing_columns:
                logger.info("Adding 'comments' column to RSVP table...")
                cursor.execute('ALTER TABLE rsvp ADD COLUMN comments TEXT')
                connection.commit()
                changes_made = True
                print("✅ Added 'comments' column")
            else:
                print("✅ 'comments' column already exists")
            
            # Add likelihood field if it doesn't exist
            if 'likelihood' not in existing_columns:
                logger.info("Adding 'likelihood' column to RSVP table...")
                cursor.execute('ALTER TABLE rsvp ADD COLUMN likelihood INTEGER DEFAULT NULL')
                connection.commit()
                changes_made = True
                print("✅ Added 'likelihood' column")
            else:
                print("✅ 'likelihood' column already exists")
            
            # Add updated_at field if it doesn't exist
            if 'updated_at' not in existing_columns:
                logger.info("Adding 'updated_at' column to RSVP table...")
                cursor.execute('ALTER TABLE rsvp ADD COLUMN updated_at TIMESTAMP DEFAULT NULL')
                connection.commit()
                changes_made = True
                print("✅ Added 'updated_at' column")
            else:
                print("✅ 'updated_at' column already exists")
            
            cursor.close()
            connection.close()
            
            if changes_made:
                print("\\n🎉 Enhanced RSVP migration completed successfully!")
                print("\\n📋 New RSVP features available:")
                print("   - Comments: Users can add optional comments with their RSVP")
                print("   - Likelihood: 'Maybe' responses can include 1-100% likelihood")
                print("   - Updated tracking: Better timestamp management")
            else:
                print("\\n✅ All Enhanced RSVP features already exist - no migration needed")
                
            return True
            
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting Enhanced RSVP Production Migration...")
    success = add_rsvp_enhancements()
    
    if success:
        print("\\n✅ Production migration completed successfully!")
        print("\\n🎉 Enhanced RSVP features are now live!")
        print("\\nNew features:")
        print("   📝 Response Comments")
        print("   📊 Maybe Likelihood Slider (1-100%)")
        print("   ⏰ Enhanced Timestamp Tracking")
    else:
        print("\\n❌ Migration failed!")
        sys.exit(1)
'''
    
    with open('production_rsvp_migration.py', 'w') as f:
        f.write(migration_content)
    
    print("✅ Created production migration script")

def deploy_to_railway():
    """Deploy to Railway with migration"""
    print(f"\n🚂 Deploying Enhanced RSVP Features to Railway...")
    
    # Create production migration
    create_production_migration()
    
    # Add migration to git
    run_command("git add production_rsvp_migration.py", "Adding production migration")
    run_command('git commit -m "Add production migration for enhanced RSVP features"', "Committing migration")
    run_command("git push origin main", "Pushing migration")
    
    # Deploy to Railway
    print(f"\\n🚀 Triggering Railway deployment...")
    result = run_command("railway up", "Deploying to Railway", check=False)
    
    if result.returncode == 0:
        print(f"\\n✅ Deployment triggered successfully!")
        print(f"\\n📋 Post-deployment steps:")
        print(f"   1. Monitor Railway logs for deployment progress")
        print(f"   2. Run production migration once deployed")
        print(f"   3. Test enhanced RSVP features on production")
        return True
    else:
        print(f"\\n❌ Deployment failed!")
        return False

def run_production_migration():
    """Run the migration on Railway production"""
    print(f"\\n🔧 Running production migration...")
    
    # Run migration via Railway CLI
    result = run_command("railway run python production_rsvp_migration.py", 
                        "Running Enhanced RSVP migration on production", check=False)
    
    if result.returncode == 0:
        print(f"\\n✅ Production migration completed!")
        return True
    else:
        print(f"\\n❌ Production migration failed!")
        return False

def main():
    """Main deployment function"""
    print(f"=" * 60)
    print(f"🎉 BANDSYNC ENHANCED RSVP DEPLOYMENT")
    print(f"Phase 1 Feature 1: Response Comments & Maybe Slider")
    print(f"Deployment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 60)
    
    # Check prerequisites
    if not check_railway_cli():
        print("\\n❌ Please install Railway CLI and try again")
        sys.exit(1)
    
    # Check git status
    if not check_git_status():
        print("\\n📝 Committing current changes...")
        commit_and_push_changes()
    
    # Deploy to Railway
    if deploy_to_railway():
        print(f"\\n🎉 Deployment initiated successfully!")
        print(f"\\n📋 Next steps:")
        print(f"   1. Wait for Railway deployment to complete")
        print(f"   2. Run: python {__file__} --migrate")
        print(f"   3. Test enhanced RSVP features at your Railway URL")
        
        # Ask if user wants to run migration now
        response = input("\\n🤔 Run production migration now? (y/n): ").lower()
        if response == 'y':
            time.sleep(30)  # Wait for deployment
            run_production_migration()
    else:
        print(f"\\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--migrate':
        run_production_migration()
    else:
        main()
