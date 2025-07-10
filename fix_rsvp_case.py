#!/usr/bin/env python3
"""
Fix RSVP Status Case Migration
Updates any lowercase RSVP statuses to proper case format
"""

import sys
import os
sys.path.append('backend')

from backend.models import db, RSVP
from backend.app import app

def fix_rsvp_case():
    """Fix RSVP status case in database"""
    with app.app_context():
        # Find all RSVPs with lowercase statuses
        lowercase_rsvps = RSVP.query.filter(
            RSVP.status.in_(['yes', 'no', 'maybe'])
        ).all()
        
        if not lowercase_rsvps:
            print("✅ No lowercase RSVP statuses found - database is already consistent")
            return
        
        print(f"🔧 Found {len(lowercase_rsvps)} RSVPs with lowercase statuses")
        
        # Update them to proper case
        for rsvp in lowercase_rsvps:
            old_status = rsvp.status
            rsvp.status = rsvp.status.capitalize()
            print(f"  Updated RSVP {rsvp.id}: '{old_status}' → '{rsvp.status}'")
        
        # Commit the changes
        db.session.commit()
        print(f"✅ Successfully updated {len(lowercase_rsvps)} RSVP statuses")

if __name__ == "__main__":
    fix_rsvp_case()
