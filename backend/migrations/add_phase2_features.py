#!/usr/bin/env python3
"""
Phase 2 Database Migration: Group Email System and Substitution Management
Adds support for organization email addresses, message threading, and substitute requests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text
from datetime import datetime

def migrate():
    print("🚀 Starting Phase 2 Migration: Group Email & Substitution System")
    print("=" * 60)
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                print("📧 Creating email system tables...")
                
                # Organization Email Aliases
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS organization_email_aliases (
                        id SERIAL PRIMARY KEY,
                        organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                        alias_name VARCHAR(100) NOT NULL,
                        email_address VARCHAR(255) NOT NULL UNIQUE,
                        alias_type VARCHAR(50) NOT NULL DEFAULT 'organization',
                        section_id INTEGER REFERENCES section(id) ON DELETE CASCADE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER REFERENCES "user"(id),
                        UNIQUE(organization_id, alias_name)
                    );
                """))
                
                # Email Forwarding Rules
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS email_forwarding_rules (
                        id SERIAL PRIMARY KEY,
                        alias_id INTEGER NOT NULL REFERENCES organization_email_aliases(id) ON DELETE CASCADE,
                        forward_to_type VARCHAR(50) NOT NULL DEFAULT 'all_members',
                        user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
                        section_id INTEGER REFERENCES section(id) ON DELETE CASCADE,
                        role_filter VARCHAR(50),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Internal Message Threads
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS message_threads (
                        id SERIAL PRIMARY KEY,
                        organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                        subject VARCHAR(255) NOT NULL,
                        created_by INTEGER NOT NULL REFERENCES "user"(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_archived BOOLEAN DEFAULT FALSE,
                        thread_type VARCHAR(50) DEFAULT 'general'
                    );
                """))
                
                # Individual Messages
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        thread_id INTEGER NOT NULL REFERENCES message_threads(id) ON DELETE CASCADE,
                        sender_id INTEGER NOT NULL REFERENCES "user"(id),
                        content TEXT NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_edited BOOLEAN DEFAULT FALSE,
                        edited_at TIMESTAMP,
                        parent_message_id INTEGER REFERENCES messages(id)
                    );
                """))
                
                # Message Recipients (for tracking read status)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS message_recipients (
                        id SERIAL PRIMARY KEY,
                        message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        read_at TIMESTAMP,
                        is_archived BOOLEAN DEFAULT FALSE,
                        UNIQUE(message_id, user_id)
                    );
                """))
                
                print("✅ Email system tables created successfully")
                
                print("🔄 Creating substitution system tables...")
                
                # Substitute Requests
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS substitute_requests (
                        id SERIAL PRIMARY KEY,
                        event_id INTEGER NOT NULL REFERENCES event(id) ON DELETE CASCADE,
                        requested_by INTEGER NOT NULL REFERENCES "user"(id),
                        section_id INTEGER REFERENCES section(id),
                        request_message TEXT,
                        urgency_level VARCHAR(20) DEFAULT 'normal',
                        status VARCHAR(50) DEFAULT 'open',
                        filled_by INTEGER REFERENCES "user"(id),
                        filled_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    );
                """))
                
                # Call Lists (ordered list of potential substitutes)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS call_lists (
                        id SERIAL PRIMARY KEY,
                        organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                        section_id INTEGER REFERENCES section(id),
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        is_default BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER REFERENCES "user"(id)
                    );
                """))
                
                # Call List Members (ordered list)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS call_list_members (
                        id SERIAL PRIMARY KEY,
                        call_list_id INTEGER NOT NULL REFERENCES call_lists(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        order_position INTEGER NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        availability_notes TEXT,
                        last_contacted TIMESTAMP,
                        UNIQUE(call_list_id, user_id)
                    );
                """))
                
                # Substitute Responses
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS substitute_responses (
                        id SERIAL PRIMARY KEY,
                        request_id INTEGER NOT NULL REFERENCES substitute_requests(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES "user"(id),
                        response VARCHAR(20) NOT NULL,
                        response_message TEXT,
                        responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        contacted_at TIMESTAMP,
                        contact_method VARCHAR(50),
                        UNIQUE(request_id, user_id)
                    );
                """))
                
                print("✅ Substitution system tables created successfully")
                
                print("👥 Creating enhanced section management tables...")
                
                # Section Memberships (sections table already exists)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS section_memberships (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                        section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
                        organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                        role VARCHAR(50) DEFAULT 'member',
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        UNIQUE(user_id, section_id, organization_id)
                    );
                """))
                
                print("✅ Section management tables created successfully")
                
                print("📊 Creating survey enhancement tables...")
                
                # Quick Polls
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS quick_polls (
                        id SERIAL PRIMARY KEY,
                        organization_id INTEGER NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                        created_by INTEGER NOT NULL REFERENCES "user"(id),
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        poll_type VARCHAR(50) DEFAULT 'multiple_choice',
                        options JSON,
                        target_audience VARCHAR(50) DEFAULT 'all_members',
                        section_id INTEGER REFERENCES section(id),
                        expires_at TIMESTAMP,
                        is_anonymous BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Poll Responses
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS poll_responses (
                        id SERIAL PRIMARY KEY,
                        poll_id INTEGER NOT NULL REFERENCES quick_polls(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
                        response_data JSON NOT NULL,
                        response_text TEXT,
                        responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address INET,
                        UNIQUE(poll_id, user_id)
                    );
                """))
                
                print("✅ Survey enhancement tables created successfully")
                
                print("🔧 Adding indexes for performance...")
                
                # Email system indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_email_aliases_org ON organization_email_aliases(organization_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_email_aliases_active ON organization_email_aliases(is_active);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_message_threads_org ON message_threads(organization_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);"))
                
                # Substitution system indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_substitute_requests_event ON substitute_requests(event_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_substitute_requests_status ON substitute_requests(status);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_call_list_members_list ON call_list_members(call_list_id);"))
                
                # Section management indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sections_org ON section(organization_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_section_memberships_user ON section_memberships(user_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_section_memberships_section ON section_memberships(section_id);"))
                
                # Survey indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_quick_polls_org ON quick_polls(organization_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_poll_responses_poll ON poll_responses(poll_id);"))
                
                print("✅ Performance indexes created successfully")
                
                print("🎛️ Adding new user preferences...")
                
                # Add new email and notification preferences
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN IF NOT EXISTS email_group_messages BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS email_substitute_requests BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS email_substitute_filled BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS notification_messages BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS notification_substitute_requests BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS substitute_availability VARCHAR(50) DEFAULT 'available',
                    ADD COLUMN IF NOT EXISTS substitute_notes TEXT;
                """))
                
                print("✅ User preferences updated successfully")
                
                print("📋 Creating default data...")
                
                # Create default call lists for existing organizations
                existing_orgs = conn.execute(text("SELECT id, name FROM organization;")).fetchall()
                
                for org in existing_orgs:
                    org_id, org_name = org.id, org.name
                    
                    # Create default organization email alias
                    safe_name = org_name.lower().replace(' ', '').replace('-', '').replace('_', '')[:20]
                    default_email = f"{safe_name}@bandsync.com"
                    
                    conn.execute(text("""
                        INSERT INTO organization_email_aliases (organization_id, alias_name, email_address, alias_type)
                        VALUES (:org_id, 'main', :email, 'organization')
                        ON CONFLICT DO NOTHING;
                    """), {"org_id": org_id, "email": default_email})
                    
                    # Create default call list
                    conn.execute(text("""
                        INSERT INTO call_lists (organization_id, name, description, is_default)
                        VALUES (:org_id, 'Default Substitute List', 'Default list for substitute requests', TRUE)
                        ON CONFLICT DO NOTHING;
                    """), {"org_id": org_id})
                
                print("✅ Default data created successfully")
                
                conn.commit()
                print("\n🎉 Phase 2 migration completed successfully!")
                print("📧 Group email system ready")
                print("🔄 Substitution management ready") 
                print("👥 Enhanced section management ready")
                print("📊 Survey enhancements ready")
                
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("Rolling back changes...")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
