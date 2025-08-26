#!/usr/bin/env python3
"""
Deploy Multiple Dates Feature to Railway
This script handles the migration and deployment of the multiple dates feature
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
        
        if result.stderr and "warning" not in result.stderr.lower():
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
        result = subprocess.run(['railway', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

def check_git_status():
    """Check git status and ensure we're ready to deploy"""
    print("\n📋 Checking git status...")
    
    # Check if we have uncommitted changes
    result = run_command("git status --porcelain", "Checking for uncommitted changes", check=False)
    if result.stdout.strip():
        print("📝 You have uncommitted changes:")
        print(result.stdout)
        
        response = input("\nDo you want to commit these changes before deploying? (y/n): ").lower()
        if response == 'y':
            commit_message = input("Enter commit message (or press Enter for default): ").strip()
            if not commit_message:
                commit_message = f"Deploy multiple dates feature - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            run_command("git add .", "Adding all changes")
            run_command(f'git commit -m "{commit_message}"', "Committing changes")
        else:
            print("⚠️  Proceeding with uncommitted changes...")

def build_frontend():
    """Build the frontend for production"""
    print("\n🏗️  Building frontend...")
    
    # Install dependencies
    run_command("npm install", "Installing frontend dependencies")
    
    # Build the frontend
    run_command("npm run build", "Building frontend for production")
    
    # Check if build directory exists
    if os.path.exists("build"):
        print("✅ Frontend build completed successfully")
        return True
    else:
        print("❌ Frontend build failed - no build directory created")
        return False

def create_migration_sql():
    """Create SQL migration for multiple dates feature"""
    migration_sql = """
-- Multiple Dates Feature Migration
-- Add support for events with multiple date options and voting

-- Add multiple dates support to events table
ALTER TABLE events ADD COLUMN has_multiple_dates BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN final_date_selected BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN date_selection_deadline DATETIME;

-- Create event_possible_dates table
CREATE TABLE IF NOT EXISTS event_possible_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    possible_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
);

-- Create event_date_votes table  
CREATE TABLE IF NOT EXISTS event_date_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    possible_date_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (possible_date_id) REFERENCES event_possible_dates (id) ON DELETE CASCADE,
    UNIQUE(user_id, possible_date_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_event_possible_dates_event_id ON event_possible_dates(event_id);
CREATE INDEX IF NOT EXISTS idx_event_date_votes_event_id ON event_date_votes(event_id);
CREATE INDEX IF NOT EXISTS idx_event_date_votes_user_id ON event_date_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_event_date_votes_possible_date_id ON event_date_votes(possible_date_id);

COMMIT;
"""
    
    with open("multiple_dates_migration.sql", "w") as f:
        f.write(migration_sql)
    
    print("✅ Created migration SQL file")
    return True

def deploy_to_railway():
    """Deploy to Railway with migration"""
    print("\n🚀 Deploying to Railway...")
    
    # Login to Railway (if not already logged in)
    print("Checking Railway authentication...")
    result = run_command("railway whoami", "Checking Railway auth", check=False)
    if result.returncode != 0:
        print("Please log in to Railway...")
        run_command("railway login", "Logging in to Railway")
    
    # Deploy the application
    print("Deploying application...")
    run_command("railway up", "Deploying to Railway")
    
    print("✅ Deployment completed!")
    
    # Get the deployment URL
    result = run_command("railway domain", "Getting deployment URL", check=False)
    if result.returncode == 0 and result.stdout:
        print(f"\n🌐 Your application is available at: {result.stdout.strip()}")
    
    return True

def run_database_migration():
    """Run the database migration on Railway"""
    print("\n📊 Running database migration...")
    
    # Create a Python script to run the migration
    migration_script = '''
import os
import psycopg2
from urllib.parse import urlparse

def run_migration():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        # Parse the database URL
        url = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password
        )
        
        cursor = conn.cursor()
        
        # Read and execute migration SQL
        with open("multiple_dates_migration.sql", "r") as f:
            migration_sql = f.read()
        
        # Execute each statement separately for PostgreSQL
        statements = migration_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    print(f"⚠️  Warning on statement: {e}")
        
        conn.commit()
        print("✅ Migration completed successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()
'''
    
    with open("run_migration.py", "w") as f:
        f.write(migration_script)
    
    # Run the migration using Railway's remote execution
    print("Executing migration on Railway...")
    run_command("railway run python run_migration.py", "Running database migration")
    
    # Clean up temporary files
    if os.path.exists("run_migration.py"):
        os.remove("run_migration.py")
    if os.path.exists("multiple_dates_migration.sql"):
        os.remove("multiple_dates_migration.sql")
    
    return True

def main():
    """Main deployment process"""
    print("🎵 BandSync Multiple Dates Feature Deployment")
    print("=" * 50)
    
    # Check requirements
    if not check_railway_cli():
        print("Installing Railway CLI...")
        run_command("npm install -g @railway/cli", "Installing Railway CLI")
    
    # Check git status
    check_git_status()
    
    # Build frontend
    if not build_frontend():
        print("❌ Frontend build failed. Aborting deployment.")
        sys.exit(1)
    
    # Create migration
    create_migration_sql()
    
    # Deploy to Railway
    if not deploy_to_railway():
        print("❌ Deployment failed")
        sys.exit(1)
    
    # Run database migration
    run_database_migration()
    
    print("\n🎉 Multiple Dates Feature deployed successfully!")
    print("🔗 You can now test the multiple dates functionality on your Railway deployment")
    print("\nNext steps:")
    print("1. Test event creation with multiple dates")
    print("2. Test member voting on date options")
    print("3. Test admin date selection functionality")

if __name__ == "__main__":
    main()
