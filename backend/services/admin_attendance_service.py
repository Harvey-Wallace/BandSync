"""
Admin Attendance Notification Service

Handles sending attendance reports to admin users before events
and notifying admins of RSVP changes after reports are sent.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models import (
    db, User, Event, RSVP, Organization, Section, 
    AdminAttendanceReport, AdminRSVPChangeNotification, EmailLog
)
from services.email_service import send_email
import logging

logger = logging.getLogger(__name__)

class AdminAttendanceService:
    
    @staticmethod
    def check_and_send_attendance_reports():
        """Check for events that need attendance reports sent to admins"""
        try:
            # Get all organizations
            organizations = Organization.query.all()
            
            for org in organizations:
                AdminAttendanceService._process_organization_reports(org)
                
        except Exception as e:
            logger.error(f"Error checking attendance reports: {str(e)}")
    
    @staticmethod
    def _process_organization_reports(organization):
        """Process attendance reports for a specific organization"""
        try:
            # Get admin users for this organization who want attendance reports
            admin_users = User.query.filter(
                User.organization_id == organization.id,
                User.role == 'admin',
                User.email_admin_attendance_reports == True
            ).all()
            
            if not admin_users:
                return
            
            # Get timing preference from first admin (could be made org-level setting)
            timing_minutes = admin_users[0].admin_attendance_report_timing
            timing_unit = admin_users[0].admin_attendance_report_unit
            
            # Convert to minutes
            minutes_before = AdminAttendanceService._convert_to_minutes(timing_minutes, timing_unit)
            
            # Calculate the time window for when reports should be sent
            now = datetime.utcnow()
            report_window_start = now
            report_window_end = now + timedelta(minutes=5)  # 5-minute window
            
            # Find events that should have reports sent
            target_time = now + timedelta(minutes=minutes_before)
            
            events_needing_reports = Event.query.filter(
                Event.organization_id == organization.id,
                Event.date >= target_time - timedelta(minutes=5),
                Event.date <= target_time + timedelta(minutes=5)
            ).all()
            
            for event in events_needing_reports:
                # Check if report already sent
                existing_report = AdminAttendanceReport.query.filter(
                    AdminAttendanceReport.event_id == event.id,
                    AdminAttendanceReport.organization_id == organization.id
                ).first()
                
                if not existing_report:
                    AdminAttendanceService._send_attendance_report(event, admin_users)
                    
        except Exception as e:
            logger.error(f"Error processing reports for org {organization.id}: {str(e)}")
    
    @staticmethod
    def _convert_to_minutes(timing_value, timing_unit):
        """Convert timing value to minutes"""
        if timing_unit == 'minutes':
            return timing_value
        elif timing_unit == 'hours':
            return timing_value * 60
        elif timing_unit == 'days':
            return timing_value * 24 * 60
        else:
            return timing_value  # Default to minutes
    
    @staticmethod
    def _send_attendance_report(event, admin_users):
        """Send attendance report for an event to admin users"""
        try:
            # Get attendance data
            attendance_data = AdminAttendanceService._get_event_attendance_data(event)
            
            # Create attendance report record
            report = AdminAttendanceReport(
                event_id=event.id,
                organization_id=event.organization_id,
                total_yes=attendance_data['totals']['yes'],
                total_no=attendance_data['totals']['no'],
                total_maybe=attendance_data['totals']['maybe'],
                total_no_response=attendance_data['totals']['no_response']
            )
            db.session.add(report)
            db.session.commit()
            
            # Send email to each admin
            for admin in admin_users:
                try:
                    AdminAttendanceService._send_attendance_email(admin, event, attendance_data)
                except Exception as e:
                    logger.error(f"Error sending attendance report to admin {admin.id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error sending attendance report for event {event.id}: {str(e)}")
    
    @staticmethod
    def _get_event_attendance_data(event):
        """Get detailed attendance data for an event"""
        # Get all RSVPs for the event
        rsvps = db.session.query(
            RSVP.status,
            User.name,
            User.email,
            Section.name.label('section_name')
        ).join(User, RSVP.user_id == User.id).outerjoin(
            Section, User.section_id == Section.id
        ).filter(
            RSVP.event_id == event.id
        ).all()
        
        # Get all organization members for no-response tracking
        all_members = User.query.filter(
            User.organization_id == event.organization_id
        ).all()
        
        # Organize by section and status
        sections = {}
        responded_user_ids = set()
        
        for rsvp in rsvps:
            section_name = rsvp.section_name or 'No Section'
            if section_name not in sections:
                sections[section_name] = {
                    'yes': [], 'no': [], 'maybe': []
                }
            
            sections[section_name][rsvp.status.lower()].append({
                'name': rsvp.name,
                'email': rsvp.email
            })
            responded_user_ids.add(rsvp.name)  # Using name as identifier
        
        # Find members who haven't responded
        no_response_members = []
        for member in all_members:
            if member.name not in responded_user_ids:
                section_name = member.section.name if member.section else 'No Section'
                if section_name not in sections:
                    sections[section_name] = {
                        'yes': [], 'no': [], 'maybe': []
                    }
                no_response_members.append({
                    'name': member.name,
                    'email': member.email,
                    'section': section_name
                })
        
        # Calculate totals
        totals = {
            'yes': sum(len(section['yes']) for section in sections.values()),
            'no': sum(len(section['no']) for section in sections.values()),
            'maybe': sum(len(section['maybe']) for section in sections.values()),
            'no_response': len(no_response_members)
        }
        
        return {
            'sections': sections,
            'no_response_members': no_response_members,
            'totals': totals
        }
    
    @staticmethod
    def _send_attendance_email(admin, event, attendance_data):
        """Send attendance report email to an admin"""
        # Format event date
        event_date = event.date.strftime('%A, %B %d, %Y at %I:%M %p')
        
        # Build email content
        subject = f"📋 Attendance Report: {event.title}"
        
        # Start building HTML content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                📋 Attendance Report
            </h2>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #007bff; margin: 0 0 10px 0;">{event.title}</h3>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Date:</strong> {event_date}<br>
                    <strong>Type:</strong> {event.type}<br>
                    <strong>Location:</strong> {event.location_address or 'Not specified'}
                </p>
            </div>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #333;">📊 Summary</h3>
                <div style="display: flex; gap: 15px; margin: 15px 0;">
                    <div style="background: #d4edda; padding: 10px; border-radius: 5px; text-align: center; flex: 1;">
                        <div style="font-size: 24px; font-weight: bold; color: #155724;">
                            {attendance_data['totals']['yes']}
                        </div>
                        <div style="color: #155724;">Attending</div>
                    </div>
                    <div style="background: #f8d7da; padding: 10px; border-radius: 5px; text-align: center; flex: 1;">
                        <div style="font-size: 24px; font-weight: bold; color: #721c24;">
                            {attendance_data['totals']['no']}
                        </div>
                        <div style="color: #721c24;">Not Attending</div>
                    </div>
                    <div style="background: #fff3cd; padding: 10px; border-radius: 5px; text-align: center; flex: 1;">
                        <div style="font-size: 24px; font-weight: bold; color: #856404;">
                            {attendance_data['totals']['maybe']}
                        </div>
                        <div style="color: #856404;">Maybe</div>
                    </div>
                    <div style="background: #e2e3e5; padding: 10px; border-radius: 5px; text-align: center; flex: 1;">
                        <div style="font-size: 24px; font-weight: bold; color: #383d41;">
                            {attendance_data['totals']['no_response']}
                        </div>
                        <div style="color: #383d41;">No Response</div>
                    </div>
                </div>
            </div>
        """
        
        # Add section-by-section breakdown
        for section_name, section_data in attendance_data['sections'].items():
            html_content += f"""
            <div style="margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; padding: 15px;">
                <h4 style="color: #007bff; margin: 0 0 15px 0;">🎵 {section_name}</h4>
            """
            
            # Add attending members
            if section_data['yes']:
                html_content += f"""
                <div style="margin: 10px 0;">
                    <strong style="color: #155724;">✅ Attending ({len(section_data['yes'])}):</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                """
                for member in section_data['yes']:
                    html_content += f"<li style='color: #155724;'>{member['name']}</li>"
                html_content += "</ul></div>"
            
            # Add maybe members
            if section_data['maybe']:
                html_content += f"""
                <div style="margin: 10px 0;">
                    <strong style="color: #856404;">❓ Maybe ({len(section_data['maybe'])}):</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                """
                for member in section_data['maybe']:
                    html_content += f"<li style='color: #856404;'>{member['name']}</li>"
                html_content += "</ul></div>"
            
            # Add not attending members
            if section_data['no']:
                html_content += f"""
                <div style="margin: 10px 0;">
                    <strong style="color: #721c24;">❌ Not Attending ({len(section_data['no'])}):</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                """
                for member in section_data['no']:
                    html_content += f"<li style='color: #721c24;'>{member['name']}</li>"
                html_content += "</ul></div>"
            
            html_content += "</div>"
        
        # Add no response members
        if attendance_data['no_response_members']:
            html_content += f"""
            <div style="margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; padding: 15px; background-color: #f8f9fa;">
                <h4 style="color: #6c757d; margin: 0 0 15px 0;">⏳ No Response ({len(attendance_data['no_response_members'])})</h4>
                <ul style="margin: 5px 0; padding-left: 20px;">
            """
            for member in attendance_data['no_response_members']:
                html_content += f"<li style='color: #6c757d;'>{member['name']} ({member['section']})</li>"
            html_content += "</ul></div>"
        
        html_content += """
            <div style="margin: 30px 0; padding: 15px; background-color: #e9ecef; border-radius: 5px;">
                <p style="margin: 0; color: #6c757d; font-size: 14px;">
                    This attendance report was automatically generated. You'll receive notifications 
                    if anyone changes their RSVP status after this report was sent.
                </p>
            </div>
        </div>
        """
        
        # Send email
        success = send_email(
            to_email=admin.email,
            subject=subject,
            html_content=html_content,
            email_type='admin_attendance_report'
        )
        
        if success:
            # Log the email
            email_log = EmailLog(
                user_id=admin.id,
                email_type='admin_attendance_report',
                event_id=event.id,
                organization_id=event.organization_id,
                status='sent'
            )
            db.session.add(email_log)
            db.session.commit()
            
            logger.info(f"Attendance report sent to admin {admin.email} for event {event.id}")
        else:
            logger.error(f"Failed to send attendance report to admin {admin.email}")
    
    @staticmethod
    def track_rsvp_change(event_id, user_id, previous_status, new_status):
        """Track RSVP changes after attendance report has been sent"""
        try:
            # Check if attendance report has been sent for this event
            report = AdminAttendanceReport.query.filter(
                AdminAttendanceReport.event_id == event_id
            ).first()
            
            if report:
                # Log the change
                change_notification = AdminRSVPChangeNotification(
                    event_id=event_id,
                    user_id=user_id,
                    organization_id=report.organization_id,
                    previous_status=previous_status,
                    new_status=new_status
                )
                db.session.add(change_notification)
                db.session.commit()
                
                # Send notification to admins
                AdminAttendanceService._send_rsvp_change_notification(change_notification)
                
        except Exception as e:
            logger.error(f"Error tracking RSVP change: {str(e)}")
    
    @staticmethod
    def _send_rsvp_change_notification(change_notification):
        """Send RSVP change notification to admins"""
        try:
            # Get admin users who want these notifications
            admin_users = User.query.filter(
                User.organization_id == change_notification.organization_id,
                User.role == 'admin',
                User.email_admin_rsvp_changes == True
            ).all()
            
            if not admin_users:
                return
            
            # Get event and user details
            event = Event.query.get(change_notification.event_id)
            user = User.query.get(change_notification.user_id)
            
            if not event or not user:
                return
            
            # Format change message
            status_icons = {
                'Yes': '✅',
                'No': '❌',
                'Maybe': '❓'
            }
            
            from_status = status_icons.get(change_notification.previous_status, '❓')
            to_status = status_icons.get(change_notification.new_status, '❓')
            
            subject = f"🔄 RSVP Change: {event.title}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333; border-bottom: 2px solid #ffc107; padding-bottom: 10px;">
                    🔄 RSVP Status Change
                </h2>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404; margin: 0 0 10px 0;">{user.name} changed their RSVP</h3>
                    <p style="margin: 5px 0; color: #856404;">
                        <strong>Event:</strong> {event.title}<br>
                        <strong>Date:</strong> {event.date.strftime('%A, %B %d, %Y at %I:%M %p')}<br>
                        <strong>Change:</strong> {from_status} {change_notification.previous_status or 'No Response'} → {to_status} {change_notification.new_status}<br>
                        <strong>Changed at:</strong> {change_notification.changed_at.strftime('%I:%M %p on %B %d, %Y')}
                    </p>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #e9ecef; border-radius: 5px;">
                    <p style="margin: 0; color: #6c757d; font-size: 14px;">
                        This notification was sent because {user.name} changed their RSVP status 
                        after the attendance report was sent for this event.
                    </p>
                </div>
            </div>
            """
            
            # Send to each admin
            for admin in admin_users:
                try:
                    success = send_email(
                        to_email=admin.email,
                        subject=subject,
                        html_content=html_content,
                        email_type='admin_rsvp_change'
                    )
                    
                    if success:
                        # Log the email
                        email_log = EmailLog(
                            user_id=admin.id,
                            email_type='admin_rsvp_change',
                            event_id=event.id,
                            organization_id=event.organization_id,
                            status='sent'
                        )
                        db.session.add(email_log)
                        
                except Exception as e:
                    logger.error(f"Error sending RSVP change notification to admin {admin.id}: {str(e)}")
            
            # Mark notification as sent
            change_notification.notification_sent = True
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending RSVP change notification: {str(e)}")
    
    @staticmethod
    def get_timing_options():
        """Get available timing options for admin settings"""
        return [
            {'value': 30, 'unit': 'minutes', 'label': '30 minutes'},
            {'value': 60, 'unit': 'minutes', 'label': '1 hour'},
            {'value': 90, 'unit': 'minutes', 'label': '1.5 hours'},
            {'value': 120, 'unit': 'minutes', 'label': '2 hours'},
            {'value': 300, 'unit': 'minutes', 'label': '5 hours'},
            {'value': 1, 'unit': 'days', 'label': '1 day'},
        ]
