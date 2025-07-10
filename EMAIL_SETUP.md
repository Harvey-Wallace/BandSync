# Email Setup for BandSync

## Current Implementation

The BandSync admin dashboard now includes user creation and email invitation functionality. Currently, the email system is implemented as a **console logger** for development purposes.

## Features Added

### 1. User Creation
- Admins can create new users with:
  - Username (required)
  - Email (required)
  - Full name (optional)
  - Phone number (optional)
  - Role (Member/Admin)
  - Password (optional - auto-generates if empty)

### 2. Email Invitations
- Send invitation emails to new or existing users
- Auto-generates temporary passwords
- Includes login credentials in the email
- Currently logs email content to console

### 3. Admin Dashboard UI
- "Add User" button in User Management tab
- Comprehensive user creation form
- Send invitation checkbox
- Email invitation button for existing users
- Enhanced user table with name column

## How to Use

1. **Create a New User:**
   - Go to Admin Dashboard → User Management tab
   - Click "Add User" button
   - Fill out the form
   - Check "Send invitation email" to send credentials
   - Click "Create User"

2. **Send Invitation to Existing User:**
   - In the User Management table
   - Click the envelope icon next to any user
   - This resets their password and sends invitation

## Email Content Example

```
=== EMAIL INVITATION ===
To: user@example.com
Subject: Welcome to BandSync!

Hi John Doe,

You've been invited to join BandSync!

Login details:
Username: johndoe
Temporary Password: temp_johndoe123

Please log in and change your password immediately.
=========================
```

## Production Email Setup

To implement actual email sending in production, replace the `send_invitation_email` function in `/backend/routes/admin.py` with a real email service:

### Option 1: SendGrid
```python
import sendgrid
from sendgrid.helpers.mail import Mail

def send_invitation_email(user, password):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    
    message = Mail(
        from_email='noreply@yourband.com',
        to_emails=user.email,
        subject='Welcome to BandSync!',
        html_content=f'''
        <h2>Welcome to BandSync!</h2>
        <p>Hi {user.name or user.username},</p>
        <p>You've been invited to join BandSync!</p>
        <p><strong>Login details:</strong><br>
        Username: {user.username}<br>
        Temporary Password: {password}</p>
        <p>Please log in and change your password immediately.</p>
        '''
    )
    
    response = sg.send(message)
    return response
```

### Option 2: AWS SES
```python
import boto3

def send_invitation_email(user, password):
    ses = boto3.client('ses', region_name='us-east-1')
    
    response = ses.send_email(
        Source='noreply@yourband.com',
        Destination={'ToAddresses': [user.email]},
        Message={
            'Subject': {'Data': 'Welcome to BandSync!'},
            'Body': {
                'Html': {
                    'Data': f'''
                    <h2>Welcome to BandSync!</h2>
                    <p>Hi {user.name or user.username},</p>
                    <p>You've been invited to join BandSync!</p>
                    <p><strong>Login details:</strong><br>
                    Username: {user.username}<br>
                    Temporary Password: {password}</p>
                    <p>Please log in and change your password immediately.</p>
                    '''
                }
            }
        }
    )
    return response
```

### Option 3: SMTP (Gmail, etc.)
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_invitation_email(user, password):
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to BandSync!"
    message["From"] = sender_email
    message["To"] = user.email
    
    html = f'''
    <h2>Welcome to BandSync!</h2>
    <p>Hi {user.name or user.username},</p>
    <p>You've been invited to join BandSync!</p>
    <p><strong>Login details:</strong><br>
    Username: {user.username}<br>
    Temporary Password: {password}</p>
    <p>Please log in and change your password immediately.</p>
    '''
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, user.email, text)
```

## Environment Variables Needed

Add to your `.env` file:

```
# For SendGrid
SENDGRID_API_KEY=your_sendgrid_api_key

# For AWS SES
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# For SMTP
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password

# General
FROM_EMAIL=noreply@yourband.com
```

## API Endpoints

- `POST /api/admin/users` - Create new user
- `POST /api/admin/users/{id}/invite` - Send invitation to existing user

## Security Notes

- Temporary passwords are automatically generated
- Users should be prompted to change password on first login
- Email validation prevents duplicate emails
- Username validation prevents duplicate usernames
- Only admins can create users and send invitations
