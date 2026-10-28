from django.shortcuts import render

from .forms import PerfilForm
from .services import catalogo_general, recomendar


def index(request):
    formulario = PerfilForm(request.POST if request.method == "POST" else None)
    recomendaciones = []
    procesado = False
    volver_catalogo = request.method == "POST" and request.POST.get("accion") == "catalogo"
    validar = request.method == "POST" and not volver_catalogo
    if validar and formulario.is_valid():
        recomendaciones = recomendar(formulario.cleaned_data)
        procesado = True
    return render(request, "workconnectapp/index.html", {
        "formulario": formulario,
        "recomendaciones": recomendaciones,
        "procesado": procesado,
        "oportunidades": recomendaciones if procesado else catalogo_general(),
        "panel_abierto": request.method == "POST" and not volver_catalogo,
        "mostrar_errores": validar,
    })
