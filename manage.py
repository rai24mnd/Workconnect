#!/usr/bin/env python
"""Ejecutar comandos de Django: migrate, check, runserver, entre otros."""
import os
import sys

def main():
    """Cargar settings.py y entregar a Django el comando escrito en la terminal."""
    # setdefault usa esta configuración si no se indicó otra mediante el entorno.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workconnect.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
