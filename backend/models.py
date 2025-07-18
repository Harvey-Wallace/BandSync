from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time

# Create db instance that will be imported by app.py
db = SQLAlchemy()

# Multi-organization association table
class UserOrganization(db.Model):
    __tablename__ = 'user_organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    role = db.Column(db.String(20), default='Member')  # Role in this specific organization
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)  # Section in this org
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='user_organizations')
    organization = db.relationship('Organization', backref='user_organizations')
    section = db.relationship('Section', backref='user_organizations')
    
    # Unique constraint: one record per user-organization pair
    __table_args__ = (db.UniqueConstraint('user_id', 'organization_id'),)


# Multi-tenant: Organization model
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)  # For organization logos
    theme_color = db.Column(db.String(7), default='#007bff')  # Primary color for branding
    
    # Organization profile information
    rehearsal_address = db.Column(db.Text, nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    
    # Social media links
    facebook_url = db.Column(db.String(255), nullable=True)
    instagram_url = db.Column(db.String(255), nullable=True)
    twitter_url = db.Column(db.String(255), nullable=True)
    tiktok_url = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - specify foreign keys to avoid ambiguity
    events = db.relationship('Event', backref='organization', lazy=True)
    sections = db.relationship('Section', backref='organization', lazy=True)
    event_categories = db.relationship('EventCategory', backref='organization', lazy=True)


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    display_order = db.Column(db.Integer, default=0)  # For ordering sections
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='section', lazy=True)
    
    # Unique constraint: section name must be unique per organization
    __table_args__ = (db.UniqueConstraint('name', 'organization_id'),)


class EventCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#007bff')  # Color for UI display
    icon = db.Column(db.String(50), default='calendar')  # Bootstrap icon class
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)  # Default category for new events
    requires_location = db.Column(db.Boolean, default=True)  # Some events might not need location
    default_duration_hours = db.Column(db.Integer, default=2)  # Default event duration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='category', lazy=True)
    
    # Unique constraint: category name must be unique per organization
    __table_args__ = (db.UniqueConstraint('name', 'organization_id'),)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)  # Full name
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)  # Phone number
    address = db.Column(db.Text, nullable=True)  # Address
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='Member')  # Kept for backward compatibility
    super_admin = db.Column(db.Boolean, default=False)  # Super Admin flag for app oversight
    
    # Multi-organization support
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)  # Legacy field
    current_organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)  # Current session org
    primary_organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)  # Main org
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)  # Band section
    
    avatar_url = db.Column(db.String(255), nullable=True)  # For profile pictures
    
    # Email preferences
    email_notifications = db.Column(db.Boolean, default=True)
    email_event_reminders = db.Column(db.Boolean, default=True)
    email_new_events = db.Column(db.Boolean, default=True)
    email_rsvp_reminders = db.Column(db.Boolean, default=True)
    email_daily_summary = db.Column(db.Boolean, default=False)
    email_weekly_summary = db.Column(db.Boolean, default=True)
    email_group_messages = db.Column(db.Boolean, default=True)
    email_substitute_requests = db.Column(db.Boolean, default=True)
    email_substitute_filled = db.Column(db.Boolean, default=True)
    
    # Admin attendance notification preferences
    email_admin_attendance_reports = db.Column(db.Boolean, default=True)
    admin_attendance_report_timing = db.Column(db.Integer, default=120)  # Minutes before event
    admin_attendance_report_unit = db.Column(db.String(20), default='minutes')  # 'minutes', 'hours', 'days'
    email_admin_rsvp_changes = db.Column(db.Boolean, default=True)
    
    unsubscribe_token = db.Column(db.String(255), nullable=True)
    
    # Password reset
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # Notification preferences
    notification_messages = db.Column(db.Boolean, default=True)
    notification_substitute_requests = db.Column(db.Boolean, default=True)
    
    # Substitute availability
    substitute_availability = db.Column(db.String(50), default='available')  # 'available', 'unavailable', 'limited'
    substitute_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    rsvps = db.relationship('RSVP', backref='user', lazy=True)
    current_organization = db.relationship('Organization', foreign_keys=[current_organization_id], overlaps="primary_organization")
    primary_organization = db.relationship('Organization', foreign_keys=[primary_organization_id], overlaps="current_organization")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_password_reset_token(self):
        """Generate a password reset token that expires in 1 hour"""
        import secrets
        from datetime import datetime, timedelta
        
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        return token
    
    def verify_password_reset_token(self, token):
        """Verify if the password reset token is valid and not expired"""
        from datetime import datetime
        
        if not self.password_reset_token or not self.password_reset_expires:
            return False
        
        if self.password_reset_token != token:
            return False
        
        if datetime.utcnow() > self.password_reset_expires:
            return False
        
        return True
    
    def clear_password_reset_token(self):
        """Clear the password reset token after use"""
        self.password_reset_token = None
        self.password_reset_expires = None
    
    def get_organizations(self):
        """Get all organizations this user belongs to"""
        return [uo.organization for uo in self.user_organizations if uo.is_active]
    
    def get_role_in_organization(self, org_id):
        """Get user's role in a specific organization"""
        uo = UserOrganization.query.filter_by(user_id=self.id, organization_id=org_id).first()
        return uo.role if uo else None
    
    def switch_organization(self, org_id):
        """Switch user's current organization context"""
        # Verify user has access to this organization
        uo = UserOrganization.query.filter_by(user_id=self.id, organization_id=org_id, is_active=True).first()
        if uo:
            self.current_organization_id = org_id
            return True
        return False


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='Rehearsal')  # Keep for backward compatibility
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=True)  # Nullable for templates
    end_date = db.Column(db.DateTime, nullable=True)  # For events with duration
    
    # Time fields for better event scheduling (commented out until migration runs)
    # arrive_by_time = db.Column(db.Time, nullable=True)  # When participants should arrive
    # start_time = db.Column(db.Time, nullable=True)      # When the event actually starts
    # end_time = db.Column(db.Time, nullable=True)        # When the event ends
    
    # Enhanced location fields for Google Maps integration
    location_address = db.Column(db.Text, nullable=True)  # Full formatted address
    location_lat = db.Column(db.Float, nullable=True)  # Latitude (keep original name for DB compatibility)
    location_lng = db.Column(db.Float, nullable=True)  # Longitude (keep original name for DB compatibility)
    location_place_id = db.Column(db.String(255), nullable=True)  # Google Places ID
    
    # Add property aliases for backwards compatibility
    @property
    def lat(self):
        return self.location_lat
    
    @lat.setter
    def lat(self, value):
        self.location_lat = value
    
    @property
    def lng(self):
        return self.location_lng
    
    @lng.setter
    def lng(self, value):
        self.location_lng = value
    
    # Event categorization
    category_id = db.Column(db.Integer, db.ForeignKey('event_category.id'), nullable=True)
    
    # Recurring event support
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_pattern = db.Column(db.String(50), nullable=True)  # 'daily', 'weekly', 'monthly', 'yearly'
    recurring_interval = db.Column(db.Integer, default=1)  # Every N days/weeks/months/years
    recurring_end_date = db.Column(db.DateTime, nullable=True)  # When to stop recurring
    recurring_count = db.Column(db.Integer, nullable=True)  # Max number of occurrences
    parent_event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)  # Reference to parent if this is a recurring instance
    
    # Event template support
    is_template = db.Column(db.Boolean, default=False)
    template_name = db.Column(db.String(120), nullable=True)
    
    # Notification settings
    send_reminders = db.Column(db.Boolean, default=True)
    reminder_days_before = db.Column(db.Integer, default=1)  # Days before event to send reminder
    
    # Event cancellation
    is_cancelled = db.Column(db.Boolean, default=False)
    cancelled_at = db.Column(db.DateTime, nullable=True)  # When event was cancelled
    cancelled_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who cancelled it
    cancellation_reason = db.Column(db.Text, nullable=True)  # Why it was cancelled
    cancellation_notification_sent = db.Column(db.Boolean, default=False)  # Whether notification was sent
    
    # Basic metadata
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    rsvps = db.relationship('RSVP', backref='event', lazy=True)
    child_events = db.relationship('Event', backref=db.backref('parent_event', remote_side=[id]), lazy=True)
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_events', lazy=True)
    canceller = db.relationship('User', foreign_keys=[cancelled_by], backref='cancelled_events', lazy=True)

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # Yes, No, Maybe
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailLog(db.Model):
    """Track sent emails for delivery status and avoiding duplicates"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email_type = db.Column(db.String(50), nullable=False)  # 'event_reminder', 'new_event', etc.
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')  # 'sent', 'failed', 'bounce'
    error_message = db.Column(db.Text, nullable=True)
    sendgrid_message_id = db.Column(db.String(255), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='email_logs')
    event = db.relationship('Event', backref='email_logs')
    organization = db.relationship('Organization', backref='email_logs')


class AdminAttendanceReport(db.Model):
    """Track which events have had admin attendance reports sent"""
    __tablename__ = 'admin_attendance_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    report_sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_yes = db.Column(db.Integer, default=0)
    total_no = db.Column(db.Integer, default=0)
    total_maybe = db.Column(db.Integer, default=0)
    total_no_response = db.Column(db.Integer, default=0)
    
    # Relationships
    event = db.relationship('Event', backref='admin_attendance_reports')
    organization = db.relationship('Organization', backref='admin_attendance_reports')


class AdminRSVPChangeNotification(db.Model):
    """Track RSVP changes that occurred after attendance report was sent"""
    __tablename__ = 'admin_rsvp_change_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    previous_status = db.Column(db.String(10), nullable=True)  # Previous RSVP status
    new_status = db.Column(db.String(10), nullable=False)  # New RSVP status
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    notification_sent = db.Column(db.Boolean, default=False)
    
    # Relationships
    event = db.relationship('Event', backref='admin_rsvp_change_notifications')
    user = db.relationship('User', backref='admin_rsvp_change_notifications')
    organization = db.relationship('Organization', backref='admin_rsvp_change_notifications')


class EventCustomField(db.Model):
    """Custom fields for events (e.g., uniform requirements, meal preferences)"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)  # 'text', 'select', 'checkbox', 'textarea', 'number'
    field_options = db.Column(db.Text, nullable=True)  # JSON for select options
    field_description = db.Column(db.Text, nullable=True)  # Help text for users
    required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    event = db.relationship('Event', backref='custom_fields')
    responses = db.relationship('EventFieldResponse', backref='field', cascade='all, delete-orphan')


