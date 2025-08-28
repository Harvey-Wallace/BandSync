#!/usr/bin/env python3
"""
Test Railway Database Connection
Debug connection issues with Railway PostgreSQL
"""

import os
import sys

def test_database_connection():
    """Test the Railway database connection with detailed debugging"""
    
    print("🔍 Testing Railway database connection...")
    
    # Get the Railway DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"🔗 Database URL found: {database_url[:50]}...{database_url[-20:]}")
    
    # Try different connection methods
    print("\n1️⃣ Testing with psycopg2 directly...")
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the database URL
        url = urlparse(database_url)
        print(f"   Host: {url.hostname}")
        print(f"   Port: {url.port}")
        print(f"   Database: {url.path[1:]}")
        print(f"   User: {url.username}")
        
        # Try to connect
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ psycopg2 connection successful! PostgreSQL version: {version[0][:50]}...")
        
        # Test if event table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'event'
        """)
        result = cursor.fetchone()
        if result:
            print("✅ Event table exists")
            
            # Check existing columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'event'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"📋 Event table columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}")
            
            # Check specifically for multiple date columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'event' 
                AND column_name IN ('has_multiple_dates', 'final_date_selected', 'date_selection_deadline')
            """)
            multi_date_columns = [row[0] for row in cursor.fetchall()]
            print(f"📋 Multiple date columns: {multi_date_columns}")
            
        else:
            print("❌ Event table does not exist")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not available")
    except Exception as e:
        print(f"❌ psycopg2 connection failed: {e}")
    
    print("\n2️⃣ Testing with SQLAlchemy...")
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"✅ SQLAlchemy connection successful! PostgreSQL version: {version[0][:50]}...")
            
            # Test event table
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'event'
            """))
            table_exists = result.fetchone()
            
            if table_exists:
                print("✅ Event table exists via SQLAlchemy")
                
                # Check for multiple date columns
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'event' 
                    AND column_name IN ('has_multiple_dates', 'final_date_selected', 'date_selection_deadline')
                """))
                multi_date_columns = [row[0] for row in result.fetchall()]
                print(f"📋 Multiple date columns via SQLAlchemy: {multi_date_columns}")
                
                return True
            else:
                print("❌ Event table does not exist via SQLAlchemy")
                return False
        
    except ImportError as e:
        print(f"❌ SQLAlchemy not available: {e}")
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_database_connection()
    print(f"\n{'✅ Connection test passed!' if success else '❌ Connection test failed!'}")
    sys.exit(0 if success else 1)
