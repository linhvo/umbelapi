"""
Django settings for umbelapi project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name, default):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l=t-3hz06-xzc(xgys6hgwn=8q3!xdwqz3o=*m!%kqrxii=^=d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_variable('DJANGO_DEBUG', 'False') == 'True'
LOCAL_DEV = get_env_variable('DJANGO_LOCAL_DEV', 'True') == 'True'

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'umbelapi'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'umbelapi.urls'

WSGI_APPLICATION = 'umbelapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'umbelapi',
        'USER': os.environ.get('USER_NAME'),
        'PASSWORD': os.environ.get('PASSWORD'),
        'HOST': os.environ.get('HOST')
    }
}

if not LOCAL_DEV:
    DATABASES = {
        'default': dj_database_url.config()
    }

os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')

if LOCAL_DEV:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'OPTIONS': {
                'MAX_ENTRIES': 10000
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'BINARY': False,
            'LOCATION': 'localhost:11211',
            'OPTIONS': {
                'no_block': True,
                'tcp_nodelay': True,
                'tcp_keepalive': True,
                'remove_failed': 4,
                'retry_timeout': 2,
                'dead_timeout': 10,
                '_poll_timeout': 2000
            }
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG'
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Catch All Logger -- Captures any other logging
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

BRAND_CACHE_FORMAT_STRING = 'brand_%s'
PROFILE_CACHE_FORMAT_STRING = 'profile_%s'