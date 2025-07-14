"""
Health check endpoint for Railway deployment debugging
Add this to your Flask app to diagnose deployment issues
"""

from flask import Blueprint, jsonify
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    
    try:
        # Check environment variables
        env_vars = {
            'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
            'RESEND_API_KEY': bool(os.getenv('RESEND_API_KEY')),
            'FROM_EMAIL': os.getenv('FROM_EMAIL'),
            'BASE_URL': os.getenv('BASE_URL'),
            'SECRET_KEY': bool(os.getenv('SECRET_KEY')),
            'JWT_SECRET_KEY': bool(os.getenv('JWT_SECRET_KEY'))
        }
        
        # Check database connection
        try:
            from models import db, User
            db.engine.execute('SELECT 1')
            db_status = "✅ Connected"
            
            # Check if user table exists and has data
            user_count = User.query.count()
            db_details = f"Users: {user_count}"
            
            # Check if password reset columns exist
            try:
                result = db.engine.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' 
                    AND column_name IN ('password_reset_token', 'password_reset_expires')
                """)
                password_reset_columns = [row[0] for row in result.fetchall()]
                db_details += f", Password reset columns: {password_reset_columns}"
            except:
                db_details += ", Password reset columns: Error checking"
                
        except Exception as e:
            db_status = f"❌ Error: {str(e)}"
            db_details = None
        
        # Check email service
        try:
            from services.email_service import EmailService
            email_service = EmailService()
            email_status = "✅ Configured" if email_service.client else "❌ Not configured"
        except Exception as e:
            email_status = f"❌ Error: {str(e)}"
        
        return jsonify({
            'status': 'healthy',
            'environment_variables': env_vars,
            'database': {
                'status': db_status,
                'details': db_details
            },
            'email_service': email_status,
            'python_path': os.sys.path
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
