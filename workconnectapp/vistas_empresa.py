"""Perfil y publicaciones de la empresa autenticada, con propiedad comprobada."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EditorHorarios, OfertaForm, PerfilEmpresaForm
from .models import AlternativaHorario, HorarioOferta, Oferta, PerfilEmpresa, TipoCuenta
from .permisos import tipo_cuenta_requerido


@tipo_cuenta_requerido(TipoCuenta.EMPRESA)
@require_http_methods(["GET"])
def panel_empresa(request):
    """Muestra únicamente las publicaciones de la empresa que inició sesión."""
    empresa = get_object_or_404(PerfilEmpresa, cuenta__usuario=request.user)
    return render(request, "workconnectapp/panel_empresa.html", {
        "empresa": empresa,
        "ofertas": empresa.ofertas.filter(es_demo=False).order_by("-pk"),
    })


@tipo_cuenta_requerido(TipoCuenta.EMPRESA)
@require_http_methods(["GET", "POST"])
def perfil_empresa(request):
    """Recibe los datos del perfil, los valida y los guarda si están completos."""
    empresa = get_object_or_404(PerfilEmpresa, cuenta__usuario=request.user)
    # GET precarga el perfil. POST recibe lo escrito y conserva los errores para mostrarlos.
    formulario = PerfilEmpresaForm(request.POST if request.method == "POST" else None, instance=empresa)
    if request.method == "POST" and formulario.is_valid():
        try:
            with transaction.atomic():
                # commit=False permite comprobar el modelo antes de escribir en la base.
                empresa = formulario.save(commit=False)
                empresa.full_clean()
                empresa.save()
        except (ValidationError, IntegrityError):
            formulario.add_error(None, "No se pudieron guardar los cambios. El perfil anterior se conserva.")
        else:
            messages.success(request, "El perfil empresarial quedó guardado.")
            return redirect("panel_empresa")
    return render(request, "workconnectapp/perfil_empresa.html", {"formulario": formulario})


@tipo_cuenta_requerido(TipoCuenta.EMPRESA)
@require_http_methods(["GET", "POST"])
def formulario_oferta(request, pk=None):
    """Publica o edita una oferta con sus horarios; pk identifica una oferta existente."""
    empresa = get_object_or_404(PerfilEmpresa, cuenta__usuario=request.user)
    if pk is None:
        oferta = Oferta(empresa=empresa, es_demo=False, codigo_demo=None)
    else:
        # La consulta incluye la propietaria: conocer el ID de otra oferta no permite editarla.
        oferta = get_object_or_404(Oferta, pk=pk, empresa=empresa, es_demo=False)
    if not empresa.nombre.strip() or not empresa.comuna or not (empresa.email or empresa.telefono):
        messages.info(request, "Completa el nombre, comuna y contacto público de tu empresa antes de publicar.")
        return redirect("perfil_empresa")
    datos = request.POST if request.method == "POST" else None
    # Un formulario valida los datos de la oferta y el editor comprueba todos sus horarios.
    editor = EditorHorarios(datos, oferta)
    formulario = OfertaForm(datos, instance=oferta)
    if request.method == "POST":
        formulario_valido = formulario.is_valid()
        horarios_validos = editor.is_valid(formulario.cleaned_data.get("modalidad_horario"))
        if formulario_valido and horarios_validos:
            try:
                guardar_oferta(formulario, editor.bloques)
            except (ValidationError, IntegrityError):
                formulario.add_error(None, "No se pudo guardar la oferta. La publicación anterior se conserva.")
            else:
                messages.success(request, "La oferta quedó guardada.")
                return redirect("panel_empresa")
    return render(request, "workconnectapp/formulario_oferta.html", {
        "formulario": formulario, "editor": editor, "editando": pk is not None,
    })


@tipo_cuenta_requerido(TipoCuenta.EMPRESA)
@require_http_methods(["GET", "POST"])
def eliminar_oferta(request, pk):
    """GET pide confirmación; POST elimina una publicación de esta empresa."""
    empresa = get_object_or_404(PerfilEmpresa, cuenta__usuario=request.user)
    oferta = get_object_or_404(Oferta, pk=pk, empresa=empresa, es_demo=False)
    if request.method == "POST":
        with transaction.atomic():
            oferta.delete()
        messages.success(request, "La oferta fue eliminada.")
        return redirect("panel_empresa")
    return render(request, "workconnectapp/eliminar_oferta.html", {"oferta": oferta})


@transaction.atomic
def guardar_oferta(formulario, bloques):
    """Guarda el formulario validado y sus alternativas; devuelve la oferta.

    atomic revierte todos los cambios si falla una parte, incluso al editar.
    Así no quedan ofertas sin sus intereses o con horarios guardados a medias.
    """
    oferta = formulario.save(commit=False)
    oferta.full_clean()
    oferta.save()
    # Los intereses son una relación de varios a varios: se guardan después de la oferta.
    formulario.save_m2m()
    # Reemplazamos los horarios anteriores dentro de la misma transacción.
    oferta.alternativas.all().delete()
    for orden, alternativa in enumerate(bloques, start=1):
        grupo = AlternativaHorario(oferta=oferta, orden=orden)
        grupo.full_clean()
        grupo.save()
        for datos in alternativa:
            bloque = HorarioOferta(alternativa=grupo, **datos)
            bloque.full_clean()
            bloque.save()
    oferta.validar_publicacion()
    return oferta
