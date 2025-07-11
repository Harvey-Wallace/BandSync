#!/usr/bin/env python3
"""
Test script to verify static file serving logic
"""
import os

def test_flask_static_logic():
    """Test the Flask static file logic"""
    
    base_dir = "/Users/robertharvey/Documents/GitHub/BandSync/backend"
    
    # Test the exact logic from Flask app
    def test_path(path):
        print(f"Testing path: {path}")
        
        if path.startswith('static/'):
            # The built React app creates a nested static structure
            # So /static/css/file.css should be served from static/static/css/file.css
            nested_path = 'static/' + path
            full_path = os.path.join(base_dir, nested_path)
            print(f"  Nested path: {nested_path}")
            print(f"  Full path: {full_path}")
            print(f"  Exists: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                print(f"  ✅ SUCCESS: File found at {full_path}")
            else:
                print(f"  ❌ FAIL: File not found at {full_path}")
        else:
            # Try to serve from static directory
            full_path = os.path.join(base_dir, 'static', path)
            print(f"  Direct path: static/{path}")
            print(f"  Full path: {full_path}")
            print(f"  Exists: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                print(f"  ✅ SUCCESS: File found at {full_path}")
            else:
                print(f"  ❌ FAIL: File not found at {full_path}")
        
        print()
    
    # Test cases that should work
    test_path("static/css/main.e3bc04ff.css")
    test_path("static/js/main.be6581e9.js")
    test_path("manifest.json")
    test_path("index.html")

if __name__ == "__main__":
    test_flask_static_logic()
