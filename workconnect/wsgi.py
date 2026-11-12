"""Punto de entrada para servidores compatibles con WSGI."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workconnect.settings')

# El servidor entrega las peticiones a esta aplicación Django.
application = get_wsgi_application()
