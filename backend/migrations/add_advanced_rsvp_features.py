#!/usr/bin/env python3
"""
Migration script to add advanced RSVP features tables
- Custom event fields
- Event attachments
- Event surveys
"""

import sqlite3
import sys
import os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_database():
    """Add tables for advanced RSVP features"""
    
    # Connect to database
    conn = sqlite3.connect('bandsync.db')
    cursor = conn.cursor()
    
    try:
        # Create event_custom_field table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_custom_field (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                field_type VARCHAR(50) NOT NULL,
                field_options TEXT,
                field_description TEXT,
                required BOOLEAN DEFAULT FALSE,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES event(id)
            )
        ''')
        
        # Create event_field_response table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_field_response (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                field_id INTEGER NOT NULL,
                response_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES event(id),
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (field_id) REFERENCES event_custom_field(id),
                UNIQUE(user_id, field_id)
            )
        ''')
        
        # Create event_attachment table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_attachment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_url VARCHAR(500) NOT NULL,
                file_size INTEGER,
                file_type VARCHAR(100),
                description TEXT,
                uploaded_by INTEGER NOT NULL,
                is_public BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES event(id),
                FOREIGN KEY (uploaded_by) REFERENCES user(id)
            )
        ''')
        
        # Create event_survey table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_survey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                is_anonymous BOOLEAN DEFAULT FALSE,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deadline TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES event(id),
                FOREIGN KEY (created_by) REFERENCES user(id)
            )
        ''')
        
        # Create survey_question table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_question (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type VARCHAR(50) NOT NULL,
                question_options TEXT,
                required BOOLEAN DEFAULT FALSE,
                display_order INTEGER DEFAULT 0,
                FOREIGN KEY (survey_id) REFERENCES event_survey(id)
            )
        ''')
        
        # Create survey_response table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_response (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                user_id INTEGER,
                response_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (survey_id) REFERENCES event_survey(id),
                FOREIGN KEY (question_id) REFERENCES survey_question(id),
                FOREIGN KEY (user_id) REFERENCES user(id),
                UNIQUE(user_id, question_id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_field_event ON event_custom_field(event_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_response_event ON event_field_response(event_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_response_user ON event_field_response(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_attachment_event ON event_attachment(event_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_survey_event ON event_survey(event_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_survey_question_survey ON survey_question(survey_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_survey_response_survey ON survey_response(survey_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_survey_response_user ON survey_response(user_id)')
        
        # Commit changes
        conn.commit()
        print("✅ Successfully added advanced RSVP features tables")
        
        # Show table info
        tables = [
            'event_custom_field',
            'event_field_response', 
            'event_attachment',
            'event_survey',
            'survey_question',
            'survey_response'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Adding advanced RSVP features tables...")
    success = migrate_database()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
