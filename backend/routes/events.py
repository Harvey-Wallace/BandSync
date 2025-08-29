from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Event, RSVP, EventCategory, User, UserOrganization, Organization, EventTemplate, db
from datetime import datetime, timedelta
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from dateutil.relativedelta import relativedelta

# Import email service
try:
    from services.email_service import EmailService
    email_service = EmailService()
except ImportError:
    email_service = None
    print("Email service not available - emails will be skipped")

events_bp = Blueprint('events', __name__)

# Removed debug logging - events API is working normally

def mobile_to_backend_status(mobile_status):
    """Convert mobile app status format to backend format"""
    status_map = {
        'attending': 'Yes',
        'maybe': 'Maybe', 
        'not_attending': 'No'
    }
    return status_map.get(mobile_status)

def backend_to_mobile_status(backend_status):
    """Convert backend status format to mobile app format"""
    status_map = {
        'Yes': 'attending',
        'Maybe': 'maybe',
        'No': 'not_attending'
    }
    return status_map.get(backend_status)

@events_bp.route('/', methods=['GET'])
@jwt_required()
def get_events():
    try:
        print(f"🔍 Starting get_events() function")
        claims = get_jwt()
        org_id = claims.get('organization_id')
        print(f"🏢 Organization ID: {org_id}")
        
        # Get query parameters
        include_templates = request.args.get('include_templates', 'false').lower() == 'true'
        category_id = request.args.get('category_id')
        print(f"📊 Query params - include_templates: {include_templates}, category_id: {category_id}")
        
        # Base query
        query = Event.query.filter_by(organization_id=org_id)
        
        # Filter by template status
        if not include_templates:
            query = query.filter_by(is_template=False)
        
        # Filter by category
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        print(f"🔍 Executing database query...")
        events = query.order_by(Event.date.asc()).all()
        print(f"📅 Found {len(events)} events")
    
        print(f"🔍 Getting total org users...")
        
        # Method 1: Count via UserOrganization (modern approach)
        modern_count = db.session.query(User).join(
            UserOrganization, 
            (User.id == UserOrganization.user_id) & 
            (UserOrganization.organization_id == org_id) & 
            (UserOrganization.is_active == True)
        ).count()
        
        # Method 2: Count via legacy User.organization_id
        legacy_count = User.query.filter_by(organization_id=org_id).count()
        
        # Method 3: Count unique users who have RSVPs for this organization's events
        rsvp_user_count = db.session.query(User.id).join(RSVP).join(Event).filter(
            Event.organization_id == org_id
        ).distinct().count()
        
        # Use the highest count that makes sense
        total_org_users = max(modern_count, legacy_count, rsvp_user_count)
        
        print(f"👥 Total org users: {total_org_users}")
        
        def safe_get_time_field(event, field_name):
            """Safely get time field, handling missing columns"""
            try:
                value = getattr(event, field_name, None)
                return value.strftime('%H:%M') if value else None
            except AttributeError:
                # Column doesn't exist yet (before migration)
                return None
        
        def format_timing_display(event):
            """Format timing information for compact display"""
            arrive_by = safe_get_time_field(event, 'arrive_by_time')
            start_time = safe_get_time_field(event, 'start_time')
            end_time = safe_get_time_field(event, 'end_time')
            
            timing_parts = []
            if arrive_by:
                timing_parts.append(f"Arrive: {arrive_by}")
            if start_time:
                timing_parts.append(f"Start: {start_time}")
            if end_time:
                timing_parts.append(f"End: {end_time}")
            
            if timing_parts:
                return " | ".join(timing_parts)
            
            # Fallback to legacy time from date
            if event.date:
                return f"Time: {event.date.strftime('%H:%M')}"
            
            return None
        
        def get_rsvp_stats(event_id):
            """Get RSVP statistics for an event with detailed user information"""
            try:
                from flask_jwt_extended import get_jwt_identity
                
                # Get organization privacy setting
                org = Organization.query.get(org_id)
                members_can_view_rsvp = getattr(org, 'members_can_view_rsvp_status', True) if org else True
                
                # Get current user's role
                current_user_role = claims.get('role', 'Member')
                current_user_id = get_jwt_identity()
                
                # Determine if user can see detailed RSVP information
                can_see_details = (current_user_role == 'Admin') or members_can_view_rsvp
                
                rsvps = RSVP.query.filter_by(event_id=event_id).all()
                rsvp_count = 0
                yes_count = 0
                no_count = 0
                maybe_count = 0
                detailed_rsvps = []
                
                for rsvp in rsvps:
                    user = User.query.get(rsvp.user_id)
                    if user:
                        # Check if user belongs to the organization
                        user_in_org = (user.organization_id == org_id) or \
                                     UserOrganization.query.filter_by(
                                         user_id=user.id, 
                                         organization_id=org_id, 
                                         is_active=True
                                     ).first()
                        
                        if user_in_org:
                            rsvp_count += 1
                            if rsvp.status == 'Yes':
                                yes_count += 1
                            elif rsvp.status == 'No':
                                no_count += 1
                            elif rsvp.status == 'Maybe':
                                maybe_count += 1
                            
                            # Only include detailed RSVP info if user can see it or it's their own RSVP
                            if can_see_details or str(user.id) == str(current_user_id):
                                # Get user's section (check both UserOrganization and legacy User field)
                                section_name = "Unassigned"
                                user_org = UserOrganization.query.filter_by(
                                    user_id=user.id, 
                                    organization_id=org_id, 
                                    is_active=True
                                ).first()
                                
                                if user_org and user_org.section:
                                    section_name = user_org.section.name
                                elif user.section:
                                    section_name = user.section.name
                                
                                user_rsvp = {
                                    'user_id': user.id,
                                    'name': user.name or user.username,
                                    'status': rsvp.status,
                                    'section': section_name
                                }
                                
                                # Include comments and likelihood if available
                                if hasattr(rsvp, 'comments') and rsvp.comments:
                                    user_rsvp['comments'] = rsvp.comments
                                
                                if hasattr(rsvp, 'likelihood') and rsvp.likelihood is not None:
                                    user_rsvp['likelihood'] = rsvp.likelihood
                                
                                if hasattr(rsvp, 'updated_at') and rsvp.updated_at:
                                    user_rsvp['updated_at'] = rsvp.updated_at.isoformat()
                                
                                detailed_rsvps.append(user_rsvp)
                
                # Build response based on privacy settings
                response = {
                    'total_responses': rsvp_count,
                    'total_users': total_org_users,
                    'yes_count': yes_count,
                    'no_count': no_count,
                    'maybe_count': maybe_count,
                    'no_response_count': total_org_users - rsvp_count,
                    'can_view_details': can_see_details
                }
                
                # Only include detailed responses if user can see them
                if can_see_details:
                    response['responses'] = detailed_rsvps
                else:
                    # For non-admin users when visibility is disabled, 
                    # only show their own RSVP in the responses
                    current_user_rsvp = [r for r in detailed_rsvps if str(r['user_id']) == str(current_user_id)]
                    response['responses'] = current_user_rsvp
                    response['privacy_message'] = "Individual RSVP details are private. Only totals and your own response are shown."
                
                return response
                
            except Exception as e:
                print(f"❌ Error getting RSVP stats for event {event_id}: {e}")
                return {
                    'total_responses': 0,
                    'total_users': total_org_users,
                    'yes_count': 0,
                    'no_count': 0,
                    'maybe_count': 0,
                    'no_response_count': total_org_users,
                    'can_view_details': False
                }

        print(f"🔍 Building event response data...")
        event_data = []
        for i, e in enumerate(events):
            try:
                print(f"📅 Processing event {i+1}/{len(events)}: {e.title}")
                event_obj = {
                    'id': e.id,
                    'title': e.title,
                    'type': e.type,
                    'description': e.description,
                    'date': e.date.isoformat(),
                    'end_date': e.end_date.isoformat() if e.end_date else None,
                    'arrive_by_time': safe_get_time_field(e, 'arrive_by_time'),
                    'start_time': safe_get_time_field(e, 'start_time'),
                    'end_time': safe_get_time_field(e, 'end_time'),
                    # Legacy time field extracted from date for backward compatibility
                    'time': e.date.strftime('%H:%M') if e.date else None,
                    # Combined timing display for better UI
                    'timing_display': format_timing_display(e),
                    'location': e.location_address,  # For backward compatibility
                    'location_address': e.location_address,
                    'lat': e.location_lat,
                    'lng': e.location_lng,
                    'location_place_id': e.location_place_id,
                    'category_id': e.category_id,
                    'category': e.category.name if e.category else None,
                    'is_recurring': e.is_recurring,
                    'recurring_pattern': e.recurring_pattern,
                    'recurring_interval': e.recurring_interval,
                    'recurring_end_date': e.recurring_end_date.isoformat() if e.recurring_end_date else None,
                    'parent_event_id': e.parent_event_id,
                    'is_template': e.is_template,
                    'template_name': e.template_name,
                    'send_reminders': e.send_reminders,
                    'reminder_days_before': e.reminder_days_before,
                    'created_at': e.created_at.isoformat() if e.created_at else None,
                    'created_by': e.created_by,
                    'creator_name': e.creator.name if e.creator else None,
                    # Cancellation information
                    'is_cancelled': e.is_cancelled,
                    'cancelled_at': e.cancelled_at.isoformat() if e.cancelled_at else None,
                    'cancelled_by': e.cancelled_by,
                    'canceller_name': e.canceller.name if e.canceller else None,
                    'cancellation_reason': e.cancellation_reason,
                    'cancellation_notification_sent': e.cancellation_notification_sent,
                    # Multiple dates support
                    'has_multiple_dates': getattr(e, 'has_multiple_dates', False),
                    'final_date_selected': getattr(e, 'final_date_selected', True),
                    'date_selection_deadline': e.date_selection_deadline.isoformat() if getattr(e, 'date_selection_deadline', None) else None,
                    # RSVP statistics
                    'rsvp_stats': get_rsvp_stats(e.id)
                }
                event_data.append(event_obj)
            except Exception as e_error:
                print(f"❌ Error processing event {e.id} ({e.title}): {e_error}")
                continue
        
        print(f"✅ Successfully processed {len(event_data)} events, returning JSON response")
        return jsonify(event_data)
        
    except Exception as e:
        print(f"❌ Fatal error in get_events(): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load events', 'details': str(e)}), 500

@events_bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Parse dates (templates don't require dates)
    event_date = None
    end_date = None
    recurring_end_date = None
    
    if not data.get('is_template', False):
        # Regular events require a date
        if 'date' not in data:
            return jsonify({'error': 'Date is required for non-template events'}), 400
        event_date = datetime.fromisoformat(data['date'])
        end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
        recurring_end_date = datetime.fromisoformat(data['recurring_end_date']) if data.get('recurring_end_date') else None
    else:
        # Templates can have optional dates for reference
        if data.get('date'):
            event_date = datetime.fromisoformat(data['date'])
        if data.get('end_date'):
            end_date = datetime.fromisoformat(data['end_date'])
        if data.get('recurring_end_date'):
            recurring_end_date = datetime.fromisoformat(data['recurring_end_date'])
    
    # Parse time fields
    arrive_by_time = None
    start_time = None
    end_time = None
    
    if data.get('arrive_by_time'):
        arrive_by_time = datetime.strptime(data['arrive_by_time'], '%H:%M').time()
    if data.get('start_time'):
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    if data.get('end_time'):
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    
    # Create the main event (time fields will be ignored if columns don't exist)
    event_data = {
        'title': data.get('title') or data.get('name'),
        'type': data.get('type', 'Rehearsal'),
        'description': data.get('description'),
        'date': event_date,
        'end_date': end_date,
        'location_address': data.get('location_address'),
        'location_lat': data.get('lat'),
        'location_lng': data.get('lng'),
        'location_place_id': data.get('location_place_id'),
        'category_id': data.get('category_id'),
        'is_recurring': data.get('is_recurring', False),
        'recurring_pattern': data.get('recurring_pattern'),
        'recurring_interval': data.get('recurring_interval', 1),
        'recurring_end_date': recurring_end_date,
        'recurring_count': data.get('recurring_count'),
        'is_template': data.get('is_template', False),
        'template_name': data.get('template_name'),
        'send_reminders': data.get('send_reminders', True),
        'reminder_days_before': data.get('reminder_days_before', 1),
        'organization_id': org_id,
        'created_by': user_id
    }
    
    # Add time fields only if they exist in the model
    try:
        if hasattr(Event, 'arrive_by_time'):
            event_data['arrive_by_time'] = arrive_by_time
        if hasattr(Event, 'start_time'):
            event_data['start_time'] = start_time
        if hasattr(Event, 'end_time'):
            event_data['end_time'] = end_time
        if hasattr(Event, 'has_multiple_dates'):
            event_data['has_multiple_dates'] = data.get('has_multiple_dates', False)
        if hasattr(Event, 'final_date_selected'):
            event_data['final_date_selected'] = not data.get('has_multiple_dates', False)
        if hasattr(Event, 'date_selection_deadline'):
            event_data['date_selection_deadline'] = datetime.fromisoformat(data['date_selection_deadline']) if data.get('date_selection_deadline') else None
    except Exception:
        # Fields not available yet, skip them
        pass
    
    event = Event(**event_data)
    
    db.session.add(event)
    db.session.flush()  # Get the event ID for possible dates
    
    # Add multiple possible dates if specified
    if data.get('has_multiple_dates') and data.get('possible_dates'):
        from models import EventPossibleDate
        print(f"Creating multiple dates for event {event.id}")
        print(f"Possible dates data: {data.get('possible_dates')}")
        
        for i, pdate_data in enumerate(data['possible_dates']):
            try:
                print(f"Processing possible date {i}: {pdate_data}")
                
                # Skip if no date provided
                if not pdate_data.get('date') or pdate_data['date'] == '':
                    print(f"Skipping possible date {i} - no date provided")
                    continue
                
                pdate = EventPossibleDate(
                    event_id=event.id,
                    date=datetime.fromisoformat(pdate_data['date']),
                    end_date=datetime.fromisoformat(pdate_data['end_date']) if pdate_data.get('end_date') and pdate_data['end_date'] != '' else None,
                    arrive_by_time=datetime.strptime(pdate_data['arrive_by_time'], '%H:%M').time() if pdate_data.get('arrive_by_time') and pdate_data['arrive_by_time'] != '' else None,
                    start_time=datetime.strptime(pdate_data['start_time'], '%H:%M').time() if pdate_data.get('start_time') and pdate_data['start_time'] != '' else None,
                    end_time=datetime.strptime(pdate_data['end_time'], '%H:%M').time() if pdate_data.get('end_time') and pdate_data['end_time'] != '' else None
                )
                db.session.add(pdate)
                print(f"Successfully added possible date {i}")
            except Exception as e:
                print(f"Error processing possible date {i}: {e}")
                print(f"Problematic data: {pdate_data}")
                # Continue processing other dates instead of failing completely
                continue
    
    db.session.commit()
    
    # Create recurring events if specified
    if event.is_recurring and not event.is_template:
        create_recurring_events(event)
    
    # Send new event notifications (only for non-template events)
    if not event.is_template and email_service and data.get('send_notification', True):
        try:
            # Get all users in the organization
            users = User.query.filter_by(organization_id=org_id).all()
            email_service.send_new_event_notification(event, users)
        except Exception as e:
            print(f"Failed to send new event notification: {e}")
    
    return jsonify({'msg': 'Event created', 'id': event.id})

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def edit_event(event_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    data = request.get_json()
    
    # Update basic fields
    event.title = data.get('title', event.title)
    event.type = data.get('type', event.type)
    event.description = data.get('description', event.description)
    
    # Update dates
    if 'date' in data:
        event.date = datetime.fromisoformat(data['date'])
    if 'end_date' in data:
        event.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
    
    # Update time fields (only if columns exist)
    if 'arrive_by_time' in data:
        try:
            if hasattr(event, 'arrive_by_time'):
                event.arrive_by_time = datetime.strptime(data['arrive_by_time'], '%H:%M').time() if data['arrive_by_time'] else None
        except AttributeError:
            # Column doesn't exist yet
            pass
    if 'start_time' in data:
        try:
            if hasattr(event, 'start_time'):
                event.start_time = datetime.strptime(data['start_time'], '%H:%M').time() if data['start_time'] else None
        except AttributeError:
            # Column doesn't exist yet
            pass
    if 'end_time' in data:
        try:
            if hasattr(event, 'end_time'):
                event.end_time = datetime.strptime(data['end_time'], '%H:%M').time() if data['end_time'] else None
        except AttributeError:
            # Column doesn't exist yet
            pass
    
    # Update location
    event.location_address = data.get('location_address', event.location_address)
    event.location_lat = data.get('lat', event.location_lat)
    event.location_lng = data.get('lng', event.location_lng)
    event.location_place_id = data.get('location_place_id', event.location_place_id)
    
    # Update category and settings
    event.category_id = data.get('category_id', event.category_id)
    event.send_reminders = data.get('send_reminders', event.send_reminders)
    event.reminder_days_before = data.get('reminder_days_before', event.reminder_days_before)
    
    # Update template fields
    event.is_template = data.get('is_template', event.is_template)
    event.template_name = data.get('template_name', event.template_name)
    
    db.session.commit()
    return jsonify({'msg': 'Event updated'})

@events_bp.route('/<int:event_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_event(event_id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    user_id = get_jwt_identity()
    data = request.get_json()
    
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    
    # Check if event is already cancelled
    if event.is_cancelled:
        return jsonify({'msg': 'Event is already cancelled'}), 400
    
    # Get cancellation data
    reason = data.get('reason', '').strip()
    send_notification = data.get('send_notification', False)
    
    if not reason:
        return jsonify({'msg': 'Cancellation reason is required'}), 400
    
    # Mark event as cancelled
    event.is_cancelled = True
    event.cancelled_at = datetime.utcnow()
    event.cancelled_by = user_id
    event.cancellation_reason = reason
    event.cancellation_notification_sent = False
    
    try:
        db.session.commit()
        
        # Send cancellation notifications if requested
        if send_notification and email_service:
            try:
                print(f"🔍 Starting cancellation notification process for event {event_id}")
                
                # Get all active members of the organization
                from models import UserOrganization
                user_orgs = UserOrganization.query.filter_by(
                    organization_id=org_id,
                    is_active=True
                ).all()
                
                print(f"📊 Found {len(user_orgs)} active user organizations")
                
                users_to_notify = []
                for user_org in user_orgs:
                    user = User.query.get(user_org.user_id)
                    if user and user.email and user.email_notifications:
                        users_to_notify.append(user)
                        print(f"✅ Added user {user.name} ({user.email}) to notification list")
                    elif user:
                        print(f"⚠️  Skipped user {user.name} - email: {user.email}, notifications: {user.email_notifications}")
                
                print(f"📧 Will send notifications to {len(users_to_notify)} users")
                
                success_count = 0
                # Send cancellation email to each user
                for user in users_to_notify:
                    try:
                        result = email_service.send_event_cancellation_notification(
                            user=user,
                            event=event,
                            reason=reason
                        )
                        if result:
                            success_count += 1
                            print(f"✅ Successfully sent cancellation email to {user.email}")
                        else:
                            print(f"❌ Failed to send cancellation email to {user.email}")
                    except Exception as e:
                        print(f"❌ Error sending to {user.email}: {e}")
                
                print(f"📈 Successfully sent {success_count} of {len(users_to_notify)} cancellation emails")
                
                # Mark notification as sent
                event.cancellation_notification_sent = True
                db.session.commit()
                
                return jsonify({
                    'msg': 'Event cancelled successfully',
                    'notification_sent': True,
                    'notifications_count': len(users_to_notify),
                    'success_count': success_count
                })
                
            except Exception as e:
                print(f"Error sending cancellation notifications: {e}")
                return jsonify({
                    'msg': 'Event cancelled successfully but failed to send notifications',
                    'notification_sent': False,
                    'error': str(e)
                })
        else:
            return jsonify({
                'msg': 'Event cancelled successfully',
                'notification_sent': False
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to cancel event', 'error': str(e)}), 500

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    print(f"🗑️  DELETE event request received for event_id: {event_id}")
    
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        print(f"❌ Access denied - user role: {claims.get('role')}")
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    print(f"🏢 Organization ID: {org_id}")
    
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    print(f"📅 Found event: {event.title} (ID: {event.id})")
    
    try:
        # First, delete all RSVPs associated with this event
        rsvps = RSVP.query.filter_by(event_id=event_id).all()
        print(f"🎫 Found {len(rsvps)} RSVPs to delete")
        
        for rsvp in rsvps:
            db.session.delete(rsvp)
        
        # Delete any recurring child events if this is a parent event
        child_events = Event.query.filter_by(parent_event_id=event_id).all()
        print(f"🔗 Found {len(child_events)} child events to delete")
        
        for child_event in child_events:
            # Delete RSVPs for child events too
            child_rsvps = RSVP.query.filter_by(event_id=child_event.id).all()
            for child_rsvp in child_rsvps:
                db.session.delete(child_rsvp)
            db.session.delete(child_event)
        
        # Now delete the main event
        db.session.delete(event)
        db.session.commit()
        
        print(f"✅ Successfully deleted event: {event.title} (ID: {event_id})")
        return jsonify({'msg': 'Event deleted'})
        
    except Exception as e:
        print(f"❌ Error deleting event {event_id}: {e}")
        db.session.rollback()
        return jsonify({'msg': f'Failed to delete event: {str(e)}'}), 500

@events_bp.route('/<int:event_id>/rsvp', methods=['POST'])
@jwt_required()
def rsvp_event(event_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    status = data.get('status')
    comments = data.get('comments', '').strip() or None  # Optional comments
    likelihood = data.get('likelihood')  # Optional likelihood (1-100) for "Maybe" responses
    
    # Handle both mobile format (attending/maybe/not_attending) and web format (Yes/No/Maybe)
    mobile_statuses = ['attending', 'maybe', 'not_attending']
    web_statuses = ['Yes', 'No', 'Maybe', 'yes', 'no', 'maybe']
    
    if status in mobile_statuses:
        # Convert mobile format to backend format
        status = mobile_to_backend_status(status)
    elif status in web_statuses:
        # Normalize web status values to proper case
        if status in ['Yes', 'No', 'Maybe']:
            # Already in proper case
            pass
        elif status in ['yes', 'no', 'maybe']:
            # Convert lowercase to proper case
            status = status.capitalize()
    else:
        return jsonify({'msg': 'Invalid RSVP status. Use: Yes/No/Maybe or attending/maybe/not_attending'}), 400
    
    # Validate likelihood for "Maybe" responses
    if likelihood is not None:
        if status != 'Maybe':
            return jsonify({'msg': 'Likelihood can only be set for "Maybe" responses'}), 400
        if not isinstance(likelihood, int) or likelihood < 1 or likelihood > 100:
            return jsonify({'msg': 'Likelihood must be an integer between 1 and 100'}), 400
    elif status == 'Maybe' and likelihood is None:
        # Default likelihood for "Maybe" responses if not provided
        likelihood = 50
    
    # Clear likelihood if status is not "Maybe"
    if status != 'Maybe':
        likelihood = None
    
    # Track previous status for admin notifications
    previous_status = None
    rsvp = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()
    if rsvp:
        previous_status = rsvp.status
        rsvp.status = status
        rsvp.comments = comments
        rsvp.likelihood = likelihood
        rsvp.updated_at = datetime.utcnow()
    else:
        rsvp = RSVP(user_id=user_id, event_id=event_id, status=status, 
                   comments=comments, likelihood=likelihood)
        db.session.add(rsvp)
    
    db.session.commit()
    
    # Track RSVP change for admin notifications
    try:
        from services.admin_attendance_service import AdminAttendanceService
        AdminAttendanceService.track_rsvp_change(event_id, user_id, previous_status, status)
    except Exception as e:
        # Don't fail the RSVP if notification tracking fails
        print(f"Error tracking RSVP change: {str(e)}")
    
    return jsonify({'msg': 'RSVP updated'})

# New RSVP endpoints for mobile app
@events_bp.route('/<int:event_id>/rsvp/', methods=['GET'])
@jwt_required()
def get_user_rsvp(event_id):
    """Get the current user's RSVP status for an event"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    # Verify event exists and belongs to user's organization
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
    if not event:
        return jsonify({'msg': 'Event not found'}), 404
    
    # Find user's RSVP
    rsvp = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()
    if not rsvp:
        return jsonify({'msg': 'RSVP not found'}), 404
    
    # Convert backend status to mobile format
    mobile_status = backend_to_mobile_status(rsvp.status)
    
    return jsonify({
        'status': mobile_status,
        'event_id': event_id,
        'user_id': int(user_id),
        'comments': rsvp.comments,
        'likelihood': rsvp.likelihood,
        'timestamp': rsvp.created_at.isoformat() if rsvp.created_at else None,
        'updated_at': rsvp.updated_at.isoformat() if hasattr(rsvp, 'updated_at') and rsvp.updated_at else None
    })

@events_bp.route('/<int:event_id>/rsvp/', methods=['POST'])
@jwt_required()
def create_user_rsvp(event_id):
    """Create a new RSVP for the current user"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    org_id = claims.get('organization_id')
    data = request.get_json()
    
    # Verify event exists and belongs to user's organization
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
    if not event:
        return jsonify({'msg': 'Event not found'}), 404
    
    # Validate mobile status format
    mobile_status = data.get('status')
    if not mobile_status or mobile_status not in ['attending', 'maybe', 'not_attending']:
        return jsonify({'msg': 'Invalid status. Must be: attending, maybe, or not_attending'}), 400
    
    # Check if RSVP already exists
    existing_rsvp = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing_rsvp:
        return jsonify({'msg': 'RSVP already exists. Use PUT to update.'}), 400
    
    # Convert mobile status to backend format
    backend_status = mobile_to_backend_status(mobile_status)
    
    # Create new RSVP
    rsvp = RSVP(user_id=user_id, event_id=event_id, status=backend_status)
    db.session.add(rsvp)
    db.session.commit()
    
    # Track RSVP change for admin notifications
    try:
        from services.admin_attendance_service import AdminAttendanceService
        AdminAttendanceService.track_rsvp_change(event_id, user_id, None, backend_status)
    except Exception as e:
        # Don't fail the RSVP if notification tracking fails
        print(f"Error tracking RSVP change: {str(e)}")
    
    return jsonify({
        'status': mobile_status,
        'event_id': event_id,
        'user_id': int(user_id),
        'timestamp': rsvp.created_at.isoformat() if rsvp.created_at else None
    }), 201

@events_bp.route('/<int:event_id>/rsvp/', methods=['PUT'])
@jwt_required()
def update_user_rsvp(event_id):
    """Update the current user's RSVP for an event"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    org_id = claims.get('organization_id')
    data = request.get_json()
    
    # Verify event exists and belongs to user's organization
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
    if not event:
        return jsonify({'msg': 'Event not found'}), 404
    
    # Validate mobile status format
    mobile_status = data.get('status')
    if not mobile_status or mobile_status not in ['attending', 'maybe', 'not_attending']:
        return jsonify({'msg': 'Invalid status. Must be: attending, maybe, or not_attending'}), 400
    
    # Find existing RSVP
    rsvp = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()
    if not rsvp:
        return jsonify({'msg': 'RSVP not found'}), 404
    
    # Convert mobile status to backend format
    previous_status = rsvp.status
    backend_status = mobile_to_backend_status(mobile_status)
    
    # Update RSVP
    rsvp.status = backend_status
    db.session.commit()
    
    # Track RSVP change for admin notifications
    try:
        from services.admin_attendance_service import AdminAttendanceService
        AdminAttendanceService.track_rsvp_change(event_id, user_id, previous_status, backend_status)
    except Exception as e:
        # Don't fail the RSVP if notification tracking fails
        print(f"Error tracking RSVP change: {str(e)}")
    
    return jsonify({
        'status': mobile_status,
        'event_id': event_id,
        'user_id': int(user_id),
        'timestamp': rsvp.created_at.isoformat() if rsvp.created_at else None
    })

@events_bp.route('/<int:event_id>/rsvp/', methods=['DELETE'])
@jwt_required()
def delete_user_rsvp(event_id):
    """Delete the current user's RSVP for an event"""
    user_id = get_jwt_identity()
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    # Verify event exists and belongs to user's organization
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
    if not event:
        return jsonify({'msg': 'Event not found'}), 404
    
    # Find existing RSVP
    rsvp = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()
    if not rsvp:
        return jsonify({'msg': 'RSVP not found'}), 404
    
    # Track RSVP deletion for admin notifications
    try:
        from services.admin_attendance_service import AdminAttendanceService
        AdminAttendanceService.track_rsvp_change(event_id, user_id, rsvp.status, None)
    except Exception as e:
        # Don't fail the RSVP if notification tracking fails
        print(f"Error tracking RSVP change: {str(e)}")
    
    # Delete RSVP
    db.session.delete(rsvp)
    db.session.commit()
    
    return '', 204

@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    claims = get_jwt()
    org_id = claims.get('organization_id')
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    
    # Method 1: Count via UserOrganization (modern approach)
    modern_count = db.session.query(User).join(
        UserOrganization, 
        (User.id == UserOrganization.user_id) & 
        (UserOrganization.organization_id == org_id) & 
        (UserOrganization.is_active == True)
    ).count()
    
    # Method 2: Count via legacy User.organization_id
    legacy_count = User.query.filter_by(organization_id=org_id).count()
    
    # Method 3: Count unique users who have RSVPs for this organization's events
    rsvp_user_count = db.session.query(User.id).join(RSVP).join(Event).filter(
        Event.organization_id == org_id
    ).distinct().count()
    
    # Use the highest count that makes sense
    total_org_users = max(modern_count, legacy_count, rsvp_user_count)
    
    def safe_get_time_field(event, field_name):
        """Safely get time field, handling missing columns"""
        try:
            value = getattr(event, field_name, None)
            return value.strftime('%H:%M') if value else None
        except AttributeError:
            # Column doesn't exist yet (before migration)
            return None
    
    def format_timing_display(event):
        """Format timing information for compact display"""
        arrive_by = safe_get_time_field(event, 'arrive_by_time')
        start_time = safe_get_time_field(event, 'start_time')
        end_time = safe_get_time_field(event, 'end_time')
        
        timing_parts = []
        if arrive_by:
            timing_parts.append(f"Arrive: {arrive_by}")
        if start_time:
            timing_parts.append(f"Start: {start_time}")
        if end_time:
            timing_parts.append(f"End: {end_time}")
        
        if timing_parts:
            return " | ".join(timing_parts)
        
        # Fallback to legacy time from date
        if event.date:
            return f"Time: {event.date.strftime('%H:%M')}"
        
        return None
    
    def get_rsvp_stats(event_id):
        """Get RSVP statistics for an event with detailed user information"""
        rsvps = RSVP.query.filter_by(event_id=event_id).all()
        rsvp_count = 0
        yes_count = 0
        no_count = 0
        maybe_count = 0
        detailed_rsvps = []
        
        for rsvp in rsvps:
            user = User.query.get(rsvp.user_id)
            if user:
                # Check if user belongs to the organization
                user_in_org = (user.organization_id == org_id) or \
                             UserOrganization.query.filter_by(
                                 user_id=user.id, 
                                 organization_id=org_id, 
                                 is_active=True
                             ).first()
                
                if user_in_org:
                    rsvp_count += 1
                    if rsvp.status == 'Yes':
                        yes_count += 1
                    elif rsvp.status == 'No':
                        no_count += 1
                    elif rsvp.status == 'Maybe':
                        maybe_count += 1
                    
                    # Get user's section (check both UserOrganization and legacy User field)
                    section_name = "Unassigned"
                    user_org = UserOrganization.query.filter_by(
                        user_id=user.id, 
                        organization_id=org_id, 
                        is_active=True
                    ).first()
                    
                    if user_org and user_org.section:
                        section_name = user_org.section.name
                    elif user.section:
                        section_name = user.section.name
                    
                    detailed_rsvps.append({
                        'user_id': user.id,
                        'name': user.name or user.username,
                        'status': rsvp.status,
                        'section': section_name
                    })
        
        return {
            'total_responses': rsvp_count,
            'total_users': total_org_users,
            'yes_count': yes_count,
            'no_count': no_count,
            'maybe_count': maybe_count,
            'no_response_count': total_org_users - rsvp_count,
            'responses': detailed_rsvps
        }
    
    return jsonify({
        'id': event.id,
        'title': event.title,
        'type': event.type,
        'description': event.description,
        'date': event.date.isoformat(),
        'end_date': event.end_date.isoformat() if event.end_date else None,
        'arrive_by_time': safe_get_time_field(event, 'arrive_by_time'),
        'start_time': safe_get_time_field(event, 'start_time'),
        'end_time': safe_get_time_field(event, 'end_time'),
        # Legacy time field extracted from date for backward compatibility
        'time': event.date.strftime('%H:%M') if event.date else None,
        # Combined timing display for better UI
        'timing_display': format_timing_display(event),
        'location': event.location_address,  # For backward compatibility
        'location_address': event.location_address,
        'lat': event.location_lat,
        'lng': event.location_lng,
        'location_place_id': event.location_place_id,
        'category_id': event.category_id,
        'category': event.category.name if event.category else None,
        'is_recurring': event.is_recurring,
        'recurring_pattern': event.recurring_pattern,
        'recurring_interval': event.recurring_interval,
        'recurring_end_date': event.recurring_end_date.isoformat() if event.recurring_end_date else None,
        'parent_event_id': event.parent_event_id,
        'is_template': event.is_template,
        'template_name': event.template_name,
        'send_reminders': event.send_reminders,
        'reminder_days_before': event.reminder_days_before,
        'created_at': event.created_at.isoformat() if event.created_at else None,
        'created_by': event.created_by,
        'creator_name': event.creator.name if event.creator else None,
        # Cancellation information
        'is_cancelled': event.is_cancelled,
        'cancelled_at': event.cancelled_at.isoformat() if event.cancelled_at else None,
        'cancelled_by': event.cancelled_by,
        'canceller_name': event.canceller.name if event.canceller else None,
        'cancellation_reason': event.cancellation_reason,
        'cancellation_notification_sent': event.cancellation_notification_sent,
        # RSVP statistics
        'rsvp_stats': get_rsvp_stats(event.id)
    })

@events_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_event_categories():
    """Get all event categories for the organization."""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    categories = EventCategory.query.filter_by(organization_id=org_id).order_by(EventCategory.name).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'color': c.color,
        'icon': c.icon,
        'is_default': c.is_default,
        'requires_location': c.requires_location,
        'default_duration_hours': c.default_duration_hours
    } for c in categories])

@events_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_event_category():
    """Create a new event category."""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name', '').strip():
        return jsonify({'error': 'Category name is required'}), 400
    
    # Check if category name already exists for this organization
    existing_category = EventCategory.query.filter_by(
        name=data['name'].strip(),
        organization_id=org_id
    ).first()
    
    if existing_category:
        return jsonify({'error': f'A category named "{data["name"].strip()}" already exists'}), 400
    
    try:
        category = EventCategory(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            color=data.get('color', '#007bff'),
            icon=data.get('icon', '📅'),
            organization_id=org_id,
            is_default=data.get('is_default', False),
            requires_location=data.get('requires_location', True),
            default_duration_hours=data.get('default_duration_hours', 2)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'color': category.color,
                'icon': category.icon,
                'is_default': category.is_default,
                'requires_location': category.requires_location,
                'default_duration_hours': category.default_duration_hours
            },
            'message': 'Category created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        
        # Handle specific database errors
        error_message = str(e)
        if 'duplicate key value violates unique constraint' in error_message:
            if 'event_category_name_organization_id_key' in error_message:
                return jsonify({'error': f'A category named "{data.get("name", "")}" already exists'}), 400
        
        # Generic error fallback
        return jsonify({'error': 'Failed to create category. Please try again.'}), 400

@events_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_event_category(category_id):
    """Update an event category."""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    data = request.get_json()
    
    category = EventCategory.query.filter_by(id=category_id, organization_id=org_id).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    try:
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.color = data.get('color', category.color)
        category.icon = data.get('icon', category.icon)
        category.is_default = data.get('is_default', category.is_default)
        category.requires_location = data.get('requires_location', category.requires_location)
        category.default_duration_hours = data.get('default_duration_hours', category.default_duration_hours)
        
        db.session.commit()
        
        return jsonify({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'color': category.color,
                'icon': category.icon,
                'is_default': category.is_default,
                'requires_location': category.requires_location,
                'default_duration_hours': category.default_duration_hours
            },
            'message': 'Category updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@events_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_event_category(category_id):
    """Delete an event category."""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    category = EventCategory.query.filter_by(id=category_id, organization_id=org_id).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Check if any events use this category
    events_count = Event.query.filter_by(category_id=category_id).count()
    if events_count > 0:
        return jsonify({'error': f'Cannot delete category. {events_count} events are using this category.'}), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@events_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_event_templates():
    """Get all event templates for the organization."""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        
        # Use the new EventTemplate model
        templates = EventTemplate.query.filter_by(
            organization_id=org_id,
            is_active=True
        ).order_by(EventTemplate.name).all()
        
        # Format for frontend compatibility
        template_list = []
        for template in templates:
            template_dict = {
                'id': template.id,
                'template_name': template.name,  # Frontend expects template_name
                'description': template.description,
                'category_id': template.category_id,
                'default_location_address': template.default_location_address,
                'default_start_time': template.default_start_time.strftime('%H:%M') if template.default_start_time else None,
                'default_end_time': None,  # Calculate from duration if needed
                'default_arrive_by_time': None,  # Calculate from offset if needed
                'default_rsvp_required': template.default_rsvp_required,
                'default_rsvp_deadline_hours': 24,  # Default value
                'default_reminder_hours': template.default_reminder_days_before * 24 if template.default_reminder_days_before else 24,
                'default_send_invitations': template.default_send_reminders,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None
            }
            
            # Add category information if available
            if template.category_id:
                category = EventCategory.query.get(template.category_id)
                if category:
                    template_dict['category'] = {
                        'id': category.id,
                        'name': category.name,
                        'color': category.color,
                        'description': category.description
                    }
            
            template_list.append(template_dict)
        
        return jsonify(template_list), 200
        
    except Exception as e:
        print(f"Error fetching templates: {str(e)}")
        return jsonify({'error': 'Failed to fetch templates'}), 500

@events_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_event_template():
    """Create a new event template."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        org_id = claims.get('organization_id')
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('template_name', '').strip():
            return jsonify({'error': 'Template name is required'}), 400
        
        # Check for duplicate template names in organization
        existing = EventTemplate.query.filter_by(
            name=data['template_name'].strip(),
            organization_id=org_id,
            is_active=True
        ).first()
        
        if existing:
            return jsonify({'error': 'A template with this name already exists'}), 400
        
        # Create new template
        template = EventTemplate(
            name=data['template_name'].strip(),
            description=data.get('description', '').strip() or None,
            category_id=data.get('category_id') or None,
            default_location_address=data.get('default_location_address', '').strip() or None,
            default_start_time=None,
            default_rsvp_required=data.get('default_rsvp_required', True),
            default_send_reminders=data.get('default_send_invitations', True),
            default_reminder_days_before=data.get('default_reminder_hours', 24) // 24,
            organization_id=org_id,
            created_by=user_id
        )
        
        # Handle time fields
        if data.get('default_start_time'):
            try:
                start_time = datetime.strptime(data['default_start_time'], '%H:%M').time()
                template.default_start_time = start_time
            except ValueError:
                pass
        
        db.session.add(template)
        db.session.commit()
        
        # Return template in expected format
        result = {
            'id': template.id,
            'template_name': template.name,
            'description': template.description,
            'category_id': template.category_id,
            'default_location_address': template.default_location_address,
            'default_start_time': template.default_start_time.strftime('%H:%M') if template.default_start_time else None,
            'default_end_time': None,
            'default_arrive_by_time': None,
            'default_rsvp_required': template.default_rsvp_required,
            'default_rsvp_deadline_hours': 24,
            'default_reminder_hours': template.default_reminder_days_before * 24 if template.default_reminder_days_before else 24,
            'default_send_invitations': template.default_send_reminders,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat()
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating template: {str(e)}")
        return jsonify({'error': 'Failed to create template'}), 500

@events_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_event_template(template_id):
    """Update an event template."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        org_id = claims.get('organization_id')
        data = request.get_json()
        
        # Get template
        template = EventTemplate.query.filter_by(
            id=template_id,
            organization_id=org_id,
            is_active=True
        ).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Validate required fields
        if not data.get('template_name', '').strip():
            return jsonify({'error': 'Template name is required'}), 400
        
        # Check for duplicate names (excluding current template)
        existing = EventTemplate.query.filter(
            EventTemplate.name == data['template_name'].strip(),
            EventTemplate.organization_id == org_id,
            EventTemplate.id != template_id,
            EventTemplate.is_active == True
        ).first()
        
        if existing:
            return jsonify({'error': 'A template with this name already exists'}), 400
        
        # Update template
        template.name = data['template_name'].strip()
        template.description = data.get('description', '').strip() or None
        template.category_id = data.get('category_id') or None
        template.default_location_address = data.get('default_location_address', '').strip() or None
        template.default_rsvp_required = data.get('default_rsvp_required', True)
        template.default_send_reminders = data.get('default_send_invitations', True)
        template.default_reminder_days_before = data.get('default_reminder_hours', 24) // 24
        template.updated_at = datetime.utcnow()
        
        # Handle time fields
        if data.get('default_start_time'):
            try:
                start_time = datetime.strptime(data['default_start_time'], '%H:%M').time()
                template.default_start_time = start_time
            except ValueError:
                template.default_start_time = None
        else:
            template.default_start_time = None
        
        db.session.commit()
        
        # Return updated template
        result = {
            'id': template.id,
            'template_name': template.name,
            'description': template.description,
            'category_id': template.category_id,
            'default_location_address': template.default_location_address,
            'default_start_time': template.default_start_time.strftime('%H:%M') if template.default_start_time else None,
            'default_end_time': None,
            'default_arrive_by_time': None,
            'default_rsvp_required': template.default_rsvp_required,
            'default_rsvp_deadline_hours': 24,
            'default_reminder_hours': template.default_reminder_days_before * 24 if template.default_reminder_days_before else 24,
            'default_send_invitations': template.default_send_reminders,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat()
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating template: {str(e)}")
        return jsonify({'error': 'Failed to update template'}), 500

@events_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_event_template(template_id):
    """Delete an event template (soft delete)."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        org_id = claims.get('organization_id')
        
        # Get template
        template = EventTemplate.query.filter_by(
            id=template_id,
            organization_id=org_id,
            is_active=True
        ).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Soft delete
        template.is_active = False
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting template: {str(e)}")
        return jsonify({'error': 'Failed to delete template'}), 500

@events_bp.route('/from-template/<int:template_id>', methods=['POST'])
@jwt_required()
def create_from_template(template_id):
    """Create a new event from a template."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        org_id = claims.get('organization_id')
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get the template from EventTemplate model
        template = EventTemplate.query.filter_by(
            id=template_id, 
            organization_id=org_id,
            is_active=True
        ).first()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Validate required data
        if not data.get('date'):
            return jsonify({'error': 'Event date is required'}), 400
        
        try:
            event_date = datetime.fromisoformat(data['date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Calculate end date if duration is available
        end_date = None
        if template.default_duration_hours:
            end_date = event_date + timedelta(hours=template.default_duration_hours)
        
        # Create event from template
        event = Event(
            title=data.get('title', template.default_title or template.name),
            type='Event',  # Default type
            description=data.get('description', template.default_description or template.description),
            date=event_date,
            end_date=end_date,
            location_address=data.get('location_address', template.default_location_address),
            location_lat=template.default_location_lat,
            location_lng=template.default_location_lng,
            location_place_id=template.default_location_place_id,
            category_id=template.category_id,
            send_reminders=template.default_send_reminders,
            reminder_days_before=template.default_reminder_days_before,
            organization_id=org_id,
            created_by=user_id,
            template_id=template_id  # Link to the template used
        )
        
        # Add time fields if they exist in the model
        try:
            if template.default_start_time:
                event.start_time = template.default_start_time
            if template.default_arrive_by_offset and template.default_start_time:
                # Calculate arrive by time from start time and offset
                start_datetime = datetime.combine(event_date.date(), template.default_start_time)
                arrive_by_datetime = start_datetime - timedelta(minutes=template.default_arrive_by_offset)
                event.arrive_by_time = arrive_by_datetime.time()
        except AttributeError:
            # Time fields don't exist in Event model yet
            pass
        
        db.session.add(event)
        db.session.flush()  # Get the event ID
        
        # Update template usage count
        template.usage_count = (template.usage_count or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Event created from template successfully',
            'id': event.id,
            'event': {
                'id': event.id,
                'title': event.title,
                'date': event.date.isoformat(),
                'location_address': event.location_address
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating event from template: {str(e)}")
        return jsonify({'error': 'Failed to create event from template'}), 500

@events_bp.route('/<int:event_id>/export-rsvps', methods=['GET'])
@jwt_required()
def export_rsvps(event_id):
    """Export RSVP list as CSV or PDF."""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    
    # Get format (csv or pdf)
    export_format = request.args.get('format', 'csv').lower()
    
    # Get all RSVPs for the event
    rsvps = db.session.query(RSVP, User).join(User).filter(RSVP.event_id == event_id).all()
    
    if export_format == 'csv':
        return export_rsvps_csv(event, rsvps)
    elif export_format == 'pdf':
        return export_rsvps_pdf(event, rsvps)
    else:
        return jsonify({'msg': 'Invalid format. Use csv or pdf'}), 400

def export_rsvps_csv(event, rsvps):
    """Export RSVPs as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Username', 'Email', 'Phone', 'Section', 'RSVP Status'])
    
    # Write data
    for rsvp, user in rsvps:
        writer.writerow([
            user.name or user.username,
            user.username,
            user.email,
            user.phone or '',
            user.section.name if user.section else '',
            rsvp.status
        ])
    
    # Create response
    from flask import make_response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{event.title}_rsvps.csv"'
    return response

def export_rsvps_pdf(event, rsvps):
    """Export RSVPs as PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create content
    story = []
    
    # Title
    title = Paragraph(f"RSVP List: {event.title}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Event details
    event_info = Paragraph(f"Date: {event.date.strftime('%Y-%m-%d %H:%M')}<br/>Location: {event.location_address or 'TBD'}", styles['Normal'])
    story.append(event_info)
    story.append(Spacer(1, 12))
    
    # RSVP table
    data = [['Name', 'Username', 'Email', 'Phone', 'Section', 'RSVP']]
    for rsvp, user in rsvps:
        data.append([
            user.name or user.username,
            user.username,
            user.email,
            user.phone or '',
            user.section.name if user.section else '',
            rsvp.status
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    doc.build(story)
    
    # Create response
    from flask import make_response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{event.title}_rsvps.pdf"'
    return response

def create_recurring_events(parent_event):
    """Create recurring event instances based on the parent event's settings."""
    if not parent_event.is_recurring:
        return
    
    current_date = parent_event.date
    count = 0
    max_count = parent_event.recurring_count or 100  # Limit to prevent runaway creation
    
    while count < max_count:
        # Calculate next occurrence
        if parent_event.recurring_pattern == 'daily':
            next_date = current_date + timedelta(days=parent_event.recurring_interval)
        elif parent_event.recurring_pattern == 'weekly':
            next_date = current_date + timedelta(weeks=parent_event.recurring_interval)
        elif parent_event.recurring_pattern == 'monthly':
            next_date = current_date + relativedelta(months=parent_event.recurring_interval)
        elif parent_event.recurring_pattern == 'yearly':
            next_date = current_date + relativedelta(years=parent_event.recurring_interval)
        else:
            break
        
        # Check if we've exceeded the end date
        if parent_event.recurring_end_date and next_date > parent_event.recurring_end_date:
            break
        
        # Create the recurring event instance
        recurring_event = Event(
            title=parent_event.title,
            type=parent_event.type,
            description=parent_event.description,
            date=next_date,
            end_date=parent_event.end_date + (next_date - parent_event.date) if parent_event.end_date else None,
            location_address=parent_event.location_address,
            location_lat=parent_event.location_lat,
            location_lng=parent_event.location_lng,
            location_place_id=parent_event.location_place_id,
            category_id=parent_event.category_id,
            is_recurring=False,  # Instances are not recurring themselves
            parent_event_id=parent_event.id,
            send_reminders=parent_event.send_reminders,
            reminder_days_before=parent_event.reminder_days_before,
            organization_id=parent_event.organization_id,
            created_by=parent_event.created_by
        )
        
        db.session.add(recurring_event)
        current_date = next_date
        count += 1
    
    db.session.commit()

def send_event_reminder(event, users):
    """Send reminder emails for an event. Currently logs to console."""
    print(f"=== EVENT REMINDER ===")
    print(f"Event: {event.title}")
    print(f"Date: {event.date}")
    print(f"Location: {event.location_address}")
    print(f"Recipients: {', '.join([user.email for user in users])}")
    print("=======================")
    # TODO: Implement actual email sending when email service is configured

@events_bp.route('/<int:event_id>/rsvp-report/pdf', methods=['GET'])
@jwt_required()
def download_event_rsvp_pdf(event_id):
    """Download PDF report of event RSVP status"""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    
    try:
        from services.pdf_service import PDFReportService
        
        # Generate PDF
        pdf_data = PDFReportService.generate_event_rsvp_report(event_id, org_id)
        
        if not pdf_data:
            return jsonify({'msg': 'Event not found'}), 404
        
        # Get event name for filename
        event = Event.query.filter_by(id=event_id, organization_id=org_id).first()
        if not event:
            return jsonify({'msg': 'Event not found'}), 404
        
        # Create safe filename
        safe_title = "".join(c for c in event.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"RSVP_Report_{safe_title}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        
        # Create response
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except ImportError:
        return jsonify({'msg': 'PDF service not available. Please install reportlab: pip install reportlab'}), 500
    except Exception as e:
        return jsonify({'msg': f'Error generating PDF: {str(e)}'}), 500


# =====================
# ADVANCED EVENT TEMPLATE ROUTES
# =====================

@events_bp.route('/advanced-templates', methods=['GET'])
@jwt_required()
def get_advanced_event_templates():
    """Get all advanced event templates for the user's organization"""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        
        templates = EventTemplate.query.filter_by(
            organization_id=org_id,
            is_active=True
        ).order_by(EventTemplate.name).all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200
        
    except Exception as e:
        return jsonify({'msg': f'Error fetching templates: {str(e)}'}), 500


@events_bp.route('/advanced-templates', methods=['POST'])
@jwt_required()
def create_advanced_event_template():
    """Create a new advanced event template"""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check for required fields
        if not data.get('name'):
            return jsonify({'msg': 'Template name is required'}), 400
        
        # Check if template name already exists in organization
        existing = EventTemplate.query.filter_by(
            name=data['name'],
            organization_id=org_id
        ).first()
        
        if existing:
            return jsonify({'msg': 'Template name already exists'}), 409
        
        # Create new template
        template = EventTemplate(
            name=data['name'],
            description=data.get('description'),
            default_title=data.get('default_title'),
            default_description=data.get('default_description'),
            default_duration_hours=data.get('default_duration_hours', 2),
            default_location_address=data.get('default_location_address'),
            default_location_lat=data.get('default_location_lat'),
            default_location_lng=data.get('default_location_lng'),
            default_location_place_id=data.get('default_location_place_id'),
            default_arrive_by_offset=data.get('default_arrive_by_offset', 15),
            default_start_time=datetime.strptime(data['default_start_time'], '%H:%M').time() if data.get('default_start_time') else None,
            default_rsvp_required=data.get('default_rsvp_required', True),
            default_send_reminders=data.get('default_send_reminders', True),
            default_reminder_days_before=data.get('default_reminder_days_before', 1),
            category_id=data.get('category_id'),
            organization_id=org_id,
            created_by=user_id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'msg': 'Template created successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error creating template: {str(e)}'}), 500


@events_bp.route('/advanced-templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_advanced_event_template(template_id):
    """Get a specific advanced event template"""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        
        template = EventTemplate.query.filter_by(
            id=template_id,
            organization_id=org_id
        ).first()
        
        if not template:
            return jsonify({'msg': 'Template not found'}), 404
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'msg': f'Error fetching template: {str(e)}'}), 500


@events_bp.route('/advanced-templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_advanced_event_template(template_id):
    """Update an advanced event template"""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        data = request.get_json()
        
        template = EventTemplate.query.filter_by(
            id=template_id,
            organization_id=org_id
        ).first()
        
        if not template:
            return jsonify({'msg': 'Template not found'}), 404
        
        # Check if template name already exists (excluding current template)
        if data.get('name') and data['name'] != template.name:
            existing = EventTemplate.query.filter_by(
                name=data['name'],
                organization_id=org_id
            ).filter(EventTemplate.id != template_id).first()
            
            if existing:
                return jsonify({'msg': 'Template name already exists'}), 409
        
        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'default_title' in data:
            template.default_title = data['default_title']
        if 'default_description' in data:
            template.default_description = data['default_description']
        if 'default_duration_hours' in data:
            template.default_duration_hours = data['default_duration_hours']
        if 'default_location_address' in data:
            template.default_location_address = data['default_location_address']
        if 'default_location_lat' in data:
            template.default_location_lat = data['default_location_lat']
        if 'default_location_lng' in data:
            template.default_location_lng = data['default_location_lng']
        if 'default_location_place_id' in data:
            template.default_location_place_id = data['default_location_place_id']
        if 'default_arrive_by_offset' in data:
            template.default_arrive_by_offset = data['default_arrive_by_offset']
        if 'default_start_time' in data:
            template.default_start_time = datetime.strptime(data['default_start_time'], '%H:%M').time() if data['default_start_time'] else None
        if 'default_rsvp_required' in data:
            template.default_rsvp_required = data['default_rsvp_required']
        if 'default_send_reminders' in data:
            template.default_send_reminders = data['default_send_reminders']
        if 'default_reminder_days_before' in data:
            template.default_reminder_days_before = data['default_reminder_days_before']
        if 'category_id' in data:
            template.category_id = data['category_id']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Template updated successfully',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error updating template: {str(e)}'}), 500


@events_bp.route('/advanced-templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_advanced_event_template(template_id):
    """Delete an advanced event template (soft delete)"""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        
        template = EventTemplate.query.filter_by(
            id=template_id,
            organization_id=org_id
        ).first()
        
        if not template:
            return jsonify({'msg': 'Template not found'}), 404
        
        # Soft delete by setting is_active to False
        template.is_active = False
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'msg': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting template: {str(e)}'}), 500


@events_bp.route('/from-advanced-template/<int:template_id>', methods=['POST'])
@jwt_required()
def create_from_advanced_template(template_id):
    """Create a new event from an advanced template"""
    try:
        claims = get_jwt()
        org_id = claims.get('organization_id')
        user_id = get_jwt_identity()
        data = request.get_json()
        
        template = EventTemplate.query.filter_by(
            id=template_id,
            organization_id=org_id,
            is_active=True
        ).first()
        
        if not template:
            return jsonify({'msg': 'Template not found'}), 404
        
        # Get the event date from request (required)
        if not data.get('date'):
            return jsonify({'msg': 'Event date is required'}), 400
        
        try:
            event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except:
            return jsonify({'msg': 'Invalid date format'}), 400
        
        # Calculate times based on template defaults
        start_time = template.default_start_time if template.default_start_time else None
        arrive_by_time = None
        end_time = None
        
        if start_time:
            # Calculate arrive_by_time
            start_datetime = datetime.combine(event_date.date(), start_time)
            arrive_by_datetime = start_datetime - timedelta(minutes=template.default_arrive_by_offset)
            arrive_by_time = arrive_by_datetime.time()
            
            # Calculate end_time
            end_datetime = start_datetime + timedelta(hours=template.default_duration_hours)
            end_time = end_datetime.time()
        
        # Create new event from template
        event = Event(
            title=data.get('title', template.default_title),
            description=data.get('description', template.default_description),
            date=event_date,
            arrive_by_time=arrive_by_time,
            start_time=start_time,
            end_time=end_time,
            location_address=data.get('location_address', template.default_location_address),
            location_lat=data.get('location_lat', template.default_location_lat),
            location_lng=data.get('location_lng', template.default_location_lng),
            location_place_id=data.get('location_place_id', template.default_location_place_id),
            category_id=template.category_id,
            template_id=template_id,  # Link back to template
            send_reminders=template.default_send_reminders,
            reminder_days_before=template.default_reminder_days_before,
            organization_id=org_id,
            created_by=user_id
        )
        
        db.session.add(event)
        
        # Increment template usage count
        template.usage_count = (template.usage_count or 0) + 1
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Event created from template successfully',
            'event_id': event.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error creating event from template: {str(e)}'}), 500