class EventFieldResponse(db.Model):
    """User responses to custom event fields"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('event_custom_field.id'), nullable=False)
    response_value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = db.relationship('Event', backref='field_responses')
    user = db.relationship('User', backref='field_responses')
    
    # Unique constraint: one response per user per field
    __table_args__ = (db.UniqueConstraint('user_id', 'field_id'),)


class EventAttachment(db.Model):
    """File attachments for events (e.g., music scores, directions)"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    file_type = db.Column(db.String(100), nullable=True)  # MIME type
    description = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)  # Whether all attendees can see
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    event = db.relationship('Event', backref='attachments')
    uploader = db.relationship('User', backref='uploaded_attachments')


class EventSurvey(db.Model):
    """Post-event surveys for feedback"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)  # Survey deadline
    
    # Relationships
    event = db.relationship('Event', backref='surveys')
    creator = db.relationship('User', backref='created_surveys')
    questions = db.relationship('SurveyQuestion', backref='survey', cascade='all, delete-orphan')


class SurveyQuestion(db.Model):
    """Questions within event surveys"""
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('event_survey.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # 'text', 'rating', 'multiple_choice', 'checkbox'
    question_options = db.Column(db.Text, nullable=True)  # JSON for multiple choice options
    required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    
    # Relationships
    responses = db.relationship('SurveyResponse', backref='question', cascade='all, delete-orphan')


class SurveyResponse(db.Model):
    """User responses to survey questions"""
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('event_survey.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for anonymous surveys
    response_value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    survey = db.relationship('EventSurvey', backref='responses')
    user = db.relationship('User', backref='survey_responses')
    
    # Unique constraint: one response per user per question (if not anonymous)
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id'),)


# =============================================================================
# PHASE 2 MODELS - Group Email System, Substitution Management, Enhanced Features
# =============================================================================

class OrganizationEmailAlias(db.Model):
    """Email aliases for organizations and sections (e.g., yourband@bandsync.com)"""
    __tablename__ = 'organization_email_aliases'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    alias_name = db.Column(db.String(100), nullable=False)  # e.g., 'main', 'trumpets'
    email_address = db.Column(db.String(255), nullable=False, unique=True)  # e.g., 'yourband@bandsync.com'
    alias_type = db.Column(db.String(50), nullable=False, default='organization')  # 'organization', 'section'
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    organization = db.relationship('Organization', backref='email_aliases')
    section = db.relationship('Section', backref='email_aliases')
    creator = db.relationship('User', backref='created_email_aliases')
    forwarding_rules = db.relationship('EmailForwardingRule', backref='alias', cascade='all, delete-orphan')
    
    # Unique constraint: one alias name per organization
    __table_args__ = (db.UniqueConstraint('organization_id', 'alias_name'),)


class EmailForwardingRule(db.Model):
    """Rules for forwarding emails from aliases to members"""
    __tablename__ = 'email_forwarding_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    alias_id = db.Column(db.Integer, db.ForeignKey('organization_email_aliases.id'), nullable=False)
    forward_to_type = db.Column(db.String(50), nullable=False, default='all_members')  # 'all_members', 'specific_user', 'section_members', 'role_based'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # For specific user forwarding
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)  # For section-based forwarding
    role_filter = db.Column(db.String(50), nullable=True)  # 'Admin', 'Member', etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='email_forwarding_rules')
    section = db.relationship('Section', backref='email_forwarding_rules')


class MessageThread(db.Model):
    """Internal message threads within organizations"""
    __tablename__ = 'message_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False)
    thread_type = db.Column(db.String(50), default='general')  # 'general', 'announcement', 'event', 'section'
    
    # Relationships
    organization = db.relationship('Organization', backref='message_threads')
    creator = db.relationship('User', backref='created_threads')
    messages = db.relationship('Message', backref='thread', cascade='all, delete-orphan')


class Message(db.Model):
    """Individual messages within threads"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('message_threads.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)  # For replies
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')
    parent_message = db.relationship('Message', remote_side=[id], backref='replies')
    recipients = db.relationship('MessageRecipient', backref='message', cascade='all, delete-orphan')


