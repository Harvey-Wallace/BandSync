from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
import os
load_dotenv()

# Import models and db
from models import db, User, Event, RSVP, Organization

# Auto-migration for Railway
def auto_migrate_password_reset():
    """Automatically add password reset fields on app startup"""
    
    # Only run in production
    if os.getenv('ENVIRONMENT') != 'production':
        return True
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found - skipping migration")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name IN ('password_reset_token', 'password_reset_expires')
            """))
            
            existing = [row[0] for row in result.fetchall()]
            
            # Add missing columns
            if 'password_reset_token' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_token VARCHAR(255) NULL'))
                print("✅ Added password_reset_token column")
            
            if 'password_reset_expires' not in existing:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN password_reset_expires TIMESTAMP NULL'))
                print("✅ Added password_reset_expires column")
            
            conn.commit()
            print("🎉 Password reset migration completed")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def auto_migrate_organization():
    """Automatically add organization profile fields on app startup"""
    
    # Only run in production
    if os.getenv('ENVIRONMENT') != 'production':
        return True
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found - skipping organization migration")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("🚀 Starting organization migration...")
            
            # Check if organization columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'organization' 
                AND column_name IN ('rehearsal_address', 'contact_phone', 'contact_email', 
                                  'website', 'facebook_url', 'instagram_url', 'twitter_url', 
                                  'tiktok_url', 'created_at', 'members_can_view_rsvp_status')
            """))
            
            existing = [row[0] for row in result.fetchall()]
            
            # Define new columns to add
            new_columns = [
                ('rehearsal_address', 'TEXT'),
                ('contact_phone', 'VARCHAR(20)'),
                ('contact_email', 'VARCHAR(255)'),
                ('website', 'VARCHAR(255)'),
                ('facebook_url', 'VARCHAR(255)'),
                ('instagram_url', 'VARCHAR(255)'),
                ('twitter_url', 'VARCHAR(255)'),
                ('tiktok_url', 'VARCHAR(255)'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('members_can_view_rsvp_status', 'BOOLEAN DEFAULT TRUE')
            ]
            
            # Add missing columns
            added_count = 0
            for column_name, column_type in new_columns:
                if column_name not in existing:
                    conn.execute(text(f'ALTER TABLE "organization" ADD COLUMN {column_name} {column_type}'))
                    print(f"✅ Added {column_name} column")
                    added_count += 1
            
            conn.commit()
            
            if added_count > 0:
                print(f"🎉 Organization migration completed! Added {added_count} columns.")
            else:
                print("✅ Organization columns already exist - no migration needed")
            
            return True
            
    except Exception as e:
        print(f"❌ Organization migration failed: {e}")
        return False

def auto_migrate_time_fields():
    """Automatically add time fields to events table on app startup"""
    
    print("🚀 Starting time fields migration check...")
    
    # Only run in production
    if os.getenv('ENVIRONMENT') != 'production':
        print("⚠️  Skipping migration - not in production environment")
        return True
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found - skipping time fields migration")
        return False
    
    print(f"🔗 DATABASE_URL found: {database_url[:50]}...")
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        print("📦 Connecting to database...")
        
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Check if time columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'event' 
                AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            """))
            
            existing = [row[0] for row in result.fetchall()]
            print(f"📋 Found existing time columns: {existing}")
            
            # Define new time columns to add
            time_columns = [
                ('arrive_by_time', 'TIME'),
                ('start_time', 'TIME'),
                ('end_time', 'TIME')
            ]
            
            # Add missing columns
            added_count = 0
            for column_name, column_type in time_columns:
                if column_name not in existing:
                    try:
                        sql = f'ALTER TABLE "event" ADD COLUMN {column_name} {column_type}'
                        print(f"🔄 Executing: {sql}")
                        conn.execute(text(sql))
                        conn.commit()
                        print(f"✅ Added {column_name} column")
                        added_count += 1
                    except Exception as e:
                        print(f"❌ Failed to add {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            if added_count > 0:
                print(f"🎉 Time fields migration completed! Added {added_count} columns.")
            else:
                print("✅ Time fields already exist - no migration needed")
            
            # Final verification
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'event' 
                AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            """))
            
            final_columns = [row[0] for row in result.fetchall()]
            print(f"🔍 Final verification - found {len(final_columns)} time columns: {final_columns}")
            
            return len(final_columns) == 3
            
    except Exception as e:
        print(f"❌ Time fields migration failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

# Disable Flask's default static file serving to use our custom route
app = Flask(__name__, static_folder=None)
app.config.from_object(Config)

# Disable automatic trailing slash redirects to prevent CORS issues
app.url_map.strict_slashes = False

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
from routes.analytics import analytics_bp
from routes.debug import debug_bp
from routes.admin_oversight import admin_oversight

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(events_bp, url_prefix='/api/events')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(rsvps_bp, url_prefix='/api/events')
app.register_blueprint(admin_tools_bp, url_prefix='/api/admin-tools')
app.register_blueprint(org_bp, url_prefix='/api/organizations')
# Mobile app endpoints
from routes.mobile_api import mobile_api_bp
app.register_blueprint(mobile_api_bp, url_prefix='/api/organization')
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
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(admin_oversight, url_prefix='/api')
app.register_blueprint(debug_bp, url_prefix='/api/debug')

# JWT error handlers
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    print(f"🚫 JWT UNAUTHORIZED ERROR: {callback}")
    print(f"🚫 This usually means no Authorization header was provided")
    return {"msg": callback}, 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    from flask import request
    auth_header = request.headers.get('Authorization', 'No Authorization header')
    print(f"🚫 JWT INVALID TOKEN ERROR: {callback}")
    print(f"🚫 This usually means the token format is wrong or corrupted")
    print(f"🚫 Authorization header: {auth_header}")
    
    # Check if it's a "Not enough segments" error
    if "Not enough segments" in str(callback):
        if auth_header.startswith('Bearer '):
            token_part = auth_header[7:]  # Remove "Bearer " prefix
            segment_count = len(token_part.split('.'))
            print(f"🚫 Token has {segment_count} segments (should be 3)")
            print(f"🚫 Token preview: {token_part[:50]}...")
        else:
            print(f"🚫 Authorization header doesn't start with 'Bearer '")
    
    return {"msg": callback}, 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"🚫 JWT EXPIRED TOKEN ERROR")
    print(f"🚫 Token payload: {jwt_payload}")
    return {"msg": "Token has expired"}, 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(jwt_header, jwt_payload):
    print(f"🚫 JWT NEEDS FRESH TOKEN ERROR")
    print(f"🚫 Token payload: {jwt_payload}")
    return {"msg": "Fresh token required"}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    print(f"🚫 JWT REVOKED TOKEN ERROR")
    print(f"🚫 Token payload: {jwt_payload}")
    return {"msg": "Token has been revoked"}, 401

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
        response = send_from_directory('static', 'index.html')
        # Add cache headers to prevent stale index.html
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return f"<h1>BandSync Backend is Running</h1><p>Error serving frontend: {e}</p><p>Try <a href='/health'>/health</a> endpoint</p>", 200

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
            "index_html_exists": os.path.exists('static/index.html'),
            "static_static_exists": os.path.exists('static/static')
        }
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

