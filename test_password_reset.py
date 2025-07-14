#!/usr/bin/env python3
"""
Test password reset functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User
from services.email_service import EmailService
from datetime import datetime, timedelta
import requests
import json

def test_password_reset():
    """Test the complete password reset flow"""
    
    with app.app_context():
        print("🧪 Testing Password Reset Functionality")
        print("=" * 50)
        
        # Create a test user if not exists
        test_email = "rob@harvey-wallace.co.uk"
        test_user = User.query.filter_by(email=test_email).first()
        
        if not test_user:
            print(f"❌ Test user with email {test_email} not found")
            print("Please create a test user first")
            return
        
        print(f"✅ Found test user: {test_user.username} ({test_user.email})")
        
        # Test 1: Password reset request
        print("\n📧 Test 1: Password Reset Request")
        print("-" * 30)
        
        # Simulate the request
        base_url = "http://localhost:5000"  # Adjust if needed
        
        try:
            response = requests.post(f"{base_url}/api/auth/password-reset-request", 
                                   json={"email": test_email})
            
            if response.status_code == 200:
                print("✅ Password reset request successful")
                print(f"Response: {response.json()}")
                
                # Check if token was generated
                updated_user = User.query.filter_by(email=test_email).first()
                if updated_user.password_reset_token:
                    print(f"✅ Reset token generated: {updated_user.password_reset_token[:20]}...")
                    print(f"✅ Token expires: {updated_user.password_reset_expires}")
                    
                    # Test 2: Password reset with token
                    print("\n🔐 Test 2: Password Reset with Token")
                    print("-" * 30)
                    
                    new_password = "newpassword123"
                    reset_response = requests.post(f"{base_url}/api/auth/password-reset", 
                                                 json={
                                                     "token": updated_user.password_reset_token,
                                                     "password": new_password
                                                 })
                    
                    if reset_response.status_code == 200:
                        print("✅ Password reset successful")
                        print(f"Response: {reset_response.json()}")
                        
                        # Test 3: Login with new password
                        print("\n🔓 Test 3: Login with New Password")
                        print("-" * 30)
                        
                        login_response = requests.post(f"{base_url}/api/auth/login", 
                                                     json={
                                                         "email": test_email,
                                                         "password": new_password
                                                     })
                        
                        if login_response.status_code == 200:
                            print("✅ Login with new password successful")
                            print("🎉 Password reset flow completed successfully!")
                        else:
                            print(f"❌ Login failed: {login_response.json()}")
                    else:
                        print(f"❌ Password reset failed: {reset_response.json()}")
                else:
                    print("❌ Reset token not generated")
            else:
                print(f"❌ Password reset request failed: {response.json()}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to the server. Make sure the Flask app is running.")
            print("Run: python app.py")
            return
        except Exception as e:
            print(f"❌ Error testing password reset: {e}")

def test_email_service():
    """Test email service configuration"""
    
    with app.app_context():
        print("\n📧 Testing Email Service")
        print("-" * 30)
        
        email_service = EmailService()
        
        if email_service.client:
            print("✅ Email service configured")
            print(f"✅ From email: {email_service.from_email}")
            print(f"✅ API key: {email_service.api_key[:10]}...")
        else:
            print("❌ Email service not configured")
            print("Check your RESEND_API_KEY environment variable")

if __name__ == "__main__":
    print("🔐 Password Reset Testing Suite")
    print("=" * 50)
    
    test_email_service()
    test_password_reset()
