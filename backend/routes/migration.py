"""
Railway Migration Endpoint
Provides a secure endpoint to run database migrations on Railway
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from services.stripe_service import StripeService
from sqlalchemy import text
import logging

migration_bp = Blueprint('migration', __name__)

@migration_bp.route('/run-subscription-migration', methods=['POST'])
@jwt_required()
def run_subscription_migration():
    """
    Run the subscription tables migration
    Only accessible by super admins
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_super_admin:
            return jsonify({'success': False, 'message': 'Unauthorized - Super admin access required'}), 403
        
        logging.info(f"Super admin {user.username} initiated subscription migration")
        
        # SQL for creating subscription table
        subscription_table_sql = """
        CREATE TABLE IF NOT EXISTS subscription (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL UNIQUE,
            tier VARCHAR(20) NOT NULL DEFAULT 'free',
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            current_user_count INTEGER NOT NULL DEFAULT 0,
            max_users INTEGER DEFAULT 5,
            stripe_customer_id VARCHAR(255),
            stripe_subscription_id VARCHAR(255),
            billing_period_start TIMESTAMP,
            billing_period_end TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organization (id)
        );
        """
        
        # SQL for creating payment history table
        payment_history_table_sql = """
        CREATE TABLE IF NOT EXISTS payment_history (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL,
            stripe_payment_intent_id VARCHAR(255) NOT NULL,
            amount INTEGER NOT NULL,
            currency VARCHAR(3) NOT NULL DEFAULT 'usd',
            status VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organization (id)
        );
        """
        
        # Execute migrations
        db.session.execute(text(subscription_table_sql))
        db.session.execute(text(payment_history_table_sql))
        db.session.commit()
        
        logging.info("Subscription tables migration completed successfully")
        
        return jsonify({
            'success': True,
            'message': 'Subscription tables migration completed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Migration failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Migration failed: {str(e)}'
        }), 500

@migration_bp.route('/check-subscription-tables', methods=['GET'])
@jwt_required()
def check_subscription_tables():
    """
    Check if subscription tables exist
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_super_admin:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Check if tables exist
        subscription_check = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'subscription'
            );
        """)).scalar()
        
        payment_history_check = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'payment_history'
            );
        """)).scalar()
        
        return jsonify({
            'success': True,
            'tables_exist': {
                'subscription': subscription_check,
                'payment_history': payment_history_check
            }
        })
        
    except Exception as e:
        logging.error(f"Table check failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Table check failed: {str(e)}'
        }), 500
