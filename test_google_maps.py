#!/usr/bin/env python3
"""
Test Google Maps API key availability
"""

import requests
import json

def test_google_maps_availability():
    """Test if Google Maps API key is available"""
    print("🧪 Testing Google Maps API key availability...")
    
    try:
        # Test if env-config.js is accessible
        response = requests.get("https://bandsync-production.up.railway.app/env-config.js")
        
        print(f"env-config.js Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ env-config.js is accessible")
            print(f"Content: {response.text[:500]}...")
            
            # Check if the Google Maps API key is in the response
            if 'REACT_APP_GOOGLE_MAPS_API_KEY' in response.text:
                print("✅ Google Maps API key found in env-config.js")
                
                # Extract and validate the key
                lines = response.text.split('\n')
                for line in lines:
                    if 'REACT_APP_GOOGLE_MAPS_API_KEY' in line:
                        print(f"Key line: {line.strip()}")
                        # Check if it's not the placeholder
                        if 'AIzaSyC11N3v1N5Gl14LJ2Cl9TjasJNzE5wVkEc' in line:
                            print("✅ Valid Google Maps API key configured")
                        else:
                            print("⚠️  API key might be placeholder")
                        break
            else:
                print("❌ Google Maps API key not found in env-config.js")
        else:
            print(f"❌ env-config.js not accessible: {response.status_code}")
            
        # Test the actual Google Maps API key
        print("\n🧪 Testing Google Maps API key directly...")
        api_key = "AIzaSyC11N3v1N5Gl14LJ2Cl9TjasJNzE5wVkEc"
        
        # Test with a simple geocoding request
        test_url = f"https://maps.googleapis.com/maps/api/geocode/json?address=London&key={api_key}"
        response = requests.get(test_url)
        
        print(f"Google Maps API test status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'OK':
                print("✅ Google Maps API key is working!")
            else:
                print(f"❌ Google Maps API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
        else:
            print(f"❌ Failed to test Google Maps API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_google_maps_availability()
