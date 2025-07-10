from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Organization
from datetime import datetime, timedelta

quick_polls_bp = Blueprint('quick_polls', __name__)

def get_current_user_and_org():
    """Helper function to get current user and organization from JWT"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    organization_id = claims.get('organization_id')
    
    user = User.query.get(current_user_id)
    organization = Organization.query.get(organization_id) if organization_id else None
    
    return user, organization

def is_admin(user, organization_id):
    """Check if user is admin in the organization"""
    if not user or not organization_id:
        return False
    return user.get_role_in_organization(organization_id) == 'Admin'

@quick_polls_bp.route('/', methods=['GET'])
@jwt_required()
def get_quick_polls():
    """Get all quick polls for the organization"""
    try:
        user, organization = get_current_user_and_org()
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
        
        # For now, return empty list since QuickPoll model needs to be created
        return jsonify([])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quick_polls_bp.route('/', methods=['POST'])
@jwt_required()
def create_quick_poll():
    """Create a new quick poll"""
    try:
        user, organization = get_current_user_and_org()
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
        
        # Only admins can create polls
        if not is_admin(user, organization.id):
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('question'):
            return jsonify({'error': 'Question is required'}), 400
        
        if not data.get('options') or len(data.get('options', [])) < 2:
            return jsonify({'error': 'At least 2 options are required'}), 400
        
        # For now, return success without creating since models need to be updated
        return jsonify({
            'id': 1,
            'question': data['question'],
            'options': data['options'],
            'anonymous': data.get('anonymous', False),
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quick_polls_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_poll_templates():
    """Get pre-defined poll templates"""
    templates = [
        {
            'name': 'Simple Yes/No',
            'question': 'Do you agree?',
            'options': ['Yes', 'No'],
            'poll_type': 'simple'
        },
        {
            'name': 'Attendance Check',
            'question': 'Will you attend the next rehearsal?',
            'options': ['Yes', 'No', 'Maybe'],
            'poll_type': 'simple'
        },
        {
            'name': 'Performance Feedback',
            'question': 'How would you rate tonight\'s performance?',
            'options': ['Excellent', 'Good', 'Average', 'Needs Improvement'],
            'poll_type': 'simple'
        }
    ]
    
    return jsonify(templates)
