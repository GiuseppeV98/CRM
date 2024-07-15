"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from decouple import config


#   SECRET_KEY = config('DJANGO_SECRET_KEY')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



AUTHENTICATION_BACKENDS = (
    "django_python3_ldap.auth.LDAPBackend", 
    "django.contrib.auth.backends.ModelBackend",
)

# LDAP auth settings.

LDAP_AUTH_URL = ["ldap://192.168.1.2:389"]

LDAP_AUTH_SEARCH_BASE = "dc=corporate,dc=it"

# Initiate TLS on connection.
LDAP_AUTH_USE_TLS = False

# Specify which TLS version to use (Python 3.10 requires TLSv1 or higher)
import ssl
LDAP_AUTH_TLS_VERSION = ssl.PROTOCOL_TLSv1_2



# The LDAP class that represents a user.
LDAP_AUTH_OBJECT_CLASS = "organizationalPerson"

# User model fields mapped to the LDAP
# attributes that represent them.
LDAP_AUTH_USER_FIELDS = {
    "username": "userPrincipalName", #"sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# A tuple of django model fields used to uniquely identify a user.
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

# Path to a callable that takes a dict of {model_field_name: value},
# returning a dict of clean model data.
# Use this to customize how data loaded from LDAP is saved to the User model.
LDAP_AUTH_CLEAN_USER_DATA = "django_python3_ldap.utils.clean_user_data"

# Path to a callable that takes a user model, a dict of {ldap_field_name: [value]}
# a LDAP connection object (to allow further lookups), and saves any additional
# user relationships based on the LDAP data.
# Use this to customize how data loaded from LDAP is saved to User model relations.
# For customizing non-related User model fields, use LDAP_AUTH_CLEAN_USER_DATA.
LDAP_AUTH_SYNC_USER_RELATIONS = "django_python3_ldap.utils.sync_user_relations"

# Path to a callable that takes a dict of {ldap_field_name: value},
# returning a list of [ldap_search_filter]. The search filters will then be AND'd
# together when creating the final search filter.
LDAP_AUTH_FORMAT_SEARCH_FILTERS = "django_python3_ldap.utils.format_search_filters"

# Path to a callable that takes a dict of {model_field_name: value}, and returns
# a string of the username to bind to the LDAP server.
# Use this to support different types of LDAP server.
#LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory"
LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory"

# Sets the login domain for Active Directory users.
#LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = "corporate.it"

# The LDAP username and password of a user for querying the LDAP database for user
# details. If None, then the authenticated user will be used for querying, and
# the `ldap_sync_users`, `ldap_clean_users` commands will perform an anonymous query.
#0LDAP_AUTH_CONNECTION_USERNAME = "TestLdap"
#LDAP_AUTH_CONNECTION_PASSWORD = "T3st@Ld4p"

# Set connection/receive timeouts (in seconds) on the underlying `ldap3` library.
LDAP_AUTH_CONNECT_TIMEOUT = None
LDAP_AUTH_RECEIVE_TIMEOUT = None

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django_python3_ldap": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


INSTALLED_APPS = [
    'dashboard',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'two_factor_auth',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_python3_ldap',
]
    
    
    
# Aggiunge 'user' all'oggetto request
    
    
    
    # Aggiungi qui il tuo middleware personalizzato, dopo 'AuthenticationMiddleware'
    # Assicurati che questo sia dopo 'AuthenticationMiddleware'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'two_factor_auth.middleware.TwoFactorAuthMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"mysite/templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



#import environ
#env = environ.Env()
# Sostituisci '/path/to/your/.env' con il percorso assoluto al tuo file .env
#env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
#environ.Env.read_env(env_file)
#DATABASES = {
#    'default': env.db(),
#}

import environ

# Inizializza django-environ
env = environ.Env()

# Leggi il file .env
env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)


# Imposta la SECRET_KEY leggendo dalla variabile d'ambiente
SECRET_KEY = env('SECRET_KEY')

# Configura il database usando l'URL dal file .env
DATABASES = {
    'default': env.db(),
}
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]  
LOGIN_URL = "two_factor_auth:login"


SITE_NAME = 'MySite'
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'vallarelli39@gmail.com'  # sostituisci con il tuo indirizzo email reale
EMAIL_HOST_PASSWORD = 'vxtmuksqcnpigudm'  # sostituisci con la tua password o password per app
DEFAULT_FROM_EMAIL = 'vallarelli39@gmail.com'