from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Event, RSVP, EventCategory, User, db
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

@events_bp.route('/', methods=['GET'])
@jwt_required()
def get_events():
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    # Get query parameters
    include_templates = request.args.get('include_templates', 'false').lower() == 'true'
    category_id = request.args.get('category_id')
    
    # Base query
    query = Event.query.filter_by(organization_id=org_id)
    
    # Filter by template status
    if not include_templates:
        query = query.filter_by(is_template=False)
    
    # Filter by category
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    events = query.order_by(Event.date.asc()).all()
    
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'type': e.type,
        'description': e.description,
        'date': e.date.isoformat(),
        'end_date': e.end_date.isoformat() if e.end_date else None,
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
        'cancellation_notification_sent': e.cancellation_notification_sent
    } for e in events])

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
    
    # Create the main event
    event = Event(
        title=data.get('title') or data.get('name'),
        type=data.get('type', 'Rehearsal'),
        description=data.get('description'),
        date=event_date,
        end_date=end_date,
        location_address=data.get('location_address'),
        location_lat=data.get('lat'),
        location_lng=data.get('lng'),
        location_place_id=data.get('location_place_id'),
        category_id=data.get('category_id'),
        is_recurring=data.get('is_recurring', False),
        recurring_pattern=data.get('recurring_pattern'),
        recurring_interval=data.get('recurring_interval', 1),
        recurring_end_date=recurring_end_date,
        recurring_count=data.get('recurring_count'),
        is_template=data.get('is_template', False),
        template_name=data.get('template_name'),
        send_reminders=data.get('send_reminders', True),
        reminder_days_before=data.get('reminder_days_before', 1),
        organization_id=org_id,
        created_by=user_id
    )
    
    db.session.add(event)
    db.session.commit()
    
    # Create recurring events if specified
    if event.is_recurring and not event.is_template:
        create_recurring_events(event)
    
    # Send new event notifications (only for non-template events)
    if not event.is_template and email_service:
        try:
            email_service.send_new_event_notification(event)
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
                # Get all active members of the organization
                from models import UserOrganization
                user_orgs = UserOrganization.query.filter_by(
                    organization_id=org_id,
                    is_active=True
                ).all()
                
                users_to_notify = []
                for user_org in user_orgs:
                    user = User.query.get(user_org.user_id)
                    if user and user.email and user.email_notifications:
                        users_to_notify.append(user)
                
                # Send cancellation email to each user
                for user in users_to_notify:
                    email_service.send_event_cancellation_notification(
                        user=user,
                        event=event,
                        reason=reason
                    )
                
                # Mark notification as sent
                event.cancellation_notification_sent = True
                db.session.commit()
                
                return jsonify({
                    'msg': 'Event cancelled successfully',
                    'notification_sent': True,
                    'notifications_count': len(users_to_notify)
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
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    org_id = claims.get('organization_id')
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return jsonify({'msg': 'Event deleted'})

@events_bp.route('/<int:event_id>/rsvp', methods=['POST'])
@jwt_required()
def rsvp_event(event_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    status = data.get('status')
    
    # Normalize status values to proper case
    valid_statuses = ['Yes', 'No', 'Maybe']
    if status in valid_statuses:
        # Already in proper case
        pass
    elif status in ['yes', 'no', 'maybe']:
        # Convert lowercase to proper case
        status = status.capitalize()
    else:
        return jsonify({'msg': 'Invalid RSVP status'}), 400
    
    rsvp = RSVP.query.filter_by(user_id=user_id, event_id=event_id).first()
    if rsvp:
        rsvp.status = status
    else:
        rsvp = RSVP(user_id=user_id, event_id=event_id, status=status)
        db.session.add(rsvp)
    
    db.session.commit()
    return jsonify({'msg': 'RSVP updated'})

@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    claims = get_jwt()
    org_id = claims.get('organization_id')
    event = Event.query.filter_by(id=event_id, organization_id=org_id).first_or_404()
    return jsonify({
        'id': event.id,
        'title': event.title,
        'type': event.type,
        'description': event.description,
        'date': event.date.isoformat(),
        'end_date': event.end_date.isoformat() if event.end_date else None,
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
        'creator_name': event.creator.name if event.creator else None
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

@events_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_event_templates():
    """Get all event templates for the organization."""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    templates = Event.query.filter_by(organization_id=org_id, is_template=True).all()
    return jsonify([{
        'id': t.id,
        'template_name': t.template_name,
        'title': t.title,
        'type': t.type,
        'description': t.description,
        'category_id': t.category_id,
        'category': t.category.name if t.category else None,
        'send_reminders': t.send_reminders,
        'reminder_days_before': t.reminder_days_before
    } for t in templates])

@events_bp.route('/from-template/<int:template_id>', methods=['POST'])
@jwt_required()
def create_from_template(template_id):
    """Create a new event from a template."""
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    org_id = claims.get('organization_id')
    user_id = get_jwt_identity()
    
    # Get the template
    template = Event.query.filter_by(id=template_id, organization_id=org_id, is_template=True).first_or_404()
    
    # Get additional data from request
    data = request.get_json()
    event_date = datetime.fromisoformat(data['date'])
    
    # Create event from template
    event = Event(
        title=data.get('title', template.title),
        type=template.type,
        description=data.get('description', template.description),
        date=event_date,
        end_date=event_date + timedelta(hours=template.category.default_duration_hours) if template.category else None,
        location_address=data.get('location_address'),
        location_lat=data.get('lat'),
        location_lng=data.get('lng'),
        location_place_id=data.get('location_place_id'),
        category_id=template.category_id,
        send_reminders=template.send_reminders,
        reminder_days_before=template.reminder_days_before,
        organization_id=org_id,
        created_by=user_id
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'msg': 'Event created from template', 'id': event.id})

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
