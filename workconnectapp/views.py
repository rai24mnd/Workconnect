from django.shortcuts import render

from .forms import PerfilForm
from .services import catalogo_general, recomendar


def index(request):
    # Recibe una petición web, prepara los resultados y devuelve la página HTML.
    es_envio = request.method == "POST"  # POST indica que se enviaron preferencias.
    if es_envio:
        formulario = PerfilForm(request.POST)
    else:
        formulario = PerfilForm()

    recomendaciones = []  # Solo se llena cuando el perfil enviado es válido.
    procesado = False  # Indica si se calcularon recomendaciones, aunque sean cero.
    volver_catalogo = es_envio and request.POST.get("accion") == "catalogo"
    validar = es_envio and not volver_catalogo
    if validar and formulario.is_valid():
        recomendaciones = recomendar(formulario.cleaned_data)
        procesado = True

    # La misma lista alimenta las tarjetas del catálogo o de las recomendaciones.
    if procesado:
        oportunidades = recomendaciones
    else:
        oportunidades = catalogo_general()

    contexto = {  # Datos que la plantilla necesita para construir la página.
        "formulario": formulario,
        "recomendaciones": recomendaciones,
        "procesado": procesado,
        "oportunidades": oportunidades,
        "panel_abierto": es_envio and not volver_catalogo,
        "mostrar_errores": validar,
    }
    return render(request, "workconnectapp/index.html", contexto)