class MessageRecipient(db.Model):
    """Tracking read status and delivery for message recipients"""
    __tablename__ = 'message_recipients'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='message_receipts')
    
    # Unique constraint: one receipt per message per user
    __table_args__ = (db.UniqueConstraint('message_id', 'user_id'),)


class SubstituteRequest(db.Model):
    """Requests for substitutes for events"""
    __tablename__ = 'substitute_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    request_message = db.Column(db.Text, nullable=True)
    urgency_level = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'
    status = db.Column(db.String(50), default='open')  # 'open', 'filled', 'cancelled', 'expired'
    filled_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    filled_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    event = db.relationship('Event', backref='substitute_requests')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='substitute_requests')
    substitute = db.relationship('User', foreign_keys=[filled_by], backref='filled_substitute_requests')
    section = db.relationship('Section', backref='substitute_requests')
    responses = db.relationship('SubstituteResponse', backref='request', cascade='all, delete-orphan')


class CallList(db.Model):
    """Ordered lists of potential substitutes"""
    __tablename__ = 'call_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    organization = db.relationship('Organization', backref='call_lists')
    section = db.relationship('Section', backref='call_lists')
    creator = db.relationship('User', backref='created_call_lists')
    members = db.relationship('CallListMember', backref='call_list', cascade='all, delete-orphan')


class CallListMember(db.Model):
    """Members in call lists with their order and availability"""
    __tablename__ = 'call_list_members'
    
    id = db.Column(db.Integer, primary_key=True)
    call_list_id = db.Column(db.Integer, db.ForeignKey('call_lists.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_position = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    availability_notes = db.Column(db.Text, nullable=True)
    last_contacted = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='call_list_memberships')
    
    # Unique constraint: one entry per user per call list
    __table_args__ = (db.UniqueConstraint('call_list_id', 'user_id'),)


class SubstituteResponse(db.Model):
    """Responses to substitute requests"""
    __tablename__ = 'substitute_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('substitute_requests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response = db.Column(db.String(20), nullable=False)  # 'available', 'unavailable', 'maybe'
    response_message = db.Column(db.Text, nullable=True)
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)
    contacted_at = db.Column(db.DateTime, nullable=True)
    contact_method = db.Column(db.String(50), nullable=True)  # 'email', 'sms', 'call', 'app'
    
    # Relationships
    user = db.relationship('User', backref='substitute_responses')
    
    # Unique constraint: one response per user per request
    __table_args__ = (db.UniqueConstraint('request_id', 'user_id'),)


