"""
WSGI config for davis_exporter project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'davis_exporter.settings')

application = get_wsgi_application() 