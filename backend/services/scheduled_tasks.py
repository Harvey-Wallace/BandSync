"""
Scheduled Task Service for BandSync
Handles background tasks like sending email reminders using APScheduler.
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from models import db, Event, User, UserOrganization, EmailLog
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class ScheduledTaskService:
    """Service for managing scheduled background tasks"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the scheduler with Flask app context"""
        self.app = app
        
        # Start scheduler when app starts
        if not self.scheduler.running:
            self.scheduler.start()
        
        # Schedule regular tasks
        self.schedule_tasks()
        
        # Ensure scheduler shuts down when app shuts down
        import atexit
        atexit.register(lambda: self.scheduler.shutdown())
    
    def schedule_tasks(self):
        """Schedule all recurring tasks"""
        
        # Send event reminders every hour
        self.scheduler.add_job(
            func=self.send_event_reminders,
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id='send_event_reminders',
            name='Send Event Reminders',
            replace_existing=True
        )
        
        # Send daily summaries at 8 AM
        self.scheduler.add_job(
            func=self.send_daily_summaries,
            trigger=CronTrigger(hour=8, minute=0),  # 8:00 AM daily
            id='send_daily_summaries',
            name='Send Daily Summaries',
            replace_existing=True
        )
        
        # Send weekly summaries on Monday at 8 AM
        self.scheduler.add_job(
            func=self.send_weekly_summaries,
            trigger=CronTrigger(day_of_week='mon', hour=8, minute=0),
            id='send_weekly_summaries',
            name='Send Weekly Summaries',
            replace_existing=True
        )
        
        # Send RSVP deadline reminders daily at 10 AM
        self.scheduler.add_job(
            func=self.send_rsvp_deadline_reminders,
            trigger=CronTrigger(hour=10, minute=0),
            id='send_rsvp_deadline_reminders',
            name='Send RSVP Deadline Reminders',
            replace_existing=True
        )
    
    def send_event_reminders(self):
        """Send event reminders based on event settings"""
        with self.app.app_context():
            try:
                # Get all events that need reminders
                cutoff_time = datetime.utcnow() + timedelta(hours=72)  # Look 3 days ahead
                events = Event.query.filter(
                    Event.send_reminders == True,
                    Event.date.isnot(None),
                    Event.date <= cutoff_time,
                    Event.date >= datetime.utcnow(),
                    Event.is_template == False
                ).all()
                
                for event in events:
                    # Check if it's time to send reminder
                    reminder_time = event.date - timedelta(days=event.reminder_days_before)
                    
                    if datetime.utcnow() >= reminder_time:
                        # Check if we've already sent this reminder
                        existing_reminder = EmailLog.query.filter_by(
                            event_id=event.id,
                            email_type='event_reminder'
                        ).first()
                        
                        if not existing_reminder:
                            self.email_service.send_event_reminder(event)
                            logger.info(f"Sent reminder for event {event.id}: {event.title}")
                
                logger.info(f"Processed {len(events)} events for reminders")
                
            except Exception as e:
                logger.error(f"Error sending event reminders: {e}")
    
    def send_daily_summaries(self):
        """Send daily summaries to users who have opted in"""
        with self.app.app_context():
            try:
                # Get users who want daily summaries
                users = User.query.filter_by(email_daily_summary=True).all()
                
                for user in users:
                    # Get user's organizations
                    orgs = user.get_organizations()
                    
                    for org in orgs:
                        # Get events for today and tomorrow
                        today = datetime.utcnow().date()
                        tomorrow = today + timedelta(days=1)
                        
                        events = Event.query.filter(
                            Event.organization_id == org.id,
                            Event.date.isnot(None),
                            Event.date >= datetime.combine(today, datetime.min.time()),
                            Event.date <= datetime.combine(tomorrow, datetime.max.time()),
                            Event.is_template == False
                        ).all()
                        
                        if events:
                            self.email_service.send_daily_summary(user, org, events)
                
                logger.info(f"Sent daily summaries to {len(users)} users")
                
            except Exception as e:
                logger.error(f"Error sending daily summaries: {e}")
    
    def send_weekly_summaries(self):
        """Send weekly summaries to users who have opted in"""
        with self.app.app_context():
            try:
                # Get users who want weekly summaries
                users = User.query.filter_by(email_weekly_summary=True).all()
                
                for user in users:
                    # Get user's organizations
                    orgs = user.get_organizations()
                    
                    for org in orgs:
                        # Get events for the next week
                        today = datetime.utcnow().date()
                        next_week = today + timedelta(days=7)
                        
                        events = Event.query.filter(
                            Event.organization_id == org.id,
                            Event.date.isnot(None),
                            Event.date >= datetime.combine(today, datetime.min.time()),
                            Event.date <= datetime.combine(next_week, datetime.max.time()),
                            Event.is_template == False
                        ).order_by(Event.date.asc()).all()
                        
                        if events:
                            self.email_service.send_weekly_summary(user, org, events)
                
                logger.info(f"Sent weekly summaries to {len(users)} users")
                
            except Exception as e:
                logger.error(f"Error sending weekly summaries: {e}")
    
    def send_rsvp_deadline_reminders(self):
        """Send RSVP deadline reminders for events happening soon to non-responders"""
        with self.app.app_context():
            try:
                # Get events happening in the next 3 days
                cutoff_time = datetime.utcnow() + timedelta(days=3)
                events = Event.query.filter(
                    Event.date.isnot(None),
                    Event.date <= cutoff_time,
                    Event.date >= datetime.utcnow(),
                    Event.is_template == False
                ).all()
                
                total_reminders_sent = 0
                
                for event in events:
                    # Check if we've already sent RSVP reminder for this event
                    existing_reminder = EmailLog.query.filter_by(
                        event_id=event.id,
                        email_type='rsvp_deadline_reminder'
                    ).first()
                    
                    if not existing_reminder:
                        # Get all active users in the organization
                        active_user_orgs = UserOrganization.query.filter_by(
                            organization_id=event.organization_id,
                            is_active=True
                        ).all()
                        
                        if not active_user_orgs:
                            continue
                        
                        # Get users who have RSVP'd to this event
                        rsvp_user_ids = {rsvp.user_id for rsvp in event.rsvps}
                        
                        # Find non-responders (active users who haven't RSVP'd)
                        non_responders = []
                        for user_org in active_user_orgs:
                            user = User.query.get(user_org.user_id)
                            if (user and user.id not in rsvp_user_ids and 
                                user.email_rsvp_reminders and user.email_notifications):
                                non_responders.append(user)
                        
                        # Calculate RSVP rate
                        total_users = len(active_user_orgs)
                        rsvp_count = len(rsvp_user_ids)
                        rsvp_rate = rsvp_count / total_users if total_users > 0 else 1.0
                        
                        # Send reminder if less than 70% have RSVP'd and there are non-responders
                        if rsvp_rate < 0.7 and non_responders:
                            success = self.email_service.send_rsvp_deadline_reminder(event, non_responders)
                            if success:
                                total_reminders_sent += len(non_responders)
                                logger.info(f"Sent RSVP deadline reminder for event {event.id}: {event.title} to {len(non_responders)} non-responders")
                        elif rsvp_rate >= 0.7:
                            logger.info(f"Event {event.id} has good RSVP rate ({rsvp_rate:.1%}), skipping reminder")
                
                logger.info(f"Processed {len(events)} events, sent {total_reminders_sent} RSVP deadline reminders")
                
            except Exception as e:
                logger.error(f"Error sending RSVP deadline reminders: {e}")
    
    def send_substitute_request(self, event_id, requesting_user_id, message=""):
        """Send substitute request email immediately"""
        with self.app.app_context():
            try:
                event = Event.query.get(event_id)
                requesting_user = User.query.get(requesting_user_id)
                
                if event and requesting_user:
                    self.email_service.send_substitute_request(event, requesting_user, message)
                    logger.info(f"Sent substitute request for event {event_id} from user {requesting_user_id}")
                
            except Exception as e:
                logger.error(f"Error sending substitute request: {e}")
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs for admin monitoring"""
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]

# Global instance
task_service = ScheduledTaskService()
