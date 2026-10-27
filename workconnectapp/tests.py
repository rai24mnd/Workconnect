from copy import deepcopy

from django.test import SimpleTestCase
from django.urls import reverse

from .datos import OPORTUNIDADES

class RecomendacionesTests(SimpleTestCase):
    """Comprueba el flujo web completo sin crear una base de datos."""

    def test_perfil_con_coincidencias(self):
        catalogo_original = deepcopy(OPORTUNIDADES)
        respuesta = self.client.post(reverse("index"), {
            "comuna": "valparaiso", "edad": 19, "experiencia": 0,
            "estudios": "media_completa", "intereses": ["tecnologia"],
            "horarios": ["tarde", "fin_semana"],
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["procesado"])
        resultados = respuesta.context["recomendaciones"]
        self.assertEqual([oferta["id"] for oferta in resultados], [1, 2, 6])
        self.assertEqual([oferta["puntos"] for oferta in resultados], [3, 2, 1])
        self.assertContains(respuesta, "Intereses en común: Tecnología")
        self.assertContains(respuesta, "Horario compatible: Tarde, Fines de semana")
        self.assertContains(respuesta, "Modalidad remota: puedes participar desde tu comuna")
        self.assertContains(respuesta, "Sin intereses en común; cumple tus requisitos y horarios")
        self.assertNotContains(respuesta, "Herramientas digitales para oficinas")
        self.assertContains(respuesta, "Contacto ficticio:")
        self.assertEqual(OPORTUNIDADES, catalogo_original)

    def test_perfil_sin_coincidencias_por_horario(self):
        # Cumple la oferta de oficina en Quilpué, salvo su turno de mañana.
        # Los cursos remotos tampoco ofrecen un turno de tarde.
        respuesta = self.client.post(reverse("index"), {
            "comuna": "quilpue", "edad": 19, "experiencia": 1,
            "estudios": "media_completa", "intereses": ["administracion"],
            "horarios": ["tarde"],
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["procesado"])
        self.assertEqual(respuesta.context["recomendaciones"], [])
        self.assertContains(respuesta, "No encontramos oportunidades compatibles")
        self.assertEqual(respuesta.context["formulario"]["horarios"].value(), ["tarde"])
        # Cambiar solo el horario permite encontrar la oficina local y el
        # curso remoto: demuestra que el horario sí altera el resultado.
        respuesta_manana = self.client.post(reverse("index"), {
            "comuna": "quilpue", "edad": 19, "experiencia": 1,
            "estudios": "media_completa", "intereses": ["administracion"],
            "horarios": ["manana"],
        })
        self.assertEqual(
            [oferta["id"] for oferta in respuesta_manana.context["recomendaciones"]],
            [3, 5],
        )
