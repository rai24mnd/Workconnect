from django.shortcuts import render

from .forms import PerfilForm
from .services import recomendar


def index(request):
    formulario = PerfilForm(request.POST if request.method == "POST" else None)
    recomendaciones = []
    procesado = False
    if request.method == "POST" and formulario.is_valid():
        recomendaciones = recomendar(formulario.cleaned_data)
        procesado = True
    return render(request, "workconnectapp/index.html", {
        "formulario": formulario,
        "recomendaciones": recomendaciones,
        "procesado": procesado,
    })
