"""
Calendar Service for BandSync
Handles iCal feed generation and calendar integration.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from icalendar import Calendar, Event as ICalEvent, vText
from models import db, Event, Organization, User, UserOrganization, Section
from flask import current_app

logger = logging.getLogger(__name__)

class CalendarService:
    """Service for generating calendar feeds and managing calendar integrations"""
    
    def __init__(self):
        self.base_url = os.environ.get('BASE_URL', 'http://localhost:3000')
        self.calendar_url = os.environ.get('CALENDAR_URL', 'http://localhost:5001')
    
    def generate_organization_calendar(self, organization_id: int, include_templates: bool = False) -> bytes:
        """
        Generate iCal feed for an organization
        
        Args:
            organization_id: ID of the organization
            include_templates: Whether to include template events
            
        Returns:
            bytes: iCal calendar data
        """
        try:
            # Get organization
            organization = Organization.query.get(organization_id)
            if not organization:
                raise ValueError(f"Organization {organization_id} not found")
            
            # Create calendar
            cal = Calendar()
            cal.add('prodid', f'-//BandSync//{organization.name} Calendar//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f'{organization.name} Events')
            cal.add('x-wr-caldesc', f'Event calendar for {organization.name}')
            cal.add('x-wr-timezone', 'America/New_York')  # TODO: Make configurable
            
            # Get events
            query = Event.query.filter_by(organization_id=organization_id)
            if not include_templates:
                query = query.filter_by(is_template=False)
            
            events = query.filter(Event.date.isnot(None)).all()
            
            # Add events to calendar
            for event in events:
                ical_event = self._create_ical_event(event, organization)
                cal.add_component(ical_event)
            
            logger.info(f"Generated calendar for organization {organization_id} with {len(events)} events")
            return cal.to_ical()
            
        except Exception as e:
            logger.error(f"Error generating organization calendar: {e}")
            raise
    
    def generate_user_calendar(self, user_id: int, organization_id: int) -> bytes:
        """
        Generate iCal feed for a specific user in an organization
        
        Args:
            user_id: ID of the user
            organization_id: ID of the organization
            
        Returns:
            bytes: iCal calendar data
        """
        try:
            # Get user and organization
            user = User.query.get(user_id)
            organization = Organization.query.get(organization_id)
            
            if not user or not organization:
                raise ValueError("User or organization not found")
            
            # Verify user membership
            user_org = UserOrganization.query.filter_by(
                user_id=user_id, 
                organization_id=organization_id,
                is_active=True
            ).first()
            
            if not user_org:
                raise ValueError("User is not a member of this organization")
            
            # Create calendar
            cal = Calendar()
            cal.add('prodid', f'-//BandSync//{user.name or user.username} Calendar//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f'{organization.name} - {user.name or user.username}')
            cal.add('x-wr-caldesc', f'Personal event calendar for {user.name or user.username}')
            cal.add('x-wr-timezone', 'America/New_York')
            
            # Get events for this organization
            events = Event.query.filter_by(
                organization_id=organization_id,
                is_template=False
            ).filter(Event.date.isnot(None)).all()
            
            # Add events to calendar
            for event in events:
                ical_event = self._create_ical_event(event, organization, user)
                cal.add_component(ical_event)
            
            logger.info(f"Generated user calendar for user {user_id} in organization {organization_id}")
            return cal.to_ical()
            
        except Exception as e:
            logger.error(f"Error generating user calendar: {e}")
            raise
    
    def generate_section_calendar(self, section_id: int) -> bytes:
        """
        Generate iCal feed for a specific section
        
        Args:
            section_id: ID of the section
            
        Returns:
            bytes: iCal calendar data
        """
        try:
            # Get section
            section = Section.query.get(section_id)
            if not section:
                raise ValueError(f"Section {section_id} not found")
            
            # Create calendar
            cal = Calendar()
            cal.add('prodid', f'-//BandSync//{section.name} Calendar//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f'{section.organization.name} - {section.name}')
            cal.add('x-wr-caldesc', f'Event calendar for {section.name}')
            cal.add('x-wr-timezone', 'America/New_York')
            
            # Get events for this organization (sections see all org events)
            events = Event.query.filter_by(
                organization_id=section.organization_id,
                is_template=False
            ).filter(Event.date.isnot(None)).all()
            
            # Add events to calendar
            for event in events:
                ical_event = self._create_ical_event(event, section.organization)
                cal.add_component(ical_event)
            
            logger.info(f"Generated section calendar for section {section_id}")
            return cal.to_ical()
            
        except Exception as e:
            logger.error(f"Error generating section calendar: {e}")
            raise
    
    def generate_public_calendar(self, organization_id: int) -> bytes:
        """
        Generate public iCal feed for an organization (public events only)
        
        Args:
            organization_id: ID of the organization
            
        Returns:
            bytes: iCal calendar data
        """
        try:
            # Get organization
            organization = Organization.query.get(organization_id)
            if not organization:
                raise ValueError(f"Organization {organization_id} not found")
            
            # Create calendar
            cal = Calendar()
            cal.add('prodid', f'-//BandSync//{organization.name} Public Calendar//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f'{organization.name} Public Events')
            cal.add('x-wr-caldesc', f'Public event calendar for {organization.name}')
            cal.add('x-wr-timezone', 'America/New_York')
            
            # Get public events (assume all events are public for now)
            # TODO: Add public/private flag to events
            events = Event.query.filter_by(
                organization_id=organization_id,
                is_template=False
            ).filter(Event.date.isnot(None)).all()
            
            # Add events to calendar
            for event in events:
                ical_event = self._create_ical_event(event, organization, include_sensitive=False)
                cal.add_component(ical_event)
            
            logger.info(f"Generated public calendar for organization {organization_id}")
            return cal.to_ical()
            
        except Exception as e:
            logger.error(f"Error generating public calendar: {e}")
            raise
    
    def _create_ical_event(self, event: Event, organization: Organization, 
                          user: Optional[User] = None, include_sensitive: bool = True) -> ICalEvent:
        """
        Create an iCal event from a BandSync event
        
        Args:
            event: BandSync event object
            organization: Organization object
            user: User object (optional, for personalized info)
            include_sensitive: Whether to include sensitive information
            
        Returns:
            ICalEvent: iCal event object
        """
        ical_event = ICalEvent()
        
        # Basic event info
        ical_event.add('uid', f'event-{event.id}@bandsync.com')
        ical_event.add('dtstart', event.date)
        ical_event.add('dtend', event.end_date or event.date + timedelta(hours=2))
        ical_event.add('dtstamp', datetime.utcnow())
        ical_event.add('created', event.created_at or datetime.utcnow())
        ical_event.add('last-modified', datetime.utcnow())
        
        # Event details
        ical_event.add('summary', event.title)
        
        # Description with event details
        description_parts = []
        if event.description:
            description_parts.append(event.description)
        
        if event.type:
            description_parts.append(f"Type: {event.type}")
        
        if event.category:
            description_parts.append(f"Category: {event.category.name}")
        
        if include_sensitive:
            # Add RSVP information for authenticated users
            if user:
                rsvp = next((r for r in event.rsvps if r.user_id == user.id), None)
                if rsvp:
                    description_parts.append(f"Your RSVP: {rsvp.status.title()}")
                else:
                    description_parts.append("RSVP: Not responded")
        
        # Add link to BandSync
        description_parts.append(f"View in BandSync: {self.base_url}/events")
        
        if description_parts:
            ical_event.add('description', '\n\n'.join(description_parts))
        
        # Location
        if event.location_address:
            ical_event.add('location', event.location_address)
        
        # Categories
        categories = [organization.name]
        if event.category:
            categories.append(event.category.name)
        if event.type:
            categories.append(event.type)
        ical_event.add('categories', categories)
        
        # Organizer
        if event.creator:
            ical_event.add('organizer', f'mailto:{event.creator.email}')
        
        # URL
        ical_event.add('url', f'{self.base_url}/events')
        
        # Status
        ical_event.add('status', 'CONFIRMED')
        
        # Class (privacy)
        ical_event.add('class', 'PUBLIC' if not include_sensitive else 'PRIVATE')
        
        # Sequence (for updates)
        ical_event.add('sequence', 0)
        
        # Reminders (alarms)
        if event.send_reminders and event.reminder_days_before:
            from icalendar import Alarm
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f'Reminder: {event.title}')
            alarm.add('trigger', timedelta(days=-event.reminder_days_before))
            ical_event.add_component(alarm)
        
        return ical_event
    
    def get_calendar_url(self, calendar_type: str, resource_id: int, 
                        user_id: Optional[int] = None) -> str:
        """
        Get the URL for a calendar feed
        
        Args:
            calendar_type: Type of calendar ('org', 'user', 'section', 'public')
            resource_id: ID of the resource (org, section, etc.)
            user_id: User ID for user-specific calendars
            
        Returns:
            str: Calendar URL
        """
        base_url = f"{self.calendar_url}/api/calendar"
        
        if calendar_type == 'org':
            return f"{base_url}/org/{resource_id}/events.ics"
        elif calendar_type == 'user':
            return f"{base_url}/user/{user_id}/org/{resource_id}/events.ics"
        elif calendar_type == 'section':
            return f"{base_url}/section/{resource_id}/events.ics"
        elif calendar_type == 'public':
            return f"{base_url}/public/{resource_id}/events.ics"
        else:
            raise ValueError(f"Unknown calendar type: {calendar_type}")
    
    def get_calendar_subscription_info(self, organization_id: int, user_id: Optional[int] = None) -> dict:
        """
        Get calendar subscription information for a user
        
        Args:
            organization_id: ID of the organization
            user_id: ID of the user (optional)
            
        Returns:
            dict: Calendar subscription information
        """
        organization = Organization.query.get(organization_id)
        if not organization:
            raise ValueError(f"Organization {organization_id} not found")
        
        info = {
            'organization': {
                'name': organization.name,
                'url': self.get_calendar_url('org', organization_id),
                'description': f'All events for {organization.name}'
            },
            'public': {
                'name': f'{organization.name} Public Events',
                'url': self.get_calendar_url('public', organization_id),
                'description': f'Public events for {organization.name}'
            }
        }
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                info['user'] = {
                    'name': f'{organization.name} - Personal',
                    'url': self.get_calendar_url('user', organization_id, user_id),
                    'description': f'Personal calendar for {user.name or user.username}'
                }
        
        # Add section calendars
        sections = Section.query.filter_by(organization_id=organization_id).all()
        if sections:
            info['sections'] = []
            for section in sections:
                info['sections'].append({
                    'name': f'{organization.name} - {section.name}',
                    'url': self.get_calendar_url('section', section.id),
                    'description': f'Calendar for {section.name}'
                })
        
        return info

# Global instance
calendar_service = CalendarService()
