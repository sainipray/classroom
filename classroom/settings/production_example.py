# settings/production_example.py

from .base import *

# ---------------------------------------------------------------------
# Production-Specific Settings
# ---------------------------------------------------------------------

# Debug mode should be disabled in production
DEBUG = False

# Define your allowed hosts in production
ALLOWED_HOSTS = ['your-production-domain.com']  # Replace with your actual domain

# Secret key for production (must be kept secret and unique)
SECRET_KEY = "your-production-secret-key"

# Database configuration for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": 'db_prod',          # Change to your production DB name
        "USER": 'user_prod',          # Change to your production DB user
        "PASSWORD": 'password_prod',    # Change to your production DB password
        "HOST": 'localhost',         # Change to your production DB host
        "PORT": '5432',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR.parent.joinpath('assets')  # Replace with your actual static root

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent.joinpath('media')  # Replace with your actual media root

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email backend for production (configure SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-email-provider.com'          # Replace with your SMTP host
EMAIL_PORT = 587                                     # Replace with your SMTP port
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'           # Replace with your SMTP username
EMAIL_HOST_PASSWORD = 'your-email-password'          # Replace with your SMTP password
EMAIL_FROM_ADDRESS = 'your-email@example.com'        # Replace with your "from" email address
EMAIL_FROM_NAME = 'Your Project Name'               # Replace with your "from" name
EMAIL_BCC_LIST = ['bcc1@example.com', 'bcc2@example.com']  # Replace with your BCC list if any

# Default file storage (e.g., using AWS S3)
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# AWS S3 settings
AWS_ACCESS_KEY_ID = "your-aws-access-key-id"
AWS_SECRET_ACCESS_KEY = "your-aws-secret-access-key"
AWS_STORAGE_BUCKET_NAME = "your-aws-bucket-name"
AWS_S3_REGION_NAME = "your-aws-region"  # e.g., 'us-east-1'

# Additional production-specific settings can be added below
