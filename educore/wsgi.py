"""WSGI config for EduCore API."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "educore.settings.prod")

application = get_wsgi_application()
