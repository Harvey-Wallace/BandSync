#!/usr/bin/env python3
"""
Setup new Railway database after deletion
"""

import psycopg2
from werkzeug.security import generate_password_hash
import os

def create_tables(conn):
    """Create all necessary tables"""
    cur = conn.cursor()
    
    # Create organization table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS organization (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Create user table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'member',
            organization_id INTEGER REFERENCES organization(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Create events table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS event (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            time TIME NOT NULL,
            location VARCHAR(200),
            organization_id INTEGER REFERENCES organization(id),
            created_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Create RSVP table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rsvp (
            id SERIAL PRIMARY KEY,
            event_id INTEGER REFERENCES event(id),
            user_id INTEGER REFERENCES "user"(id),
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(event_id, user_id)
        );
    ''')
    
    conn.commit()
    print("✅ Tables created successfully!")

def create_test_data(conn):
    """Create test organization and user"""
    cur = conn.cursor()
    
    # Create test organization
    cur.execute('''
        INSERT INTO organization (name) 
        VALUES ('Test Band') 
        ON CONFLICT DO NOTHING
        RETURNING id;
    ''')
    
    result = cur.fetchone()
    if result:
        org_id = result[0]
        print(f"✅ Created organization with ID: {org_id}")
    else:
        # Get existing organization ID
        cur.execute("SELECT id FROM organization WHERE name = 'Test Band';")
        org_id = cur.fetchone()[0]
        print(f"✅ Using existing organization with ID: {org_id}")
    
    # Create Rob123 user
    password_hash = generate_password_hash("Rob123pass")
    
    cur.execute('''
        INSERT INTO "user" (username, email, password_hash, role, organization_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE SET
            password_hash = EXCLUDED.password_hash,
            role = EXCLUDED.role,
            organization_id = EXCLUDED.organization_id
        RETURNING id;
    ''', ('Rob123', 'rob@test.com', password_hash, 'admin', org_id))
    
    user_id = cur.fetchone()[0]
    print(f"✅ Created/updated user Rob123 with ID: {user_id}")
    
    conn.commit()

def setup_new_database(database_url):
    """Setup new database with tables and test data"""
    try:
        print("🔄 Setting up new Railway database...")
        
        conn = psycopg2.connect(database_url)
        
        # Create tables
        create_tables(conn)
        
        # Create test data
        create_test_data(conn)
        
        # Verify setup
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "user";')
        user_count = cur.fetchone()[0]
        print(f"✅ Database setup complete! Found {user_count} users.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BandSync New Database Setup")
    print("=" * 50)
    
    # You'll need to update this with the new database URL after creating it
    database_url = input("Enter the new Railway database URL: ")
    
    if database_url.strip():
        success = setup_new_database(database_url)
        if success:
            print("\n✅ Database setup completed successfully!")
            print("You can now update your .env file with the new DATABASE_URL")
        else:
            print("\n❌ Database setup failed. Please check the URL and try again.")
    else:
        print("❌ No database URL provided.")
