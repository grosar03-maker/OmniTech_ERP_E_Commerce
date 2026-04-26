"""
OmniTech ERP & E-Commerce
Django Settings Configuration
"""

import os
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-omnitech-dev-key-change-in-production-2026'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'omnitech.apps.OmniTechConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'omnitech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'omnitech.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_NAME = 'OmniTech'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CART_SESSION_KEY = 'carrito'

SUBSIDIO_REGION = 'La Araucanía'
SUBSIDIO_MONTO = Decimal('100000')

RESERVA_TIMEOUT_MINUTES = 15

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'grosar2006@gmail.com'
EMAIL_HOST_PASSWORD = 'jlio nvhr zejx xonz'
EMAIL_FROM = 'OmniTech <noreply@omnitech.cl>'
DEFAULT_FROM_EMAIL = 'OmniTech <noreply@omnitech.cl>'

STRIPE_PUBLIC_KEY = 'pk_test_51TJPnb1Bg6LSaOB5kc6pzah1I2zr9PRE4fJejBbjygAp0fGkMtm3SDzmL1BJ3AGPspYokIk9GS1B40bp5OwkOGV700W4tdXM27'
STRIPE_SECRET_KEY = 'sk_test_51TJPnb1Bg6LSaOB5rKhHA5U5CpYE2a5MLwHaUfVj6r8AjlJUCBwg5p2Esx8V14MFs4HF4AxenH8At0eLtVWkOszf0079aUwPU2'
STRIPE_CURRENCY = 'clp'
