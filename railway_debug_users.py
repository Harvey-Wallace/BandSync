#!/usr/bin/env python3
"""
Railway-compatible debug script to investigate user data differences
"""

import os
import sys
import json

# Add the backend directory to Python path
sys.path.insert(0, '/app')

try:
    from app import app, db
    from models import User, Organization, UserOrganization
    
    def debug_user_data(username):
        """Get comprehensive user data for debugging"""
        with app.app_context():
            try:
                # Get user
                user = User.query.filter_by(name=username).first()
                if not user:
                    return {"error": f"User {username} not found"}
                
                result = {
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                        "created_at": str(user.created_at) if hasattr(user, 'created_at') and user.created_at else None
                    }
                }
                
                # Get organization relationships
                user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
                orgs = []
                
                for user_org in user_orgs:
                    org = Organization.query.get(user_org.organization_id)
                    if org:
                        org_data = {
                            "id": org.id,
                            "name": org.name,
                            "description": org.description,
                            "user_role": user_org.role,
                            "joined_at": str(user_org.created_at) if hasattr(user_org, 'created_at') and user_org.created_at else None
                        }
                        
                        # Check for None/null values that might cause React errors
                        null_fields = []
                        for key, value in org_data.items():
                            if value is None:
                                null_fields.append(key)
                        
                        if null_fields:
                            org_data["null_fields"] = null_fields
                        
                        orgs.append(org_data)
                
                result["organizations"] = orgs
                result["organization_count"] = len(orgs)
                
                # Additional checks for potential React error causes
                issues = []
                if len(orgs) == 0:
                    issues.append("NO_ORGANIZATIONS")
                
                for org in orgs:
                    if org.get("name") is None:
                        issues.append("NULL_ORG_NAME")
                    if org.get("description") is None:
                        issues.append("NULL_ORG_DESCRIPTION")
                
                result["potential_issues"] = issues
                
                return result
                
            except Exception as e:
                return {"error": f"Database query failed: {str(e)}"}
    
    def main():
        print("🔍 Debugging Rob123 vs Harvey258 data differences...")
        print("=" * 60)
        
        # Debug both users
        for username in ["Rob123", "Harvey258"]:
            print(f"\n📊 User: {username}")
            print("-" * 40)
            
            data = debug_user_data(username)
            print(json.dumps(data, indent=2, default=str))
            print("\n" + "=" * 60)
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This script should be run in the Railway environment")
    sys.exit(1)
