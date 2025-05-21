"""
ASGI config for davis_exporter project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'davis_exporter.settings')

application = get_asgi_application() 