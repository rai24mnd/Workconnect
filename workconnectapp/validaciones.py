"""Reglas de horarios compartidas por modelos, formularios y recomendador."""

from datetime import time

from django.core.exceptions import ValidationError

from .datos import DIAS


def validar_bloque_horario(dia, inicio, fin):
    """Recibir un día y dos objetos time; rechazar bloques incompletos."""
    errores = {}
    if dia not in dict(DIAS):
        errores["dia"] = "Selecciona un día válido."
    for nombre, hora in (("inicio", inicio), ("fin", fin)):
        if not isinstance(hora, time) or hora.tzinfo is not None:
            errores[nombre] = "Indica una hora válida, sin zona horaria."
    if not errores and inicio >= fin:
        errores["fin"] = "El inicio debe ser anterior al término, dentro del mismo día."
    if errores:
        raise ValidationError(errores)


def validar_horarios_oferta(modalidad, alternativas):
    """Validar listas de alternativas, cada una con diccionarios de bloques.

    Las horas deben ser objetos time ya convertidos por Django. Esta función
    no guarda datos y también permite validar formularios antes de persistirlos.
    """
    if not isinstance(alternativas, (list, tuple)):
        raise ValidationError("Indica una lista de alternativas de horario.")
    cantidad = len(alternativas)
    if modalidad == "fijo":
        if cantidad != 1:
            raise ValidationError("El horario fijo requiere exactamente una alternativa.")
    elif modalidad == "varias_opciones":
        if cantidad < 2:
            raise ValidationError("Varias opciones requiere al menos dos alternativas completas.")
    elif modalidad == "flexible":
        if cantidad:
            raise ValidationError("El horario flexible no debe tener alternativas ni bloques obligatorios.")
        return
    else:
        raise ValidationError("Selecciona una de las tres modalidades de horario.")

    alternativas_vistas = set()
    for numero, bloques in enumerate(alternativas, start=1):
        if not isinstance(bloques, (list, tuple)) or not bloques:
            raise ValidationError(f"La alternativa {numero} debe tener al menos un bloque.")
        claves = []
        for bloque in bloques:
            if not isinstance(bloque, dict):
                raise ValidationError(f"La alternativa {numero} contiene un bloque inválido.")
            dia, inicio, fin = bloque.get("dia"), bloque.get("inicio"), bloque.get("fin")
            try:
                validar_bloque_horario(dia, inicio, fin)
            except ValidationError as error:
                raise ValidationError(f"Alternativa {numero}: {'; '.join(error.messages)}") from error
            claves.append((dia, inicio, fin))

        # Ordenar por día e inicio permite detectar si dos bloques se superponen.
        claves.sort()
        for anterior, actual in zip(claves, claves[1:]):
            if anterior[0] == actual[0] and actual[1] < anterior[2]:
                raise ValidationError(f"La alternativa {numero} contiene bloques duplicados o superpuestos.")
        # Una tupla permite reconocer dos alternativas completas idénticas.
        firma = tuple(claves)
        if firma in alternativas_vistas:
            raise ValidationError(f"La alternativa {numero} repite otra alternativa completa.")
        alternativas_vistas.add(firma)
