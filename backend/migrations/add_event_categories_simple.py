#!/usr/bin/env python3
"""
Simple Migration: Add Event Categories
- Add EventCategory model
- Add default event categories for each organization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Organization, EventCategory

def run_migration():
    with app.app_context():
        print("Running Event Categories migration...")
        
        # Create new tables
        db.create_all()
        print("✓ Created new tables")
        
        # Create default event categories for each organization
        organizations = Organization.query.all()
        
        default_categories = [
            {
                'name': 'Rehearsal',
                'description': 'Regular band rehearsals and practice sessions',
                'color': '#007bff',
                'icon': 'music-note',
                'is_default': True,
                'requires_location': True,
                'default_duration_hours': 2
            },
            {
                'name': 'Concert',
                'description': 'Public performances and concerts',
                'color': '#dc3545',
                'icon': 'play-circle',
                'is_default': False,
                'requires_location': True,
                'default_duration_hours': 3
            },
            {
                'name': 'Competition',
                'description': 'Competitions and contests',
                'color': '#ffc107',
                'icon': 'trophy',
                'is_default': False,
                'requires_location': True,
                'default_duration_hours': 4
            },
            {
                'name': 'Social Event',
                'description': 'Social gatherings and band social activities',
                'color': '#28a745',
                'icon': 'people',
                'is_default': False,
                'requires_location': True,
                'default_duration_hours': 3
            },
            {
                'name': 'Committee Meeting',
                'description': 'Committee and administrative meetings',
                'color': '#6c757d',
                'icon': 'clipboard-check',
                'is_default': False,
                'requires_location': False,
                'default_duration_hours': 1
            },
            {
                'name': 'AGM',
                'description': 'Annual General Meeting',
                'color': '#6f42c1',
                'icon': 'calendar-event',
                'is_default': False,
                'requires_location': False,
                'default_duration_hours': 2
            },
            {
                'name': 'Workshop',
                'description': 'Educational workshops and masterclasses',
                'color': '#fd7e14',
                'icon': 'mortarboard',
                'is_default': False,
                'requires_location': True,
                'default_duration_hours': 2
            },
            {
                'name': 'Sectional',
                'description': 'Section-specific rehearsals',
                'color': '#17a2b8',
                'icon': 'diagram-3',
                'is_default': False,
                'requires_location': True,
                'default_duration_hours': 1
            }
        ]
        
        for org in organizations:
            print(f"Creating default categories for organization: {org.name}")
            
            for cat_data in default_categories:
                # Check if category already exists
                existing_category = EventCategory.query.filter_by(
                    name=cat_data['name'],
                    organization_id=org.id
                ).first()
                
                if not existing_category:
                    category = EventCategory(
                        name=cat_data['name'],
                        description=cat_data['description'],
                        color=cat_data['color'],
                        icon=cat_data['icon'],
                        organization_id=org.id,
                        is_default=cat_data['is_default'],
                        requires_location=cat_data['requires_location'],
                        default_duration_hours=cat_data['default_duration_hours']
                    )
                    db.session.add(category)
                    print(f"  ✓ Created category: {cat_data['name']}")
                else:
                    print(f"  - Category {cat_data['name']} already exists, skipping")
        
        # Commit all changes
        db.session.commit()
        print("✓ Migration completed successfully!")
        print(f"✓ Created default categories for {len(organizations)} organizations")

if __name__ == '__main__':
    run_migration()
