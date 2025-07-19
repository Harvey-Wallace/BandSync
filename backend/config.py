import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # Handle Railway's DATABASE_URL format
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/bandsync')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    # Set JWT token to expire after 8 hours for better user experience
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
