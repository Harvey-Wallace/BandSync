#!/usr/bin/env python3
"""
Add multi-organization support for users
Creates a many-to-many relationship between users and organizations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Create user_organizations association table
                conn.execute(text("""
                    CREATE TABLE user_organizations (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                        role VARCHAR(20) DEFAULT 'Member',
                        section_id INTEGER REFERENCES section(id),
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        UNIQUE(user_id, organization_id)
                    );
                """))
                
                print("✓ Created user_organizations table")
                
                # Create indexes for performance
                conn.execute(text("""
                    CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
                    CREATE INDEX idx_user_organizations_org_id ON user_organizations(organization_id);
                """))
                
                print("✓ Created indexes")
                
                # Migrate existing user-organization relationships
                conn.execute(text("""
                    INSERT INTO user_organizations (user_id, organization_id, role, section_id)
                    SELECT id, organization_id, role, section_id 
                    FROM "user" 
                    WHERE organization_id IS NOT NULL;
                """))
                
                print("✓ Migrated existing user-organization relationships")
                
                # Add new columns to user table for current session context
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN current_organization_id INTEGER REFERENCES organization(id),
                    ADD COLUMN primary_organization_id INTEGER REFERENCES organization(id);
                """))
                
                print("✓ Added session context columns to user table")
                
                # Set current and primary organization based on existing data
                conn.execute(text("""
                    UPDATE "user" 
                    SET current_organization_id = organization_id,
                        primary_organization_id = organization_id
                    WHERE organization_id IS NOT NULL;
                """))
                
                print("✓ Set initial current/primary organizations")
                
                conn.commit()
                print("✓ Multi-organization migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            raise

if __name__ == "__main__":
    migrate()
