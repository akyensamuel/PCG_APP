"""
WSGI config for PCG_APP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCG_APP.settings')

# Collect static files on startup for production
import django
from django.conf import settings
django.setup()

if not settings.DEBUG:
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    except Exception:
        pass  # Ignore errors during static collection

application = get_wsgi_application()

# Vercel serverless function entry point
app = application
handler = application
