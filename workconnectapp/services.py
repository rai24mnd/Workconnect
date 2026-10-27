"""Reglas de demostración. Recibe un perfil validado y no guarda datos."""

from .datos import COMUNAS, ESTUDIOS, HORARIOS, INTERESES, OPORTUNIDADES


def recomendar(perfil):
    niveles = [clave for clave, etiqueta in ESTUDIOS]
    nombres_intereses = dict(INTERESES)
    nombres_horarios = dict(HORARIOS)
    resultados = []

    for oferta in OPORTUNIDADES:
        misma_comuna = oferta["comuna"] == perfil["comuna"]
        turnos = [turno for turno in oferta["horarios"] if turno in perfil["horarios"]]
        # Requisitos obligatorios: si alguno falla, se descarta la oferta.
        if not misma_comuna and not oferta["remota"]:
            continue
        if perfil["edad"] < oferta["edad_min"]:
            continue
        if perfil["experiencia"] < oferta["experiencia_min"]:
            continue
        if niveles.index(perfil["estudios"]) < niveles.index(oferta["estudios_min"]):
            continue
        if not turnos:
            continue

        coincidencias = [interes for interes in oferta["intereses"] if interes in perfil["intereses"]]
        # Afinidad: 2 puntos por interés coincidente, 1 por misma comuna.
        puntos = 2 * len(coincidencias) + int(misma_comuna)
        motivos = [
            "En tu comuna" if misma_comuna else "Modalidad remota: puedes participar desde tu comuna",
            "Horario compatible: " + ", ".join(nombres_horarios[turno] for turno in turnos),
            "Cumples la edad mínima y la experiencia requerida",
            "Tu nivel de estudios cumple el mínimo solicitado",
        ]
        if coincidencias:
            motivos.append("Intereses en común: " + ", ".join(nombres_intereses[i] for i in coincidencias))
        else:
            motivos.append("Sin intereses en común; cumple tus requisitos y horarios")

        # Creamos otro diccionario para no modificar el catálogo compartido.
        resultados.append({
            **oferta, "puntos": puntos, "motivos": motivos,
            "comuna_nombre": dict(COMUNAS)[oferta["comuna"]],
        })

    # Los empates mantienen el orden del catálogo (identificador ascendente).
    resultados.sort(key=lambda oferta: (-oferta["puntos"], oferta["id"]))
    return resultados
