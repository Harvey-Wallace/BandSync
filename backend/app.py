from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
import os
load_dotenv()

# Import models and db
from models import db, User, Event, RSVP, Organization

# Disable Flask's default static file serving to use our custom route
app = Flask(__name__, static_folder=None)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Initialize scheduled tasks
from services.scheduled_tasks import task_service
task_service.init_app(app)

# Import and register blueprints BEFORE the catch-all route
from auth.routes import auth_bp
from routes.events import events_bp
from routes.admin import admin_bp
from routes.rsvps import rsvps_bp
from routes.admin_tools import admin_tools_bp
from routes.organizations import org_bp
from routes.email_preferences import email_prefs_bp
from routes.calendar import calendar_bp
from routes.custom_fields import custom_fields_bp
from routes.attachments import attachments_bp
from routes.surveys import surveys_bp
from routes.email_management import email_management_bp
from routes.messages import messages_bp
from routes.substitutes import substitutes_bp
from routes.bulk_ops import bulk_ops_bp
from routes.quick_polls import quick_polls_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(events_bp, url_prefix='/api/events')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(rsvps_bp, url_prefix='/api/events')
app.register_blueprint(admin_tools_bp, url_prefix='/api/admin-tools')
app.register_blueprint(org_bp, url_prefix='/api/organizations')
app.register_blueprint(email_prefs_bp, url_prefix='/api/email')
app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
app.register_blueprint(custom_fields_bp)
app.register_blueprint(attachments_bp)
app.register_blueprint(surveys_bp)
app.register_blueprint(email_management_bp, url_prefix='/api/email-management')
app.register_blueprint(messages_bp, url_prefix='/api/messages')
app.register_blueprint(substitutes_bp, url_prefix='/api/substitutes')
app.register_blueprint(bulk_ops_bp, url_prefix='/api/bulk-ops')
app.register_blueprint(quick_polls_bp, url_prefix='/api/quick-polls')

# JWT error handlers
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    print("JWT unauthorized error:", callback)
    return {"msg": callback}, 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    print("JWT invalid token error:", callback)
    return {"msg": callback}, 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("JWT expired token error")
    return {"msg": "Token has expired"}, 401

# Health check endpoint for deployment
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Check database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

# Serve React frontend - Updated to fix static file serving
@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return f"<h1>BandSync Backend is Running</h1><p>Error serving frontend: {e}</p><p>Try <a href='/health'>/health</a> endpoint</p>", 200

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files for React frontend"""
    # Don't serve static files for API routes - be more specific
    if path.startswith('api/'):
        # Let Flask handle API routes normally
        from flask import abort
        abort(404)
    
    print(f"Requested path: {path}")
    
    # Handle static file requests - React is looking for files like:
    # /static/js/main.be6581e9.js but they're at /static/static/js/main.be6581e9.js
    if path.startswith('static/'):
        # The built React app creates a nested static structure
        # So /static/css/file.css should be served from static/static/css/file.css
        nested_path = 'static/' + path
        print(f"Trying nested path: {nested_path}")
        try:
            return send_from_directory('.', nested_path)
        except Exception as e:
            print(f"Error serving nested static file {nested_path}: {e}")
    
    # Try to serve the requested file normally from static directory
    try:
        return send_from_directory('static', path)
    except Exception as e:
        print(f"Error serving static file {path}: {e}")
        # If file doesn't exist, serve index.html (for React Router)
        try:
            return send_from_directory('static', 'index.html')
        except Exception as e2:
            print(f"Error serving index.html fallback: {e2}")
            return f"<h1>BandSync Backend is Running</h1><p>Static file not found: {path}</p><p>Try <a href='/health'>/health</a> endpoint</p>", 200

# Debug route to test specific static file access
@app.route('/debug/css')
def debug_css():
    """Test direct CSS file access"""
    try:
        # Try to serve the CSS file directly
        return send_from_directory('static/static/css', 'main.e3bc04ff.css')
    except Exception as e:
        return f"<h1>Error serving CSS</h1><p>{e}</p>"

# Debug route to check static files
@app.route('/debug/static')
def debug_static():
    """Debug endpoint to check static files"""
    try:
        static_files = []
        for root, dirs, files in os.walk('static'):
            for file in files:
                static_files.append(os.path.join(root, file))
        return {
            "static_files": static_files,
            "current_dir": os.getcwd(),
            "static_dir_exists": os.path.exists('static'),
            "index_html_exists": os.path.exists('static/index.html')
        }
    except Exception as e:
        return {"error": str(e)}

# Test CSS file access directly
@app.route('/test-css')
def test_css():
    """Test if we can access the CSS file"""
    try:
        # Test both possible paths
        paths_to_try = [
            'static/css/main.e3bc04ff.css',
            'static/static/css/main.e3bc04ff.css'
        ]
        results = {}
        for path in paths_to_try:
            try:
                return send_from_directory('static', path.replace('static/', ''))
            except Exception as e:
                results[path] = str(e)
        return {"tested_paths": results, "message": "None of the CSS paths worked"}
    except Exception as e:
        return {"error": str(e)}

# Test route to check if frontend HTML is loading
@app.route('/test')
def test_frontend():
    """Test endpoint to see the raw HTML content"""
    try:
        with open('static/index.html', 'r') as f:
            content = f.read()
        # Return as plain text to see the full content
        from flask import Response
        return Response(content, mimetype='text/plain')
    except Exception as e:
        return f"<h1>Error reading HTML</h1><p>{e}</p>"

# Debug endpoint to test API routes
@app.route('/debug/routes')
def debug_routes():
    """Debug endpoint to show registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {"routes": routes}

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Add some startup logging
print("BandSync Flask app is starting...")
print(f"Current working directory: {os.getcwd()}")
print(f"Static directory exists: {os.path.exists('static')}")
print(f"Index.html exists: {os.path.exists('static/index.html')}")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