# Catch-all route for React frontend - MUST be at the end
@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files for React frontend"""
    # Don't serve static files for API routes - be more specific
    if path.startswith('api/'):
        # Return 404 for API routes - they should be handled by blueprints
        from flask import abort
        abort(404)
    
    print(f"Requested path: {path}")
    
    # Handle static file requests more systematically
    if path.startswith('static/'):
        # React build creates /static/js/main.xyz.js, /static/css/main.xyz.css etc.
        # These are copied to our static folder as static/static/js/main.xyz.js
        nested_path = os.path.join('static', path)
        print(f"Trying nested path: {nested_path}")
        
        # Check if file exists before attempting to serve
        if os.path.isfile(nested_path):
            try:
                return send_from_directory('static', path)
            except Exception as e:
                print(f"Error serving nested static file {path}: {e}")
        else:
            print(f"File not found: {nested_path}")
        
        # If nested path fails, return 404 for static files
        from flask import abort
        abort(404)
    
    # For other static file extensions in root, try to serve them directly
    static_extensions = ['.js', '.css', '.html', '.ico', '.png', '.jpg', '.svg', '.woff', '.woff2', '.ttf', '.json', '.txt', '.map']
    if any(path.endswith(ext) for ext in static_extensions) or path in ['manifest.json', 'sw.js', 'favicon.ico', 'robots.txt', 'env-config.js']:
        # Try root level files first (like manifest.json, env-config.js)
        root_path = os.path.join('static', path)
        if os.path.isfile(root_path):
            try:
                return send_from_directory('static', path)
            except Exception as e:
                print(f"Error serving root static file {path}: {e}")
        else:
            print(f"Root static file not found: {root_path}")
        
        # For missing static files, return 404 instead of index.html
        from flask import abort
        abort(404)
    
    # For everything else (React Router paths), serve index.html
    try:
        response = send_from_directory('static', 'index.html')
        # Add cache headers to prevent stale index.html
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"Error serving index.html for React Router: {e}")
        return f"<h1>Page not found</h1>", 404

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

# Run auto-migration on startup
auto_migrate_password_reset()
auto_migrate_organization()
auto_migrate_time_fields()

if __name__ == '__main__':
    # Railway sets the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
