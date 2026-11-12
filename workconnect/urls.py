"""Rutas generales: administración de Django y páginas de WorkConnect."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # include continúa la búsqueda de la ruta en los urls de nuestra aplicación.
    path('', include('workconnectapp.urls')),
]
