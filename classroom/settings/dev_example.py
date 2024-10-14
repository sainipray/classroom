# settings/dev_example.py

from .base import *

# ---------------------------------------------------------------------
# Development-Specific Settings
# ---------------------------------------------------------------------

# Debug mode should be enabled in development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Secret key for development (should be unique and kept secret)
SECRET_KEY = "your-development-secret-key"

# Database configuration for development (using PostgreSQL as in base.py)
# You can change this to use SQLite if preferred
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": 'db_name',          # Change to your development DB name
        "USER": 'db_user',          # Change to your development DB user
        "PASSWORD": 'db_password',    # Change to your development DB password
        "HOST": 'localhost',
        "PORT": '5432',
    }
}

# Email backend for development (prints emails to the console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Additional development-specific settings can be added below
