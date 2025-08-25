from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import os

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/token-validation', methods=['GET'])
def validate_token():
    """Debug endpoint to validate JWT token format"""
    try:
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return jsonify({
                'error': 'No Authorization header found',
                'token_valid': False
            }), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authorization header does not start with Bearer',
                'header': auth_header,
                'token_valid': False
            }), 401
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        segments = token.split('.')
        
        return jsonify({
            'token_valid': len(segments) == 3,
            'segment_count': len(segments),
            'expected_segments': 3,
            'token_length': len(token),
            'token_preview': token[:50] + '...' if len(token) > 50 else token,
            'header_correct': auth_header.startswith('Bearer '),
            'segments_lengths': [len(seg) for seg in segments] if len(segments) <= 3 else 'Too many segments'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'token_valid': False
        }), 500

@debug_bp.route('/token-identity', methods=['GET'])
@jwt_required()
def check_token_identity():
    """Debug endpoint to check JWT token identity (requires valid token)"""
    try:
        current_user = get_jwt_identity()
        claims = get_jwt()
        
        return jsonify({
            'token_valid': True,
            'user_identity': current_user,
            'token_claims': claims
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'token_valid': False
        }), 500

@debug_bp.route('/schema-status', methods=['GET'])
def check_schema_status():
    """Check if time fields exist in the database"""
    try:
        import psycopg2
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'DATABASE_URL not found'}), 500
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check for time columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'event' 
            AND column_name IN ('arrive_by_time', 'start_time', 'end_time')
            ORDER BY column_name
        """)
        
        time_columns = cur.fetchall()
        
        # Get all event columns for debugging
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'event'
            ORDER BY column_name
        """)
        
        all_columns = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'time_columns_found': len(time_columns),
            'time_columns': [{'name': col[0], 'type': col[1], 'nullable': col[2]} for col in time_columns],
            'migration_needed': len(time_columns) < 3,
            'total_event_columns': len(all_columns),
            'all_columns': [{'name': col[0], 'type': col[1]} for col in all_columns]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
