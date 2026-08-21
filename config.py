import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_12345'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/bookrecommendation_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe settings
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Custom settings
    PREMIUM_PRICE = 9.99  # Monthly subscription or one-time premium access
