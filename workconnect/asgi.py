"""Punto de entrada para servidores compatibles con ASGI."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workconnect.settings')

# El servidor entrega las peticiones a esta aplicación Django.
application = get_asgi_application()
