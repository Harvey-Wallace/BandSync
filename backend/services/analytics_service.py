"""
Analytics Service for BandSync
        # Engagement rate
        total_possible_rsvps = db.session.query(func.count()).select_from(
            db.session.query(Event.id, User.id)
            .filter(Event.organization_id == org_id)
            .filter(User.organization_id == org_id)
            .filter(Event.date >= start_date)
            .subquery()
        ).scalar()
        
        engagement_rate = (recent_rsvps / total_possible_rsvps * 100) if total_possible_rsvps > 0 else 0
        
        return {
            'total_members': total_members,
            'total_events': total_events,
            'recent_events': recent_events,
            'recent_rsvps': recent_rsvps,
            'engagement_rate': round(engagement_rate, 1),
            'activity_score': min(100, (recent_events * 10) + (recent_rsvps * 2))
        }ive analytics and insights for administrators
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, case, desc
from models import (
    db, User, Event, RSVP, Organization, Section, 
    Message, MessageThread, EmailLog, SubstituteRequest
)

class AnalyticsService:
    
    @staticmethod
    def get_organization_overview(org_id, days=30):
        """Get high-level organization metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total counts
        total_members = User.query.filter_by(organization_id=org_id).count()
        total_events = Event.query.filter_by(organization_id=org_id).count()
        
        # Recent activity
        recent_events = Event.query.filter(
            Event.organization_id == org_id,
            Event.date >= start_date
        ).count()
        
        recent_rsvps = RSVP.query.join(Event).filter(
            Event.organization_id == org_id,
            RSVP.created_at >= start_date
        ).count()
        
        # Simplified engagement rate calculation
        # Calculate as: (actual RSVPs / (total members * recent events)) * 100
        engagement_rate = 0
        if total_members > 0 and recent_events > 0:
            max_possible_rsvps = total_members * recent_events
            engagement_rate = (recent_rsvps / max_possible_rsvps * 100) if max_possible_rsvps > 0 else 0
        
        return {
            'total_members': total_members,
            'total_events': total_events,
            'recent_events': recent_events,
            'recent_rsvps': recent_rsvps,
            'engagement_rate': round(engagement_rate, 1),
            'period_days': days
        }
    
    @staticmethod
    def get_member_analytics(org_id, days=30):
        """Get detailed member engagement analytics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Member engagement scores
        member_stats = db.session.query(
            User.id,
            User.name,
            User.username,
            User.email,
            User.section_id,
            func.count(RSVP.id).label('total_rsvps'),
            func.count(case((RSVP.status == 'Yes', 1))).label('yes_rsvps'),
            func.count(case((RSVP.status == 'No', 1))).label('no_rsvps'),
            func.count(case((RSVP.status == 'Maybe', 1))).label('maybe_rsvps'),
            func.max(RSVP.created_at).label('last_rsvp')
        ).select_from(User).outerjoin(RSVP).outerjoin(Event, Event.id == RSVP.event_id).filter(
            User.organization_id == org_id,
            db.or_(Event.date >= start_date, Event.date.is_(None))
        ).group_by(User.id).all()
        
        # Section participation - fix nested aggregate function
        section_stats = db.session.query(
            Section.id.label('section_id'),
            Section.name.label('section_name'),
            func.count(func.distinct(User.id)).label('member_count')
        ).select_from(Section).outerjoin(User, User.section_id == Section.id).filter(
            Section.organization_id == org_id
        ).group_by(Section.id, Section.name).all()
        
        # Calculate average participation per section separately
        section_participation = []
        for section in section_stats:
            # Get RSVP count for this section's users
            rsvp_count = db.session.query(func.count(RSVP.id)).select_from(RSVP).join(User).join(Event).filter(
                User.section_id == section.section_id,
                Event.organization_id == org_id,
                Event.date >= start_date
            ).scalar() or 0
            
            avg_participation = (rsvp_count / section.member_count) if section.member_count > 0 else 0
            section_participation.append({
                'section_name': section.section_name,
                'member_count': section.member_count,
                'avg_participation': round(avg_participation, 1)
            })
        
        section_stats = section_participation
        
        # Top participants
        top_participants = sorted(
            member_stats, 
            key=lambda x: x.total_rsvps, 
            reverse=True
        )[:10]
        
        # Inactive members (no RSVP in period)
        inactive_members = [m for m in member_stats if m.total_rsvps == 0]
        
        return {
            'member_stats': [
                {
                    'id': m.id,
                    'name': m.name,
                    'username': m.username,
                    'email': m.email,
                    'section_id': m.section_id,
                    'total_rsvps': m.total_rsvps,
                    'yes_rsvps': m.yes_rsvps,
                    'no_rsvps': m.no_rsvps,
                    'maybe_rsvps': m.maybe_rsvps,
                    'attendance_rate': round((m.yes_rsvps / m.total_rsvps * 100) if m.total_rsvps > 0 else 0, 1),
                    'last_rsvp': m.last_rsvp.isoformat() if m.last_rsvp else None
                } for m in member_stats
            ],
            'section_stats': section_stats,
            'top_participants': [
                {
                    'name': m.name,
                    'total_rsvps': m.total_rsvps,
                    'attendance_rate': round((m.yes_rsvps / m.total_rsvps * 100) if m.total_rsvps > 0 else 0, 1)
                } for m in top_participants
            ],
            'inactive_count': len(inactive_members)
        }
    
    @staticmethod
    def get_event_analytics(org_id, days=90):
        """Get event performance analytics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Event attendance trends
        event_stats = db.session.query(
            Event.id,
            Event.title,
            Event.date,
            Event.event_type,
            func.count(RSVP.id).label('total_responses'),
            func.count(case((RSVP.status == 'Yes', 1))).label('yes_count'),
            func.count(case((RSVP.status == 'No', 1))).label('no_count'),
            func.count(case((RSVP.status == 'Maybe', 1))).label('maybe_count')
        ).select_from(Event).outerjoin(RSVP).filter(
            Event.organization_id == org_id,
            Event.date >= start_date
        ).group_by(Event.id).order_by(desc(Event.date)).all()
        
        # Event type performance - simplified approach
        type_stats = db.session.query(
            Event.event_type,
            func.count(Event.id).label('event_count'),
            func.count(case((RSVP.status == 'Yes', 1))).label('total_attendance'),
            func.count(RSVP.id).label('total_responses')
        ).select_from(Event).outerjoin(RSVP).filter(
            Event.organization_id == org_id,
            Event.date >= start_date
        ).group_by(Event.event_type).all()
        
        # Calculate averages manually
        type_performance = []
        for event_type in type_stats:
            avg_attendance = (event_type.total_attendance / event_type.event_count) if event_type.event_count > 0 else 0
            avg_responses = (event_type.total_responses / event_type.event_count) if event_type.event_count > 0 else 0
            
            type_performance.append({
                'event_type': event_type.event_type,
                'event_count': event_type.event_count,
                'avg_attendance': round(avg_attendance, 1),
                'avg_responses': round(avg_responses, 1)
            })
        
        type_stats = type_performance
        
        # Monthly trends
        monthly_stats = db.session.query(
            func.date_trunc('month', Event.date).label('month'),
            func.count(Event.id).label('event_count'),
            func.count(case((RSVP.status == 'Yes', 1))).label('total_attendance')
        ).select_from(Event).outerjoin(RSVP).filter(
            Event.organization_id == org_id,
            Event.date >= start_date
        ).group_by(func.date_trunc('month', Event.date)).order_by('month').all()
        
        return {
            'event_stats': [
                {
                    'id': e.id,
                    'title': e.title,
                    'date': e.date.isoformat(),
                    'event_type': e.event_type,
                    'total_responses': e.total_responses,
                    'yes_count': e.yes_count,
                    'no_count': e.no_count,
                    'maybe_count': e.maybe_count,
                    'attendance_rate': round((e.yes_count / e.total_responses * 100) if e.total_responses > 0 else 0, 1)
                } for e in event_stats
            ],
            'type_stats': type_stats,
            'monthly_trends': [
                {
                    'month': m.month.strftime('%Y-%m') if m.month else None,
                    'event_count': m.event_count,
                    'total_attendance': m.total_attendance
                } for m in monthly_stats
            ]
        }
    
    @staticmethod
    def get_communication_analytics(org_id, days=30):
        """Get communication and engagement analytics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Message statistics
        message_stats = db.session.query(
            func.count(Message.id).label('total_messages'),
            func.count(func.distinct(MessageThread.id)).label('active_threads'),
            func.count(func.distinct(Message.sender_id)).label('active_users')
        ).select_from(Message).join(MessageThread).filter(
            MessageThread.organization_id == org_id,
            Message.created_at >= start_date
        ).first()
        
        # Email statistics
        email_stats = db.session.query(
            func.count(EmailLog.id).label('total_emails'),
            func.count(case((EmailLog.status == 'sent', 1))).label('sent_emails'),
            func.count(case((EmailLog.status == 'failed', 1))).label('failed_emails')
        ).filter(
            EmailLog.organization_id == org_id,
            EmailLog.created_at >= start_date
        ).first()
        
        # Substitute request analytics
        substitute_stats = db.session.query(
            func.count(SubstituteRequest.id).label('total_requests'),
            func.count(case((SubstituteRequest.status == 'fulfilled', 1))).label('fulfilled_requests'),
            func.avg(func.extract('epoch', SubstituteRequest.fulfilled_at - SubstituteRequest.created_at) / 3600).label('avg_response_hours')
        ).select_from(SubstituteRequest).join(Event).filter(
            Event.organization_id == org_id,
            SubstituteRequest.created_at >= start_date
        ).first()
        
        return {
            'messaging': {
                'total_messages': message_stats.total_messages or 0,
                'active_threads': message_stats.active_threads or 0,
                'active_users': message_stats.active_users or 0
            },
            'email': {
                'total_emails': email_stats.total_emails or 0,
                'sent_emails': email_stats.sent_emails or 0,
                'failed_emails': email_stats.failed_emails or 0,
                'success_rate': round((email_stats.sent_emails / email_stats.total_emails * 100) if email_stats.total_emails > 0 else 0, 1)
            },
            'substitution': {
                'total_requests': substitute_stats.total_requests or 0,
                'fulfilled_requests': substitute_stats.fulfilled_requests or 0,
                'fulfillment_rate': round((substitute_stats.fulfilled_requests / substitute_stats.total_requests * 100) if substitute_stats.total_requests > 0 else 0, 1),
                'avg_response_hours': round(substitute_stats.avg_response_hours or 0, 1)
            }
        }
    
    @staticmethod
    def get_organization_health_score(org_id):
        """Calculate overall organization health score"""
        
        # Get recent metrics (last 30 days)
        overview = AnalyticsService.get_organization_overview(org_id, 30)
        member_analytics = AnalyticsService.get_member_analytics(org_id, 30)
        event_analytics = AnalyticsService.get_event_analytics(org_id, 30)
        comm_analytics = AnalyticsService.get_communication_analytics(org_id, 30)
        
        # Calculate health metrics (0-100 scale)
        
        # Engagement Score (40% weight)
        engagement_score = min(overview['engagement_rate'] * 2, 100)  # Cap at 100
        
        # Activity Score (30% weight) - Based on recent events and responses
        activity_score = min((overview['recent_events'] * 10) + (overview['recent_rsvps'] / 10), 100)
        
        # Communication Score (20% weight)
        comm_score = min((comm_analytics['messaging']['total_messages'] * 2) + 
                        (comm_analytics['email']['success_rate']), 100)
        
        # Retention Score (10% weight) - Based on inactive members
        total_members = overview['total_members']
        inactive_count = member_analytics['inactive_count']
        retention_score = ((total_members - inactive_count) / total_members * 100) if total_members > 0 else 0
        
        # Calculate weighted health score
        health_score = (
            engagement_score * 0.4 +
            activity_score * 0.3 +
            comm_score * 0.2 +
            retention_score * 0.1
        )
        
        # Determine health level
        if health_score >= 80:
            health_level = "Excellent"
        elif health_score >= 60:
            health_level = "Good"
        elif health_score >= 40:
            health_level = "Fair"
        else:
            health_level = "Needs Attention"
        
        return {
            'health_score': round(health_score, 1),
            'health_level': health_level,
            'component_scores': {
                'engagement': round(engagement_score, 1),
                'activity': round(activity_score, 1),
                'communication': round(comm_score, 1),
                'retention': round(retention_score, 1)
            },
            'recommendations': AnalyticsService._get_recommendations(health_score, overview, member_analytics, comm_analytics)
        }
    
    @staticmethod
    def _get_recommendations(health_score, overview, member_analytics, comm_analytics):
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        if overview['engagement_rate'] < 50:
            recommendations.append({
                'type': 'engagement',
                'title': 'Low Engagement Rate',
                'description': 'Consider sending event reminders and following up with members who haven\'t responded.',
                'priority': 'high'
            })
        
        if member_analytics['inactive_count'] > overview['total_members'] * 0.3:
            recommendations.append({
                'type': 'retention',
                'title': 'High Inactive Member Count',
                'description': 'Reach out to inactive members and consider re-engagement campaigns.',
                'priority': 'medium'
            })
        
        if comm_analytics['email']['success_rate'] < 90:
            recommendations.append({
                'type': 'communication',
                'title': 'Email Delivery Issues',
                'description': 'Check email configurations and member email addresses for delivery problems.',
                'priority': 'high'
            })
        
        if overview['recent_events'] < 5:
            recommendations.append({
                'type': 'activity',
                'title': 'Low Event Activity',
                'description': 'Consider scheduling more regular events to maintain member engagement.',
                'priority': 'medium'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'title': 'Great Performance!',
                'description': 'Your organization is performing well. Keep up the excellent work!',
                'priority': 'low'
            })
        
        return recommendations
