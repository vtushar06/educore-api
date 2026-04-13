"""
Development settings — SQLite, debug toolbar, relaxed security.
"""
from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Use SQLite for local dev without Postgres
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = ()  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405

# Allow all CORS origins in dev
CORS_ALLOW_ALL_ORIGINS = True

# Email to console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
