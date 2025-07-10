from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Organization, OrganizationEmailAlias, EmailForwardingRule, Section
from datetime import datetime
import re

email_management_bp = Blueprint('email_management', __name__)

def get_current_user_and_org():
    """Helper function to get current user and organization from JWT"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    organization_id = claims.get('organization_id')
    
    user = User.query.get(current_user_id)
    organization = Organization.query.get(organization_id) if organization_id else None
    
    return user, organization

def is_admin(user, organization_id):
    """Check if user is admin in the specified organization"""
    if not user or not organization_id:
        return False
    return user.get_role_in_organization(organization_id) == 'Admin'

def validate_email_alias(alias_name):
    """Validate email alias name format"""
    # Allow alphanumeric, hyphens, and underscores, 3-20 characters
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{2,19}$'
    return re.match(pattern, alias_name) is not None

@email_management_bp.route('/aliases', methods=['GET'])
@jwt_required()
def get_email_aliases():
    """Get all email aliases for the current organization"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    aliases = OrganizationEmailAlias.query.filter_by(
        organization_id=organization.id,
        is_active=True
    ).all()
    
    result = []
    for alias in aliases:
        forwarding_rules = EmailForwardingRule.query.filter_by(
            alias_id=alias.id,
            is_active=True
        ).all()
        
        alias_data = {
            'id': alias.id,
            'alias_name': alias.alias_name,
            'email_address': alias.email_address,
            'alias_type': alias.alias_type,
            'section_id': alias.section_id,
            'section_name': alias.section.name if alias.section else None,
            'created_at': alias.created_at.isoformat(),
            'forwarding_rules': [
                {
                    'id': rule.id,
                    'forward_to_type': rule.forward_to_type,
                    'user_id': rule.user_id,
                    'user_name': rule.user.name if rule.user else None,
                    'section_id': rule.section_id,
                    'section_name': rule.section.name if rule.section else None,
                    'role_filter': rule.role_filter
                }
                for rule in forwarding_rules
            ]
        }
        result.append(alias_data)
    
    return jsonify(result)

