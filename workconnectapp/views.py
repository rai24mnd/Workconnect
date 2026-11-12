"""Vistas de cuentas, preferencias y catálogo: reciben la petición y preparan el HTML."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST

from .datos import DIAS, ESTUDIOS, INTERESES
from .forms import BusquedaForm, InicioSesionForm, PerfilForm, RegistroForm
from .adaptadores import obtener_ofertas
from .models import Cuenta, DisponibilidadJoven, Interes, PerfilEmpresa, PerfilJoven, TipoCuenta
from .permisos import acceso_denegado, cuenta_del_usuario, tipo_cuenta_requerido
from .services import clasificar_recomendaciones, evaluar_horario, evaluar_oferta, presentar


def redirigir_por_cuenta(request):
    """Después del login, abrir el catálogo joven o el panel de su empresa."""
    cuenta = cuenta_del_usuario(request.user)
    if cuenta is None:
        return acceso_denegado(request, "Tu cuenta no tiene un tipo de usuario asignado.")
    if cuenta.tipo == TipoCuenta.EMPRESA:
        return redirect("panel_empresa")
    if cuenta.tipo == TipoCuenta.JOVEN:
        return redirect("index")
    return acceso_denegado(request, "Tu cuenta no tiene un tipo de usuario válido.")


@sensitive_post_parameters("password1", "password2")
@require_http_methods(["GET", "POST"])
def registro(request):
    """Validar el POST y crear usuario, cuenta y perfil juntos, o no guardar nada."""
    if request.user.is_authenticated:
        return redirigir_por_cuenta(request)
    es_envio = request.method == "POST"
    tipo = request.POST.get("tipo") if es_envio else request.GET.get("tipo")
    tipo = tipo if tipo in TipoCuenta.values else ""
    formulario = RegistroForm(request.POST if es_envio else None, initial={"tipo": tipo})
    formulario_perfil = PerfilForm(request.POST if es_envio and tipo == TipoCuenta.JOVEN else None)
    cuenta_valida = False
    preferencias_validas = True
    if es_envio:
        # is_valid() convierte y valida los campos; cleaned_data contiene lo aceptado.
        cuenta_valida = formulario.is_valid()
        if tipo == TipoCuenta.JOVEN:
            preferencias_validas = formulario_perfil.is_valid()
    if es_envio and cuenta_valida and preferencias_validas:
        try:
            with transaction.atomic():
                # UserCreationForm guarda un hash de la contraseña mediante Django.
                usuario = formulario.save()
                cuenta = Cuenta(usuario=usuario, tipo=formulario.cleaned_data["tipo"])
                cuenta.full_clean()
                cuenta.save()
                if cuenta.tipo == TipoCuenta.JOVEN:
                    guardar_preferencias(PerfilJoven(cuenta=cuenta), formulario_perfil.cleaned_data)
                else:
                    perfil = PerfilEmpresa(cuenta=cuenta)
                    perfil.full_clean()
                    perfil.save()
        except (ValidationError, IntegrityError):
            formulario.add_error(None, "No pudimos completar el registro. Revisa los datos e inténtalo nuevamente.")
        else:
            messages.success(request, "Tu cuenta fue creada. Ya puedes iniciar sesión.")
            return redirect("iniciar_sesion")
    return render(request, "workconnectapp/registro.html", {
        "formulario": formulario,
        "formulario_perfil": formulario_perfil,
        "tipo_seleccionado": tipo,
        "mostrar_formulario": bool(tipo) or es_envio,
        "mostrar_preferencias": tipo == TipoCuenta.JOVEN,
        "mostrar_errores": es_envio,
    })


@sensitive_post_parameters("password")
@require_http_methods(["GET", "POST"])
def iniciar_sesion(request):
    """Django comprueba las credenciales y asocia el usuario a su sesión."""
    if request.user.is_authenticated:
        return redirigir_por_cuenta(request)
    formulario = InicioSesionForm(request=request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and formulario.is_valid():
        login(request, formulario.get_user())
        return redirigir_por_cuenta(request)
    return render(request, "workconnectapp/iniciar_sesion.html", {"formulario": formulario})


@require_POST
def cerrar_sesion(request):
    # Solo acepta POST para que un enlace externo no cierre la sesión del usuario.
    logout(request)
    return redirect("iniciar_sesion")


@tipo_cuenta_requerido(TipoCuenta.JOVEN)
@require_http_methods(["GET"])
def mi_perfil(request):
    """Consultar el perfil autorizado y sus relaciones para mostrarlos en HTML."""
    # filter limita la consulta; first devuelve el perfil o None si no existe.
    perfil = PerfilJoven.objects.filter(cuenta__usuario=request.user).prefetch_related("intereses", "disponibilidad").first()
    if perfil is None:
        return acceso_denegado(request, "Tu cuenta no tiene un perfil de joven asociado.")
    bloques = {bloque.dia: bloque for bloque in perfil.disponibilidad.all()}
    filas = []
    for dia, nombre in DIAS:
        bloque = bloques.get(dia)
        filas.append({
            "nombre": nombre,
            "inicio": bloque.inicio if bloque else None,
            "fin": bloque.fin if bloque else None,
        })
    # render combina los datos de este diccionario con la plantilla indicada.
    return render(request, "workconnectapp/perfil_joven.html", {
        "perfil": perfil, "filas_disponibilidad": filas,
    })


@tipo_cuenta_requerido(TipoCuenta.JOVEN)
@require_http_methods(["GET", "POST"])
def mis_preferencias(request):
    """Mostrar los valores guardados o validar y guardar los cambios enviados."""
    perfil = PerfilJoven.objects.filter(cuenta__usuario=request.user).first()
    if perfil is None:
        return acceso_denegado(request, "Tu cuenta no tiene un perfil de joven asociado.")
    formulario = PerfilForm(
        request.POST if request.method == "POST" else None,
        initial=datos_del_perfil(perfil),
    )
    if request.method == "POST" and formulario.is_valid():
        try:
            guardar_preferencias(perfil, formulario.cleaned_data)
        except (ValidationError, IntegrityError):
            formulario.add_error(None, "No se pudieron guardar los cambios. Tus preferencias anteriores se conservaron.")
        else:
            messages.success(request, "Tus preferencias quedaron guardadas.")
            if request.POST.get("accion") == "guardar_recomendar":
                return redirect("recomendaciones_guardadas")
            return redirect("mis_preferencias")
    return render(request, "workconnectapp/mis_preferencias.html", {
        "formulario": formulario,
        "mostrar_errores": request.method == "POST",
    })


@tipo_cuenta_requerido(TipoCuenta.JOVEN)
@require_http_methods(["GET"])
def recomendaciones_guardadas(request):
    """Evaluar únicamente las preferencias persistentes, sin usar filtros temporales."""
    perfil = PerfilJoven.objects.filter(cuenta__usuario=request.user).first()
    if perfil is None:
        return acceso_denegado(request, "Tu cuenta no tiene un perfil de joven asociado.")
    formulario = PerfilForm(datos_del_perfil(perfil))
    if not formulario.is_valid():
        messages.info(request, "Completa y guarda tus preferencias antes de consultar tus recomendaciones.")
        return redirect("mis_preferencias")
    clasificacion = clasificar_recomendaciones(formulario.cleaned_data)
    resultados = clasificacion["compatibles"]
    return render(request, "workconnectapp/index.html", {
        "oportunidades": resultados,
        "recomendaciones": resultados,
        "pendientes": clasificacion["pendientes"],
        "procesado": True,
    })


@login_required(login_url="iniciar_sesion")
@require_http_methods(["GET"])
def index(request):
    """Consultar el catálogo con filtros de la URL y mostrar sus tarjetas."""
    cuenta = cuenta_del_usuario(request.user)
    if cuenta is None:
        return acceso_denegado(request, "Tu cuenta no tiene un tipo de usuario asignado.")
    if cuenta.tipo == TipoCuenta.EMPRESA:
        return redirect("panel_empresa")
    if cuenta.tipo != TipoCuenta.JOVEN:
        return acceso_denegado(request, "Tu cuenta no tiene un tipo de usuario válido.")
    perfil = PerfilJoven.objects.filter(cuenta=cuenta).first()
    if perfil is None:
        return acceso_denegado(request, "Tu cuenta no tiene un perfil de joven asociado.")
    formulario = BusquedaForm(request.GET)
    preferencias = PerfilForm(datos_del_perfil(perfil))
    perfil_valido = preferencias.is_valid()
    valido = formulario.is_valid()
    # Copiamos GET para preparar enlaces que quiten el texto o los filtros.
    sin_busqueda = request.GET.copy()
    sin_busqueda.pop("q", None)
    solo_busqueda = request.GET.copy()
    for clave in list(solo_busqueda):
        if clave != "q":
            solo_busqueda.pop(clave)
    oportunidades = []
    if valido:
        perfil_guardado = preferencias.cleaned_data if perfil_valido else None
        oportunidades = buscar_ofertas(formulario.cleaned_data, perfil_guardado)
    busqueda_activa = False
    filtros_abiertos = not valido
    for clave, valores in request.GET.lists():
        if any(valores):
            busqueda_activa = True
            if clave != "q":
                filtros_abiertos = True
    return render(request, "workconnectapp/index.html", {
        "oportunidades": oportunidades,
        "procesado": False,
        "busqueda_form": formulario,
        "busqueda_activa": busqueda_activa,
        "filtros_abiertos": filtros_abiertos,
        "sin_busqueda": sin_busqueda.urlencode(),
        "solo_busqueda": solo_busqueda.urlencode(),
        "perfil_evaluado": perfil_valido,
    })


# Leer o guardar preferencias son dos pasos distintos de consultar el catálogo.
def datos_del_perfil(perfil):
    """Convertir un perfil y sus horarios a los campos que entiende PerfilForm."""
    datos = {
        "comuna": perfil.comuna,
        "edad": perfil.edad,
        "experiencia": perfil.experiencia,
        "estudios": perfil.estudios,
        "intereses": list(perfil.intereses.values_list("codigo", flat=True)),
        "sin_experiencia": perfil.sin_experiencia,
    }
    for bloque in perfil.disponibilidad.all():
        datos[f"{bloque.dia}_disponible"] = True
        datos[f"{bloque.dia}_inicio"] = bloque.inicio
        datos[f"{bloque.dia}_fin"] = bloque.fin
    return datos


@transaction.atomic
def guardar_preferencias(perfil, datos):
    """Recibir únicamente cleaned_data de PerfilForm; guardar todo o nada."""
    # atomic revierte todos los cambios si falla un interés o un bloque horario.
    for campo in ("comuna", "edad", "experiencia", "estudios", "sin_experiencia"):
        setattr(perfil, campo, datos[campo])
    perfil.full_clean()  # Comprobar las reglas del modelo antes de escribir en SQLite.
    perfil.save()

    intereses = []
    nombres = dict(INTERESES)
    for codigo in datos["intereses"]:
        interes, _ = Interes.objects.get_or_create(codigo=codigo, defaults={"nombre": nombres[codigo]})
        interes.full_clean()
        intereses.append(interes)
    perfil.intereses.set(intereses)  # Actualizar la relación de varios intereses.

    perfil.disponibilidad.all().delete()
    for dia, intervalos in datos["disponibilidad"].items():
        for inicio, fin in intervalos:
            bloque = DisponibilidadJoven(perfil=perfil, dia=dia, inicio=inicio, fin=fin)
            bloque.full_clean()
            bloque.save()


# Estos filtros reciben GET y nunca guardan datos del joven.
def buscar_ofertas(filtros, perfil=None):
    """Devolver ofertas que cumplen los filtros, sin cambiar las preferencias."""
    resultados = []
    niveles = [codigo for codigo, _ in ESTUDIOS]
    texto = filtros.get("q", "").casefold()
    for oferta in obtener_ofertas():
        # casefold también cubre mayúsculas acentuadas, que SQLite LIKE no cubre.
        titulo = oferta["titulo"].casefold()
        descripcion = oferta["descripcion"].casefold()
        if texto and texto not in titulo and texto not in descripcion:
            continue
        if filtros.get("comuna") and oferta["comuna"] != filtros["comuna"]:
            continue
        modalidad = filtros.get("modalidad")
        if modalidad and oferta["remota"] is not (modalidad == "remota"):
            continue
        estado = filtros.get("experiencia_estado")
        if estado and oferta["experiencia_estado"] != estado:
            continue
        if filtros.get("sin_experiencia") and oferta["experiencia_estado"] != "no_requerido":
            continue
        maximo = filtros.get("experiencia")
        if maximo is not None and (oferta["experiencia_min"] is None or oferta["experiencia_min"] > maximo):
            continue
        estudios = filtros.get("estudios")
        if estudios and oferta["estudios_estado"] != "no_requerido":
            minimo = oferta["estudios_min"]
            if oferta["estudios_estado"] != "especifico" or minimo not in niveles or niveles.index(minimo) > niveles.index(estudios):
                continue
        if filtros.get("intereses") and not set(filtros["intereses"]).intersection(oferta["intereses"]):
            continue
        if filtros.get("disponibilidad") and evaluar_horario(oferta, filtros["disponibilidad"])[0] != "compatible":
            continue
        # Las etiquetas usan el perfil guardado; los filtros solo acotan la lista.
        if perfil is None:
            resultados.append(presentar(oferta))
        else:
            resultados.append(evaluar_oferta(oferta, perfil))
    return resultados
