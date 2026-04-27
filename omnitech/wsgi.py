"""
WSGI config for OmniTech project.
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnitech.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root='/opt/render/project/repo/staticfiles')
