from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import User, Organization, Event, UserOrganization, EmailLog, db
from utils.admin_utils import is_super_admin, get_admin_context
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash
import secrets
import string
from datetime import datetime, timedelta

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

@super_admin_bp.route('/user/<int:target_user_id>/reset-password', methods=['POST'])
@jwt_required()
def reset_user_password(target_user_id):
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        user = User.query.get(target_user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        data = request.get_json() or {}
        new_password = data.get('new_password')
        
        if not new_password:
            # Generate a temporary password
            new_password = f"temp_{user.username}123"
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({
            'msg': 'Password reset successfully',
            'new_password': new_password,
            'is_temporary': not data.get('new_password')
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error resetting password: {str(e)}'}), 500

@super_admin_bp.route('/user/<int:target_user_id>/impersonate', methods=['POST'])
@jwt_required()
def impersonate_user(target_user_id):
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        user = User.query.get(target_user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        data = request.get_json() or {}
        organization_id = data.get('organization_id')
        
        # Get user's organization context
        if organization_id:
            # Check if user belongs to this organization
            user_org = UserOrganization.query.filter_by(
                user_id=user.id,
                organization_id=organization_id
            ).first()
            
            if user_org:
                selected_org = user_org.organization
                selected_role = user_org.role
            else:
                # Fallback to legacy organization
                if user.organization_id == organization_id:
                    selected_org = Organization.query.get(organization_id)
                    selected_role = user.role
                else:
                    return jsonify({'msg': 'User does not belong to specified organization'}), 400
        else:
            # Get user's primary organization
            user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
            if user_orgs:
                user_org = user_orgs[0]
                selected_org = user_org.organization
                selected_role = user_org.role
            else:
                # Fallback to legacy
                selected_org = Organization.query.get(user.organization_id) if user.organization_id else None
                selected_role = user.role
        
        if not selected_org:
            return jsonify({'msg': 'User has no organization context'}), 400
        
        # Create impersonation token
        impersonation_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': selected_role,
                'organization_id': selected_org.id,
                'organization': selected_org.name,
                'super_admin': getattr(user, 'super_admin', False),
                'impersonated_by': user_id
            }
        )
        
        return jsonify({
            'msg': f'Impersonating user {user.username}',
            'impersonation_token': impersonation_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email
            },
            'organization': {
                'id': selected_org.id,
                'name': selected_org.name
            },
            'role': selected_role
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error impersonating user: {str(e)}'}), 500

@super_admin_bp.route('/users/bulk-operations', methods=['POST'])
@jwt_required()
def bulk_user_operations():
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        data = request.get_json()
        operation = data.get('operation')
        user_ids = data.get('user_ids', [])
        
        if not operation or not user_ids:
            return jsonify({'msg': 'Operation and user_ids required'}), 400
        
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if len(users) != len(user_ids):
            return jsonify({'msg': 'Some users not found'}), 404
        
        results = []
        
        if operation == 'disable':
            for user in users:
                user.is_active = False
                results.append(f"Disabled user: {user.username}")
                
        elif operation == 'enable':
            for user in users:
                user.is_active = True
                results.append(f"Enabled user: {user.username}")
                
        elif operation == 'reset_passwords':
            for user in users:
                temp_password = f"temp_{user.username}123"
                user.password_hash = generate_password_hash(temp_password)
                results.append(f"Reset password for: {user.username} -> {temp_password}")
                
        elif operation == 'delete':
            # Soft delete by setting a deleted flag or moving to deleted table
            for user in users:
                user.is_active = False
                # Add a note that it was deleted by Super Admin
                user.notes = f"Deleted by Super Admin on {db.func.now()}"
                results.append(f"Deleted user: {user.username}")
                
        else:
            return jsonify({'msg': f'Unknown operation: {operation}'}), 400
        
        db.session.commit()
        
        return jsonify({
            'msg': f'Bulk operation {operation} completed',
            'affected_users': len(users),
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error performing bulk operation: {str(e)}'}), 500

@super_admin_bp.route('/system/health', methods=['GET'])
@jwt_required()
def get_system_health():
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    # Initialize variables
    db_health = True
    db_response_time = None
    
    # Database health check
    try:
        import time
        start_time = time.time()
        db.session.execute(db.text('SELECT 1'))
        db_response_time = time.time() - start_time
    except Exception as e:
        db_health = False
        db_response_time = None
    
    try:
        import psutil
        
        # System metrics
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Recent activity
        recent_logins = User.query.filter(
            User.last_login > datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        recent_events = Event.query.filter(
            Event.created_at > datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return jsonify({
            'status': 'healthy' if db_health else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': 'connected' if db_health else 'disconnected',
                'response_time_ms': round(db_response_time * 1000, 2) if db_response_time else None
            },
            'system': system_metrics,
            'activity': {
                'recent_logins_24h': recent_logins,
                'recent_events_24h': recent_events
            }
        })
        
    except ImportError:
        # psutil not available, return basic health
        return jsonify({
            'status': 'limited',
            'message': 'Full system monitoring not available (psutil not installed)',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': 'connected' if db_health else 'disconnected',
                'response_time_ms': round(db_response_time * 1000, 2) if db_response_time else None
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting system health: {str(e)}',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': 'connected' if db_health else 'disconnected',
                'response_time_ms': round(db_response_time * 1000, 2) if db_response_time else None
            }
        }), 500

@super_admin_bp.route('/system/logs', methods=['GET'])
@jwt_required()
def get_system_logs():
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        from datetime import datetime, timedelta
        
        # Get recent email logs as a proxy for system activity
        recent_logs = db.session.query(
            EmailLog.id,
            EmailLog.recipient_email,
            EmailLog.subject,
            EmailLog.status,
            EmailLog.created_at,
            EmailLog.error_message
        ).filter(
            EmailLog.created_at > datetime.utcnow() - timedelta(hours=24)
        ).order_by(EmailLog.created_at.desc()).limit(100).all()
        
        logs = []
        for log in recent_logs:
            logs.append({
                'id': log[0],
                'type': 'email',
                'level': 'error' if log[3] == 'failed' else 'info',
                'message': f"Email to {log[1]}: {log[2]}",
                'status': log[3],
                'timestamp': log[4].isoformat() if log[4] else None,
                'error': log[5] if log[5] else None
            })
        
        return jsonify({
            'logs': logs,
            'total_count': len(logs),
            'timeframe': '24 hours'
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error getting system logs: {str(e)}'}), 500

@super_admin_bp.route('/system/performance', methods=['GET'])
@jwt_required()
def get_system_performance():
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        from datetime import datetime, timedelta
        
        # Database performance metrics
        slow_queries = []  # Would need query logging to populate this
        
        # User activity patterns
        hourly_activity = db.session.execute(db.text("""
            SELECT 
                EXTRACT(hour FROM last_login) as hour,
                COUNT(*) as login_count
            FROM "user" 
            WHERE last_login > NOW() - INTERVAL '7 days'
            GROUP BY EXTRACT(hour FROM last_login)
            ORDER BY hour
        """)).fetchall()
        
        activity_data = [{'hour': int(row[0]) if row[0] else 0, 'logins': row[1]} for row in hourly_activity]
        
        # Organization growth
        org_growth = db.session.execute(db.text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as new_orgs
            FROM "organization" 
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)).fetchall()
        
        growth_data = [{'date': row[0].isoformat() if row[0] else None, 'count': row[1]} for row in org_growth]
        
        return jsonify({
            'performance_metrics': {
                'avg_response_time': None,  # Would need instrumentation
                'error_rate': None,         # Would need error tracking
                'throughput': None          # Would need request tracking
            },
            'user_activity': activity_data,
            'organization_growth': growth_data
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error getting performance metrics: {str(e)}'}), 500
