"""
WSGI config for library_platform project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_platform.settings')

application = get_wsgi_application()