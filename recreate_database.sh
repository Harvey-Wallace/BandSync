#!/bin/bash

# Quick Database Recreation Script for Railway

echo "🚀 BandSync Database Recreation Script"
echo "======================================"

echo "Step 1: Opening Railway Dashboard..."
railway open

echo ""
echo "📋 Manual Steps Required:"
echo "1. In the Railway dashboard, delete the Postgres service"
echo "2. Add a new PostgreSQL service"
echo "3. Wait for it to deploy"
echo "4. Come back and press Enter when ready"

read -p "Press Enter when you've created the new database..."

echo ""
echo "Step 2: Getting new database URL..."
railway service Postgres
NEW_DB_URL=$(railway variables get DATABASE_URL)

if [ -z "$NEW_DB_URL" ]; then
    echo "❌ Could not get DATABASE_URL. Please check Railway service."
    exit 1
fi

echo "✅ Got new database URL: ${NEW_DB_URL:0:50}..."

echo ""
echo "Step 3: Setting up database schema..."
cd backend
source venv/bin/activate

# Create a temporary setup script
cat > temp_setup.py << 'EOF'
import psycopg2
from werkzeug.security import generate_password_hash
import os

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not found")
    exit(1)

try:
    conn = psycopg2.connect(database_url)
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
    else:
        cur.execute("SELECT id FROM organization WHERE name = 'Test Band';")
        org_id = cur.fetchone()[0]
    
    # Create Rob123 user
    password_hash = generate_password_hash("Rob123pass")
    cur.execute('''
        INSERT INTO "user" (username, email, password_hash, role, organization_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE SET
            password_hash = EXCLUDED.password_hash,
            role = EXCLUDED.role,
            organization_id = EXCLUDED.organization_id;
    ''', ('Rob123', 'rob@test.com', password_hash, 'admin', org_id))
    
    conn.commit()
    conn.close()
    
    print("✅ Database setup completed successfully!")
    print("✅ User 'Rob123' created with password 'Rob123pass'")
    
except Exception as e:
    print(f"❌ Database setup error: {e}")
    exit(1)
EOF

# Run the setup
DATABASE_URL="$NEW_DB_URL" python temp_setup.py

# Clean up
rm temp_setup.py

echo ""
echo "Step 4: Redeploying application..."
cd ..
railway service BandSync
railway redeploy

echo ""
echo "✅ Database recreation completed!"
echo "🧪 Test your login with:"
echo "   Username: Rob123"
echo "   Password: Rob123pass"
echo ""
echo "🔗 App URL: https://bandsync-production.up.railway.app"
