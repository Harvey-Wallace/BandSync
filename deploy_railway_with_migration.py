#!/usr/bin/env python3
"""
Complete Railway deployment with password reset migration
This script handles the full deployment process to Railway
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
        
        if result.stderr:
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
    
    # Check if we're in a git repo
    result = run_command("git status", "Checking git status", check=False)
    if result.returncode != 0:
        print("❌ Not in a git repository")
        return False
    
    # Check for uncommitted changes
    result = run_command("git diff --name-only", "Checking for uncommitted changes", check=False)
    if result.stdout.strip():
        print("⚠️  Uncommitted changes detected:")
        print(result.stdout)
        response = input("Do you want to commit these changes? (y/N): ")
        if response.lower().startswith('y'):
            commit_message = input("Enter commit message: ") or "Deploy: Update password reset and email migration"
            run_command(f'git add -A && git commit -m "{commit_message}"', "Committing changes")
        else:
            print("❌ Please commit or stash changes before deploying")
            return False
    
    return True

def verify_env_vars():
    """Verify that required environment variables are set"""
    print("\n🔍 Verifying environment variables...")
    
    required_vars = [
        'DATABASE_URL',
        'RESEND_API_KEY',
        'FROM_EMAIL',
        'BASE_URL',
        'JWT_SECRET_KEY',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET',
        'REACT_APP_API_URL',
        'REACT_APP_GOOGLE_MAPS_API_KEY'
    ]
    
    print("Please verify these environment variables are set in Railway dashboard:")
    for var in required_vars:
        print(f"  - {var}")
    
    response = input("\nAre all required environment variables set in Railway? (y/N): ")
    if not response.lower().startswith('y'):
        print("❌ Please set all required environment variables in Railway dashboard")
        print("Visit: https://railway.app/dashboard")
        return False
    
    return True

def build_frontend():
    """Build the React frontend"""
    print("\n🏗️  Building React frontend...")
    
    # Change to frontend directory
    os.chdir('frontend')
    
    # Install dependencies
    run_command("npm install", "Installing frontend dependencies")
    
    # Build the frontend
    run_command("npm run build", "Building React frontend")
    
    # Copy build to backend/static
    run_command("rm -rf ../backend/static && cp -r build ../backend/static", "Copying build to backend")
    
    # Return to root directory
    os.chdir('..')
    
    print("✅ Frontend build completed")

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n🚀 Deploying to Railway...")
    
    # Deploy using Railway CLI
    result = run_command("railway up", "Deploying to Railway", check=False)
    
    if result.returncode == 0:
        print("✅ Deployment initiated successfully")
        return True
    else:
        print("❌ Deployment failed")
        return False

def wait_for_deployment():
    """Wait for deployment to complete and check logs"""
    print("\n⏳ Waiting for deployment to complete...")
    
    # Wait a bit for deployment to start
    time.sleep(10)
    
    # Check deployment status
    print("Checking deployment logs...")
    run_command("railway logs", "Recent deployment logs", check=False)
    
    print("\n📊 Deployment status check:")
    response = input("Did the deployment complete successfully? Check Railway dashboard. (y/N): ")
    return response.lower().startswith('y')

def test_endpoints():
    """Test critical endpoints"""
    print("\n🧪 Testing critical endpoints...")
    
    # Get the app URL
    app_url = input("Enter your Railway app URL (e.g., https://your-app.railway.app): ")
    if not app_url:
        print("❌ App URL required for testing")
        return False
    
    # Test health check
    print(f"Testing health check at {app_url}/health")
    result = run_command(f"curl -s {app_url}/health", "Health check", check=False)
    
    if result.returncode == 0:
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
    
    # Test API routes
    print(f"Testing API routes at {app_url}/debug/routes")
    result = run_command(f"curl -s {app_url}/debug/routes", "API routes test", check=False)
    
    if result.returncode == 0:
        print("✅ API routes accessible")
    else:
        print("❌ API routes failed")
    
    return True

def main():
    """Main deployment process"""
    print("🚀 BandSync Railway Deployment with Password Reset Migration")
    print("=" * 60)
    
    # Check prerequisites
    if not check_railway_cli():
        print("\n❌ Please install Railway CLI first:")
        print("npm install -g @railway/cli")
        sys.exit(1)
    
    if not check_git_status():
        sys.exit(1)
    
    if not verify_env_vars():
        sys.exit(1)
    
    # Build frontend
    try:
        build_frontend()
    except Exception as e:
        print(f"❌ Frontend build failed: {e}")
        sys.exit(1)
    
    # Deploy to Railway
    if not deploy_to_railway():
        sys.exit(1)
    
    # Wait for deployment
    if not wait_for_deployment():
        print("❌ Deployment may have failed. Check Railway logs.")
        sys.exit(1)
    
    # Test endpoints
    test_endpoints()
    
    print("\n🎉 Deployment completed!")
    print("\nNext steps:")
    print("1. Check Railway logs for migration success")
    print("2. Test login functionality")
    print("3. Test password reset feature")
    print("4. Monitor for any errors")
    
    print("\nImportant notes:")
    print("- The auto-migration should run automatically on startup")
    print("- Check logs for: '🎉 Password reset migration completed'")
    print("- If migration fails, check DATABASE_URL and permissions")

if __name__ == "__main__":
    main()
