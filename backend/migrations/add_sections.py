"""
Migration: Add Sections functionality
This migration adds:
1. Section model for organizing band members
2. section_id foreign key to User model
3. Default sections for existing organizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Organization, User

def run_migration():
    with app.app_context():
        print("Running sections migration...")
        
        # Create the Section table
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS section (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                organization_id INTEGER NOT NULL,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organization (id) ON DELETE CASCADE,
                UNIQUE(name, organization_id)
            );
        """))
        
        # Add section_id column to User table
        try:
            db.session.execute(db.text("""
                ALTER TABLE "user" ADD COLUMN section_id INTEGER;
            """))
            print("Added section_id column to user table")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("section_id column already exists")
            else:
                print(f"Error adding section_id column: {e}")
        
        # Add foreign key constraint
        try:
            db.session.execute(db.text("""
                ALTER TABLE "user" ADD CONSTRAINT fk_user_section 
                FOREIGN KEY (section_id) REFERENCES section (id) ON DELETE SET NULL;
            """))
            print("Added foreign key constraint for section_id")
        except Exception as e:
            if "already exists" in str(e).lower() or "constraint" in str(e).lower():
                print("Foreign key constraint already exists")
            else:
                print(f"Error adding foreign key constraint: {e}")
        
        # Insert default sections for existing organizations
        orgs = Organization.query.all()
        for org in orgs:
            print(f"Adding default sections for organization: {org.name}")
            
            # Default brass band sections
            default_sections = [
                ("Conductor", "Musical Director and Conductor", 1),
                ("Cornets", "Soprano, Solo, Repiano, and 2nd/3rd Cornets", 2),
                ("Horns", "Solo, 1st, and 2nd Horns", 3),
                ("Baritones", "1st and 2nd Baritones", 4),
                ("Trombones", "1st and 2nd Trombones", 5),
                ("Euphoniums", "Solo and 2nd Euphoniums", 6),
                ("Basses", "Eb and Bb Basses", 7),
                ("Percussion", "Timpani, Kit, and Tuned Percussion", 8),
            ]
            
            for section_name, description, order in default_sections:
                try:
                    db.session.execute(db.text("""
                        INSERT INTO section (name, description, organization_id, display_order)
                        VALUES (:name, :desc, :org_id, :order)
                        ON CONFLICT (name, organization_id) DO NOTHING;
                    """), {"name": section_name, "desc": description, "org_id": org.id, "order": order})
                except Exception as e:
                    print(f"Error inserting section {section_name}: {e}")
        
        db.session.commit()
        print("Sections migration completed successfully!")

if __name__ == "__main__":
    run_migration()
