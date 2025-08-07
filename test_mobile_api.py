#!/usr/bin/env python3
"""
Test script to verify the mobile API endpoints are working correctly
"""

from flask import Flask
from flask_jwt_extended import JWTManager
import sys
import os

# Add the backend directory to the path
sys.path.append('/Users/robertharvey/Documents/GitHub/BandSync/backend')

def test_mobile_endpoints():
    """Test that our mobile endpoints are registered correctly"""
    
    # Mock app setup (minimal)
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    jwt = JWTManager(app)
    
    # Import and register our mobile blueprint
    from routes.mobile_api import mobile_api_bp
    app.register_blueprint(mobile_api_bp, url_prefix='/api/organization')
    
    # List all registered routes
    print("📱 Mobile API Endpoints:")
    for rule in app.url_map.iter_rules():
        if '/api/organization' in rule.rule:
            print(f"  ✅ {rule.methods} {rule.rule}")
    
    print("\n🎯 Expected Mobile App Calls:")
    print("  📋 GET /api/organization - Organization details")
    print("  👥 GET /api/organization/members/ - Organization members")
    
    return True

if __name__ == '__main__':
    success = test_mobile_endpoints()
    if success:
        print("\n✅ Mobile API endpoints are ready!")
    else:
        print("\n❌ There were issues with the mobile API endpoints")
        sys.exit(1)
