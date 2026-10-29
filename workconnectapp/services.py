"""Reglas de demostración. Recibe un perfil validado y no guarda datos."""

from datetime import time

from .datos import COMUNAS, DIAS, ESTUDIOS, INTERESES, OPORTUNIDADES


def bloques_validos(oferta):
    # Recibe una oferta y devuelve True si todos sus bloques horarios son válidos.
    bloques = oferta.get("horarios")  # Horarios obligatorios de la oportunidad.
    if not isinstance(bloques, list) or not bloques:
        return False
    nombres_dias = dict(DIAS)  # Relaciona cada clave de día con su nombre visible.
    for bloque in bloques:
        try:
            if bloque["dia"] not in nombres_dias:
                return False
            inicio = time.fromisoformat(bloque["inicio"])
            fin = time.fromisoformat(bloque["fin"])
            if inicio.tzinfo is not None or fin.tzinfo is not None or inicio >= fin:
                return False
        except (KeyError, TypeError, ValueError):
            return False
    return True


def horario_compatible(oferta, disponibilidad):
    # Recibe una oferta y la disponibilidad; devuelve True si cubre todos los bloques.
    if not bloques_validos(oferta):
        return False
    for bloque in oferta["horarios"]:
        inicio = time.fromisoformat(bloque["inicio"])
        fin = time.fromisoformat(bloque["fin"])
        intervalos = disponibilidad.get(bloque["dia"], [])  # Disponibilidad de ese día.
        bloque_cubierto = False
        for desde, hasta in intervalos:
            if desde <= inicio and fin <= hasta:
                bloque_cubierto = True
                break
        if not bloque_cubierto:
            return False
    return True


def presentar(oferta):
    # Recibe una oferta y devuelve una copia con comuna y horarios para mostrar.
    horarios = []  # Textos de los bloques que aparecerán en la tarjeta.
    if bloques_validos(oferta):
        nombres_dias = dict(DIAS)
        for bloque in oferta["horarios"]:
            nombre_dia = nombres_dias[bloque["dia"]]
            texto_horario = f"{nombre_dia} {bloque['inicio']}–{bloque['fin']}"
            horarios.append(texto_horario)

    nombres_comunas = dict(COMUNAS)
    oferta_presentada = oferta.copy()  # Evita agregar etiquetas al catálogo original.
    oferta_presentada["comuna_nombre"] = nombres_comunas[oferta["comuna"]]
    oferta_presentada["horarios_texto"] = horarios
    return oferta_presentada


def catalogo_general():
    # No recibe argumentos; devuelve las seis oportunidades preparadas para la página.
    catalogo = []
    for oferta in OPORTUNIDADES:
        catalogo.append(presentar(oferta))
    return catalogo


def clave_orden_recomendacion(oferta):
    # Recibe una recomendación y devuelve sus criterios de orden: puntos e identificador.
    # El negativo permite mostrar más puntos primero; los empates usan el menor id.
    return [-oferta["puntos"], oferta["id"]]


def recomendar(perfil):
    # Recibe un perfil validado; filtra, puntúa y devuelve recomendaciones ordenadas.
    niveles = []  # Niveles de estudios ordenados desde el menor al mayor.
    for clave, nombre_nivel in ESTUDIOS:
        niveles.append(clave)
    nombres_intereses = dict(INTERESES)  # Nombres que se muestran en los motivos.
    resultados = []  # Ofertas que cumplen todos los requisitos del perfil.

    for oferta in OPORTUNIDADES:
        misma_comuna = oferta["comuna"] == perfil["comuna"]  # Coincidencia de ubicación.
        # Requisitos obligatorios: si alguno falla, se descarta la oferta.
        if not misma_comuna and not oferta["remota"]:
            continue
        if perfil["edad"] < oferta["edad_min"]:
            continue
        if perfil["experiencia"] < oferta["experiencia_min"]:
            continue
        if perfil.get("sin_experiencia") and oferta["experiencia_min"] != 0:
            continue
        nivel_persona = niveles.index(perfil["estudios"])
        nivel_minimo = niveles.index(oferta["estudios_min"])
        if nivel_persona < nivel_minimo:
            continue
        if not horario_compatible(oferta, perfil.get("disponibilidad", {})):
            continue

        coincidencias = []  # Intereses compartidos entre el perfil y la oferta.
        for interes in oferta["intereses"]:
            if interes in perfil["intereses"]:
                coincidencias.append(interes)
        # Afinidad: 2 puntos por interés coincidente, 1 por misma comuna.
        puntos = 2 * len(coincidencias)
        if misma_comuna:
            puntos += 1

        recomendacion = presentar(oferta)  # Copia preparada para agregar puntos y motivos.
        motivos = []  # Explicaciones que se muestran debajo de cada recomendación.
        if misma_comuna:
            motivos.append("En tu comuna")
        else:
            motivos.append("Modalidad remota: puedes participar desde tu comuna")
        texto_horarios = "; ".join(recomendacion["horarios_texto"])
        motivos.append("Horario completo compatible: " + texto_horarios)
        motivos.append("Cumples la edad mínima")
        if oferta["experiencia_min"] == 0:
            motivos.append("Sin experiencia requerida")
        else:
            motivos.append("Cumples la experiencia mínima requerida")
        motivos.append("Tu nivel de estudios cumple el mínimo solicitado")

        if coincidencias:
            intereses_compartidos = []
            for interes in coincidencias:
                intereses_compartidos.append(nombres_intereses[interes])
            motivos.append("Intereses en común: " + ", ".join(intereses_compartidos))
        else:
            motivos.append("Sin intereses en común; cumple tus requisitos y horarios")

        recomendacion["puntos"] = puntos
        recomendacion["motivos"] = motivos
        resultados.append(recomendacion)

    # Los empates mantienen el orden del catálogo (identificador ascendente).
    resultados.sort(key=clave_orden_recomendacion)
    return resultados
