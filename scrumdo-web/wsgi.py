"""
WSGI config for dotcloud_project project.

This is the config for PRODUCTION. The development config is located
in the dotcloud_project folder inside the project.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
pinax_apps = os.path.join(PROJECT_ROOT, 'pinax_apps')

sys.path.append(pinax_apps)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
