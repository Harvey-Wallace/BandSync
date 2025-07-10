#!/usr/bin/env python3
"""
Fix route prefixes in BandSync Phase 2 blueprints
"""

import os
import re

def fix_route_prefixes():
    """Fix route prefixes in all Phase 2 blueprints"""
    
    # Define the route fixes for each blueprint
    fixes = {
        'backend/routes/messages.py': [
            (r'@messages_bp\.route\(\'/api/messages/', r'@messages_bp.route(\'/'),
        ],
        'backend/routes/substitutes.py': [
            (r'@substitutes_bp\.route\(\'/api/substitutes/', r'@substitutes_bp.route(\'/'),
        ],
        'backend/routes/bulk_ops.py': [
            (r'@bulk_ops_bp\.route\(\'/api/bulk-ops/', r'@bulk_ops_bp.route(\'/'),
        ],
        'backend/routes/quick_polls.py': [
            (r'@quick_polls_bp\.route\(\'/api/quick-polls/', r'@quick_polls_bp.route(\'/'),
        ],
    }
    
    for file_path, route_fixes in fixes.items():
        if os.path.exists(file_path):
            print(f"Fixing routes in {file_path}...")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            for old_pattern, new_pattern in route_fixes:
                content = re.sub(old_pattern, new_pattern, content)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed {file_path}")
        else:
            print(f"❌ File not found: {file_path}")

if __name__ == "__main__":
    fix_route_prefixes()
    print("🎉 All route prefixes fixed!")
