"""
Production settings — Postgres, strict security, no debug.
"""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

# Allow Render hostnames securely
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Security hardening
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True") == "True"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

import dj_database_url

db_from_env = dj_database_url.config(
    default=os.environ.get("DATABASE_URL"),
    conn_max_age=500,
    ssl_require=False  # Render manages SSL internally via their VPC network
)

if db_from_env:
    DATABASES["default"].update(db_from_env)
