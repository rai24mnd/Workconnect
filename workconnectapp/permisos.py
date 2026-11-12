"""Comprobar autenticación y tipo de cuenta en las vistas privadas."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Cuenta


def acceso_denegado(request, mensaje):
    # El código HTTP 403 señala que la sesión no tiene permiso para esta página.
    return render(request, "workconnectapp/acceso_denegado.html", {"mensaje": mensaje}, status=403)


def cuenta_del_usuario(usuario):
    # first devuelve la cuenta o None; no crea cuentas automáticamente.
    return Cuenta.objects.filter(usuario=usuario).first()


def tipo_cuenta_requerido(tipo):
    """Proteger varias vistas con la misma comprobación de sesión y tipo de cuenta."""
    # El decorador envuelve la vista: comprueba permisos antes de ejecutarla.
    def decorar(vista):
        @wraps(vista)
        def protegida(request, *args, **kwargs):
            cuenta = cuenta_del_usuario(request.user)
            if cuenta is None:
                return acceso_denegado(request, "Tu cuenta no tiene un tipo de usuario asignado.")
            if cuenta.tipo != tipo:
                return acceso_denegado(request, "Tu tipo de cuenta no tiene acceso a esta sección.")
            return vista(request, *args, **kwargs)
        # Django redirige al login a los visitantes antes de consultar su cuenta.
        return login_required(protegida, login_url="iniciar_sesion")
    return decorar
