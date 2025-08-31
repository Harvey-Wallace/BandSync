"""
Stripe Payment Service
Handles Stripe integration for subscription payments
"""

import stripe
import os
import logging
from flask import current_app
from models import db, Subscription, PaymentHistory, Organization, SubscriptionTier, SubscriptionStatus
from datetime import datetime

logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        # Set Stripe API key from environment
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        # Pricing configuration
        self.pricing = {
            'pro_monthly': {
                'amount': 2999,  # $29.99 in cents
                'currency': 'usd',
                'interval': 'month',
                'product_name': 'BandSync Pro',
                'description': 'Unlimited users for your band organization'
            }
        }
    
    def create_customer(self, organization):
        """Create a Stripe customer for an organization"""
        try:
            customer = stripe.Customer.create(
                email=organization.email if hasattr(organization, 'email') else None,
                name=organization.name,
                metadata={
                    'organization_id': organization.id,
                    'organization_name': organization.name
                }
            )
            
            logger.info(f"Created Stripe customer {customer.id} for organization {organization.id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for organization {organization.id}: {e}")
            raise e
    
    def create_checkout_session(self, organization_id, success_url, cancel_url):
        """Create a Stripe Checkout session for Pro subscription"""
        try:
            organization = Organization.query.get(organization_id)
            if not organization:
                raise ValueError(f"Organization {organization_id} not found")
            
            subscription = Subscription.query.filter_by(organization_id=organization_id).first()
            if not subscription:
                # Create subscription record if it doesn't exist
                subscription = Subscription(organization_id=organization_id)
                db.session.add(subscription)
                db.session.commit()
            
            # Create or get Stripe customer
            if not subscription.stripe_customer_id:
                customer = self.create_customer(organization)
                subscription.stripe_customer_id = customer.id
                db.session.commit()
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=subscription.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': self.pricing['pro_monthly']['currency'],
                        'product_data': {
                            'name': self.pricing['pro_monthly']['product_name'],
                            'description': self.pricing['pro_monthly']['description'],
                        },
                        'unit_amount': self.pricing['pro_monthly']['amount'],
                        'recurring': {
                            'interval': self.pricing['pro_monthly']['interval'],
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'organization_id': organization_id,
                    'subscription_id': subscription.id
                }
            )
            
            logger.info(f"Created checkout session {session.id} for organization {organization_id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session for organization {organization_id}: {e}")
            raise e
    
    def create_billing_portal_session(self, organization_id, return_url):
        """Create a Stripe billing portal session for subscription management"""
        try:
            subscription = Subscription.query.filter_by(organization_id=organization_id).first()
            if not subscription or not subscription.stripe_customer_id:
                raise ValueError(f"No Stripe customer found for organization {organization_id}")
            
            session = stripe.billing_portal.Session.create(
                customer=subscription.stripe_customer_id,
                return_url=return_url,
            )
            
            logger.info(f"Created billing portal session for organization {organization_id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session for organization {organization_id}: {e}")
            raise e
    
    def handle_webhook(self, payload, signature):
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            logger.info(f"Received Stripe webhook: {event['type']}")
            
            if event['type'] == 'checkout.session.completed':
                self._handle_checkout_completed(event['data']['object'])
            elif event['type'] == 'invoice.payment_succeeded':
                self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                self._handle_payment_failed(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                self._handle_subscription_deleted(event['data']['object'])
            
            return event
            
        except ValueError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise e
        except stripe.error.StripeError as e:
            logger.error(f"Webhook error: {e}")
            raise e
    
    def _handle_checkout_completed(self, session):
        """Handle successful checkout completion"""
        try:
            organization_id = session['metadata']['organization_id']
            subscription_id = session['metadata']['subscription_id']
            
            # Get the subscription from Stripe
            stripe_subscription = stripe.Subscription.retrieve(session['subscription'])
            
            # Update our subscription record
            subscription = Subscription.query.get(subscription_id)
            if subscription:
                subscription.upgrade_to_pro(
                    stripe_subscription_id=stripe_subscription.id,
                    stripe_customer_id=session['customer']
                )
                subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
                subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
                subscription.status = SubscriptionStatus.ACTIVE
                
                db.session.commit()
                
                logger.info(f"Successfully upgraded organization {organization_id} to Pro")
            
        except Exception as e:
            logger.error(f"Failed to handle checkout completion: {e}")
    
    def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        try:
            stripe_subscription_id = invoice['subscription']
            
            # Find subscription
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=stripe_subscription_id
            ).first()
            
            if subscription:
                # Create payment history record
                payment = PaymentHistory(
                    subscription_id=subscription.id,
                    stripe_invoice_id=invoice['id'],
                    stripe_payment_intent_id=invoice.get('payment_intent'),
                    amount=invoice['amount_paid'],
                    currency=invoice['currency'],
                    status='succeeded',
                    description=f"Payment for {subscription.organization.name} - Pro subscription",
                    period_start=datetime.fromtimestamp(invoice['period_start']) if invoice.get('period_start') else None,
                    period_end=datetime.fromtimestamp(invoice['period_end']) if invoice.get('period_end') else None,
                    paid_at=datetime.fromtimestamp(invoice['status_transitions']['paid_at']) if invoice['status_transitions'].get('paid_at') else None
                )
                
                db.session.add(payment)
                db.session.commit()
                
                logger.info(f"Recorded successful payment for subscription {subscription.id}")
                
        except Exception as e:
            logger.error(f"Failed to handle payment success: {e}")
    
    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        try:
            stripe_subscription_id = invoice['subscription']
            
            # Find subscription
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=stripe_subscription_id
            ).first()
            
            if subscription:
                # Update subscription status
                subscription.status = SubscriptionStatus.PAST_DUE
                
                # Create payment history record
                payment = PaymentHistory(
                    subscription_id=subscription.id,
                    stripe_invoice_id=invoice['id'],
                    stripe_payment_intent_id=invoice.get('payment_intent'),
                    amount=invoice['amount_due'],
                    currency=invoice['currency'],
                    status='failed',
                    description=f"Failed payment for {subscription.organization.name} - Pro subscription",
                    period_start=datetime.fromtimestamp(invoice['period_start']) if invoice.get('period_start') else None,
                    period_end=datetime.fromtimestamp(invoice['period_end']) if invoice.get('period_end') else None
                )
                
                db.session.add(payment)
                db.session.commit()
                
                logger.warning(f"Payment failed for subscription {subscription.id}")
                
        except Exception as e:
            logger.error(f"Failed to handle payment failure: {e}")
    
    def _handle_subscription_updated(self, stripe_subscription):
        """Handle subscription update"""
        try:
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=stripe_subscription['id']
            ).first()
            
            if subscription:
                # Update subscription details
                subscription.status = SubscriptionStatus(stripe_subscription['status'])
                subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
                subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
                
                db.session.commit()
                
                logger.info(f"Updated subscription {subscription.id} status to {stripe_subscription['status']}")
                
        except Exception as e:
            logger.error(f"Failed to handle subscription update: {e}")
    
    def _handle_subscription_deleted(self, stripe_subscription):
        """Handle subscription cancellation"""
        try:
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=stripe_subscription['id']
            ).first()
            
            if subscription:
                # Downgrade to free tier
                subscription.downgrade_to_free()
                subscription.status = SubscriptionStatus.CANCELED
                
                db.session.commit()
                
                logger.info(f"Downgraded subscription {subscription.id} to free tier")
                
        except Exception as e:
            logger.error(f"Failed to handle subscription deletion: {e}")
    
    def cancel_subscription(self, organization_id):
        """Cancel a Pro subscription"""
        try:
            subscription = Subscription.query.filter_by(organization_id=organization_id).first()
            if not subscription or not subscription.stripe_subscription_id:
                raise ValueError(f"No active subscription found for organization {organization_id}")
            
            # Cancel in Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            
            # Update our records
            subscription.downgrade_to_free()
            subscription.status = SubscriptionStatus.CANCELED
            
            db.session.commit()
            
            logger.info(f"Cancelled subscription for organization {organization_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription for organization {organization_id}: {e}")
            raise e

# Global service instance
stripe_service = StripeService()