class SectionMembership(db.Model):
    """Enhanced section membership with roles and status"""
    __tablename__ = 'section_memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    role = db.Column(db.String(50), default='member')  # 'member', 'section_leader', 'principal'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='section_memberships')
    section = db.relationship('Section', backref='memberships')
    organization = db.relationship('Organization', backref='section_memberships')
    
    # Unique constraint: one membership per user per section per organization
    __table_args__ = (db.UniqueConstraint('user_id', 'section_id', 'organization_id'),)


class QuickPoll(db.Model):
    """Quick polls for gathering feedback and preferences"""
    __tablename__ = 'quick_polls'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    poll_type = db.Column(db.String(50), default='multiple_choice')  # 'multiple_choice', 'yes_no', 'rating', 'text'
    options = db.Column(db.Text, nullable=True)  # JSON for poll options
    target_audience = db.Column(db.String(50), default='all_members')  # 'all_members', 'section_members', 'role_based'
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('Organization', backref='quick_polls')
    creator = db.relationship('User', backref='created_polls')
    section = db.relationship('Section', backref='quick_polls')
    responses = db.relationship('PollResponse', backref='poll', cascade='all, delete-orphan')


class PollResponse(db.Model):
    """Responses to quick polls"""
    __tablename__ = 'poll_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('quick_polls.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for anonymous polls
    response_data = db.Column(db.Text, nullable=False)  # JSON for response data
    response_text = db.Column(db.Text, nullable=True)  # For text responses
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)  # For anonymous tracking
    
    # Relationships
    user = db.relationship('User', backref='poll_responses')
    
    # Unique constraint: one response per user per poll (if not anonymous)
    __table_args__ = (db.UniqueConstraint('poll_id', 'user_id'),)


# =============================================================================
# PHASE 3 MODELS - Security & Compliance, Audit Trails, Data Privacy
# =============================================================================

class AuditLog(db.Model):
    """Comprehensive audit trail for all system actions"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=False, index=True)
    resource_id = db.Column(db.Integer, nullable=True, index=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True, index=True)
    user_agent = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    organization = db.relationship('Organization', backref='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action_type': self.action_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'organization_id': self.organization_id,
            'organization_name': self.organization.name if self.organization else None
        }


class SecurityEvent(db.Model):
    """Security events and threats tracking"""
    __tablename__ = 'security_event'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)  # low, medium, high, critical
    source_ip = db.Column(db.String(45), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    details = db.Column(db.JSON, nullable=True)
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='security_events')
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'details': self.details,
            'resolved': self.resolved,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class DataPrivacyRequest(db.Model):
    """GDPR and data privacy request tracking"""
    __tablename__ = 'data_privacy_request'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_type = db.Column(db.String(20), nullable=False, index=True)  # export, delete, modify
    status = db.Column(db.String(20), default='pending', index=True)  # pending, processing, completed, failed
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='privacy_requests')
    processor = db.relationship('User', foreign_keys=[processed_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'request_type': self.request_type,
            'status': self.status,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processed_by': self.processed_by,
            'notes': self.notes
        }


class UserSession(db.Model):
    """Active user sessions for security monitoring"""
    __tablename__ = 'user_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    device_fingerprint = db.Column(db.String(255), nullable=True)
    location_info = db.Column(db.JSON, nullable=True)  # City, country, timezone
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    logout_reason = db.Column(db.String(50), nullable=True)  # 'user_logout', 'timeout', 'force_logout', 'security'
    
    # Relationships
    user = db.relationship('User', backref='active_sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent[:100] + '...' if self.user_agent and len(self.user_agent) > 100 else self.user_agent,
            'location_info': self.location_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_active': self.is_active,
            'logout_reason': self.logout_reason
        }


class SecurityPolicy(db.Model):
    """Security policies and configurations"""
    __tablename__ = 'security_policy'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)  # Null for global policies
    policy_name = db.Column(db.String(100), nullable=False)
    policy_type = db.Column(db.String(50), nullable=False)  # 'password', 'session', 'access', 'data_retention'
    policy_config = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    organization = db.relationship('Organization', backref='security_policies')
    creator = db.relationship('User', backref='created_security_policies')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'policy_name': self.policy_name,
            'policy_type': self.policy_type,
            'policy_config': self.policy_config,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
