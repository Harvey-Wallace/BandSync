#!/bin/bash

# BandSync Update Script
# Use this script to push updates to your live application

set -e

echo "🔄 BandSync Update Script"
echo "========================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[UPDATE]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! -f "backend/app.py" ]]; then
    print_error "Please run this script from the BandSync root directory"
    exit 1
fi

# Check for uncommitted changes
check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "You have uncommitted changes:"
        git status --short
        echo ""
        read -p "Do you want to continue? [y/N]: " continue_anyway
        if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
            print_info "Aborting update. Please commit your changes first."
            exit 1
        fi
    fi
}

# Run pre-deployment checks
pre_deployment_checks() {
    print_status "Running pre-deployment checks..."
    
    # Test backend
    print_status "Testing backend..."
    cd backend
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✓ Backend imports successfully')
except Exception as e:
    print(f'✗ Backend import failed: {e}')
    sys.exit(1)
"
    cd ..
    
    # Test frontend build
    print_status "Testing frontend build..."
    cd frontend
    npm run build > /dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        print_status "✓ Frontend builds successfully"
    else
        print_error "✗ Frontend build failed"
        exit 1
    fi
    cd ..
    
    print_status "Pre-deployment checks passed ✓"
}

# Get commit message
get_commit_message() {
    echo ""
    echo "Enter a commit message for this update:"
    read -p "> " commit_message
    
    if [[ -z "$commit_message" ]]; then
        commit_message="Update: $(date '+%Y-%m-%d %H:%M:%S')"
        print_info "Using default commit message: $commit_message"
    fi
}

# Git operations
git_operations() {
    print_status "Preparing Git operations..."
    
    # Add all changes
    git add .
    
    # Commit changes
    git commit -m "$commit_message"
    
    # Push to main branch
    print_status "Pushing to main branch..."
    git push origin main
    
    print_status "Git operations completed ✓"
}

# Railway deployment
deploy_railway() {
    print_status "Deploying to Railway..."
    
    if command -v railway &> /dev/null; then
        railway up
        print_status "Railway deployment triggered ✓"
    else
        print_warning "Railway CLI not found. Deployment will happen automatically via GitHub integration."
    fi
}

# Vercel deployment
deploy_vercel() {
    print_status "Deploying to Vercel..."
    
    if command -v vercel &> /dev/null; then
        cd frontend
        vercel --prod
        cd ..
        print_status "Vercel deployment completed ✓"
    else
        print_warning "Vercel CLI not found. Deployment will happen automatically via GitHub integration."
    fi
}

# Docker deployment
deploy_docker() {
    print_status "Rebuilding Docker containers..."
    
    # Rebuild and restart containers
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    print_status "Docker deployment completed ✓"
}

# Check deployment status
check_deployment_status() {
    print_status "Checking deployment status..."
    
    # If Railway is configured
    if command -v railway &> /dev/null; then
        echo "Railway deployment status:"
        railway status 2>/dev/null || echo "Unable to check Railway status"
    fi
    
    # If using Docker
    if command -v docker-compose &> /dev/null; then
        echo "Docker containers status:"
        docker-compose ps
    fi
}

# Main update process
main_update() {
    print_info "Starting update process..."
    echo ""
    
    # Check git status
    check_git_status
    
    # Run checks
    pre_deployment_checks
    
    # Get commit message
    get_commit_message
    
    # Git operations
    git_operations
    
    # Deployment options
    echo ""
    echo "Choose deployment method:"
    echo "1) Railway (auto-deploy from GitHub)"
    echo "2) Vercel (auto-deploy from GitHub)"
    echo "3) Docker (manual rebuild)"
    echo "4) Git push only (no deployment)"
    echo ""
    read -p "Enter your choice [1-4]: " deploy_choice
    
    case $deploy_choice in
        1)
            deploy_railway
            ;;
        2)
            deploy_vercel
            ;;
        3)
            deploy_docker
            ;;
        4)
            print_status "Git push completed. No deployment triggered."
            ;;
        *)
            print_warning "Invalid choice. Skipping deployment."
            ;;
    esac
    
    # Check status
    check_deployment_status
    
    print_status "🎉 Update process completed!"
    echo ""
    echo "Your changes have been deployed. It may take a few minutes for changes to appear live."
    echo ""
    echo "Next steps:"
    echo "1. Test your live application"
    echo "2. Monitor for any errors"
    echo "3. Check application logs if needed"
}

# Quick update (skip checks)
quick_update() {
    print_warning "Quick update mode - skipping pre-deployment checks"
    
    get_commit_message
    git_operations
    
    print_status "Quick update completed! Check your hosting platform for deployment status."
}

# Main menu
if [[ "$1" == "--quick" ]] || [[ "$1" == "-q" ]]; then
    quick_update
else
    main_update
fi
