"""
Django settings for epl_twitter project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epl_twitter.settings")
print BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v=po_=-hmon7$xl=$)80i5r2ty14e=eu12!gmy@h$rvt5r-2%u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

DEFAULT_CHARSET = 'utf-8'

# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'mvc',
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

ROOT_URLCONF = 'mvc.urls'

WSGI_APPLICATION = 'epl_twitter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
	os.path.join(BASE_DIR, 'templates'),
)

DATE_INPUT_FORMATS = (
	'%Y-%m-%d', '%m/%d/%Y', # '2006-10-25', '10/25/2006'
	'%b %d %Y', '%b %d, %Y', # 'Oct 25 2006', 'Oct 25, 2006'
	'%d %b %Y', '%d %b, %Y', # '25 Oct 2006', '25 Oct, 2006'
	'%B %d %Y', '%B %d, %Y', # 'October 25 2006', 'October 25, 2006'
	'%d %B %Y', '%d %B, %Y', # '25 October 2006', '25 October, 2006'
	'%m/%d/%y' #'10/25/06'
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'

STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'assets/images'),
	os.path.join(BASE_DIR, 'assets/stylesheets'),
	os.path.join(BASE_DIR, 'assets/js'),
	os.path.join(BASE_DIR, '../data/streaming_data')
)

STATIC_ROOT = os.path.join(BASE_DIR, 'assets/admin_files')
