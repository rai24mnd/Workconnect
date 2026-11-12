from django.apps import AppConfig


class WorkconnectappConfig(AppConfig):
    # Django usa este nombre para encontrar los modelos, plantillas y archivos estáticos.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workconnectapp'
