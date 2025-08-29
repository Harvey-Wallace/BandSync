#!/usr/bin/env python3
"""
Create default Event Templates for testing the Advanced Event Types & Templates feature
"""

import os
import sys
from datetime import datetime, time

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the app instance directly
from app import app as flask_app
from models import db, EventTemplate, EventCategory, Organization

def create_default_templates():
    """Create default event templates for testing"""
    print("🚀 Creating default Event Templates...")
    
    # Use the existing app instance
    with flask_app.app_context():
        try:
            # Get the first organization (for testing)
            org = Organization.query.first()
            if not org:
                print("❌ No organization found. Please create an organization first.")
                return False
            
            print(f"📋 Using organization: {org.name}")
            
            # Get categories if they exist
            rehearsal_category = EventCategory.query.filter_by(
                organization_id=org.id, 
                name='Rehearsal'
            ).first()
            
            performance_category = EventCategory.query.filter_by(
                organization_id=org.id, 
                name='Performance'
            ).first()
            
            meeting_category = EventCategory.query.filter_by(
                organization_id=org.id, 
                name='Meeting'
            ).first()
            
            # Create default templates
            templates_to_create = [
                {
                    'name': 'Weekly Rehearsal',
                    'description': 'Standard weekly rehearsal template',
                    'default_title': 'Weekly Rehearsal',
                    'default_description': 'Regular weekly rehearsal session',
                    'default_duration_hours': 2,
                    'default_start_time': time(19, 0),  # 7:00 PM
                    'default_arrive_by_offset': 15,
                    'default_rsvp_required': True,
                    'default_send_reminders': True,
                    'default_reminder_days_before': 1,
                    'category_id': rehearsal_category.id if rehearsal_category else None,
                },
                {
                    'name': 'Concert Performance',
                    'description': 'Template for concert performances',
                    'default_title': 'Concert Performance',
                    'default_description': 'Concert performance event',
                    'default_duration_hours': 3,
                    'default_start_time': time(19, 30),  # 7:30 PM
                    'default_arrive_by_offset': 30,
                    'default_rsvp_required': True,
                    'default_send_reminders': True,
                    'default_reminder_days_before': 3,
                    'category_id': performance_category.id if performance_category else None,
                },
                {
                    'name': 'Section Rehearsal',
                    'description': 'Template for section-specific rehearsals',
                    'default_title': 'Section Rehearsal',
                    'default_description': 'Section rehearsal for focused practice',
                    'default_duration_hours': 1,
                    'default_start_time': time(18, 0),  # 6:00 PM
                    'default_arrive_by_offset': 10,
                    'default_rsvp_required': True,
                    'default_send_reminders': True,
                    'default_reminder_days_before': 1,
                    'category_id': rehearsal_category.id if rehearsal_category else None,
                },
                {
                    'name': 'Annual General Meeting',
                    'description': 'Template for annual general meetings',
                    'default_title': 'Annual General Meeting',
                    'default_description': 'Annual general meeting for all members',
                    'default_duration_hours': 2,
                    'default_start_time': time(19, 0),  # 7:00 PM
                    'default_arrive_by_offset': 5,
                    'default_rsvp_required': True,
                    'default_send_reminders': True,
                    'default_reminder_days_before': 7,
                    'category_id': meeting_category.id if meeting_category else None,
                },
                {
                    'name': 'Outdoor Performance',
                    'description': 'Template for outdoor performances with longer setup',
                    'default_title': 'Outdoor Performance',
                    'default_description': 'Outdoor performance event',
                    'default_duration_hours': 4,
                    'default_start_time': time(14, 0),  # 2:00 PM
                    'default_arrive_by_offset': 60,  # 1 hour early for setup
                    'default_rsvp_required': True,
                    'default_send_reminders': True,
                    'default_reminder_days_before': 5,
                    'category_id': performance_category.id if performance_category else None,
                }
            ]
            
            created_count = 0
            for template_data in templates_to_create:
                # Check if template already exists
                existing = EventTemplate.query.filter_by(
                    name=template_data['name'],
                    organization_id=org.id
                ).first()
                
                if existing:
                    print(f"⚠️  Template '{template_data['name']}' already exists")
                    continue
                
                # Create new template
                template = EventTemplate(
                    organization_id=org.id,
                    **template_data
                )
                
                db.session.add(template)
                created_count += 1
                print(f"✅ Created template: {template_data['name']}")
            
            if created_count > 0:
                db.session.commit()
                print(f"\n🎉 Successfully created {created_count} default templates!")
            else:
                print(f"\n📋 No new templates created (all already exist)")
            
            # Show all templates
            all_templates = EventTemplate.query.filter_by(
                organization_id=org.id,
                is_active=True
            ).all()
            
            print(f"\n📊 Total active templates: {len(all_templates)}")
            for template in all_templates:
                category_name = template.category.name if template.category else 'No Category'
                print(f"  • {template.name} ({category_name}) - Usage: {template.usage_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating templates: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = create_default_templates()
    if success:
        print("\n🎯 Default templates creation completed!")
    else:
        print("\n💥 Failed to create default templates")
        sys.exit(1)
