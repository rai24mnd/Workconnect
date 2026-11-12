"""Leer ofertas y sus relaciones de Django para las tarjetas y el recomendador."""

from django.core.exceptions import ValidationError

from .datos import INTERESES
from .models import EstadoRequisito, ModalidadHorario, ModalidadLaboral, Oferta, TipoCuenta, TipoOferta
from .validaciones import validar_horarios_oferta


def hora_texto(hora):
    # Conservar HH:MM en las demos sin truncar segundos de otras ofertas.
    if hora.second == 0 and hora.microsecond == 0:
        return hora.isoformat(timespec="minutes")
    return hora.isoformat()


def adaptar_oferta(oferta):
    """Recibe una Oferta de Django y devuelve un diccionario sin guardar cambios."""
    alternativas = []
    grupos = []
    # .all() lee los registros relacionados: opciones de horario y bloques de cada opción.
    for alternativa in oferta.alternativas.all():
        bloques = []
        horarios_texto = []
        for bloque in sorted(alternativa.bloques.all(), key=lambda bloque: bloque.pk):
            bloques.append({"dia": bloque.dia, "inicio": bloque.inicio, "fin": bloque.fin})
            horarios_texto.append({
                "dia": bloque.dia,
                "inicio": hora_texto(bloque.inicio),
                "fin": hora_texto(bloque.fin),
            })
        # Conservamos horas reales para validar y textos para mostrar y comparar después.
        alternativas.append(bloques)
        grupos.append({"numero": alternativa.orden, "horarios": horarios_texto})
    try:
        validar_horarios_oferta(oferta.modalidad_horario, alternativas)
        horario_valido = True
    except ValidationError:
        horario_valido = False

    # Solo el horario fijo tiene una lista única de bloques obligatorios.
    # Las demás opciones permanecen separadas en grupos; nunca mezclamos sus días.
    horarios = []
    if horario_valido and oferta.modalidad_horario == ModalidadHorario.FIJO:
        for bloque in grupos[0]["horarios"]:
            horarios.append(bloque.copy())

    experiencia_min = oferta.experiencia_min
    if oferta.experiencia_estado == EstadoRequisito.NO_REQUERIDO:
        experiencia_min = 0
    estudios_min = oferta.estudios_min
    if oferta.estudios_estado == EstadoRequisito.NO_REQUERIDO:
        estudios_min = None

    empresa_valida = oferta.empresa_id is None or oferta.empresa.cuenta.tipo == TipoCuenta.EMPRESA
    # Mantiene el orden de las opciones del formulario y agrega al final códigos antiguos.
    orden_intereses = {codigo: posicion for posicion, (codigo, _) in enumerate(INTERESES)}
    intereses = sorted(
        oferta.intereses.all(),
        key=lambda interes: (orden_intereses.get(interes.codigo, len(orden_intereses)), interes.codigo),
    )
    tipos = {TipoOferta.EMPLEO: "Empleo", TipoOferta.PRACTICA: "Pasantía", TipoOferta.CURSO: "Curso"}
    return {
        "id": oferta.pk,
        "codigo_demo": oferta.codigo_demo,
        "es_demo": oferta.es_demo,
        "titulo": oferta.titulo,
        "tipo": tipos[oferta.tipo],
        "descripcion": oferta.descripcion,
        "remuneracion_estado": oferta.remuneracion_estado,
        "remuneracion_monto": oferta.remuneracion_monto,
        "remuneracion_periodo": oferta.remuneracion_periodo,
        "remuneracion_texto": oferta.remuneracion_texto,
        "comuna": oferta.comuna,
        "remota": (oferta.modalidad_laboral == ModalidadLaboral.REMOTA
                   if oferta.modalidad_laboral else None),
        "modalidad_laboral_texto": oferta.get_modalidad_laboral_display() or "Modalidad por confirmar",
        "edad_min": oferta.edad_min,
        "experiencia_min": experiencia_min,
        "experiencia_estado": oferta.experiencia_estado,
        "experiencia_estado_texto": oferta.get_experiencia_estado_display(),
        "estudios_min": estudios_min,
        "estudios_estado": oferta.estudios_estado,
        "estudios_estado_texto": oferta.get_estudios_estado_display(),
        "estudios_min_texto": oferta.get_estudios_min_display(),
        "intereses": [interes.codigo for interes in intereses],
        "intereses_nombres": {interes.codigo: interes.nombre for interes in intereses},
        "horarios": horarios,
        "alternativas": grupos,
        "horario_valido": horario_valido,
        "modalidad_horario": oferta.modalidad_horario,
        "modalidad_horario_texto": oferta.get_modalidad_horario_display(),
        "descripcion_horario": oferta.descripcion_horario,
        "empresa_valida": empresa_valida,
        "contacto": {
            "empresa": oferta.empresa.nombre if oferta.empresa_id else oferta.empresa_demo,
            "persona": oferta.contacto_nombre,
            "email": oferta.contacto_email,
            "telefono": oferta.contacto_telefono,
            "url": oferta.url_postulacion,
            "instrucciones": oferta.instrucciones_postulacion,
        },
    }


def obtener_ofertas():
    """Consulta empleos y prácticas guardados; devuelve sus diccionarios sin escribir datos."""
    # filter excluye cursos. Las relaciones se consultan juntas para no repetir lecturas.
    # order_by fija el orden del catálogo; pk es el identificador de cada registro.
    ofertas = (
        Oferta.objects.select_related("empresa__cuenta")
        .filter(tipo__in=[TipoOferta.EMPLEO, TipoOferta.PRACTICA])
        .prefetch_related("intereses", "alternativas__bloques")
        .order_by("pk")
    )
    return [adaptar_oferta(oferta) for oferta in ofertas]
