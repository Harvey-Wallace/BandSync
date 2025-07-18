#!/usr/bin/env python3
"""
Check database table structure
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_tables():
    """Check database table structure"""
    
    print("🔍 Checking database table structure...")
    
    # Use Railway database URL directly
    db_url = 'postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway'
    
    try:
        engine = create_engine(db_url)
        print("🔧 Connecting to Railway database...")
        
        with engine.connect() as conn:
            print("✅ Connected to database")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Available tables:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            # Check if we have a user table with different name
            user_tables = [t for t in tables if 'user' in t.lower()]
            
            if user_tables:
                print(f"\n👤 User-related tables: {user_tables}")
                
                # Check the structure of the first user table
                user_table = user_tables[0]
                result = conn.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{user_table}'
                """))
                
                columns = result.fetchall()
                print(f"\n📋 Columns in {user_table}:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
                # Try to get some sample data
                result = conn.execute(text(f"SELECT * FROM {user_table} LIMIT 5"))
                rows = result.fetchall()
                print(f"\n📊 Sample data from {user_table}:")
                for row in rows:
                    print(f"  - {row}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    check_tables()
