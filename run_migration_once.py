#!/usr/bin/env python3
"""
One-time migration runner for Railway
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the migration
from railway_migration import main

if __name__ == "__main__":
    try:
        main()
        print("✅ Migration completed - you can now re-enable the organization fields!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
