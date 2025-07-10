"""
Migration script to add name, phone, and address fields to User table
Run this script to update the database schema
"""
from models import db, User
from app import app

def migrate():
    """Add new profile fields to User table"""
    with app.app_context():
        # Check if columns already exist
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        if 'name' not in columns:
            db.engine.execute('ALTER TABLE user ADD COLUMN name VARCHAR(120)')
            print("Added 'name' column to User table")
        
        if 'phone' not in columns:
            db.engine.execute('ALTER TABLE user ADD COLUMN phone VARCHAR(20)')
            print("Added 'phone' column to User table")
        
        if 'address' not in columns:
            db.engine.execute('ALTER TABLE user ADD COLUMN address TEXT')
            print("Added 'address' column to User table")
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
