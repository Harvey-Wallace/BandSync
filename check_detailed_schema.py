#!/usr/bin/env python3
"""
Check the detailed event table schema to understand the database structure
"""

import psycopg2

# Railway database connection
external_db_url = "postgresql://postgres:CZUXSFhQmnxcVOwoPTUkEockcsIMgqHS@yamanote.proxy.rlwy.net:38756/railway"

def check_detailed_event_schema():
    """Check the detailed event table schema"""
    try:
        print("🔍 Checking detailed event table schema...")
        
        conn = psycopg2.connect(external_db_url)
        cur = conn.cursor()
        
        # Get detailed info about each column
        cur.execute("""
            SELECT 
                column_name, 
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_name = 'event'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print(f"\n📊 Event table schema details:")
        
        for col_name, data_type, nullable, default, max_len, precision, scale in columns:
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f", default: {default}" if default else ""
            
            type_details = ""
            if max_len:
                type_details = f"({max_len})"
            elif precision:
                type_details = f"({precision},{scale})" if scale else f"({precision})"
            
            print(f"  {col_name:<25} {data_type}{type_details:<15} {nullable_str:<10}{default_str}")
        
        # Check if we have the problematic time column
        time_column = next((col for col in columns if col[0] == 'time'), None)
        if time_column:
            print(f"\n⚠️  Found separate 'time' column: {time_column[0]} {time_column[1]}")
            print("This suggests the database schema is inconsistent with the model.")
            print("The model expects a single 'date' datetime field, but the DB has separate 'date' and 'time' fields.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_detailed_event_schema()
