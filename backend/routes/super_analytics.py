"""
Phase 2 Super Admin: Advanced Analytics Backend
Provides comprehensive analytics and reporting capabilities for system-wide insights.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import func, text, desc, asc
from collections import defaultdict
import calendar

from models import db, User, Organization, Event, UserOrganization, RSVP
from routes.super_admin import is_super_admin

super_analytics_bp = Blueprint('super_analytics', __name__)

@super_analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get comprehensive system analytics overview"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Time periods for analysis
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        last_24_hours = now - timedelta(hours=24)
        
        # User growth metrics
        total_users = User.query.count()
        new_users_30d = User.query.filter(
            User.created_at >= last_30_days if hasattr(User, 'created_at') else True
        ).count()
        new_users_7d = User.query.filter(
            User.created_at >= last_7_days if hasattr(User, 'created_at') else True
        ).count()
        
        # Organization metrics
        total_orgs = Organization.query.count()
        active_orgs_30d = db.session.query(Organization.id).join(Event).filter(
            Event.date >= last_30_days
        ).distinct().count()
        
        # Event metrics
        total_events = Event.query.count()
        events_30d = Event.query.filter(Event.date >= last_30_days).count()
        events_7d = Event.query.filter(Event.date >= last_7_days).count()
        
        # Engagement metrics
        total_rsvps = RSVP.query.count()
        rsvps_30d = RSVP.query.join(Event).filter(
            Event.date >= last_30_days
        ).count()
        
        # Active users (users who created events or RSVP'd recently)
        active_users_from_events = db.session.query(User.id).join(Event, User.id == Event.created_by).filter(
            Event.date >= last_30_days
        ).distinct()
        
        active_users_from_rsvps = db.session.query(User.id).join(RSVP, User.id == RSVP.user_id).join(
            Event, RSVP.event_id == Event.id
        ).filter(
            Event.date >= last_30_days
        ).distinct()
        
        # Combine both queries using union
        active_users_30d = active_users_from_events.union(active_users_from_rsvps).count()
        
        # Platform health metrics using subqueries to avoid nested aggregates
        # Average events per organization
        events_per_org_subquery = db.session.query(
            Organization.id.label('org_id'),
            func.count(Event.id).label('event_count')
        ).outerjoin(Event).group_by(Organization.id).subquery()
        
        avg_events_per_org = db.session.query(
            func.avg(events_per_org_subquery.c.event_count)
        ).scalar() or 0
        
        # Average users per organization  
        users_per_org_subquery = db.session.query(
            UserOrganization.organization_id.label('org_id'),
            func.count(UserOrganization.user_id).label('user_count')
        ).group_by(UserOrganization.organization_id).subquery()
        
        avg_users_per_org = db.session.query(
            func.avg(users_per_org_subquery.c.user_count)
        ).scalar() or 0
        
        return jsonify({
            'overview': {
                'users': {
                    'total': total_users,
                    'new_30d': new_users_30d,
                    'new_7d': new_users_7d,
                    'active_30d': active_users_30d,
                    'growth_rate_30d': round((new_users_30d / max(total_users - new_users_30d, 1)) * 100, 2)
                },
                'organizations': {
                    'total': total_orgs,
                    'active_30d': active_orgs_30d,
                    'avg_users_per_org': round(avg_users_per_org, 1),
                    'activity_rate': round((active_orgs_30d / max(total_orgs, 1)) * 100, 1)
                },
                'events': {
                    'total': total_events,
                    'created_30d': events_30d,
                    'created_7d': events_7d,
                    'avg_per_org': round(avg_events_per_org, 1),
                    'total_rsvps': total_rsvps,
                    'rsvps_30d': rsvps_30d
                },
                'engagement': {
                    'avg_rsvps_per_event': round(total_rsvps / max(total_events, 1), 1),
                    'events_per_user': round(total_events / max(total_users, 1), 2),
                    'rsvp_rate': round((rsvps_30d / max(events_30d, 1)) * 100, 1) if events_30d > 0 else 0
                }
            },
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error generating analytics overview: {str(e)}'}), 500

@super_analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_analytics_trends():
    """Get trend data for charts and graphs"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Get query parameters
        period = request.args.get('period', '30d')  # 7d, 30d, 90d, 1y
        metric = request.args.get('metric', 'users')  # users, events, organizations, engagement
        
        # Calculate date range
        now = datetime.utcnow()
        if period == '7d':
            start_date = now - timedelta(days=7)
            interval = 'day'
        elif period == '30d':
            start_date = now - timedelta(days=30)
            interval = 'day'
        elif period == '90d':
            start_date = now - timedelta(days=90)
            interval = 'week'
        elif period == '1y':
            start_date = now - timedelta(days=365)
            interval = 'month'
        else:
            start_date = now - timedelta(days=30)
            interval = 'day'
        
        trends_data = []
        
        if metric == 'users':
            # User registration trends
            if hasattr(User, 'created_at'):
                results = db.session.query(
                    func.date(User.created_at).label('date'),
                    func.count(User.id).label('count')
                ).filter(
                    User.created_at >= start_date
                ).group_by(func.date(User.created_at)).order_by('date').all()
                
                trends_data = [{'date': r.date.isoformat(), 'value': r.count} for r in results]
        
        elif metric == 'events':
            # Event creation trends
            results = db.session.query(
                func.date(Event.date).label('date'),
                func.count(Event.id).label('count')
            ).filter(
                Event.date >= start_date
            ).group_by(func.date(Event.date)).order_by('date').all()
            
            trends_data = [{'date': r.date.isoformat(), 'value': r.count} for r in results]
        
        elif metric == 'engagement':
            # RSVP trends
            if hasattr(RSVP, 'created_at'):
                results = db.session.query(
                    func.date(RSVP.created_at).label('date'),
                    func.count(RSVP.id).label('count')
                ).filter(
                    RSVP.created_at >= start_date
                ).group_by(func.date(RSVP.created_at)).order_by('date').all()
                
                trends_data = [{'date': r.date.isoformat(), 'value': r.count} for r in results]
        
        return jsonify({
            'trends': trends_data,
            'period': period,
            'metric': metric,
            'interval': interval,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat()
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error generating trends data: {str(e)}'}), 500

@super_analytics_bp.route('/organizations/performance', methods=['GET'])
@jwt_required()
def get_organization_performance():
    """Get detailed performance metrics for all organizations"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Time periods
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        
        # Get organization performance data
        org_performance = []
        organizations = Organization.query.all()
        
        for org in organizations:
            # User count
            user_count = UserOrganization.query.filter_by(organization_id=org.id).count()
            
            # Event metrics
            total_events = Event.query.filter_by(organization_id=org.id).count()
            recent_events = Event.query.filter(
                Event.organization_id == org.id,
                Event.date >= last_30_days
            ).count()
            
            # RSVP metrics
            total_rsvps = db.session.query(func.count(RSVP.id)).join(Event).filter(
                Event.organization_id == org.id
            ).scalar() or 0
            
            recent_rsvps = db.session.query(func.count(RSVP.id)).join(Event).filter(
                Event.organization_id == org.id,
                Event.date >= last_30_days
            ).scalar() or 0
            
            # Calculate engagement score (0-100)
            engagement_score = 0
            if user_count > 0:
                events_per_user = total_events / user_count
                rsvps_per_user = total_rsvps / user_count
                recent_activity = min(recent_events / max(user_count * 0.1, 1), 1)  # Cap at reasonable activity
                
                engagement_score = min(
                    (events_per_user * 20 + rsvps_per_user * 10 + recent_activity * 50), 100
                )
            
            # Health status
            health_status = 'excellent' if engagement_score >= 80 else \
                          'good' if engagement_score >= 60 else \
                          'fair' if engagement_score >= 40 else \
                          'needs_attention'
            
            org_performance.append({
                'id': org.id,
                'name': org.name,
                'metrics': {
                    'user_count': user_count,
                    'total_events': total_events,
                    'recent_events_30d': recent_events,
                    'total_rsvps': total_rsvps,
                    'recent_rsvps_30d': recent_rsvps,
                    'events_per_user': round(total_events / max(user_count, 1), 2),
                    'rsvps_per_event': round(total_rsvps / max(total_events, 1), 1),
                    'engagement_score': round(engagement_score, 1),
                    'health_status': health_status
                },
                'created_at': org.created_at.isoformat() if hasattr(org, 'created_at') and org.created_at else None
            })
        
        # Sort by engagement score descending
        org_performance.sort(key=lambda x: x['metrics']['engagement_score'], reverse=True)
        
        return jsonify({
            'organizations': org_performance,
            'summary': {
                'total_organizations': len(org_performance),
                'excellent_health': len([o for o in org_performance if o['metrics']['health_status'] == 'excellent']),
                'good_health': len([o for o in org_performance if o['metrics']['health_status'] == 'good']),
                'needs_attention': len([o for o in org_performance if o['metrics']['health_status'] == 'needs_attention']),
                'avg_engagement_score': round(sum(o['metrics']['engagement_score'] for o in org_performance) / len(org_performance), 1) if org_performance else 0
            },
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        return jsonify({'msg': f'Error generating organization performance data: {str(e)}'}), 500

@super_analytics_bp.route('/export/<report_type>', methods=['GET'])
@jwt_required()
def export_analytics_report(report_type):
    """Export analytics data in various formats"""
    user_id = get_jwt_identity()
    
    if not is_super_admin(user_id):
        return jsonify({'msg': 'Super Admin access required'}), 403
    
    try:
        # Get query parameters
        format_type = request.args.get('format', 'json')  # json, csv
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_date = datetime.utcnow()
        
        export_data = {}
        
        if report_type == 'system_overview':
            # Get system-wide metrics for the date range
            export_data = {
                'report_type': 'System Overview',
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'metrics': {
                    'users': {
                        'total': User.query.count(),
                        'new_in_period': User.query.filter(
                            User.created_at.between(start_date, end_date)
                        ).count() if hasattr(User, 'created_at') else 0
                    },
                    'organizations': {
                        'total': Organization.query.count(),
                        'active_in_period': db.session.query(Organization.id).join(Event).filter(
                            Event.date.between(start_date, end_date)
                        ).distinct().count()
                    },
                    'events': {
                        'total_in_period': Event.query.filter(
                            Event.date.between(start_date, end_date)
                        ).count(),
                        'total_rsvps_in_period': db.session.query(func.count(RSVP.id)).join(Event).filter(
                            Event.date.between(start_date, end_date)
                        ).scalar() or 0
                    }
                },
                'generated_at': datetime.utcnow().isoformat()
            }
        
        elif report_type == 'user_activity':
            # Get user activity data
            users_data = []
            users = User.query.all()
            
            for user in users:
                user_events = Event.query.filter(
                    Event.user_id == user.id,
                    Event.date.between(start_date, end_date)
                ).count()
                
                user_rsvps = RSVP.query.filter(
                    RSVP.user_id == user.id,
                    RSVP.event_id.in_(
                        db.session.query(Event.id).filter(
                            Event.date.between(start_date, end_date)
                        ).subquery()
                    )
                ).count()
                
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'events_created': user_events,
                    'rsvps_made': user_rsvps,
                    'total_activity': user_events + user_rsvps
                })
            
            export_data = {
                'report_type': 'User Activity',
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'users': users_data,
                'generated_at': datetime.utcnow().isoformat()
            }
        
        return jsonify(export_data)
        
    except Exception as e:
        return jsonify({'msg': f'Error exporting analytics report: {str(e)}'}), 500
