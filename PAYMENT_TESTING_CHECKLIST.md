# 🧪 Payment System Testing Checklist

## Pre-Testing Setup
- [ ] Stripe test keys configured in Railway environment
- [ ] Database migration completed (`subscription` and `payment_history` tables created)
- [ ] Application deployed and running on https://app.bandsync.co.uk

## Frontend Testing
- [ ] Subscription link appears in navigation menu
- [ ] `/subscription` page loads and shows current plan status
- [ ] Free tier shows "Up to 5 users" limitation
- [ ] "Upgrade to Pro" button is visible for free tier users
- [ ] Tier comparison shows correct features and pricing

## Backend API Testing
- [ ] `GET /api/subscription/status` returns current subscription
- [ ] `GET /api/subscription/tiers` returns available plans
- [ ] `POST /api/subscription/create-checkout-session` creates Stripe checkout
- [ ] `POST /api/subscription/create-billing-portal-session` creates billing portal
- [ ] `GET /api/subscription/payment-history` returns payment records

## Payment Flow Testing
- [ ] Click "Upgrade to Pro" redirects to Stripe checkout
- [ ] Stripe checkout shows correct amount ($10.00)
- [ ] Test payment with card: `4242 4242 4242 4242`
- [ ] Successful payment redirects to `/subscription/success`
- [ ] Success page shows updated subscription details
- [ ] User limit changes from "5" to "Unlimited"
- [ ] Billing portal accessible for Pro users

## User Registration Testing
- [ ] Free tier organizations can add up to 5 users
- [ ] 6th user registration blocked with subscription message
- [ ] Pro tier organizations can add unlimited users
- [ ] New organizations automatically get free subscription

## Admin Features Testing
- [ ] Super admin can access migration endpoints
- [ ] Regular admins cannot access migration endpoints
- [ ] Payment history displays correctly
- [ ] Subscription status updates in real-time

## Error Handling Testing
- [ ] Failed payments show appropriate error messages
- [ ] Network errors handled gracefully
- [ ] Invalid subscription states handled
- [ ] Webhook failures logged properly

## Production Checklist
- [ ] Switch to live Stripe keys for production
- [ ] Set up Stripe webhook endpoint: https://app.bandsync.co.uk/api/subscription/webhook
- [ ] Configure webhook events: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `payment_intent.succeeded`
- [ ] Test with real payment methods
- [ ] Monitor payment success rates
- [ ] Set up subscription analytics

## 🎯 Success Criteria
✅ Users can upgrade from Free to Pro tier
✅ Payment processing works end-to-end  
✅ User limits enforced correctly
✅ Billing portal allows subscription management
✅ Webhooks update subscription status automatically
