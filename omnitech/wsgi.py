"""
WSGI config for OmniTech project.
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnitech.settings')

application = get_wsgi_application()

try:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base, 'staticfiles')
    application = WhiteNoise(application, root=static_root, prefix='static/')
except Exception:
    pass