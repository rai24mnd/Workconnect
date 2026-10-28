"""Reglas de demostración. Recibe un perfil validado y no guarda datos."""

from datetime import time

from .datos import COMUNAS, DIAS, ESTUDIOS, INTERESES, OPORTUNIDADES


def bloques_validos(oferta):
    """No suponemos horarios: un dato ausente o incorrecto invalida la agenda."""
    bloques = oferta.get("horarios")
    if not isinstance(bloques, list) or not bloques:
        return False
    for bloque in bloques:
        try:
            if bloque["dia"] not in dict(DIAS):
                return False
            inicio = time.fromisoformat(bloque["inicio"])
            fin = time.fromisoformat(bloque["fin"])
            if inicio.tzinfo is not None or fin.tzinfo is not None or inicio >= fin:
                return False
        except (KeyError, TypeError, ValueError):
            return False
    return True


def horario_compatible(oferta, disponibilidad):
    """Cada bloque obligatorio debe caber completo en un intervalo de ese día."""
    if not bloques_validos(oferta):
        return False
    for bloque in oferta["horarios"]:
        inicio = time.fromisoformat(bloque["inicio"])
        fin = time.fromisoformat(bloque["fin"])
        intervalos = disponibilidad.get(bloque["dia"], [])
        if not any(desde <= inicio and fin <= hasta for desde, hasta in intervalos):
            return False
    return True


def presentar(oferta):
    """Añade etiquetas de pantalla sin modificar los datos originales."""
    horarios = []
    if bloques_validos(oferta):
        horarios = [f"{dict(DIAS)[b['dia']]} {b['inicio']}–{b['fin']}" for b in oferta["horarios"]]
    return {**oferta, "comuna_nombre": dict(COMUNAS)[oferta["comuna"]],
            "horarios_texto": horarios}


def catalogo_general():
    return [presentar(oferta) for oferta in OPORTUNIDADES]


def recomendar(perfil):
    niveles = [clave for clave, etiqueta in ESTUDIOS]
    nombres_intereses = dict(INTERESES)
    resultados = []

    for oferta in OPORTUNIDADES:
        misma_comuna = oferta["comuna"] == perfil["comuna"]
        # Requisitos obligatorios: si alguno falla, se descarta la oferta.
        if not misma_comuna and not oferta["remota"]:
            continue
        if perfil["edad"] < oferta["edad_min"]:
            continue
        if perfil["experiencia"] < oferta["experiencia_min"]:
            continue
        if perfil.get("sin_experiencia") and oferta["experiencia_min"] != 0:
            continue
        if niveles.index(perfil["estudios"]) < niveles.index(oferta["estudios_min"]):
            continue
        if not horario_compatible(oferta, perfil.get("disponibilidad", {})):
            continue

        coincidencias = [interes for interes in oferta["intereses"] if interes in perfil["intereses"]]
        # Afinidad: 2 puntos por interés coincidente, 1 por misma comuna.
        puntos = 2 * len(coincidencias) + int(misma_comuna)
        motivos = [
            "En tu comuna" if misma_comuna else "Modalidad remota: puedes participar desde tu comuna",
            "Horario completo compatible: " + "; ".join(presentar(oferta)["horarios_texto"]),
            "Cumples la edad mínima",
            "Sin experiencia requerida" if oferta["experiencia_min"] == 0 else "Cumples la experiencia mínima requerida",
            "Tu nivel de estudios cumple el mínimo solicitado",
        ]
        if coincidencias:
            motivos.append("Intereses en común: " + ", ".join(nombres_intereses[i] for i in coincidencias))
        else:
            motivos.append("Sin intereses en común; cumple tus requisitos y horarios")

        # Creamos otro diccionario para no modificar el catálogo compartido.
        resultados.append({
            **presentar(oferta), "puntos": puntos, "motivos": motivos,
        })

    # Los empates mantienen el orden del catálogo (identificador ascendente).
    resultados.sort(key=lambda oferta: (-oferta["puntos"], oferta["id"]))
    return resultados
