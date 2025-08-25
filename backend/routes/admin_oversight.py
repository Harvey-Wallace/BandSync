"""
Simple Admin Oversight Routes for Harvey258
Clean, minimal implementation without super admin complexity
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Organization, UserOrganization
from sqlalchemy import func
from datetime import datetime

admin_oversight = Blueprint('admin_oversight', __name__)

@admin_oversight.route('/admin-oversight/health', methods=['GET'])
def health_check():
    """Simple health check for admin oversight routes."""
    return jsonify({'status': 'healthy', 'service': 'admin_oversight'})

@admin_oversight.route('/admin-oversight/debug/user/<username>', methods=['GET'])
@jwt_required()
def debug_user_organizations(username):
    """Debug endpoint to check specific user's organization relationships."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        print(f"Debugging user: {username}")
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': f'User {username} not found'}), 404
        
        # Get user's organization relationships
        user_orgs = db.session.query(
            UserOrganization.id,
            UserOrganization.role,
            UserOrganization.joined_at,
            UserOrganization.is_active,
            Organization.name.label('org_name'),
            Organization.id.label('org_id')
        ).join(Organization).filter(UserOrganization.user_id == user.id).all()
        
        # Get all organizations (to see what exists)
        all_orgs = Organization.query.all()
        
        # Check legacy organization fields
        legacy_org = None
        if user.organization_id:
            legacy_org = Organization.query.get(user.organization_id)
        
        current_org = None
        if user.current_organization_id:
            current_org = Organization.query.get(user.current_organization_id)
            
        primary_org = None
        if user.primary_organization_id:
            primary_org = Organization.query.get(user.primary_organization_id)
        
        debug_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'organization_id': user.organization_id,
                'current_organization_id': user.current_organization_id,
                'primary_organization_id': user.primary_organization_id
            },
            'legacy_organization': legacy_org.name if legacy_org else None,
            'current_organization': current_org.name if current_org else None,
            'primary_organization': primary_org.name if primary_org else None,
            'user_organization_relationships': [
                {
                    'id': uo.id,
                    'organization_name': uo.org_name,
                    'organization_id': uo.org_id,
                    'role': uo.role,
                    'joined_at': uo.joined_at.isoformat() if uo.joined_at else None,
                    'is_active': uo.is_active
                }
                for uo in user_orgs
            ],
            'all_organizations': [
                {
                    'id': org.id,
                    'name': org.name
                }
                for org in all_orgs
            ]
        }
        
        print(f"Debug data for {username}:", debug_data)
        return jsonify(debug_data)
        
    except Exception as e:
        print(f"Error debugging user {username}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Debug error: {str(e)}'}), 500

def is_harvey_admin():
    """Check if current user is Harvey258 with admin oversight privileges."""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return False
        
        user = User.query.get(current_user_id)
        return user and user.username == 'Harvey258'
    except Exception as e:
        print(f"Error in is_harvey_admin: {e}")
        return False

@admin_oversight.route('/admin-oversight/dashboard', methods=['GET'])
@jwt_required()
def get_oversight_dashboard():
    """Get system overview dashboard for Harvey258."""
    
    try:
        current_user_id = get_jwt_identity()
        print(f"Admin oversight dashboard request from user ID: {current_user_id}")
        
        if not is_harvey_admin():
            user = User.query.get(current_user_id) if current_user_id else None
            username = user.username if user else "unknown"
            print(f"Access denied for user: {username} (ID: {current_user_id})")
            return jsonify({'error': 'Access denied - Harvey258 only'}), 403
        
        print("Harvey258 access granted, fetching dashboard data...")
        
        # Get overview statistics
        total_orgs = Organization.query.count()
        total_users = User.query.count()
        
        print(f"Found {total_orgs} orgs, {total_users} users")
        
        # Get recent organizations
        recent_orgs = Organization.query.order_by(Organization.created_at.desc()).limit(5).all()
        
        # Get organizations with user counts
        org_stats = db.session.query(
            Organization.id,
            Organization.name,
            Organization.created_at,
            func.count(UserOrganization.user_id).label('user_count')
        ).outerjoin(UserOrganization).group_by(Organization.id).all()
        
        dashboard_data = {
            'stats': {
                'total_organizations': total_orgs,
                'total_users': total_users,
                'last_updated': datetime.utcnow().isoformat()
            },
            'recent_organizations': [
                {
                    'id': org.id,
                    'name': org.name,
                    'created_at': org.created_at.isoformat() if org.created_at else None
                }
                for org in recent_orgs
            ],
            'organization_stats': [
                {
                    'id': stat.id,
                    'name': stat.name,
                    'user_count': stat.user_count,
                    'created_at': stat.created_at.isoformat() if stat.created_at else None
                }
                for stat in org_stats
            ]
        }
        
        print(f"Dashboard data prepared successfully")
        return jsonify(dashboard_data)
        
    except Exception as e:
        print(f"Error in get_oversight_dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Dashboard error: {str(e)}'}), 500

@admin_oversight.route('/admin-oversight/organizations', methods=['GET'])
@jwt_required()
def get_all_organizations():
    """Get all organizations with their users."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        organizations = Organization.query.all()
        
        org_data = []
        for org in organizations:
            # Get users for this organization
            users = db.session.query(User, UserOrganization.role).join(
                UserOrganization, User.id == UserOrganization.user_id
            ).filter(UserOrganization.organization_id == org.id).all()
            
            org_data.append({
                'id': org.id,
                'name': org.name,
                'description': getattr(org, 'description', ''),
                'created_at': org.created_at.isoformat() if org.created_at else None,
                'user_count': len(users),
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'name': user.name,
                        'role': role
                    }
                    for user, role in users
                ]
            })
        
        return jsonify({
            'organizations': org_data,
            'total': len(org_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/admin-oversight/organizations/<int:org_id>', methods=['PUT'])
@jwt_required()
def update_organization(org_id):
    """Update organization information."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        organization = Organization.query.get(org_id)
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
        
        data = request.get_json()
        
        # Update basic fields
        if 'name' in data:
            organization.name = data['name']
        if 'description' in data:
            organization.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Organization updated successfully',
            'organization': {
                'id': organization.id,
                'name': organization.name,
                'description': getattr(organization, 'description', '')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/admin-oversight/organizations/<int:org_id>', methods=['DELETE'])
@jwt_required()
def delete_organization(org_id):
    """Delete an organization and all related data."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        organization = Organization.query.get(org_id)
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
        
        org_name = organization.name
        
        # Delete related records first (cascade should handle this, but being explicit)
        UserOrganization.query.filter_by(organization_id=org_id).delete()
        
        # Delete the organization
        db.session.delete(organization)
        db.session.commit()
        
        return jsonify({
            'message': f'Organization "{org_name}" deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/admin-oversight/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users in the system."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        users = User.query.all()
        
        user_data = []
        for user in users:
            # Get user's organizations
            user_orgs = db.session.query(Organization.name, UserOrganization.role).join(
                UserOrganization, Organization.id == UserOrganization.organization_id
            ).filter(UserOrganization.user_id == user.id).all()
            
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'created_at': getattr(user, 'created_at', None),
                'organizations': [
                    {
                        'name': org_name,
                        'role': role
                    }
                    for org_name, role in user_orgs
                ]
            })
        
        return jsonify({
            'users': user_data,
            'total': len(user_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/admin-oversight/fix/add-user-to-org', methods=['POST'])
@jwt_required()
def add_user_to_organization():
    """Add a user to an organization - Harvey258 only."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        data = request.get_json()
        username = data.get('username')
        org_name = data.get('organization_name')
        role = data.get('role', 'Member')
        
        if not username or not org_name:
            return jsonify({'error': 'Username and organization_name required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': f'User {username} not found'}), 404
        
        # Find organization
        organization = Organization.query.filter_by(name=org_name).first()
        if not organization:
            return jsonify({'error': f'Organization {org_name} not found'}), 404
        
        # Check if relationship already exists
        existing = UserOrganization.query.filter_by(
            user_id=user.id, 
            organization_id=organization.id
        ).first()
        
        if existing:
            return jsonify({
                'message': f'{username} is already in {org_name}',
                'existing_role': existing.role,
                'is_active': existing.is_active
            })
        
        # Create new relationship
        user_org = UserOrganization(
            user_id=user.id,
            organization_id=organization.id,
            role=role,
            is_active=True
        )
        
        db.session.add(user_org)
        
        # Update user's current organization if they don't have one
        if not user.current_organization_id:
            user.current_organization_id = organization.id
        
        # Update user's primary organization if they don't have one
        if not user.primary_organization_id:
            user.primary_organization_id = organization.id
            
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully added {username} to {org_name} as {role}',
            'user_id': user.id,
            'organization_id': organization.id,
            'role': role
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
