#!/usr/bin/env python3
"""
Fix all route prefixes in BandSync Phase 2 blueprints
"""

import os
import re

def fix_messages_routes():
    """Fix message routes"""
    file_path = 'backend/routes/messages.py'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix all message routes
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/threads\', methods=\[\'GET\'\]\)', r'@messages_bp.route(\'/threads\', methods=[\'GET\'])', content)
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/threads/<int:thread_id>/messages\', methods=\[\'GET\'\]\)', r'@messages_bp.route(\'/threads/<int:thread_id>/messages\', methods=[\'GET\'])', content)
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/threads\', methods=\[\'POST\'\]\)', r'@messages_bp.route(\'/threads\', methods=[\'POST\'])', content)
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/threads/<int:thread_id>/messages\', methods=\[\'POST\'\]\)', r'@messages_bp.route(\'/threads/<int:thread_id>/messages\', methods=[\'POST\'])', content)
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/compose\', methods=\[\'GET\'\]\)', r'@messages_bp.route(\'/compose\', methods=[\'GET\'])', content)
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/threads/<int:thread_id>\', methods=\[\'DELETE\'\]\)', r'@messages_bp.route(\'/threads/<int:thread_id>\', methods=[\'DELETE\'])', content)
        content = re.sub(r'@messages_bp\.route\(\'/api/messages/broadcast\', methods=\[\'POST\'\]\)', r'@messages_bp.route(\'/broadcast\', methods=[\'POST\'])', content)
        
        # Fix any remaining escaped quotes
        content = content.replace("\\'", "'")
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {file_path}")

def fix_substitutes_routes():
    """Fix substitute routes"""
    file_path = 'backend/routes/substitutes.py'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix all substitute routes
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/requests\', methods=\[\'GET\'\]\)', r'@substitutes_bp.route(\'/requests\', methods=[\'GET\'])', content)
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/request\', methods=\[\'POST\'\]\)', r'@substitutes_bp.route(\'/request\', methods=[\'POST\'])', content)
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/requests/<int:request_id>/respond\', methods=\[\'POST\'\]\)', r'@substitutes_bp.route(\'/requests/<int:request_id>/respond\', methods=[\'POST\'])', content)
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/availability\', methods=\[\'GET\'\]\)', r'@substitutes_bp.route(\'/availability\', methods=[\'GET\'])', content)
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/availability\', methods=\[\'POST\'\]\)', r'@substitutes_bp.route(\'/availability\', methods=[\'POST\'])', content)
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/call-list\', methods=\[\'GET\'\]\)', r'@substitutes_bp.route(\'/call-list\', methods=[\'GET\'])', content)
        content = re.sub(r'@substitutes_bp\.route\(\'/api/substitutes/call-list\', methods=\[\'POST\'\]\)', r'@substitutes_bp.route(\'/call-list\', methods=[\'POST\'])', content)
        
        # Fix any remaining escaped quotes
        content = content.replace("\\'", "'")
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {file_path}")

def fix_bulk_ops_routes():
    """Fix bulk ops routes"""
    file_path = 'backend/routes/bulk_ops.py'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix all bulk ops routes
        content = re.sub(r'@bulk_ops_bp\.route\(\'/api/bulk-ops/import-template\', methods=\[\'GET\'\]\)', r'@bulk_ops_bp.route(\'/import-template\', methods=[\'GET\'])', content)
        content = re.sub(r'@bulk_ops_bp\.route\(\'/api/bulk-ops/import-users\', methods=\[\'POST\'\]\)', r'@bulk_ops_bp.route(\'/import-users\', methods=[\'POST\'])', content)
        content = re.sub(r'@bulk_ops_bp\.route\(\'/api/bulk-ops/export\', methods=\[\'GET\'\]\)', r'@bulk_ops_bp.route(\'/export\', methods=[\'GET\'])', content)
        content = re.sub(r'@bulk_ops_bp\.route\(\'/api/bulk-ops/create-events\', methods=\[\'POST\'\]\)', r'@bulk_ops_bp.route(\'/create-events\', methods=[\'POST\'])', content)
        content = re.sub(r'@bulk_ops_bp\.route\(\'/api/bulk-ops/broadcast\', methods=\[\'POST\'\]\)', r'@bulk_ops_bp.route(\'/broadcast\', methods=[\'POST\'])', content)
        
        # Fix any remaining escaped quotes
        content = content.replace("\\'", "'")
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {file_path}")

def fix_quick_polls_routes():
    """Fix quick polls routes"""
    file_path = 'backend/routes/quick_polls.py'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix all quick polls routes
        content = re.sub(r'@quick_polls_bp\.route\(\'/api/quick-polls/\', methods=\[\'GET\'\]\)', r'@quick_polls_bp.route(\'/\', methods=[\'GET\'])', content)
        content = re.sub(r'@quick_polls_bp\.route\(\'/api/quick-polls/\', methods=\[\'POST\'\]\)', r'@quick_polls_bp.route(\'/\', methods=[\'POST\'])', content)
        content = re.sub(r'@quick_polls_bp\.route\(\'/api/quick-polls/<int:poll_id>\', methods=\[\'GET\'\]\)', r'@quick_polls_bp.route(\'/<int:poll_id>\', methods=[\'GET\'])', content)
        content = re.sub(r'@quick_polls_bp\.route\(\'/api/quick-polls/<int:poll_id>/vote\', methods=\[\'POST\'\]\)', r'@quick_polls_bp.route(\'/<int:poll_id>/vote\', methods=[\'POST\'])', content)
        content = re.sub(r'@quick_polls_bp\.route\(\'/api/quick-polls/<int:poll_id>/results\', methods=\[\'GET\'\]\)', r'@quick_polls_bp.route(\'/<int:poll_id>/results\', methods=[\'GET\'])', content)
        content = re.sub(r'@quick_polls_bp\.route\(\'/api/quick-polls/<int:poll_id>/close\', methods=\[\'POST\'\]\)', r'@quick_polls_bp.route(\'/<int:poll_id>/close\', methods=[\'POST\'])', content)
        
        # Fix any remaining escaped quotes
        content = content.replace("\\'", "'")
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {file_path}")

if __name__ == "__main__":
    fix_messages_routes()
    fix_substitutes_routes()
    fix_bulk_ops_routes()
    fix_quick_polls_routes()
    print("🎉 All route prefixes fixed properly!")
