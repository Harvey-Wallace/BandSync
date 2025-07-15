#!/usr/bin/env python3
"""
Add coordinates to events that have location addresses but no coordinates.
"""

import os
import requests
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection from DATABASE_URL"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    # Parse the URL
    parsed = urlparse(database_url)
    
    return psycopg2.connect(
        host=parsed.hostname,
        database=parsed.path[1:],  # Remove leading slash
        user=parsed.username,
        password=parsed.password,
        port=parsed.port
    )

def geocode_address(address):
    """Get coordinates for an address using a free geocoding service"""
    # Using OpenStreetMap Nominatim (free, no API key required)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    
    try:
        response = requests.get(url, headers={'User-Agent': 'BandSync/1.0'})
        response.raise_for_status()
        
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception as e:
        print(f"❌ Error geocoding address '{address}': {e}")
        return None, None

def add_coordinates_to_events():
    """Add coordinates to events that have addresses but no coordinates"""
    print("🗺️  Adding coordinates to events with addresses...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get events with addresses but no coordinates
        cursor.execute("""
            SELECT id, title, location_address, lat, lng
            FROM event
            WHERE location_address IS NOT NULL 
            AND location_address != ''
            AND (lat IS NULL OR lng IS NULL)
        """)
        
        events = cursor.fetchall()
        
        if not events:
            print("✅ No events need coordinate updates")
            return
        
        print(f"📍 Found {len(events)} events that need coordinates")
        
        for event_id, title, address, lat, lng in events:
            print(f"\n🔍 Processing event: {title}")
            print(f"   Address: {address}")
            
            # Get coordinates
            new_lat, new_lng = geocode_address(address)
            
            if new_lat and new_lng:
                # Update the event with coordinates
                cursor.execute("""
                    UPDATE event 
                    SET lat = %s, lng = %s
                    WHERE id = %s
                """, (new_lat, new_lng, event_id))
                
                print(f"   ✅ Added coordinates: {new_lat}, {new_lng}")
            else:
                print(f"   ❌ Could not geocode address")
        
        conn.commit()
        print(f"\n🎉 Updated coordinates for events!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_coordinates_to_events()
