# Resend Email Service Migration Guide

## Overview
This guide covers the migration from SendGrid to Resend for BandSync's email service.

## What Changed
- **Email Service**: Migrated from SendGrid to Resend API
- **Dependencies**: Replaced `sendgrid` with `resend` in requirements.txt
- **Environment Variables**: Changed from `SENDGRID_API_KEY` to `RESEND_API_KEY`
- **Configuration**: Updated docker-compose.yml and .env files

## Steps to Complete Migration

### 1. Sign Up for Resend Account
1. Go to [resend.com](https://resend.com)
2. Create an account
3. Verify your email address
4. Add and verify your domain (e.g., `yourdomain.com`)

### 2. Get API Key
1. In Resend dashboard, go to "API Keys"
2. Create a new API key
3. Copy the API key (starts with `re_`)

### 3. Update Environment Variables

#### For Railway Deployment:
1. Go to your Railway project dashboard
2. Navigate to Variables tab
3. **Remove** `SENDGRID_API_KEY` variable
4. **Add** new variable:
   - Key: `RESEND_API_KEY`
   - Value: `re_your_api_key_here`

#### For Local Development:
Update your `backend/.env` file:
```bash
# Email Service (Resend)
RESEND_API_KEY=re_your_api_key_here
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=BandSync
```

### 4. Deploy Updated Code
1. Commit and push your changes
2. Railway will automatically redeploy with the new email service

### 5. Test Email Functionality
After deployment, test these features:
- User registration (welcome emails)
- Event reminders
- RSVP deadline reminders
- User invitations
- Daily summaries

## Key Differences from SendGrid

### Resend Advantages:
- ✅ Modern, developer-friendly API
- ✅ Better deliverability
- ✅ Generous free tier (3,000 emails/month)
- ✅ Easier setup and configuration
- ✅ Better documentation and support

### API Changes:
- **Bulk Emails**: Resend sends individual emails instead of bulk
- **Response Format**: Returns `{"id": "message_id"}` instead of status codes
- **Attachments**: Simplified attachment format

## Email Templates
No changes needed to email templates - they remain in `backend/templates/email/`

## Troubleshooting

### Common Issues:
1. **"Email service not configured"** - Check `RESEND_API_KEY` is set
2. **"Invalid API key"** - Verify the API key starts with `re_`
3. **"Domain not verified"** - Verify your domain in Resend dashboard
4. **"From email rejected"** - Use a verified domain for `FROM_EMAIL`

### NEW ACCOUNT LIMITATIONS:
**Important**: New Resend accounts have restrictions:
- **You can only send emails to your own verified email address** until you verify a domain
- **You must use `onboarding@resend.dev` as the FROM_EMAIL** for new accounts
- **Email addresses are case-sensitive** (e.g., `rob@harvey-wallace.co.uk` vs `Rob@Harvey-Wallace.co.uk`)

### Current Working Configuration:
```bash
RESEND_API_KEY=re_your_api_key_here
FROM_EMAIL=noreply@bandsync.co.uk
FROM_NAME=BandSync
```

### Domain Status: ✅ VERIFIED
- **Domain**: `bandsync.co.uk` is verified and active
- **Restrictions**: ✅ NONE - Can send to any email address
- **Professional**: Using branded domain for better deliverability

### Debug Steps:
1. Check Railway logs for email service errors
2. Verify environment variables are set correctly
3. Test with the provided test script
4. Check Resend dashboard for delivery status
5. **Ensure test email matches your verified email exactly (case-sensitive)**

## Testing Script
Use the provided `test_resend_email.py` script to test email functionality:

```bash
# Install dependencies
pip install resend

# Set your API key in the script
python test_resend_email.py
```

## Rollback Plan
If you need to rollback to SendGrid:
1. Revert the email service code
2. Change `RESEND_API_KEY` back to `SENDGRID_API_KEY`
3. Update requirements.txt to use `sendgrid`
4. Redeploy

## Support
- **Resend Documentation**: https://resend.com/docs
- **Resend Status**: https://status.resend.com
- **Support**: help@resend.com

## Next Steps
1. Monitor email delivery for first 24-48 hours
2. Set up email bounce/complaint handling if needed
3. Configure email analytics in Resend dashboard
4. Update documentation to reflect new email service
