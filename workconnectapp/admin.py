from django.contrib import admin

# Conservamos el modelo heredado que ya se mostraba en el administrador.
from .models import Alumno

admin.site.register(Alumno)
