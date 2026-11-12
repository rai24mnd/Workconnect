"""Configuración de Django: aplicaciones, seguridad, plantillas y SQLite local."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


# BASE_DIR es la carpeta que contiene manage.py, las plantillas y SQLite.
BASE_DIR = Path(__file__).resolve().parent.parent

# La clave firma las sesiones. El entorno tiene prioridad sobre el archivo .env.
# Solo leemos .env: nunca lo guardamos ni lo incluimos en Git.
if "SECRET_KEY" not in os.environ:
    archivo_local = BASE_DIR / ".env"
    if archivo_local.is_file():
        for linea in archivo_local.read_text(encoding="utf-8").splitlines():
            nombre, separador, valor = linea.strip().partition("=")
            if separador and nombre.strip() == "SECRET_KEY":
                os.environ["SECRET_KEY"] = valor.strip().strip("\"'")
                break

SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
if not SECRET_KEY:
    raise ImproperlyConfigured("Falta SECRET_KEY: define la variable de entorno o agregala al archivo .env local.")

# DEBUG muestra detalles de errores en desarrollo local; no usar al publicar.
DEBUG = True

ALLOWED_HOSTS = []


# Componentes de Django y nuestra aplicación.

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'workconnectapp',

]

# Se ejecutan en cada petición: sesiones, autenticación y protección CSRF, entre otros.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'workconnect.urls'

# APP_DIRS busca los HTML en la carpeta templates de cada aplicación.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'workconnect.wsgi.application'


# SQLite guarda permanentemente cuentas, preferencias, ofertas y sesiones.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Django rechaza contraseñas demasiado simples o parecidas al nombre de usuario.

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


# Mostrar textos en español de Chile y usar la hora de Santiago.

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Dirección desde la que Django sirve CSS y JavaScript durante el desarrollo.

STATIC_URL = 'static/'

# Cada registro obtiene automáticamente un identificador numérico.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
