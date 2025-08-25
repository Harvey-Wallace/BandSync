"""
Simple Admin Oversight Routes for Harvey258
Clean, minimal implementation without super admin complexity
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import (
    db, User, Organization, UserOrganization, Event, RSVP, EventFieldResponse, 
    EventAttachment, EventSurvey, SurveyResponse, Section, EventCategory, 
    EmailLog, AdminAttendanceReport, AdminRSVPChangeNotification, EventCustomField,
    MessageThread, Message, MessageRecipient, OrganizationEmailAlias,
    EmailForwardingRule, CallList, CallListMember
)
from sqlalchemy import func
from datetime import datetime

admin_oversight = Blueprint('admin_oversight', __name__)

@admin_oversight.route('/admin-oversight/debug/token-info', methods=['GET'])
@jwt_required()
def debug_token_info():
    """Debug endpoint to check user's JWT claims and permissions."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's organizations
        user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
        orgs = []
        for uo in user_orgs:
            org = Organization.query.get(uo.organization_id)
            if org:
                orgs.append({
                    'id': org.id,
                    'name': org.name,
                    'role': uo.role,
                    'is_primary': user.primary_organization_id == org.id,
                    'is_current': user.current_organization_id == org.id
                })
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'primary_organization_id': user.primary_organization_id,
                'current_organization_id': user.current_organization_id
            },
            'jwt_claims': claims,
            'organizations': orgs,
            'diagnosis': {
                'has_org_id_claim': 'organization_id' in claims,
                'has_role_claim': 'role' in claims,
                'role_claim_value': claims.get('role'),
                'org_id_claim_value': claims.get('organization_id'),
                'has_multiple_orgs': len(orgs) > 1,
                'potential_issues': []
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@admin_oversight.route('/admin-oversight/debug/all-relationships', methods=['GET'])
@jwt_required()
def debug_all_user_org_relationships():
    """Debug endpoint to check all user organization relationships."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        print("Debugging all user organization relationships...")
        
        # Get all users
        users = User.query.all()
        user_data = []
        for user in users:
            user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
            orgs = []
            for uo in user_orgs:
                org = Organization.query.get(uo.organization_id)
                if org:
                    orgs.append({
                        'organization_id': org.id,
                        'organization_name': org.name,
                        'role': uo.role,
                        'joined_at': uo.joined_at.isoformat() if uo.joined_at else None
                    })
            
            user_data.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'primary_organization_id': user.primary_organization_id,
                'current_organization_id': user.current_organization_id,
                'legacy_organization_id': user.organization_id,
                'organizations': orgs
            })
        
        # Get all organizations
        orgs = Organization.query.all()
        org_data = []
        for org in orgs:
            members = UserOrganization.query.filter_by(organization_id=org.id).all()
            member_list = []
            for uo in members:
                user = User.query.get(uo.user_id)
                if user:
                    member_list.append({
                        'user_id': user.id,
                        'username': user.username,
                        'role': uo.role,
                        'joined_at': uo.joined_at.isoformat() if uo.joined_at else None
                    })
            
            org_data.append({
                'organization_id': org.id,
                'organization_name': org.name,
                'member_count': len(member_list),
                'members': member_list
            })
        
        return jsonify({
            'users': user_data,
            'organizations': org_data,
            'total_users': len(user_data),
            'total_organizations': len(org_data),
            'total_relationships': sum(len(user['organizations']) for user in user_data)
        })
        
    except Exception as e:
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

@admin_oversight.route('/admin-oversight/organizations/<int:org_id>/check-delete', methods=['GET'])
@jwt_required()
def check_organization_delete(org_id):
    """Check what would be deleted when deleting an organization (dry run)."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        organization = Organization.query.get(org_id)
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
        
        org_name = organization.name
        
        # Count what would be deleted
        events = Event.query.filter_by(organization_id=org_id).all()
        event_ids = [event.id for event in events]
        
        result = {
            'organization': {
                'id': org_id,
                'name': org_name
            },
            'would_delete': {}
        }
        
        # Count events and related data
        result['would_delete']['events'] = len(events)
        
        if event_ids:
            result['would_delete']['rsvps'] = RSVP.query.filter(RSVP.event_id.in_(event_ids)).count()
            result['would_delete']['event_responses'] = EventFieldResponse.query.filter(EventFieldResponse.event_id.in_(event_ids)).count()
            result['would_delete']['event_attachments'] = EventAttachment.query.filter(EventAttachment.event_id.in_(event_ids)).count()
            result['would_delete']['survey_responses'] = SurveyResponse.query.filter(SurveyResponse.event_id.in_(event_ids)).count()
            result['would_delete']['event_surveys'] = EventSurvey.query.filter(EventSurvey.event_id.in_(event_ids)).count()
            result['would_delete']['custom_fields'] = EventCustomField.query.filter(EventCustomField.event_id.in_(event_ids)).count()
        else:
            result['would_delete']['rsvps'] = 0
            result['would_delete']['event_responses'] = 0
            result['would_delete']['event_attachments'] = 0
            result['would_delete']['survey_responses'] = 0
            result['would_delete']['event_surveys'] = 0
            result['would_delete']['custom_fields'] = 0
        
        # Count organization structure
        result['would_delete']['sections'] = Section.query.filter_by(organization_id=org_id).count()
        result['would_delete']['event_categories'] = EventCategory.query.filter_by(organization_id=org_id).count()
        
        # Count logs and reports
        result['would_delete']['email_logs'] = EmailLog.query.filter_by(organization_id=org_id).count()
        result['would_delete']['attendance_reports'] = AdminAttendanceReport.query.filter_by(organization_id=org_id).count()
        result['would_delete']['rsvp_notifications'] = AdminRSVPChangeNotification.query.filter_by(organization_id=org_id).count()
        
        # Count user relationships
        result['would_delete']['user_relationships'] = UserOrganization.query.filter_by(organization_id=org_id).count()
        
        # Find users that would be affected
        users_with_org_ref = User.query.filter(User.organization_id == org_id).all()
        users_with_current_ref = User.query.filter(User.current_organization_id == org_id).all()
        users_with_primary_ref = User.query.filter(User.primary_organization_id == org_id).all()
        
        all_affected_users = set()
        all_affected_users.update(users_with_org_ref)
        all_affected_users.update(users_with_current_ref)
        all_affected_users.update(users_with_primary_ref)
        
        result['would_update'] = {
            'users_count': len(all_affected_users),
            'users': []
        }
        
        for user in all_affected_users:
            user_info = {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'references_to_clear': []
            }
            
            if user.organization_id == org_id:
                user_info['references_to_clear'].append('organization_id')
            if user.current_organization_id == org_id:
                user_info['references_to_clear'].append('current_organization_id')
            if user.primary_organization_id == org_id:
                user_info['references_to_clear'].append('primary_organization_id')
                
            result['would_update']['users'].append(user_info)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to check organization deletion: {str(e)}'}), 500

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
        
        print(f"🗑️ Starting cascade delete for organization: {org_name} (ID: {org_id})")
        
        # Step 1: Get all events for this organization
        events = Event.query.filter_by(organization_id=org_id).all()
        event_ids = [event.id for event in events]
        print(f"   Found {len(events)} events to delete")
        
        # Step 2: Delete all event-related data
        if event_ids:
            # Delete RSVPs for these events
            rsvp_count = RSVP.query.filter(RSVP.event_id.in_(event_ids)).delete(synchronize_session=False)
            print(f"   Deleted {rsvp_count} RSVPs")
            
            # Delete event field responses
            response_count = EventFieldResponse.query.filter(EventFieldResponse.event_id.in_(event_ids)).delete(synchronize_session=False)
            print(f"   Deleted {response_count} event field responses")
            
            # Delete event attachments
            attachment_count = EventAttachment.query.filter(EventAttachment.event_id.in_(event_ids)).delete(synchronize_session=False)
            print(f"   Deleted {attachment_count} event attachments")
            
            # Delete survey responses (via EventSurvey)
            surveys = EventSurvey.query.filter(EventSurvey.event_id.in_(event_ids)).all()
            survey_ids = [survey.id for survey in surveys]
            survey_response_count = 0
            if survey_ids:
                survey_response_count = SurveyResponse.query.filter(SurveyResponse.survey_id.in_(survey_ids)).delete(synchronize_session=False)
            print(f"   Deleted {survey_response_count} survey responses")
            
            # Delete event surveys
            survey_count = EventSurvey.query.filter(EventSurvey.event_id.in_(event_ids)).delete(synchronize_session=False)
            print(f"   Deleted {survey_count} event surveys")
            
            # Delete event custom fields
            field_count = EventCustomField.query.filter(EventCustomField.event_id.in_(event_ids)).delete(synchronize_session=False)
            print(f"   Deleted {field_count} custom fields")
        
        # Step 3: Delete events themselves
        event_count = Event.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {event_count} events")
        
        # Step 4: Delete organization structure
        section_count = Section.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {section_count} sections")
        
        category_count = EventCategory.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {category_count} event categories")
        
        # Step 5: Delete organization-specific logs and reports
        email_log_count = EmailLog.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {email_log_count} email logs")
        
        attendance_count = AdminAttendanceReport.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {attendance_count} attendance reports")
        
        notification_count = AdminRSVPChangeNotification.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {notification_count} RSVP notifications")
        
        # Step 6: Handle email aliases and forwarding rules
        # First get all aliases for this organization
        org_aliases = OrganizationEmailAlias.query.filter_by(organization_id=org_id).all()
        alias_ids = [alias.id for alias in org_aliases]
        
        # Delete forwarding rules that reference these aliases
        forwarding_count = 0
        if alias_ids:
            forwarding_count = EmailForwardingRule.query.filter(EmailForwardingRule.alias_id.in_(alias_ids)).delete(synchronize_session=False)
        print(f"   Deleted {forwarding_count} email forwarding rules")
        
        # Now delete the aliases themselves
        alias_count = OrganizationEmailAlias.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {alias_count} email aliases")
        
        # Step 7: Delete call lists (this will cascade to call list members)
        call_list_count = CallList.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {call_list_count} call lists")
        
        # Step 8: Delete messaging data
        message_thread_count = MessageThread.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {message_thread_count} message threads")
        
        # Step 9: Handle users - Update their organization references to NULL instead of deleting users
        # First, find all users that reference this organization
        users_with_org_ref = User.query.filter(User.organization_id == org_id).all()
        users_with_current_ref = User.query.filter(User.current_organization_id == org_id).all()
        users_with_primary_ref = User.query.filter(User.primary_organization_id == org_id).all()
        
        all_affected_users = set()
        all_affected_users.update(users_with_org_ref)
        all_affected_users.update(users_with_current_ref)
        all_affected_users.update(users_with_primary_ref)
        
        print(f"   Found {len(all_affected_users)} users with organization references")
        
        # Update each user's organization references
        user_update_count = 0
        for user in all_affected_users:
            if user.organization_id == org_id:
                user.organization_id = None
                print(f"     Cleared organization_id for user {user.username}")
            if user.current_organization_id == org_id:
                user.current_organization_id = None
                print(f"     Cleared current_organization_id for user {user.username}")
            if user.primary_organization_id == org_id:
                user.primary_organization_id = None
                print(f"     Cleared primary_organization_id for user {user.username}")
            user_update_count += 1
            
        # Commit user updates before proceeding
        db.session.commit()
        print(f"   Committed user updates for {user_update_count} users")
        
        # Step 10: Delete UserOrganization relationships
        user_org_count = UserOrganization.query.filter_by(organization_id=org_id).delete()
        print(f"   Deleted {user_org_count} user-organization relationships")
        
        # Step 11: Finally delete the organization itself
        print(f"   Attempting to delete organization {org_name}...")
        db.session.delete(organization)
        db.session.commit()
        
        print(f"✅ Successfully deleted organization: {org_name}")
        
        return jsonify({
            'message': f'Organization "{org_name}" and all related data deleted successfully',
            'details': {
                'events_deleted': event_count,
                'rsvps_deleted': rsvp_count if event_ids else 0,
                'sections_deleted': section_count,
                'users_updated': user_update_count,
                'relationships_deleted': user_org_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting organization: {str(e)}")
        return jsonify({'error': f'Failed to delete organization: {str(e)}'}), 500

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

@admin_oversight.route('/admin-oversight/fix/update-user-role', methods=['POST'])
@jwt_required()
def update_user_role():
    """Update a user's role in their organization."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        data = request.get_json()
        username = data.get('username')
        org_name = data.get('organization_name')
        new_role = data.get('role', 'Admin')
        
        if not username or not org_name:
            return jsonify({'error': 'Username and organization name required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': f'User {username} not found'}), 404
        
        # Find organization
        organization = Organization.query.filter_by(name=org_name).first()
        if not organization:
            return jsonify({'error': f'Organization {org_name} not found'}), 404
        
        # Find existing user-organization relationship
        user_org = UserOrganization.query.filter_by(
            user_id=user.id,
            organization_id=organization.id
        ).first()
        
        if not user_org:
            return jsonify({'error': f'User {username} is not a member of {org_name}'}), 404
        
        old_role = user_org.role
        user_org.role = new_role
        
        # Also update the user's main role if this is their primary org
        if user.primary_organization_id == organization.id or user.organization_id == organization.id:
            user.role = new_role
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully updated {username} role from {old_role} to {new_role} in {org_name}',
            'user_id': user.id,
            'organization_id': organization.id,
            'old_role': old_role,
            'new_role': new_role
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/admin-oversight/fix/update-user-context', methods=['POST'])
@jwt_required()
def update_user_context():
    """Fix a user's organization context for proper admin access."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': f'User {username} not found'}), 404
        
        # Get user's organizations
        user_orgs = UserOrganization.query.filter_by(user_id=user.id).all()
        
        if not user_orgs:
            return jsonify({'error': f'User {username} has no organization memberships'}), 400
        
        # Set the first organization as primary and current if not set
        primary_org = user_orgs[0]
        
        if not user.primary_organization_id:
            user.primary_organization_id = primary_org.organization_id
        
        if not user.current_organization_id:
            user.current_organization_id = primary_org.organization_id
        
        # Also update the organization_id field for legacy compatibility
        if not user.organization_id:
            user.organization_id = primary_org.organization_id
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully updated {username} context',
            'user_id': user.id,
            'primary_organization_id': user.primary_organization_id,
            'current_organization_id': user.current_organization_id,
            'organization_id': user.organization_id,
            'note': 'User should logout and login again for changes to take effect'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_oversight.route('/admin-oversight/delete-user', methods=['DELETE'])
@jwt_required()
def delete_user():
    """Delete a user and all their associated data."""
    
    if not is_harvey_admin():
        return jsonify({'error': 'Access denied - Harvey258 only'}), 403
    
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': f'User {username} not found'}), 404
        
        # Safety check - don't delete Harvey258
        if user.username == 'Harvey258':
            return jsonify({'error': 'Cannot delete Harvey258 admin account'}), 400
        
        user_id = user.id
        deletion_details = {
            'username': username,
            'user_id': user_id,
            'organizations_left': 0,
            'events_transferred': 0,
            'rsvps_deleted': 0,
            'survey_responses_deleted': 0,
            'user_organizations_deleted': 0,
            'call_list_memberships_deleted': 0
        }
        
        print(f"Starting deletion of user: {username} (ID: {user_id})")
        
        # 1. Get user's organizations for cleanup
        user_orgs = UserOrganization.query.filter_by(user_id=user_id).all()
        org_ids = [uo.organization_id for uo in user_orgs]
        deletion_details['organizations_left'] = len(org_ids)
        
        # 2. Delete survey responses
        survey_responses = SurveyResponse.query.filter_by(user_id=user_id).all()
        deletion_details['survey_responses_deleted'] = len(survey_responses)
        for response in survey_responses:
            db.session.delete(response)
        
        # 3. Delete RSVPs
        rsvps = RSVP.query.filter_by(user_id=user_id).all()
        deletion_details['rsvps_deleted'] = len(rsvps)
        for rsvp in rsvps:
            db.session.delete(rsvp)
        
        # 4. Transfer ownership of events created by this user to organization admin
        events_created = Event.query.filter_by(created_by=user_id).all()
        for event in events_created:
            # Find an admin for the event's organization
            org_admin = UserOrganization.query.filter_by(
                organization_id=event.organization_id,
                role='admin'
            ).first()
            
            if org_admin:
                event.created_by = org_admin.user_id
                deletion_details['events_transferred'] += 1
            else:
                # If no admin found, leave as is (this shouldn't happen in normal cases)
                pass
        
        # 5. Delete call list memberships
        call_list_memberships = CallListMember.query.filter_by(user_id=user_id).all()
        deletion_details['call_list_memberships_deleted'] = len(call_list_memberships)
        for membership in call_list_memberships:
            db.session.delete(membership)
        
        # 6. Delete user organization relationships
        deletion_details['user_organizations_deleted'] = len(user_orgs)
        for user_org in user_orgs:
            db.session.delete(user_org)
        
        # 7. Finally delete the user
        db.session.delete(user)
        
        # Commit all changes
        db.session.commit()
        
        print(f"Successfully deleted user {username} and all associated data")
        
        return jsonify({
            'message': f'User {username} and all associated data deleted successfully',
            'deletion_details': deletion_details
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500
