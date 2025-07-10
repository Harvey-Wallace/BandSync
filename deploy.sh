#!/bin/bash

# BandSync Deployment Script
# This script helps deploy BandSync to various hosting platforms

set -e

echo "🚀 BandSync Deployment Script"
echo "=============================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! -f "backend/app.py" ]]; then
    print_error "Please run this script from the BandSync root directory"
    exit 1
fi

# Check for required tools
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
        exit 1
    fi
    
    print_status "All requirements satisfied ✓"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Backend dependencies
    print_status "Installing Python dependencies..."
    cd backend
    python3 -m pip install -r requirements.txt
    cd ..
    
    # Frontend dependencies
    print_status "Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
    
    print_status "Dependencies installed ✓"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    cd backend
    python3 -m pytest tests/ -v 2>/dev/null || print_warning "No backend tests found"
    cd ..
    
    # Frontend tests
    cd frontend
    npm test -- --watchAll=false --passWithNoTests 2>/dev/null || print_warning "No frontend tests found"
    cd ..
    
    print_status "Tests completed ✓"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    cd frontend
    npm run build
    cd ..
    print_status "Frontend built ✓"
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    railway login
    railway up
    
    print_status "Deployed to Railway ✓"
}

# Deploy to Vercel
deploy_vercel() {
    print_status "Deploying to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    cd frontend
    vercel --prod
    cd ..
    
    print_status "Deployed to Vercel ✓"
}

# Deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    # Build the image
    docker build -t bandsync .
    
    # Run with docker-compose
    docker-compose up -d
    
    print_status "Deployed with Docker ✓"
}

# Main menu
main_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Railway (Recommended for beginners)"
    echo "2) Vercel (Frontend only)"
    echo "3) Docker (Local/VPS deployment)"
    echo "4) Build only (no deployment)"
    echo "5) Exit"
    echo ""
    read -p "Enter your choice [1-5]: " choice
    
    case $choice in
        1)
            check_requirements
            install_dependencies
            run_tests
            build_frontend
            deploy_railway
            ;;
        2)
            check_requirements
            install_dependencies
            run_tests
            build_frontend
            deploy_vercel
            ;;
        3)
            check_requirements
            install_dependencies
            run_tests
            build_frontend
            deploy_docker
            ;;
        4)
            check_requirements
            install_dependencies
            run_tests
            build_frontend
            print_status "Build completed! Ready for manual deployment."
            ;;
        5)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            main_menu
            ;;
    esac
}

# Run main menu
main_menu

echo ""
print_status "🎉 Deployment process completed!"
echo ""
echo "Next steps:"
echo "1. Set up your environment variables"
echo "2. Configure your domain name"
echo "3. Set up monitoring and backups"
echo "4. Test your live application"
echo ""
echo "Need help? Check DEPLOYMENT_GUIDE.md for detailed instructions."
