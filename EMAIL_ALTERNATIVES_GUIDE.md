# BandSync Email Service Migration Guide

## Option 1: Resend (Modern SendGrid Alternative)

### Step 1: Install Resend
```bash
pip install resend
```

### Step 2: Update EmailService Class
Replace the SendGrid implementation in `backend/services/email_service.py`:

```python
import resend
from resend import Resend

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@bandsync.com')
        self.from_name = os.environ.get('FROM_NAME', 'BandSync')
        self.base_url = os.environ.get('BASE_URL', 'https://bandsync.com')
        
        if self.api_key:
            resend.api_key = self.api_key
        else:
            logger.warning("RESEND_API_KEY not found. Email functionality will be disabled.")
            self.client = None
        
        # Initialize template environment (same as before)
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _send_email(self, to_emails: List[str], subject: str, html_content: str, 
                   text_content: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> bool:
        """Send email using Resend"""
        if not self.api_key:
            logger.warning(f"Email service not configured. Would send email to {to_emails} with subject: {subject}")
            return False
        
        try:
            # Send to each recipient
            for email in to_emails:
                params = {
                    'from': f"{self.from_name} <{self.from_email}>",
                    'to': [email],
                    'subject': subject,
                    'html': html_content,
                }
                
                if text_content:
                    params['text'] = text_content
                
                response = resend.Emails.send(params)
                
                if response.get('id'):
                    logger.info(f"Email sent successfully to {email}")
                else:
                    logger.error(f"Failed to send email to {email}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
```

### Step 3: Update Environment Variables
```bash
# Remove
SENDGRID_API_KEY=your-sendgrid-api-key

# Add
RESEND_API_KEY=your-resend-api-key
```

### Step 4: Update requirements.txt
```
# Remove
sendgrid==6.x.x

# Add
resend==0.7.0
```

---

## Option 2: AWS SES (Most Cost-Effective)

### Step 1: Install boto3
```bash
pip install boto3
```

### Step 2: Update EmailService Class
```python
import boto3
from botocore.exceptions import ClientError

class EmailService:
    def __init__(self):
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@bandsync.com')
        self.from_name = os.environ.get('FROM_NAME', 'BandSync')
        self.base_url = os.environ.get('BASE_URL', 'https://bandsync.com')
        
        # Initialize SES client
        try:
            self.client = boto3.client(
                'ses',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_SES_REGION', 'us-east-1')
            )
        except Exception as e:
            logger.warning(f"AWS SES not configured: {str(e)}")
            self.client = None
        
        # Initialize template environment (same as before)
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _send_email(self, to_emails: List[str], subject: str, html_content: str, 
                   text_content: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> bool:
        """Send email using AWS SES"""
        if not self.client:
            logger.warning(f"Email service not configured. Would send email to {to_emails} with subject: {subject}")
            return False
        
        try:
            response = self.client.send_email(
                Source=f"{self.from_name} <{self.from_email}>",
                Destination={'ToAddresses': to_emails},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_content, 'Charset': 'UTF-8'},
                        'Text': {'Data': text_content or '', 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS SES error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
```

### Step 3: Update Environment Variables
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_SES_REGION=us-east-1

# Email settings (same as before)
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=BandSync
```

### Step 4: Update requirements.txt
```
# Remove
sendgrid==6.x.x

# Add
boto3==1.26.0
```

---

## Option 3: Mailgun (Enterprise-Grade)

### Step 1: Install requests
```bash
pip install requests
```

### Step 2: Update EmailService Class
```python
import requests

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get('MAILGUN_API_KEY')
        self.domain = os.environ.get('MAILGUN_DOMAIN')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@bandsync.com')
        self.from_name = os.environ.get('FROM_NAME', 'BandSync')
        self.base_url = os.environ.get('BASE_URL', 'https://bandsync.com')
        
        # Initialize template environment (same as before)
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _send_email(self, to_emails: List[str], subject: str, html_content: str, 
                   text_content: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> bool:
        """Send email using Mailgun"""
        if not self.api_key or not self.domain:
            logger.warning(f"Email service not configured. Would send email to {to_emails} with subject: {subject}")
            return False
        
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.domain}/messages",
                auth=("api", self.api_key),
                data={
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": to_emails,
                    "subject": subject,
                    "html": html_content,
                    "text": text_content or ""
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully to {to_emails}")
                return True
            else:
                logger.error(f"Mailgun error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
```

### Step 3: Update Environment Variables
```bash
# Mailgun Settings
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-mailgun-domain.com

# Email settings (same as before)
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=BandSync
```

---

## 🎯 **Recommendation Summary**

**For BandSync, I recommend:**

1. **🥇 Resend** - Best overall choice for modern apps
   - Easy migration
   - Great developer experience
   - Excellent deliverability

2. **🥈 AWS SES** - If cost is primary concern
   - Extremely cheap
   - Highly scalable
   - Good for high-volume apps

3. **🥉 Mailgun** - If you need enterprise features
   - Advanced analytics
   - EU compliance
   - Established service

## 📋 **Migration Steps:**

1. **Choose your provider** (Resend recommended)
2. **Update the EmailService class** with new implementation
3. **Update environment variables** in Railway
4. **Update requirements.txt** and redeploy
5. **Test email functionality** using the debug page

The beauty of your current architecture is that you only need to modify the `_send_email` method in your `EmailService` class. All your templates, logging, and business logic remain unchanged!

Would you like me to implement any specific alternative, or do you have questions about the migration process?
