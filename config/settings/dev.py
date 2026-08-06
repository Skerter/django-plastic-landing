from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Emails are printed to the runserver console — no real SMTP needed in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# The rate limit is off in dev — 5/hour gets in the way of testing the form.
# In production (prod.py) the limit stays live.
RATELIMIT_ENABLE = False

# Tests and local dev exercise the real notification path (email to the console),
# so demo mode is forced off here regardless of .env.
DEMO_MODE = False
