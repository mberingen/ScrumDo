# -*- coding: utf-8 -*-

# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2011 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

# Django settings for code project.


# Import all
import sys
import os.path
import posixpath
import pinax
import logging


PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

scrumdo_apps = os.path.join(PROJECT_ROOT, 'apps')
sys.path.append(scrumdo_apps)

pinax_apps = os.path.join(PROJECT_ROOT, 'pinax_apps')
sys.path.append(pinax_apps)

pinax_extra_apps = os.path.join(pinax_apps, 'pinax', 'apps')
sys.path.append(pinax_extra_apps)

# tells Pinax to use the default theme
PINAX_THEME = 'default'

# An extra path to look for scrumdo extras on.
EXTRA_PATH = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = ''       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
# Set to empty string for localhost. Not used with sqlite3.
DATABASE_HOST = ''
# Set to empty string for default. Not used with sqlite3.
DATABASE_PORT = '5432'

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/media/'

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/site_media/static/'
SSL_STATIC_URL = '/site_media/static/'

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('scrumdo-web', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'cl@#$@#!%$^!42164363246y@18*^@-!+$fu^q!sa6yh2^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

AVATAR_DEFAULT_URL = STATIC_URL + 'images/defaultAvatar.png'
AVATAR_GRAVATAR_BACKUP = True


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'gadjo.requestprovider.middleware.RequestProvider',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
    "pinax.core.context_processors.pinax_settings",
    "projects.context_processors.projects_constants",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.openid",
    "account.context_processors.account",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.admin',
    'django.contrib.messages',

    'pinax.templatetags',

    # external
    'django_openid',
    'emailconfirmation',
    'mailer',
    'announcements',
    'pagination',
    'timezones',
    'avatar',
    'threadedcomments',
    'ajax_validation',
    'tagging',
    'uni_form',
    'wiki',
    'django_sorting',
    'attachments',
    'django_markup',
    'django_filters',
    'staticfiles',
    'notification',
    # 'tastypie',

    # internal (for now)
    'basic_profiles',
    'account',
    'signup_codes',
    'about',
    'tag_app',
    'tagging_utils',
    'threadedcomments_extras',
    'groups',
    'projects',
    'organizations',
    'topics',
    'activities',
    'django_extensions',
    'django_evolution',
    'extras',
    'activities',
    'tutorial',
    'api',
    'developer',
    'haystack',
    'favorites',
    'scrum_log',
)

HAYSTACK_SITECONF = "search_sites"
HAYSTACK_SEARCH_ENGINE = "solr"
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr'


ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

AUTH_PROFILE_MODULE = 'basic_profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = False

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

SITE_NAME = "ScrumDo Community Site"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "projects.views.home"


EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = '25'

CONTACT_EMAIL = "help@example.com"
DEFAULT_FROM_EMAIL = 'noreply@example.com'
SERVER_EMAIL = 'noreply@example.com'
SUPPORT_URL = "http://support.example.com/"

GOOGLE_ANALYTICS = False
GOOGLE_ANALYTICS_ACCOUNT = ""

CACHE_BACKEND = 'locmem://'

INTERNAL_IPS = ('127.0.0.1',)

BASE_URL = "http://127.0.0.1:8000"
SSL_BASE_URL = "http://127.0.0.1:8000"

SCRUMDO_EXTRAS = ()
 #"extras.plugins.github_issues.GitHubIssuesExtra",
 #                 "extras.plugins.example.ExampleExtra",)


HOOKBOX_HOST = "http://192.168.1.125:8080"
HOOKBOX_SECRET = "juy789"

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError as e:
    print "Could not import local_settings %s" % e


if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
