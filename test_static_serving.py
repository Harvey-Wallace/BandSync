#!/usr/bin/env python3
"""
Test script to verify static file serving logic
"""
import os

def test_static_path_logic():
    """Test the static file path logic"""
    
    # Simulate the directory structure
    static_dir = "/Users/robertharvey/Documents/GitHub/BandSync/backend/static"
    
    # Test cases
    test_cases = [
        "static/css/main.e3bc04ff.css",
        "static/js/main.be6581e9.js",
        "manifest.json",
        "favicon.ico"
    ]
    
    for path in test_cases:
        print(f"Testing path: {path}")
        
        if path.startswith('static/'):
            # The built React app creates a nested static structure
            # So /static/css/file.css should be served from static/static/css/file.css
            nested_path = 'static/' + path
            full_path = os.path.join(static_dir, nested_path)
            print(f"  Nested path: {nested_path}")
            print(f"  Full path: {full_path}")
            print(f"  Exists: {os.path.exists(full_path)}")
        else:
            # Try to serve from static directory
            full_path = os.path.join(static_dir, path)
            print(f"  Direct path: {full_path}")
            print(f"  Exists: {os.path.exists(full_path)}")
        
        print()

if __name__ == "__main__":
    test_static_path_logic()