@email_management_bp.route('/aliases', methods=['POST'])
@jwt_required()
def create_email_alias():
    """Create a new email alias (Admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    alias_name = data.get('alias_name', '').lower().strip()
    alias_type = data.get('alias_type', 'organization')
    section_id = data.get('section_id')
    
    # Validate alias name
    if not validate_email_alias(alias_name):
        return jsonify({'error': 'Invalid alias name. Use 3-20 characters, alphanumeric, hyphens, and underscores only.'}), 400
    
    # Check if alias already exists
    org_safe_name = organization.name.lower().replace(' ', '').replace('-', '').replace('_', '')[:15]
    email_address = f"{alias_name}@{org_safe_name}.bandsync.com"
    
    existing = OrganizationEmailAlias.query.filter_by(email_address=email_address).first()
    if existing:
        return jsonify({'error': 'Email alias already exists'}), 400
    
    # Validate section if provided
    if section_id:
        section = Section.query.filter_by(id=section_id, organization_id=organization.id).first()
        if not section:
            return jsonify({'error': 'Section not found'}), 404
    
    try:
        # Create alias
        alias = OrganizationEmailAlias(
            organization_id=organization.id,
            alias_name=alias_name,
            email_address=email_address,
            alias_type=alias_type,
            section_id=section_id,
            created_by=user.id
        )
        db.session.add(alias)
        db.session.flush()  # Get the alias ID
        
        # Create default forwarding rule
        forward_to_type = 'section_members' if section_id else 'all_members'
        forwarding_rule = EmailForwardingRule(
            alias_id=alias.id,
            forward_to_type=forward_to_type,
            section_id=section_id
        )
        db.session.add(forwarding_rule)
        
        db.session.commit()
        
        return jsonify({
            'id': alias.id,
            'alias_name': alias.alias_name,
            'email_address': alias.email_address,
            'alias_type': alias.alias_type,
            'section_id': alias.section_id,
            'message': 'Email alias created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create email alias'}), 500

@email_management_bp.route('/aliases/<int:alias_id>', methods=['PUT'])
@jwt_required()
def update_email_alias(alias_id):
    """Update an email alias (Admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    alias = OrganizationEmailAlias.query.filter_by(
        id=alias_id,
        organization_id=organization.id
    ).first()
    
    if not alias:
        return jsonify({'error': 'Email alias not found'}), 404
    
    data = request.get_json()
    is_active = data.get('is_active', alias.is_active)
    
    try:
        alias.is_active = is_active
        db.session.commit()
        
        return jsonify({
            'message': 'Email alias updated successfully',
            'is_active': alias.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update email alias'}), 500

@email_management_bp.route('/aliases/<int:alias_id>', methods=['DELETE'])
@jwt_required()
def delete_email_alias(alias_id):
    """Delete an email alias (Admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    alias = OrganizationEmailAlias.query.filter_by(
        id=alias_id,
        organization_id=organization.id
    ).first()
    
    if not alias:
        return jsonify({'error': 'Email alias not found'}), 404
    
    # Don't allow deletion of main organization alias
    if alias.alias_name == 'main':
        return jsonify({'error': 'Cannot delete main organization alias'}), 400
    
    try:
        db.session.delete(alias)
        db.session.commit()
        
        return jsonify({'message': 'Email alias deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete email alias'}), 500

@email_management_bp.route('/aliases/<int:alias_id>/forwarding-rules', methods=['POST'])
@jwt_required()
def create_forwarding_rule(alias_id):
    """Create a forwarding rule for an email alias (Admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    alias = OrganizationEmailAlias.query.filter_by(
        id=alias_id,
        organization_id=organization.id
    ).first()
    
    if not alias:
        return jsonify({'error': 'Email alias not found'}), 404
    
    data = request.get_json()
    forward_to_type = data.get('forward_to_type', 'all_members')
    user_id = data.get('user_id')
    section_id = data.get('section_id')
    role_filter = data.get('role_filter')
    
    # Validate forwarding rule
    valid_types = ['all_members', 'specific_user', 'section_members', 'role_based']
    if forward_to_type not in valid_types:
        return jsonify({'error': 'Invalid forward_to_type'}), 400
    
    if forward_to_type == 'specific_user' and not user_id:
        return jsonify({'error': 'user_id required for specific_user forwarding'}), 400
    
    if forward_to_type == 'section_members' and not section_id:
        return jsonify({'error': 'section_id required for section_members forwarding'}), 400
    
    try:
        forwarding_rule = EmailForwardingRule(
            alias_id=alias_id,
            forward_to_type=forward_to_type,
            user_id=user_id,
            section_id=section_id,
            role_filter=role_filter
        )
        db.session.add(forwarding_rule)
        db.session.commit()
        
        return jsonify({
            'id': forwarding_rule.id,
            'forward_to_type': forwarding_rule.forward_to_type,
            'user_id': forwarding_rule.user_id,
            'section_id': forwarding_rule.section_id,
            'role_filter': forwarding_rule.role_filter,
            'message': 'Forwarding rule created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create forwarding rule'}), 500

@email_management_bp.route('/forwarding-rules/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_forwarding_rule(rule_id):
    """Delete a forwarding rule (Admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get rule and verify it belongs to this organization
    rule = EmailForwardingRule.query.join(OrganizationEmailAlias).filter(
        EmailForwardingRule.id == rule_id,
        OrganizationEmailAlias.organization_id == organization.id
    ).first()
    
    if not rule:
        return jsonify({'error': 'Forwarding rule not found'}), 404
    
    try:
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({'message': 'Forwarding rule deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete forwarding rule'}), 500

@email_management_bp.route('/test-alias/<int:alias_id>', methods=['POST'])
@jwt_required()
def test_email_alias(alias_id):
    """Test an email alias by sending a test message (Admin only)"""
    user, organization = get_current_user_and_org()
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    if not is_admin(user, organization.id):
        return jsonify({'error': 'Admin access required'}), 403
    
    alias = OrganizationEmailAlias.query.filter_by(
        id=alias_id,
        organization_id=organization.id
    ).first()
    
    if not alias:
        return jsonify({'error': 'Email alias not found'}), 404
    
    # TODO: Implement actual email sending logic
    # For now, just return success message
    
    return jsonify({
        'message': f'Test email would be sent from {alias.email_address}',
        'alias_name': alias.alias_name,
        'email_address': alias.email_address
    })
