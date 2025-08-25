"""
Simple Admin Oversight Routes for Harvey258
Clean, minimal implementation without super admin complexity
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Organization, UserOrganization
from sqlalchemy import func
from datetime import datetime

admin_oversight = Blueprint('admin_oversight', __name__)

def is_harvey_admin():
    """Check if current user is Harvey258 with admin oversight privileges."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.username == 'Harvey258'

@admin_oversight.route('/api/admin-oversight/dashboard', methods=['GET'])
@jwt_required()
def get_oversight_dashboard():
    """Get system overview dashboard for Harvey258."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get overview statistics
        total_orgs = Organization.query.count()
        total_users = User.query.count()
        
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
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/api/admin-oversight/organizations', methods=['GET'])
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
                        'first_name': user.first_name,
                        'last_name': user.last_name,
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

@admin_oversight.route('/api/admin-oversight/organizations/<int:org_id>', methods=['PUT'])
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

@admin_oversight.route('/api/admin-oversight/organizations/<int:org_id>', methods=['DELETE'])
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

@admin_oversight.route('/api/admin-oversight/users', methods=['GET'])
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
                'first_name': user.first_name,
                'last_name': user.last_name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
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
