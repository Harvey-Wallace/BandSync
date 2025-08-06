from flask import Blueprint, jsonify
import os

debug_bp = Blueprint('debug', __name__)

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
