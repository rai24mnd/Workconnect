"""Comparar cada oferta con un perfil, calcular afinidad y ordenar resultados.

Los requisitos deciden la compatibilidad. Los intereses solo suman puntos:
no son obligatorios y nunca compensan un requisito incumplido.
"""

from datetime import time

from .adaptadores import obtener_ofertas
from .datos import COMUNAS, DIAS, ESTUDIOS, INTERESES
from .models import EstadoRequisito, ModalidadHorario


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
            # Un intervalo del joven debe cubrir el bloque completo, incluidos sus extremos.
            if desde <= inicio and fin <= hasta:
                bloque_cubierto = True
                break
        if not bloque_cubierto:
            return False
    return True


def presentar(oferta):
    # Recibe una oferta y devuelve una copia con comuna y horarios para mostrar.
    nombres_comunas = dict(COMUNAS)
    oferta_presentada = oferta.copy()  # Evita agregar etiquetas al catálogo original.
    oferta_presentada["comuna_nombre"] = nombres_comunas.get(oferta["comuna"], "Comuna no informada")
    oferta_presentada["horarios_texto"] = presentar_bloques(oferta.get("horarios"))
    oferta_presentada["alternativas"] = []
    for grupo in oferta.get("alternativas", []):
        # Copiamos también cada alternativa para no modificar la oferta al evaluarla.
        alternativa = grupo.copy()
        alternativa["horarios_texto"] = presentar_bloques(grupo["horarios"])
        oferta_presentada["alternativas"].append(alternativa)
    return oferta_presentada


def presentar_bloques(bloques):
    # Convierte bloques válidos en textos para las tarjetas y sus explicaciones.
    if not bloques_validos({"horarios": bloques}):
        return []
    nombres = dict(DIAS)
    return [f"{nombres[bloque['dia']]} {bloque['inicio']}–{bloque['fin']}" for bloque in bloques]


def catalogo_general():
    # No recibe argumentos; devuelve las ofertas guardadas preparadas para la página.
    catalogo = []
    for oferta in obtener_ofertas():
        catalogo.append(presentar(oferta))
    return catalogo


def clave_orden_recomendacion(oferta):
    # Recibe una recomendación y devuelve sus criterios de orden: puntos e identificador.
    # El negativo permite mostrar más puntos primero; los empates usan el menor id.
    return [-oferta["puntos"], oferta["id"]]


def evaluar_horario(oferta, disponibilidad):
    """Devuelve estado, explicación y números de alternativas completas que se cumplen."""
    if not oferta["horario_valido"]:
        return "incompatible", "La publicación no tiene una estructura horaria válida", []
    modalidad = oferta["modalidad_horario"]
    if modalidad == ModalidadHorario.FLEXIBLE:
        # Un horario negociable necesita confirmación aunque el joven tenga tiempo libre.
        return "pendiente", "Horario negociable: consultar disponibilidad con la empresa", []
    if modalidad == ModalidadHorario.FIJO:
        if horario_compatible(oferta, disponibilidad):
            texto = "; ".join(presentar_bloques(oferta["horarios"]))
            return "compatible", "Horario completo compatible: " + texto, [oferta["alternativas"][0]["numero"]]
        return "incompatible", "No puedes cubrir todos los bloques del horario fijo", []
    coincidencias = []
    for grupo in oferta["alternativas"]:
        # Comprobamos cada opción por separado: no mezclamos días de opciones distintas.
        if horario_compatible({"horarios": grupo["horarios"]}, disponibilidad):
            coincidencias.append(grupo["numero"])
    if coincidencias:
        texto = ", ".join(str(numero) for numero in coincidencias)
        return "compatible", "Alternativas completas compatibles: " + texto, coincidencias
    return "incompatible", "No puedes cumplir ninguna alternativa completa de horario", []


def evaluar_requisito(nombre, oferta, perfil):
    # Se usa para experiencia y estudios; devuelve el estado y el motivo del requisito.
    estado = oferta[f"{nombre}_estado"]
    minimo = oferta[f"{nombre}_min"]
    etiqueta = "Experiencia" if nombre == "experiencia" else "Estudios"
    if estado == EstadoRequisito.NO_REQUERIDO:
        texto = "Sin experiencia requerida" if nombre == "experiencia" else "Sin estudios mínimos requeridos"
        return "compatible", texto
    if estado == EstadoRequisito.NEGOCIABLE:
        condicion = "Experiencia negociable" if nombre == "experiencia" else "Estudios negociables"
        return "pendiente", f"{condicion}: conversar con la empresa"
    if estado == EstadoRequisito.POR_CONFIRMAR:
        return "pendiente", f"{etiqueta} por confirmar: consultar el requisito con la empresa"
    if nombre == "experiencia":
        if minimo is None:
            return "pendiente", "Experiencia mínima por confirmar"
        if perfil["experiencia"] < minimo:
            return "incompatible", "No cumples la experiencia mínima requerida"
        return "compatible", "Cumples la experiencia mínima requerida"
    niveles = [clave for clave, _ in ESTUDIOS]
    if minimo not in niveles:
        return "pendiente", "Nivel mínimo de estudios por confirmar"
    # El orden de ESTUDIOS va del nivel menor al mayor.
    if niveles.index(perfil["estudios"]) < niveles.index(minimo):
        return "incompatible", "Tu nivel de estudios no cumple el mínimo solicitado"
    return "compatible", "Tu nivel de estudios cumple el mínimo solicitado"


