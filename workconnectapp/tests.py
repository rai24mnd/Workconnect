from copy import deepcopy
from datetime import time
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.urls import reverse

from .datos import DIAS, OPORTUNIDADES
from .forms import PerfilForm
from .services import horario_compatible, recomendar


def perfil_demo(**cambios):
    """Datos exactos del primer caso del video; los demás días no disponibles."""
    datos = {
        "comuna": "valparaiso", "edad": 19, "experiencia": 0,
        "estudios": "media_completa", "intereses": ["tecnologia"],
        "lunes_disponible": "on", "lunes_inicio": "17:00", "lunes_fin": "22:00",
        "sabado_disponible": "on", "sabado_inicio": "10:00", "sabado_fin": "12:00",
    }
    datos.update(cambios)
    return datos

class RecomendacionesTests(SimpleTestCase):
    """Comprueba el flujo web completo sin crear una base de datos."""

    def test_perfil_reportado_superior_en_curso_todos_los_dias_11_a_22(self):
        """Reproduce el perfil reportado, fijando las horas en 11:00–22:00."""
        datos = {
            "accion": "recomendar", "comuna": "valparaiso", "edad": 19,
            "experiencia": 0, "estudios": "superior_en_curso",
            "intereses": ["tecnologia", "administracion", "ventas"],
            # La casilla sin_experiencia no se envía cuando está desmarcada.
        }
        for dia, nombre in DIAS:
            datos.update({f"{dia}_disponible": "on", f"{dia}_inicio": "11:00",
                          f"{dia}_fin": "22:00"})

        formulario = PerfilForm(datos)
        self.assertTrue(formulario.is_valid(), formulario.errors)
        perfil = formulario.cleaned_data
        self.assertFalse(perfil["sin_experiencia"])
        self.assertEqual(perfil["estudios"], "superior_en_curso")
        self.assertEqual(perfil["disponibilidad"], {
            dia: [(time(11), time(22))] for dia, nombre in DIAS
        })

        # Horarios comprobados individualmente para las seis oportunidades.
        self.assertEqual(
            {oferta["id"]: horario_compatible(oferta, perfil["disponibilidad"])
             for oferta in OPORTUNIDADES},
            {1: False, 2: True, 3: False, 4: True, 5: False, 6: True},
        )
        esperados = [(6, 3), (2, 2)]
        self.assertEqual([(o["id"], o["puntos"]) for o in recomendar(perfil)], esperados)
        # La pasantía 6 exige media completa: aparecer con superior en curso
        # comprueba la jerarquía de estudios además del resultado de la vista.
        respuesta = self.client.post(reverse("index"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["procesado"])
        self.assertTrue(respuesta.context["panel_abierto"])
        self.assertEqual([(o["id"], o["puntos"])
                          for o in respuesta.context["recomendaciones"]], esperados)
        self.assertContains(respuesta, "2 oportunidades compatibles")
        self.assertContains(respuesta, "Apoyo administrativo inicial")
        self.assertContains(respuesta, "Introducción al desarrollo web")
        self.assertNotContains(respuesta, "No encontramos oportunidades compatibles")
        for titulo in ["Apoyo de soporte tecnológico", "Asistente de oficina",
                       "Atención en tienda", "Herramientas digitales para oficinas"]:
            self.assertNotContains(respuesta, titulo)

    def test_perfil_con_coincidencias(self):
        catalogo_original = deepcopy(OPORTUNIDADES)
        respuesta = self.client.post(reverse("index"), perfil_demo())
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["procesado"])
        resultados = respuesta.context["recomendaciones"]
        self.assertEqual([oferta["id"] for oferta in resultados], [1, 2, 6])
        self.assertEqual([oferta["puntos"] for oferta in resultados], [3, 2, 1])
        self.assertContains(respuesta, "Intereses en común: Tecnología")
        self.assertContains(respuesta, "Horario completo compatible: Lunes 17:00–19:00; Sábado 10:00–12:00")
        self.assertContains(respuesta, "Modalidad remota: puedes participar desde tu comuna")
        self.assertContains(respuesta, "Sin intereses en común; cumple tus requisitos y horarios")
        self.assertNotContains(respuesta, "Herramientas digitales para oficinas")
        self.assertContains(respuesta, "Contacto ficticio")
        self.assertTrue(respuesta.context["panel_abierto"])
        self.assertEqual(OPORTUNIDADES, catalogo_original)

    def test_perfil_sin_coincidencias_por_horario(self):
        # La oficina exige lunes por la mañana, los cursos tampoco caben.
        datos = perfil_demo(comuna="quilpue", experiencia=1, intereses=["administracion"],
                            lunes_inicio="17:00", lunes_fin="19:00", sabado_disponible="")
        respuesta = self.client.post(reverse("index"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["procesado"])
        self.assertEqual(respuesta.context["recomendaciones"], [])
        self.assertContains(respuesta, "No encontramos oportunidades compatibles")
        self.assertEqual(respuesta.context["formulario"]["lunes_inicio"].value(), "17:00")
        # Cambiar solo el horario permite encontrar la oficina local y el
        # curso remoto: demuestra que el horario sí altera el resultado.
        datos.update(lunes_inicio="09:00", lunes_fin="13:00")
        respuesta_manana = self.client.post(reverse("index"), datos)
        self.assertEqual(
            [oferta["id"] for oferta in respuesta_manana.context["recomendaciones"]],
            [3, 5],
        )

    def test_catalogo_inicial_ruta_plantillas_estaticos_y_contactos(self):
        respuesta = self.client.get(reverse("index"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "workconnectapp/index.html")
        self.assertTemplateUsed(respuesta, "workconnectapp/tarjeta.html")
        self.assertFalse(respuesta.context["panel_abierto"])
        self.assertFalse(respuesta.context["procesado"])
        self.assertEqual(len(respuesta.context["oportunidades"]), 6)
        self.assertContains(respuesta, "Catálogo general")
        self.assertNotContains(respuesta, "puntos de afinidad")
        self.assertContains(respuesta, 'type="time"', count=14)
        self.assertContains(respuesta, 'id="preferencias" class="panel" aria-labelledby="titulo-perfil" hidden')
        self.assertContains(respuesta, "Contactar", count=4)
        self.assertContains(respuesta, "Más información", count=2)
        for oferta in OPORTUNIDADES:
            self.assertContains(respuesta, oferta["titulo"])
            self.assertContains(respuesta, 'mailto:' + oferta["contacto"]["email"])
            self.assertContains(respuesta, 'id="contacto-' + str(oferta["id"]) + '"')
        for archivo in ["styles.css", "app.js"]:
            self.assertIsNotNone(finders.find("workconnectapp/" + archivo))
            self.assertContains(respuesta, "/static/workconnectapp/" + archivo)

    def test_volver_catalogo_conserva_preferencias_sin_exigir_formulario_completo(self):
        respuesta = self.client.post(reverse("index"), perfil_demo(accion="catalogo", edad=""))
        self.assertFalse(respuesta.context["procesado"])
        self.assertFalse(respuesta.context["panel_abierto"])
        self.assertEqual(len(respuesta.context["oportunidades"]), 6)
        self.assertEqual(respuesta.context["formulario"]["lunes_inicio"].value(), "17:00")
        self.assertEqual(respuesta.context["formulario"]["intereses"].value(), ["tecnologia"])
        self.assertNotContains(respuesta, "Revisa los campos indicados")

    def test_solo_sin_experiencia_excluye_la_oficina(self):
        datos = perfil_demo(comuna="quilpue", experiencia=1, intereses=["administracion"],
                            lunes_inicio="09:00", lunes_fin="13:00", sabado_disponible="")
        respuesta = self.client.post(reverse("index"), datos)
        self.assertEqual([o["id"] for o in respuesta.context["recomendaciones"]], [3, 5])
        datos["sin_experiencia"] = "on"
        respuesta = self.client.post(reverse("index"), datos)
        self.assertEqual([o["id"] for o in respuesta.context["recomendaciones"]], [5])
        self.assertContains(respuesta, "Sin experiencia requerida")
        self.assertTrue(respuesta.context["formulario"].cleaned_data["sin_experiencia"])

    def test_experiencia_no_suma_puntos(self):
        respuestas = [self.client.post(reverse("index"), perfil_demo(experiencia=anios))
                      for anios in [0, 5]]
        self.assertEqual(
            [(o["id"], o["puntos"]) for o in respuestas[0].context["recomendaciones"]],
            [(o["id"], o["puntos"]) for o in respuestas[1].context["recomendaciones"]],
        )

    def test_intervalo_completo_limites_y_solapamientos(self):
        oferta = deepcopy(OPORTUNIDADES[1])  # Lunes 20:00–22:00.
        casos = [
            (time(20), time(22), True), (time(19), time(23), True),
            (time(20, 1), time(22), False), (time(20), time(21, 59), False),
            (time(19), time(20), False),
        ]
        for inicio, fin, esperado in casos:
            with self.subTest(inicio=inicio, fin=fin):
                self.assertEqual(horario_compatible(oferta, {"lunes": [(inicio, fin)]}), esperado)
        self.assertFalse(horario_compatible(oferta, {"martes": [(time(19), time(23))]}))
        # Dos intervalos parciales no reemplazan un intervalo completo.
        self.assertFalse(horario_compatible(oferta, {"lunes": [(time(20), time(21)), (time(21), time(22))]}))
        self.assertTrue(horario_compatible(oferta, {"lunes": [(time(8), time(10)), (time(20), time(22))]}))

    def test_todos_los_bloques_obligatorios_y_dias_no_disponibles(self):
        formulario = PerfilForm(perfil_demo(sabado_disponible=""))
        self.assertTrue(formulario.is_valid(), formulario.errors)
        resultados = recomendar(formulario.cleaned_data)
        self.assertEqual([o["id"] for o in resultados], [2, 6])
        self.assertNotIn("sabado", formulario.cleaned_data["disponibilidad"])

    def test_horarios_ausentes_incorrectos_o_nocturnos_no_se_recomiendan(self):
        formulario = PerfilForm(perfil_demo())
        self.assertTrue(formulario.is_valid())
        for horario in [None, [], [{"dia": "lunes"}],
                        [{"dia": "lunes", "inicio": "22:00", "fin": "02:00"}],
                        [{"dia": "otro", "inicio": "17:00", "fin": "18:00"}],
                        [{"dia": "lunes", "inicio": "xx", "fin": "18:00"}]]:
            with self.subTest(horario=horario):
                oferta = {**OPORTUNIDADES[0], "horarios": horario}
                with patch("workconnectapp.services.OPORTUNIDADES", [oferta]):
                    self.assertEqual(recomendar(formulario.cleaned_data), [])
        oferta = deepcopy(OPORTUNIDADES[0])
        del oferta["horarios"]
        self.assertFalse(horario_compatible(oferta, formulario.cleaned_data["disponibilidad"]))

    def test_formulario_rechaza_horas_invalidas_incompletas_o_invertidas(self):
        for inicio, fin in [("17:00", "17:00"), ("22:00", "02:00"),
                            ("", "22:00"), ("17:00", ""), ("25:00", "22:00")]:
            with self.subTest(inicio=inicio, fin=fin):
                respuesta = self.client.post(reverse("index"), perfil_demo(lunes_inicio=inicio, lunes_fin=fin))
                self.assertFalse(respuesta.context["procesado"])
                self.assertTrue(respuesta.context["panel_abierto"])
                self.assertContains(respuesta, "Revisa los campos indicados")
        formulario = PerfilForm(perfil_demo(lunes_disponible="", sabado_disponible=""))
        self.assertFalse(formulario.is_valid())
        self.assertIn("Selecciona al menos un día", str(formulario.non_field_errors()))

    def test_requisitos_de_edad_experiencia_estudios_y_comuna(self):
        for cambios in [{"edad": 15}, {"estudios": "media_en_curso"},
                        {"comuna": "quilpue"}]:
            formulario = PerfilForm(perfil_demo(**cambios))
            self.assertTrue(formulario.is_valid(), formulario.errors)
            self.assertNotIn(1, [o["id"] for o in recomendar(formulario.cleaned_data)])
        formulario = PerfilForm(perfil_demo(comuna="quilpue", experiencia=0,
                                lunes_inicio="09:00", lunes_fin="13:00", sabado_disponible=""))
        self.assertTrue(formulario.is_valid())
        self.assertEqual([o["id"] for o in recomendar(formulario.cleaned_data)], [5])

    def test_contacto_telefonico_opcional(self):
        oferta = deepcopy(OPORTUNIDADES[0])
        # Solo dato de prueba: el catálogo no inventa números de teléfono.
        oferta["contacto"]["telefono"] = "+00000000000"
        with patch("workconnectapp.services.OPORTUNIDADES", [oferta]):
            respuesta = self.client.get(reverse("index"))
        self.assertContains(respuesta, 'href="tel:+00000000000"')

    def test_post_requiere_proteccion_csrf(self):
        from django.test import Client
        cliente = Client(enforce_csrf_checks=True)
        self.assertEqual(cliente.post(reverse("index"), perfil_demo()).status_code, 403)
