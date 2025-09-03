"""
WSGI config for PCG_APP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCG_APP.settings')

application = get_wsgi_application()

# Vercel expects the WSGI app to be named 'app' or 'handler'
app = application
handler = application