def evaluar_oferta(oferta, perfil):
    """Recibe una oferta y un perfil; devuelve su clasificación, puntos y motivos.

    Solo prepara datos para la plantilla: no modifica ni guarda ofertas o perfiles.
    """
    resultado = presentar(oferta)
    # Cada criterio guarda un estado y su explicación para poder mostrar ambos después.
    criterios = []
    misma_comuna = bool(oferta["comuna"]) and oferta["comuna"] == perfil["comuna"]
    if misma_comuna:
        criterios.append(("compatible", "En tu comuna"))
    elif oferta["remota"] is True:
        criterios.append(("compatible", "Modalidad remota: puedes participar desde tu comuna"))
    elif oferta["remota"] is False and oferta["comuna"] in dict(COMUNAS):
        criterios.append(("incompatible", "La oferta es presencial en otra comuna"))
    else:
        criterios.append(("pendiente", "Ubicación o modalidad laboral por confirmar"))

    estado_horario, motivo_horario, alternativas = evaluar_horario(oferta, perfil.get("disponibilidad", {}))
    criterios.append((estado_horario, motivo_horario))
    if oferta["edad_min"] is None:
        criterios.append(("pendiente", "Edad mínima por confirmar"))
    elif perfil["edad"] < oferta["edad_min"]:
        criterios.append(("incompatible", "No cumples la edad mínima"))
    else:
        criterios.append(("compatible", "Cumples la edad mínima"))
    criterios.append(evaluar_requisito("experiencia", oferta, perfil))
    criterios.append(evaluar_requisito("estudios", oferta, perfil))
    if (perfil.get("sin_experiencia") and oferta["experiencia_estado"] == EstadoRequisito.ESPECIFICO
            and oferta["experiencia_min"] is not None and oferta["experiencia_min"] > 0):
        criterios.append(("incompatible", "La oferta exige experiencia y no cumple el filtro sin experiencia requerida"))
    if not oferta["empresa_valida"]:
        criterios.append(("incompatible", "La publicación no pertenece a una cuenta empresarial válida"))

    motivos = []
    pendientes = []
    incumplimientos = []
    for estado_criterio, texto in criterios:
        if estado_criterio == "compatible":
            motivos.append(texto)
        elif estado_criterio == "pendiente":
            pendientes.append(texto)
        elif estado_criterio == "incompatible":
            incumplimientos.append(texto)
    # Un incumplimiento conocido prevalece sobre cualquier dato pendiente de confirmar.
    if incumplimientos:
        estado = "incompatible"
    elif pendientes:
        estado = "pendiente"
    else:
        estado = "compatible"

    # La afinidad se calcula después; no cambia la clasificación anterior.
    coincidencias = [codigo for codigo in oferta["intereses"] if codigo in perfil["intereses"]]
    puntos = 2 * len(coincidencias)
    if misma_comuna:
        puntos += 1
    if coincidencias:
        nombres = dict(INTERESES)
        compartidos = [oferta["intereses_nombres"].get(codigo, nombres.get(codigo, codigo)) for codigo in coincidencias]
        motivos.append("Intereses en común: " + ", ".join(compartidos))
    elif estado == "compatible":
        motivos.append("Sin intereses en común; cumple tus requisitos y horarios")
    else:
        motivos.append("Sin intereses en común")
    for grupo in resultado["alternativas"]:
        grupo["compatible"] = grupo["numero"] in alternativas
    resultado.update(estado=estado, puntos=puntos, motivos=motivos, pendientes=pendientes,
                     incumplimientos=incumplimientos, alternativas_compatibles=alternativas)
    return resultado


def clasificar_recomendaciones(perfil):
    """Consulta las ofertas y devuelve tres listas ordenadas para el perfil recibido."""
    grupos = {"compatibles": [], "pendientes": [], "incompatibles": []}
    destinos = {"compatible": "compatibles", "pendiente": "pendientes", "incompatible": "incompatibles"}
    for oferta in obtener_ofertas():
        resultado = evaluar_oferta(oferta, perfil)
        grupos[destinos[resultado["estado"]]].append(resultado)
    for resultados in grupos.values():
        # Cada grupo se ordena por separado: más puntos primero y menor ID en empate.
        resultados.sort(key=clave_orden_recomendacion)
    return grupos


def recomendar(perfil):
    """Conservar la interfaz original que devuelve solo compatibilidad confirmada."""
    return clasificar_recomendaciones(perfil)["compatibles"]
