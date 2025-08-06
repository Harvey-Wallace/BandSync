#!/usr/bin/env python3
"""
Deploy and run time fields migration on Railway
This script creates a one-time deployment that runs the migration
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print("🚀 Railway Migration Deployment Script")
    print("=" * 50)
    
    # Check if Railway CLI is installed
    if not run_command("railway --version", "Checking Railway CLI"):
        print("\n📦 Please install Railway CLI first:")
        print("npm install -g @railway/cli")
        print("or")
        print("curl -fsSL https://railway.app/install.sh | sh")
        return False
    
    # Login check
    print("\n🔐 Checking Railway login status...")
    if not run_command("railway whoami", "Verifying Railway login"):
        print("\n🔑 Please login to Railway:")
        print("railway login")
        return False
    
    # Link to project
    print("\n🔗 Ensuring project is linked...")
    run_command("railway link", "Linking to Railway project")
    
    # Upload and run migration
    print("\n📤 Running migration on Railway...")
    migration_command = "railway run python3 railway_time_fields_migration.py"
    
    if run_command(migration_command, "Executing time fields migration"):
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("1. Uncomment time fields in backend/models.py")
        print("2. Deploy your application")
        print("3. Your event timing will now work properly!")
        return True
    else:
        print("\n💥 Migration failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
