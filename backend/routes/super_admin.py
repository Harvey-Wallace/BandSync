from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Organization, Event, UserOrganization, db
from utils.admin_utils import is_super_admin, get_admin_context
from sqlalchemy import func

super_admin_bp = Blueprint('super_admin', __name__)

@super_admin_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_super_admin_overview():
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Get all organizations with stats
        organizations = db.session.query(
            Organization,
            func.count(User.id).label('user_count'),
            func.count(Event.id).label('event_count')
        ).outerjoin(User, Organization.id == User.organization_id)\
         .outerjoin(Event, Organization.id == Event.organization_id)\
         .group_by(Organization.id)\
         .all()
        
        org_data = []
        for org, user_count, event_count in organizations:
            # Get multi-org user count
            multi_org_count = db.session.query(func.count(UserOrganization.user_id))\
                .filter(UserOrganization.organization_id == org.id)\
                .scalar() or 0
            
            total_users = max(user_count, multi_org_count)
            
            org_data.append({
                'id': org.id,
                'name': org.name,
                'created_at': org.created_at.isoformat() if org.created_at else None,
                'user_count': total_users,
                'event_count': event_count or 0
            })
        
        # Get overall stats
        total_users = User.query.count()
        total_events = Event.query.count()
        total_organizations = Organization.query.count()
        
        return jsonify({
            'organizations': org_data,
            'stats': {
                'total_users': total_users,
                'total_events': total_events,
                'total_organizations': total_organizations
            }
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error fetching overview: {str(e)}'}), 500

@super_admin_bp.route('/organization/<int:org_id>/details', methods=['GET'])
@jwt_required()
def get_organization_details(org_id):
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        org = Organization.query.get(org_id)
        if not org:
            return jsonify({'msg': 'Organization not found'}), 404
        
        # Get users in this organization
        users = db.session.query(User).join(
            UserOrganization, User.id == UserOrganization.user_id
        ).filter(UserOrganization.organization_id == org_id).all()
        
        # Also get legacy users
        legacy_users = User.query.filter_by(organization_id=org_id).all()
        
        # Combine and deduplicate
        all_users = {user.id: user for user in users + legacy_users}
        
        user_data = []
        for user in all_users.values():
            # Get user's role in this organization
            user_org = UserOrganization.query.filter_by(
                user_id=user.id,
                organization_id=org_id
            ).first()
            
            role = user_org.role if user_org else user.role
            
            user_data.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'role': role,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_active': user.last_active.isoformat() if user.last_active else None
            })
        
        # Get events in this organization
        events = Event.query.filter_by(organization_id=org_id).all()
        event_data = []
        for event in events:
            event_data.append({
                'id': event.id,
                'title': event.title,
                'date': event.date.isoformat(),
                'created_at': event.created_at.isoformat() if event.created_at else None,
                'created_by': event.created_by
            })
        
        return jsonify({
            'organization': {
                'id': org.id,
                'name': org.name,
                'created_at': org.created_at.isoformat() if org.created_at else None
            },
            'users': user_data,
            'events': event_data
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error fetching organization details: {str(e)}'}), 500

@super_admin_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    search_term = request.args.get('q', '')
    
    try:
        users = User.query.filter(
            (User.username.contains(search_term)) |
            (User.name.contains(search_term)) |
            (User.email.contains(search_term))
        ).limit(50).all()
        
        user_data = []
        for user in users:
            # Get user's organizations
            user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
            organizations = []
            for uo in user_orgs:
                organizations.append({
                    'id': uo.organization_id,
                    'name': uo.organization.name,
                    'role': uo.role
                })
            
            # Add legacy organization if exists
            if user.organization_id:
                legacy_org = Organization.query.get(user.organization_id)
                if legacy_org:
                    organizations.append({
                        'id': legacy_org.id,
                        'name': legacy_org.name,
                        'role': user.role
                    })
            
            user_data.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'super_admin': user.super_admin,
                'organizations': organizations
            })
        
        return jsonify({'users': user_data})
        
    except Exception as e:
        return jsonify({'msg': f'Error searching users: {str(e)}'}), 500

@super_admin_bp.route('/troubleshoot/user/<int:target_user_id>', methods=['GET'])
@jwt_required()
def troubleshoot_user(target_user_id):
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        user = User.query.get(target_user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        # Get comprehensive user info
        user_orgs = UserOrganization.query.filter_by(user_id=target_user_id).all()
        
        organizations = []
        for uo in user_orgs:
            organizations.append({
                'id': uo.organization_id,
                'name': uo.organization.name,
                'role': uo.role,
                'is_active': uo.is_active,
                'section_id': uo.section_id
            })
        
        # Get legacy organization
        legacy_org = None
        if user.organization_id:
            legacy_org = Organization.query.get(user.organization_id)
        
        # Get recent events user has access to
        recent_events = []
        for uo in user_orgs:
            events = Event.query.filter_by(organization_id=uo.organization_id)\
                .order_by(Event.date.desc()).limit(5).all()
            for event in events:
                recent_events.append({
                    'id': event.id,
                    'title': event.title,
                    'date': event.date.isoformat(),
                    'organization': uo.organization.name
                })
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'super_admin': user.super_admin,
                'organization_id': user.organization_id,
                'primary_organization_id': user.primary_organization_id,
                'current_organization_id': user.current_organization_id,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_active': user.last_active.isoformat() if user.last_active else None
            },
            'organizations': organizations,
            'legacy_organization': {
                'id': legacy_org.id,
                'name': legacy_org.name
            } if legacy_org else None,
            'recent_events': recent_events
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error troubleshooting user: {str(e)}'}), 500
