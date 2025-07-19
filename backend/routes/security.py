"""
Phase 3 Security & Compliance: Audit Trail System
Comprehensive audit logging and security event tracking for enterprise compliance.
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, desc, or_, and_
from functools import wraps
import json
import socket
import hashlib

from models import db, User, Organization, AuditLog, SecurityEvent, DataPrivacyRequest, UserSession, SecurityPolicy
from routes.super_admin import is_super_admin

# Phase 3 Security Blueprint
security_bp = Blueprint('security', __name__)

# =============================================================================
# AUDIT LOGGING UTILITIES
# =============================================================================

def get_client_ip():
    """Get the real client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_session_id():
    """Get or generate a session identifier"""
    if hasattr(g, 'session_id'):
        return g.session_id
    # Generate session ID from user agent and IP
    user_agent = request.headers.get('User-Agent', '')
    ip_address = get_client_ip()
    session_data = f"{user_agent}{ip_address}{datetime.utcnow().strftime('%Y%m%d')}"
    return hashlib.md5(session_data.encode()).hexdigest()

def log_audit_event(action_type, resource_type, resource_id=None, details=None, user_id=None, organization_id=None):
    """
    Log an audit event to the database
    
    Args:
        action_type: Type of action (login, logout, create, update, delete, view, etc.)
        resource_type: Type of resource (user, event, organization, etc.)
        resource_id: ID of the affected resource
        details: Additional details as a dictionary
        user_id: User who performed the action (if different from current user)
        organization_id: Organization context
    """
    try:
        # Get current user if not specified
        if user_id is None:
            try:
                user_id = get_jwt_identity()
            except:
                user_id = None
        
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            session_id=get_session_id(),
            organization_id=organization_id
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Audit logging error: {e}")
        db.session.rollback()
        return False

def log_security_event(event_type, severity, details=None, user_id=None, source_ip=None):
    """
    Log a security event
    
    Args:
        event_type: Type of security event (failed_login, brute_force, suspicious_activity, etc.)
        severity: Severity level (low, medium, high, critical)
        details: Additional details as a dictionary
        user_id: User involved (if any)
        source_ip: Source IP address
    """
    try:
        if source_ip is None:
            source_ip = get_client_ip()
            
        security_event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            details=details
        )
        
        db.session.add(security_event)
        db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Security event logging error: {e}")
        db.session.rollback()
        return False

