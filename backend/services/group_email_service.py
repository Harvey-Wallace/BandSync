import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import logging
from datetime import datetime
from models import db, OrganizationEmailAlias, EmailForwardingRule, User, Organization, MessageThread, Message
from services.email_service import EmailService
import uuid
import re

logger = logging.getLogger(__name__)

class GroupEmailService:
    def __init__(self, app=None):
        self.app = app
        self.email_service = EmailService()
        
    def init_app(self, app):
        self.app = app
        
    def process_incoming_email(self, email_data):
        """Process an incoming email to a group address"""
        try:
            # Parse email
            msg = email.message_from_string(email_data)
            
            # Extract email details
            from_email = msg['From']
            to_email = msg['To']
            subject = msg['Subject']
            
            # Decode subject if needed
            if subject:
                decoded_subject = decode_header(subject)[0]
                if decoded_subject[1]:
                    subject = decoded_subject[0].decode(decoded_subject[1])
                else:
                    subject = decoded_subject[0] if isinstance(decoded_subject[0], str) else str(decoded_subject[0])
            
            # Get message content
            content = self._extract_content(msg)
            
            # Find the email alias
            alias = self._find_alias_by_email(to_email)
            if not alias:
                logger.warning(f"No alias found for email: {to_email}")
                return False
            
            # Verify sender is authorized
            sender = self._verify_sender(from_email, alias.organization_id)
            if not sender:
                logger.warning(f"Unauthorized sender: {from_email}")
                return False
            
            # Process forwarding
            self._process_forwarding(alias, sender, subject, content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing incoming email: {str(e)}")
            return False
    
    def _extract_content(self, msg):
        """Extract content from email message"""
        content = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    content = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            content = msg.get_payload(decode=True).decode('utf-8')
        
        return content.strip()
    
    def _find_alias_by_email(self, email_address):
        """Find email alias by email address"""
        # Extract alias name from email (e.g., "yourband@bandsync.com" -> "yourband")
        if '@' not in email_address:
            return None
            
        alias_name = email_address.split('@')[0]
        
        # Handle section aliases (e.g., "trumpets.yourband" -> "trumpets", "yourband")
        if '.' in alias_name:
            parts = alias_name.split('.')
            if len(parts) == 2:
                section_name, org_alias = parts
                return OrganizationEmailAlias.query.filter_by(
                    alias_name=org_alias,
                    is_active=True
                ).first()
        
        return OrganizationEmailAlias.query.filter_by(
            alias_name=alias_name,
            is_active=True
        ).first()
    
    def _verify_sender(self, from_email, organization_id):
        """Verify sender is authorized to send to this organization"""
        # Extract email from "Name <email@domain.com>" format
        email_match = re.search(r'<([^>]+)>', from_email)
        if email_match:
            email_addr = email_match.group(1)
        else:
            email_addr = from_email
        
        # Check if sender is a member of the organization
        user = User.query.filter_by(email=email_addr).first()
        if not user:
            return None
        
        # Check if user is in the organization
        organization = Organization.query.get(organization_id)
        if not organization or user not in organization.members:
            return None
        
        return user
    
    def _process_forwarding(self, alias, sender, subject, content):
        """Process email forwarding based on alias rules"""
        # Get forwarding rules for this alias
        rules = EmailForwardingRule.query.filter_by(
            alias_id=alias.id,
            is_active=True
        ).all()
        
        if not rules:
            # Default: forward to all organization members
            self._forward_to_all_members(alias, sender, subject, content)
            return
        
        # Process each rule
        for rule in rules:
            if rule.forward_to_type == 'all_members':
                self._forward_to_all_members(alias, sender, subject, content)
            elif rule.forward_to_type == 'section':
                self._forward_to_section(alias, sender, subject, content, rule.target_section_id)
            elif rule.forward_to_type == 'user':
                self._forward_to_user(alias, sender, subject, content, rule.target_user_id)
            elif rule.forward_to_type == 'admins':
                self._forward_to_admins(alias, sender, subject, content)
    
    def _forward_to_all_members(self, alias, sender, subject, content):
        """Forward email to all organization members"""
        organization = Organization.query.get(alias.organization_id)
        if not organization:
            return
        
        # Create message thread
        thread = MessageThread(
            id=str(uuid.uuid4()),
            subject=f"[{alias.alias_name}] {subject}",
            thread_type='email_forward',
            organization_id=organization.id,
            created_by=sender.id,
            participant_ids=','.join([str(member.id) for member in organization.members if member.id != sender.id]),
            created_at=datetime.utcnow()
        )
        
        db.session.add(thread)
        
        # Add message
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            sender_id=sender.id,
            content=content,
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        thread.last_message_at = message.created_at
        
        # Send email notifications
        for member in organization.members:
            if member.id != sender.id and member.email_notifications:
                self._send_email_notification(member, sender, subject, content, alias.alias_name)
        
        db.session.commit()
    
    def _forward_to_section(self, alias, sender, subject, content, section_id):
        """Forward email to specific section members"""
        # Note: This would need proper section membership implementation
        # For now, we'll implement a basic version
        pass
    
    def _forward_to_user(self, alias, sender, subject, content, user_id):
        """Forward email to specific user"""
        user = User.query.get(user_id)
        if not user:
            return
        
        # Create direct message thread
        thread = MessageThread(
            id=str(uuid.uuid4()),
            subject=f"[{alias.alias_name}] {subject}",
            thread_type='email_forward',
            organization_id=alias.organization_id,
            created_by=sender.id,
            participant_ids=str(user.id),
            created_at=datetime.utcnow()
        )
        
        db.session.add(thread)
        
        # Add message
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            sender_id=sender.id,
            content=content,
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        thread.last_message_at = message.created_at
        
        # Send email notification
        if user.email_notifications:
            self._send_email_notification(user, sender, subject, content, alias.alias_name)
        
        db.session.commit()
    
    def _forward_to_admins(self, alias, sender, subject, content):
        """Forward email to organization admins"""
        organization = Organization.query.get(alias.organization_id)
        if not organization:
            return
        
        # Get admin users
        admin_users = [member for member in organization.members 
                      if member.get_role_in_organization(organization.id) == 'Admin']
        
        if not admin_users:
            return
        
        # Create message thread
        thread = MessageThread(
            id=str(uuid.uuid4()),
            subject=f"[{alias.alias_name}] {subject}",
            thread_type='email_forward',
            organization_id=organization.id,
            created_by=sender.id,
            participant_ids=','.join([str(admin.id) for admin in admin_users if admin.id != sender.id]),
            created_at=datetime.utcnow()
        )
        
        db.session.add(thread)
        
        # Add message
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            sender_id=sender.id,
            content=content,
            created_at=datetime.utcnow()
        )
        
        db.session.add(message)
        thread.last_message_at = message.created_at
        
        # Send email notifications
        for admin in admin_users:
            if admin.id != sender.id and admin.email_notifications:
                self._send_email_notification(admin, sender, subject, content, alias.alias_name)
        
        db.session.commit()
    
    def _send_email_notification(self, recipient, sender, subject, content, alias_name):
        """Send email notification to recipient"""
        try:
            # Create email notification
            email_subject = f"[{alias_name}] {subject}"
            email_body = f"""
You have received a new message via the {alias_name} group email:

From: {sender.full_name} ({sender.email})
Subject: {subject}

Message:
{content}

---
This message was sent to the {alias_name} group email and forwarded to you.
You can reply to this message in BandSync or by replying to this email.
"""
            
            # Send email using existing email service
            self.email_service.send_email(
                to_email=recipient.email,
                subject=email_subject,
                body=email_body
            )
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    def send_outbound_email(self, alias_name, sender, subject, content, recipients=None):
        """Send email from a group alias to external or internal recipients"""
        try:
            # Find the alias
            alias = OrganizationEmailAlias.query.filter_by(
                alias_name=alias_name,
                is_active=True
            ).first()
            
            if not alias:
                return False
            
            # Verify sender has permission
            if not self._verify_sender(sender.email, alias.organization_id):
                return False
            
            # Create from address
            from_email = f"{alias.alias_name}@bandsync.com"
            
            # Send to recipients
            if recipients:
                for recipient in recipients:
                    self.email_service.send_email(
                        to_email=recipient,
                        subject=subject,
                        body=content,
                        from_email=from_email
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending outbound email: {str(e)}")
            return False

# Initialize the service
group_email_service = GroupEmailService()
