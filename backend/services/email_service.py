"""
Email Service for BandSync
Handles all email communications including event reminders, notifications, and group emails.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader
import resend
from models import db, EmailLog

logger = logging.getLogger(__name__)

class EmailService:
    """Main email service class for BandSync"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@bandsync.com')
        self.from_name = os.environ.get('FROM_NAME', 'BandSync')
        self.base_url = os.environ.get('BASE_URL', 'https://bandsync.com')
        
        if self.api_key:
            resend.api_key = self.api_key
            self.client = True  # Mark as available
        else:
            logger.warning("RESEND_API_KEY not found. Email functionality will be disabled.")
            self.client = None
        
        # Initialize template environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _send_email(self, to_emails: List[str], subject: str, html_content: str, 
                   text_content: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> bool:
        """
        Send email using Resend
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            attachments: List of attachment dictionaries (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.client:
            logger.warning(f"Email service not configured. Would send email to {to_emails} with subject: {subject}")
            return False
        
        try:
            # For multiple recipients, send individual emails
            # Resend doesn't support bulk sending to multiple recipients in one call
            success_count = 0
            
            for to_email in to_emails:
                email_data = {
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": to_email,
                    "subject": subject,
                    "html": html_content,
                }
                
                # Add plain text version if provided
                if text_content:
                    email_data["text"] = text_content
                
                # Add attachments if provided
                if attachments:
                    email_data["attachments"] = []
                    for attachment in attachments:
                        email_data["attachments"].append({
                            "filename": attachment["filename"],
                            "content": attachment["content"],
                            "content_type": attachment.get("type", "application/octet-stream")
                        })
                
                # Send the email using Resend
                response = resend.Emails.send(email_data)
                
                if response.get("id"):
                    success_count += 1
                    logger.info(f"Email sent successfully to {to_email}, ID: {response['id']}")
                else:
                    logger.error(f"Failed to send email to {to_email}: {response}")
            
            if success_count == len(to_emails):
                logger.info(f"All {len(to_emails)} emails sent successfully")
                return True
            elif success_count > 0:
                logger.warning(f"Sent {success_count} of {len(to_emails)} emails successfully")
                return True
            else:
                logger.error(f"Failed to send all emails")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _log_email(self, user_id: int, organization_id: int, email_type: str, 
                  subject: str, status: str, event_id: Optional[int] = None, 
                  error_message: Optional[str] = None, 
                  resend_message_id: Optional[str] = None) -> None:
        """
        Log email sending attempt to database
        
        Args:
            user_id: ID of the user receiving the email
            organization_id: ID of the organization
            email_type: Type of email (event_reminder, rsvp_deadline_reminder, etc.)
            subject: Email subject line
            status: 'sent' or 'failed'
            event_id: Optional event ID if email is event-related
            error_message: Optional error message if failed
            resend_message_id: Optional Resend message ID for tracking
        """
        try:
            log_entry = EmailLog(
                user_id=user_id,
                event_id=event_id,
                organization_id=organization_id,
                email_type=email_type,
                subject=subject,
                sent_at=datetime.utcnow(),
                status=status,
                error_message=error_message,
                sendgrid_message_id=resend_message_id  # Reusing the column for Resend message ID
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging email: {str(e)}")
            # Don't let logging errors break email sending
            db.session.rollback()
    
    def send_event_reminder(self, event, users: List, days_before: int = 1) -> bool:
        """
        Send event reminder to specified users
        
        Args:
            event: Event model instance
            users: List of User model instances
            days_before: Number of days before event (for subject line)
        
        Returns:
            bool: True if emails sent successfully
        """
        try:
            template = self.template_env.get_template('event_reminder.html')
            
            # Generate RSVP URL
            rsvp_url = f"{self.base_url}/events/{event.id}"
            
            success_count = 0
            for user in users:
                # Check if user has email preferences that disable reminders
                if hasattr(user, 'email_preferences') and not user.email_preferences.get('event_reminders', True):
                    continue
                
                html_content = template.render(
                    user=user,
                    event=event,
                    organization=event.organization,
                    rsvp_url=rsvp_url,
                    days_before=days_before,
                    base_url=self.base_url
                )
                
                subject = f"Reminder: {event.title} - {event.date.strftime('%B %d, %Y')}"
                
                if self._send_email([user.email], subject, html_content):
                    success_count += 1
                else:
                    logger.error(f"Failed to send reminder to {user.email}")
            
            logger.info(f"Sent event reminders to {success_count} of {len(users)} users")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending event reminders: {str(e)}")
            return False
    
    def send_new_event_notification(self, event, users: List) -> bool:
        """
        Send new event notification to specified users
        
        Args:
            event: Event model instance
            users: List of User model instances
        
        Returns:
            bool: True if emails sent successfully
        """
        try:
            template = self.template_env.get_template('new_event_notification.html')
            
            # Generate RSVP URL
            rsvp_url = f"{self.base_url}/events/{event.id}"
            
            success_count = 0
            for user in users:
                # Check email preferences
                if hasattr(user, 'email_preferences') and not user.email_preferences.get('new_events', True):
                    continue
                
                html_content = template.render(
                    user=user,
                    event=event,
                    organization=event.organization,
                    rsvp_url=rsvp_url,
                    base_url=self.base_url
                )
                
                subject = f"New Event: {event.title} - {event.date.strftime('%B %d, %Y')}"
                
                if self._send_email([user.email], subject, html_content):
                    success_count += 1
            
            logger.info(f"Sent new event notifications to {success_count} of {len(users)} users")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending new event notifications: {str(e)}")
            return False
    
    def send_rsvp_deadline_reminder(self, event, non_responders: List) -> bool:
        """
        Send RSVP deadline reminder to users who haven't responded
        
        Args:
            event: Event model instance
            non_responders: List of User model instances who haven't RSVP'd
        
        Returns:
            bool: True if emails sent successfully
        """
        try:
            template = self.template_env.get_template('rsvp_deadline_reminder.html')
            
            rsvp_url = f"{self.base_url}/events/{event.id}"
            
            success_count = 0
            for user in non_responders:
                html_content = template.render(
                    user=user,
                    event=event,
                    organization=event.organization,
                    rsvp_url=rsvp_url,
                    base_url=self.base_url
                )
                
                subject = f"RSVP Needed: {event.title} - {event.date.strftime('%B %d, %Y')}"
                
                if self._send_email([user.email], subject, html_content):
                    # Log successful email
                    self._log_email(
                        user_id=user.id,
                        event_id=event.id,
                        organization_id=event.organization_id,
                        email_type='rsvp_deadline_reminder',
                        subject=subject,
                        status='sent'
                    )
                    success_count += 1
                else:
                    # Log failed email
                    self._log_email(
                        user_id=user.id,
                        event_id=event.id,
                        organization_id=event.organization_id,
                        email_type='rsvp_deadline_reminder',
                        subject=subject,
                        status='failed',
                        error_message='Failed to send via email service'
                    )
            
            logger.info(f"Sent RSVP reminders to {success_count}/{len(non_responders)} non-responders")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending RSVP deadline reminders: {str(e)}")
            return False
    
    def send_daily_summary(self, organization, admin_users: List, summary_data: Dict) -> bool:
        """
        Send daily summary of changes to admin users
        
        Args:
            organization: Organization model instance
            admin_users: List of admin User model instances
            summary_data: Dictionary containing summary information
        
        Returns:
            bool: True if emails sent successfully
        """
        try:
            template = self.template_env.get_template('daily_summary.html')
            
            success_count = 0
            for admin in admin_users:
                html_content = template.render(
                    user=admin,
                    organization=organization,
                    summary=summary_data,
                    base_url=self.base_url
                )
                
                subject = f"Daily Summary - {organization.name} - {datetime.now().strftime('%B %d, %Y')}"
                
                if self._send_email([admin.email], subject, html_content):
                    success_count += 1
            
            logger.info(f"Sent daily summary to {success_count} admins")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {str(e)}")
            return False
    
    def send_substitute_request(self, event, requesting_user, potential_substitutes: List, message: str = "") -> bool:
        """
        Send substitute request emails
        
        Args:
            event: Event model instance
            requesting_user: User model instance requesting substitute
            potential_substitutes: List of User model instances who could substitute
            message: Optional message from requesting user
        
        Returns:
            bool: True if emails sent successfully
        """
        try:
            template = self.template_env.get_template('substitute_request.html')
            
            substitute_url = f"{self.base_url}/events/{event.id}/substitute/{requesting_user.id}"
            
            success_count = 0
            for substitute in potential_substitutes:
                html_content = template.render(
                    substitute_user=substitute,
                    requesting_user=requesting_user,
                    event=event,
                    organization=event.organization,
                    message=message,
                    substitute_url=substitute_url,
                    base_url=self.base_url
                )
                
                subject = f"Substitute Request: {event.title} - {event.date.strftime('%B %d, %Y')}"
                
                if self._send_email([substitute.email], subject, html_content):
                    success_count += 1
            
            logger.info(f"Sent substitute requests to {success_count} potential substitutes")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending substitute requests: {str(e)}")
            return False
    
    def send_user_invitation(self, user, temporary_password: str, inviting_admin) -> bool:
        """
        Send user invitation email with login credentials
        
        Args:
            user: User model instance
            temporary_password: Temporary password for the user
            inviting_admin: User model instance of the admin sending invitation
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            template = self.template_env.get_template('user_invitation.html')
            
            login_url = f"{self.base_url}/login"
            
            # Debug: Log what we're about to render
            print(f"DEBUG: Rendering email template with:")
            print(f"  user.username: {user.username}")
            print(f"  temporary_password: '{temporary_password}'")
            print(f"  inviting_admin: {inviting_admin.username if inviting_admin else None}")
            print(f"  organization: {user.organization.name if user.organization else None}")
            
            html_content = template.render(
                user=user,
                temporary_password=temporary_password,
                inviting_admin=inviting_admin,
                organization=user.organization,
                login_url=login_url,
                base_url=self.base_url
            )
            
            subject = f"Welcome to {user.organization.name} on BandSync!"
            
            return self._send_email([user.email], subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending user invitation: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
