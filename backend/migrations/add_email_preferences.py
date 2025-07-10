"""
Add email preferences to User model
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
import os

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models import db, User
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def migrate():
    with app.app_context():
        # Add email preference columns to User table (if they don't exist)
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_notifications BOOLEAN DEFAULT TRUE
            '''))
            print("Added email_notifications column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_notifications column already exists")
            else:
                print(f"Error adding email_notifications: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_event_reminders BOOLEAN DEFAULT TRUE
            '''))
            print("Added email_event_reminders column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_event_reminders column already exists")
            else:
                print(f"Error adding email_event_reminders: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_new_events BOOLEAN DEFAULT TRUE
            '''))
            print("Added email_new_events column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_new_events column already exists")
            else:
                print(f"Error adding email_new_events: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_rsvp_reminders BOOLEAN DEFAULT TRUE
            '''))
            print("Added email_rsvp_reminders column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_rsvp_reminders column already exists")
            else:
                print(f"Error adding email_rsvp_reminders: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_daily_summary BOOLEAN DEFAULT FALSE
            '''))
            print("Added email_daily_summary column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_daily_summary column already exists")
            else:
                print(f"Error adding email_daily_summary: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_weekly_summary BOOLEAN DEFAULT TRUE
            '''))
            print("Added email_weekly_summary column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_weekly_summary column already exists")
            else:
                print(f"Error adding email_weekly_summary: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN email_substitute_requests BOOLEAN DEFAULT TRUE
            '''))
            print("Added email_substitute_requests column")
        except Exception as e:
            if "already exists" in str(e):
                print("email_substitute_requests column already exists")
            else:
                print(f"Error adding email_substitute_requests: {e}")
        
        try:
            db.session.execute(db.text('''
                ALTER TABLE "user" ADD COLUMN unsubscribe_token VARCHAR(255)
            '''))
            print("Added unsubscribe_token column")
        except Exception as e:
            if "already exists" in str(e):
                print("unsubscribe_token column already exists")
            else:
                print(f"Error adding unsubscribe_token: {e}")
        
        # Create EmailLog table for tracking sent emails
        try:
            db.session.execute(db.text('''
                CREATE TABLE email_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    email_type VARCHAR(50) NOT NULL,
                    event_id INTEGER,
                    organization_id INTEGER NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'sent',
                    error_message TEXT,
                    sendgrid_message_id VARCHAR(255),
                    FOREIGN KEY (user_id) REFERENCES "user"(id),
                    FOREIGN KEY (event_id) REFERENCES event(id),
                    FOREIGN KEY (organization_id) REFERENCES organization(id)
                )
            '''))
            print("Created EmailLog table")
        except Exception as e:
            if "already exists" in str(e):
                print("EmailLog table already exists")
            else:
                print(f"Error creating EmailLog table: {e}")
        
        # Commit all changes
        try:
            db.session.commit()
            print("All migrations committed successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing migrations: {e}")
            raise

if __name__ == '__main__':
    migrate()
