#!/usr/bin/env python3
"""Test Flask routing for static files"""

from flask import Flask, send_from_directory
import os

# Create Flask app with disabled static folder
app = Flask(__name__, static_folder=None)

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory('backend/static', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files for React frontend"""
    if path.startswith('api/'):
        return {"error": "API endpoint not found"}, 404
    
    print(f"Requested path: {path}")
    
    if path.startswith('static/'):
        nested_path = 'backend/static/static/' + path[7:]  # Remove 'static/' prefix
        print(f"Trying nested path: {nested_path}")
        if os.path.exists(nested_path):
            return send_from_directory('backend/static/static', path[7:])
        else:
            print(f"File not found: {nested_path}")
    
    try:
        return send_from_directory('backend/static', path)
    except Exception as e:
        print(f"Fallback to index.html: {e}")
        return send_from_directory('backend/static', 'index.html')

if __name__ == '__main__':
    print("Testing Flask routing logic...")
    print(f"Static folder disabled: {app.static_folder is None}")
    print(f"Current directory: {os.getcwd()}")
    
    # Test static file paths
    css_path = 'backend/static/static/css/main.e3bc04ff.css'
    js_path = 'backend/static/static/js/main.be6581e9.js'
    
    print(f"CSS file exists: {os.path.exists(css_path)}")
    print(f"JS file exists: {os.path.exists(js_path)}")
    
    # Test route matching
    with app.test_client() as client:
        print("\nTesting routes:")
        
        # Test CSS file
        response = client.get('/static/css/main.e3bc04ff.css')
        print(f"CSS response status: {response.status_code}")
        
        # Test JS file
        response = client.get('/static/js/main.be6581e9.js')
        print(f"JS response status: {response.status_code}")
        
        # Test index
        response = client.get('/')
        print(f"Index response status: {response.status_code}")