def audit_required(action_type, resource_type):
    """
    Decorator to automatically log audit events for API endpoints
    
    Usage:
        @audit_required('view', 'user_list')
        def get_users():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            result = f(*args, **kwargs)
            
            # Log the audit event after successful execution
            try:
                # Extract resource ID from kwargs or response if available
                resource_id = kwargs.get('id') or kwargs.get('user_id') or kwargs.get('organization_id')
                
                # Try to get organization context
                organization_id = None
                try:
                    user_id = get_jwt_identity()
                    if user_id:
                        # Get user's current organization context
                        # This could be enhanced to get the actual organization from the request
                        pass
                except:
                    pass
                
                log_audit_event(
                    action_type=action_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'url': request.url
                    },
                    organization_id=organization_id
                )
            except Exception as e:
                print(f"Audit decorator error: {e}")
            
            return result
        return decorated_function
    return decorator

# =============================================================================
# AUDIT TRAIL API ENDPOINTS
# =============================================================================

@security_bp.route('/audit-log', methods=['GET'])
@jwt_required()
def get_audit_log():
    """Get audit log entries with filtering and pagination"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)  # Max 200 per page
        
        # Filtering parameters
        action_type = request.args.get('action_type')
        resource_type = request.args.get('resource_type')
        user_filter = request.args.get('user_id', type=int)
        organization_filter = request.args.get('organization_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        ip_address = request.args.get('ip_address')
        
        # Build query
        query = AuditLog.query
        
        # Apply filters
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if user_filter:
            query = query.filter(AuditLog.user_id == user_filter)
        if organization_filter:
            query = query.filter(AuditLog.organization_id == organization_filter)
        if ip_address:
            query = query.filter(AuditLog.ip_address == ip_address)
            
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                return jsonify({'msg': 'Invalid start_date format'}), 400
                
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp <= end_dt)
            except ValueError:
                return jsonify({'msg': 'Invalid end_date format'}), 400
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Get summary statistics
        total_entries = AuditLog.query.count()
        unique_users = db.session.query(AuditLog.user_id).distinct().count()
        recent_entries = AuditLog.query.filter(
            AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Log this audit log access
        log_audit_event(
            action_type='view',
            resource_type='audit_log',
            details={
                'filters_applied': {
                    'action_type': action_type,
                    'resource_type': resource_type,
                    'user_id': user_filter,
                    'organization_id': organization_filter,
                    'ip_address': ip_address,
                    'date_range': f"{start_date} to {end_date}" if start_date or end_date else None
                },
                'page': page,
                'per_page': per_page
            }
        )
        
        return jsonify({
            'audit_logs': [log.to_dict() for log in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'summary': {
                'total_entries': total_entries,
                'unique_users': unique_users,
                'recent_entries_24h': recent_entries
            },
            'filters': {
                'available_actions': [
                    'login', 'logout', 'create', 'update', 'delete', 'view', 
                    'impersonate', 'export', 'admin_action'
                ],
                'available_resources': [
                    'user', 'event', 'organization', 'audit_log', 'system', 
                    'security_event', 'privacy_request'
                ]
            }
        })
        
    except Exception as e:
        print(f"Audit log retrieval error: {e}")
        return jsonify({'msg': f'Error retrieving audit log: {str(e)}'}), 500

@security_bp.route('/security-events', methods=['GET'])
@jwt_required()
def get_security_events():
    """Get security events with filtering"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        severity = request.args.get('severity')
        event_type = request.args.get('event_type')
        resolved = request.args.get('resolved', type=bool)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = SecurityEvent.query
        
        # Apply filters
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        if resolved is not None:
            query = query.filter(SecurityEvent.resolved == resolved)
            
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(SecurityEvent.timestamp >= start_dt)
            except ValueError:
                return jsonify({'msg': 'Invalid start_date format'}), 400
                
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(SecurityEvent.timestamp <= end_dt)
            except ValueError:
                return jsonify({'msg': 'Invalid end_date format'}), 400
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(SecurityEvent.timestamp))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Get summary statistics
        total_events = SecurityEvent.query.count()
        unresolved_critical = SecurityEvent.query.filter(
            and_(SecurityEvent.severity == 'critical', SecurityEvent.resolved == False)
        ).count()
        recent_events = SecurityEvent.query.filter(
            SecurityEvent.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Log this security event access
        log_audit_event(
            action_type='view',
            resource_type='security_events',
            details={
                'filters_applied': {
                    'severity': severity,
                    'event_type': event_type,
                    'resolved': resolved
                }
            }
        )
        
        return jsonify({
            'security_events': [event.to_dict() for event in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'summary': {
                'total_events': total_events,
                'unresolved_critical': unresolved_critical,
                'recent_events_24h': recent_events
            }
        })
        
    except Exception as e:
        print(f"Security events retrieval error: {e}")
        return jsonify({'msg': f'Error retrieving security events: {str(e)}'}), 500

@security_bp.route('/security-events/<int:event_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_security_event(event_id):
    """Mark a security event as resolved"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        security_event = SecurityEvent.query.get_or_404(event_id)
        
        if security_event.resolved:
            return jsonify({'msg': 'Security event already resolved'}), 400
        
        security_event.resolved = True
        security_event.resolved_by = user_id
        security_event.resolved_at = datetime.utcnow()
        
        # Add resolution notes to details
        if not security_event.details:
            security_event.details = {}
        security_event.details['resolution_notes'] = notes
        
        db.session.commit()
        
        # Log this resolution
        log_audit_event(
            action_type='update',
            resource_type='security_event',
            resource_id=event_id,
            details={
                'action': 'resolved',
                'notes': notes,
                'event_type': security_event.event_type,
                'severity': security_event.severity
            }
        )
        
        return jsonify({
            'msg': 'Security event resolved successfully',
            'event': security_event.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Security event resolution error: {e}")
        return jsonify({'msg': f'Error resolving security event: {str(e)}'}), 500

# =============================================================================
# AUDIT TRAIL SUMMARY ENDPOINT
# =============================================================================

@security_bp.route('/audit-summary', methods=['GET'])
@jwt_required()
def get_audit_summary():
    """Get comprehensive audit trail summary"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Audit log statistics
        total_audit_entries = AuditLog.query.count()
        audit_24h = AuditLog.query.filter(AuditLog.timestamp >= last_24h).count()
        audit_7d = AuditLog.query.filter(AuditLog.timestamp >= last_7d).count()
        audit_30d = AuditLog.query.filter(AuditLog.timestamp >= last_30d).count()
        
        # Security event statistics
        total_security_events = SecurityEvent.query.count()
        unresolved_events = SecurityEvent.query.filter(SecurityEvent.resolved == False).count()
        critical_events = SecurityEvent.query.filter(
            and_(SecurityEvent.severity == 'critical', SecurityEvent.resolved == False)
        ).count()
        
        # Recent activity breakdown
        recent_actions = db.session.query(
            AuditLog.action_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= last_24h
        ).group_by(AuditLog.action_type).all()
        
        # Top users by activity
        top_users = db.session.query(
            AuditLog.user_id,
            User.username,
            func.count(AuditLog.id).label('activity_count')
        ).join(User).filter(
            AuditLog.timestamp >= last_7d
        ).group_by(AuditLog.user_id, User.username).order_by(
            desc(func.count(AuditLog.id))
        ).limit(10).all()
        
        # Security trends
        security_trends = db.session.query(
            SecurityEvent.severity,
            func.count(SecurityEvent.id).label('count')
        ).filter(
            SecurityEvent.timestamp >= last_7d
        ).group_by(SecurityEvent.severity).all()
        
        return jsonify({
            'audit_statistics': {
                'total_entries': total_audit_entries,
                'entries_24h': audit_24h,
                'entries_7d': audit_7d,
                'entries_30d': audit_30d,
                'growth_rate_24h': round((audit_24h / max(audit_7d - audit_24h, 1)) * 100, 2)
            },
            'security_statistics': {
                'total_events': total_security_events,
                'unresolved_events': unresolved_events,
                'critical_unresolved': critical_events,
                'resolution_rate': round(((total_security_events - unresolved_events) / max(total_security_events, 1)) * 100, 2)
            },
            'recent_activity': {
                'actions_24h': [{'action': action, 'count': count} for action, count in recent_actions],
                'top_users_7d': [
                    {'user_id': user_id, 'username': username, 'activity_count': count} 
                    for user_id, username, count in top_users
                ]
            },
            'security_trends': {
                'severity_breakdown_7d': [{'severity': severity, 'count': count} for severity, count in security_trends]
            },
            'generated_at': now.isoformat()
        })
        
    except Exception as e:
        print(f"Audit summary error: {e}")
        return jsonify({'msg': f'Error generating audit summary: {str(e)}'}), 500
