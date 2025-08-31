"""
Add Subscription and Payment Tables Migration
Creates subscription management and Stripe integration tables
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, Organization, User, Subscription, PaymentHistory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_subscription_migration():
    """Add subscription and payment tables"""
    try:
        logger.info("="*60)
        logger.info("Add Subscription and Payment Tables Migration")
        logger.info("="*60)
        logger.info(f"Started at: {datetime.now()}")
        
        # Check environment
        environment = os.getenv('RAILWAY_ENVIRONMENT', 'local')
        logger.info(f"Running in environment: {environment}")
        
        # Create tables
        logger.info("🚀 Creating subscription and payment tables...")
        db.create_all()
        logger.info("✓ Tables created successfully")
        
        # Create subscriptions for existing organizations
        logger.info("📋 Creating free subscriptions for existing organizations...")
        
        existing_orgs = Organization.query.all()
        subscriptions_created = 0
        
        for org in existing_orgs:
            # Check if subscription already exists
            existing_subscription = Subscription.query.filter_by(organization_id=org.id).first()
            if not existing_subscription:
                # Create free subscription
                subscription = Subscription(organization_id=org.id)
                # Update user count
                user_count = User.query.filter_by(organization_id=org.id).count()
                subscription.current_user_count = user_count
                
                db.session.add(subscription)
                subscriptions_created += 1
                
                logger.info(f"✓ Created free subscription for '{org.name}' (ID: {org.id}) with {user_count} users")
        
        db.session.commit()
        
        logger.info("="*60)
        logger.info(f"✅ Migration completed successfully!")
        logger.info(f"📊 Subscriptions created: {subscriptions_created}")
        logger.info(f"📊 Total organizations: {len(existing_orgs)}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.session.rollback()
        raise e

if __name__ == "__main__":
    # Import app to initialize database
    from backend.app import app
    
    with app.app_context():
        run_subscription_migration()
