"""
Subscription and Payment Routes
Handles subscription management and Stripe integration endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Organization, Subscription, PaymentHistory, SubscriptionTier
from services.stripe_service import stripe_service
import logging

logger = logging.getLogger(__name__)

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscription/status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Get current subscription status for user's organization"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.organization_id:
            return jsonify({'error': 'User not found or not in organization'}), 404
        
        # Get or create subscription
        subscription = Subscription.query.filter_by(organization_id=user.organization_id).first()
        if not subscription:
            subscription = Subscription(organization_id=user.organization_id)
            subscription.update_user_count()
            db.session.add(subscription)
            db.session.commit()
        else:
            # Update user count
            subscription.update_user_count()
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'organization': {
                'id': user.organization.id,
                'name': user.organization.name,
                'user_count': subscription.current_user_count
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        return jsonify({'error': 'Failed to get subscription status'}), 500

@subscription_bp.route('/subscription/tiers', methods=['GET'])
def get_subscription_tiers():
    """Get available subscription tiers and pricing"""
    try:
        tiers = {
            'free': {
                'name': 'Free',
                'price': 0,
                'currency': 'USD',
                'interval': 'month',
                'user_limit': 5,
                'features': [
                    'Up to 5 band members',
                    'Event scheduling',
                    'RSVP management',
                    'Basic notifications',
                    'Mobile access'
                ]
            },
            'pro': {
                'name': 'Pro',
                'price': 29.99,
                'currency': 'USD', 
                'interval': 'month',
                'user_limit': None,  # Unlimited
                'features': [
                    'Unlimited band members',
                    'Advanced event management',
                    'Real-time activity feed',
                    'Priority support',
                    'Advanced analytics',
                    'Custom integrations'
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'tiers': tiers
        })
        
    except Exception as e:
        logger.error(f"Failed to get subscription tiers: {e}")
        return jsonify({'error': 'Failed to get subscription tiers'}), 500

@subscription_bp.route('/subscription/checkout', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create Stripe checkout session for Pro subscription"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.organization_id:
            return jsonify({'error': 'User not found or not in organization'}), 404
        
        # Check if user is admin
        if user.role not in ['Admin', 'Super Admin']:
            return jsonify({'error': 'Only admins can manage subscriptions'}), 403
        
        data = request.get_json()
        success_url = data.get('success_url')
        cancel_url = data.get('cancel_url')
        
        if not success_url or not cancel_url:
            return jsonify({'error': 'success_url and cancel_url are required'}), 400
        
        # Create checkout session
        session = stripe_service.create_checkout_session(
            organization_id=user.organization_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return jsonify({
            'success': True,
            'checkout_url': session.url,
            'session_id': session.id
        })
        
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

@subscription_bp.route('/subscription/billing-portal', methods=['POST'])
@jwt_required()
def create_billing_portal_session():
    """Create Stripe billing portal session for subscription management"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.organization_id:
            return jsonify({'error': 'User not found or not in organization'}), 404
        
        # Check if user is admin
        if user.role not in ['Admin', 'Super Admin']:
            return jsonify({'error': 'Only admins can manage subscriptions'}), 403
        
        data = request.get_json()
        return_url = data.get('return_url')
        
        if not return_url:
            return jsonify({'error': 'return_url is required'}), 400
        
        # Create billing portal session
        session = stripe_service.create_billing_portal_session(
            organization_id=user.organization_id,
            return_url=return_url
        )
        
        return jsonify({
            'success': True,
            'portal_url': session.url
        })
        
    except Exception as e:
        logger.error(f"Failed to create billing portal session: {e}")
        return jsonify({'error': 'Failed to create billing portal session'}), 500

@subscription_bp.route('/subscription/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel Pro subscription"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.organization_id:
            return jsonify({'error': 'User not found or not in organization'}), 404
        
        # Check if user is admin
        if user.role not in ['Admin', 'Super Admin']:
            return jsonify({'error': 'Only admins can manage subscriptions'}), 403
        
        # Cancel subscription
        stripe_service.cancel_subscription(user.organization_id)
        
        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500

@subscription_bp.route('/subscription/payment-history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get payment history for organization"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.organization_id:
            return jsonify({'error': 'User not found or not in organization'}), 404
        
        # Check if user is admin
        if user.role not in ['Admin', 'Super Admin']:
            return jsonify({'error': 'Only admins can view payment history'}), 403
        
        subscription = Subscription.query.filter_by(organization_id=user.organization_id).first()
        if not subscription:
            return jsonify({
                'success': True,
                'payments': []
            })
        
        payments = PaymentHistory.query.filter_by(subscription_id=subscription.id)\
                                      .order_by(PaymentHistory.created_at.desc())\
                                      .all()
        
        return jsonify({
            'success': True,
            'payments': [payment.to_dict() for payment in payments]
        })
        
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        return jsonify({'error': 'Failed to get payment history'}), 500

@subscription_bp.route('/subscription/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        # Verify and process webhook
        event = stripe_service.handle_webhook(payload, signature)
        
        return jsonify({'success': True}), 200
        
    except ValueError as e:
        logger.error(f"Invalid webhook signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@subscription_bp.route('/subscription/check-limits', methods=['GET'])
@jwt_required()
def check_subscription_limits():
    """Check if organization can add more users"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.organization_id:
            return jsonify({'error': 'User not found or not in organization'}), 404
        
        subscription = Subscription.query.filter_by(organization_id=user.organization_id).first()
        if not subscription:
            subscription = Subscription(organization_id=user.organization_id)
            subscription.update_user_count()
            db.session.add(subscription)
            db.session.commit()
        else:
            subscription.update_user_count()
        
        return jsonify({
            'success': True,
            'can_add_user': subscription.can_add_user,
            'current_user_count': subscription.current_user_count,
            'user_limit': subscription.user_limit,
            'users_remaining': subscription.users_remaining if subscription.users_remaining != float('inf') else None,
            'is_unlimited': subscription.is_unlimited,
            'tier': subscription.tier.value,
            'is_over_limit': subscription.is_over_limit
        })
        
    except Exception as e:
        logger.error(f"Failed to check subscription limits: {e}")
        return jsonify({'error': 'Failed to check subscription limits'}), 500
