from django.urls import path
from . import views
from . import vistas_empresa

# Cada dirección llama a una vista; name permite enlazarla desde las plantillas.
urlpatterns = [
    path('', views.index, name='index'),
    path('cuentas/registro/', views.registro, name='registro'),
    path('cuentas/ingresar/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cuentas/salir/', views.cerrar_sesion, name='cerrar_sesion'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('empresa/', vistas_empresa.panel_empresa, name='panel_empresa'),
    path('empresa/perfil/', vistas_empresa.perfil_empresa, name='perfil_empresa'),
    path('empresa/ofertas/nueva/', vistas_empresa.formulario_oferta, name='crear_oferta'),
    path('empresa/ofertas/<int:pk>/editar/', vistas_empresa.formulario_oferta, name='editar_oferta'),
    path('empresa/ofertas/<int:pk>/eliminar/', vistas_empresa.eliminar_oferta, name='eliminar_oferta'),
    path('mis-preferencias/', views.mis_preferencias, name='mis_preferencias'),
    path('mis-preferencias/recomendaciones/', views.recomendaciones_guardadas, name='recomendaciones_guardadas'),
]
