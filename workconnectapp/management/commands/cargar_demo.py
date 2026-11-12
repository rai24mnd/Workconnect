"""Cargar las oportunidades ficticias sin modificar publicaciones empresariales."""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction

from workconnectapp.datos import INTERESES, OPORTUNIDADES
from workconnectapp.models import (
    AlternativaHorario,
    EstadoRequisito,
    HorarioOferta,
    Interes,
    ModalidadHorario,
    ModalidadLaboral,
    Oferta,
    TipoOferta,
)


class Command(BaseCommand):
    help = "Crear o restaurar las cuatro ofertas laborales de demostración, sin eliminar cursos antiguos."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        creadas = 0
        actualizadas = 0
        origen = "el catálogo de demostración"
        try:
            with transaction.atomic():
                identificadores = [fuente["id"] for fuente in OPORTUNIDADES]
                if (len(identificadores) != 4
                        or any(type(identificador) is not int for identificador in identificadores)
                        or set(identificadores) != {1, 3, 4, 6}):
                    raise ValidationError("El catálogo laboral debe contener los identificadores 1, 3, 4 y 6, sin repetirlos.")
                nombres_intereses = dict(INTERESES)
                for fuente in sorted(OPORTUNIDADES, key=lambda dato: dato["id"]):
                    origen = f"demo-{fuente['id']}"
                    if self.cargar_oferta(fuente, nombres_intereses):
                        creadas += 1
                    else:
                        actualizadas += 1
        except (ValidationError, KeyError, TypeError, ValueError, DatabaseError) as error:
            if isinstance(error, ValidationError):
                detalle = "; ".join(error.messages)
            elif isinstance(error, KeyError):
                detalle = f"Falta el dato obligatorio {error.args[0]!r}."
            else:
                detalle = str(error)
            raise CommandError(
                f"No se pudo cargar {origen}: {detalle} Se revirtió la carga completa."
            ) from error

        self.stdout.write(self.style.SUCCESS(
            f"Demostraciones cargadas: 4 ofertas laborales; {creadas} creadas y {actualizadas} actualizadas. Los cursos antiguos no se modifican."
        ))

    def cargar_oferta(self, fuente, nombres_intereses):
        """Restaurar una demo por su código estable; devolver si fue creada."""
        codigo = f"demo-{fuente['id']}"
        oferta = Oferta.objects.filter(codigo_demo=codigo).first()
        if oferta is not None and (not oferta.es_demo or oferta.empresa_id is not None):
            raise ValidationError(
                f"El código {codigo} pertenece a una publicación empresarial y no se puede reemplazar."
            )
        creada = oferta is None
        if creada:
            oferta = Oferta(codigo_demo=codigo)

        tipos = {
            "Empleo": TipoOferta.EMPLEO,
            "Pasantía": TipoOferta.PRACTICA,
        }
        if fuente["tipo"] not in tipos:
            raise ValidationError("El tipo de oportunidad de demostración no es reconocido.")
        if type(fuente["remota"]) is not bool:
            raise ValidationError("La modalidad remota de la fuente debe ser True o False.")
        experiencia = fuente["experiencia_min"]
        if type(experiencia) is not int or experiencia < 0:
            raise ValidationError("La experiencia mínima de la fuente debe ser un entero no negativo.")
        contacto = fuente["contacto"]
        if not isinstance(contacto, dict):
            raise ValidationError("El contacto de demostración debe ser un diccionario.")
        horarios = fuente["horarios"]
        if not isinstance(horarios, list) or not horarios:
            raise ValidationError("La demostración debe contener una lista de bloques horarios.")
        codigos_intereses = fuente["intereses"]
        if not isinstance(codigos_intereses, list) or len(set(codigos_intereses)) != len(codigos_intereses):
            raise ValidationError("Los intereses de la fuente deben ser una lista sin repeticiones.")

        datos = {
            "empresa": None,
            "titulo": fuente["titulo"],
            "descripcion": fuente["descripcion"],
            "tipo": tipos[fuente["tipo"]],
            "comuna": fuente["comuna"],
            "modalidad_laboral": ModalidadLaboral.REMOTA if fuente["remota"] else ModalidadLaboral.PRESENCIAL,
            "edad_min": fuente["edad_min"],
            "experiencia_estado": EstadoRequisito.NO_REQUERIDO if experiencia == 0 else EstadoRequisito.ESPECIFICO,
            "experiencia_min": None if experiencia == 0 else experiencia,
            "estudios_estado": EstadoRequisito.ESPECIFICO,
            "estudios_min": fuente["estudios_min"],
            "modalidad_horario": ModalidadHorario.FIJO,
            "descripcion_horario": "",
            "empresa_demo": contacto["empresa"],
            "contacto_nombre": contacto["persona"],
            "contacto_email": contacto.get("email", ""),
            "contacto_telefono": contacto.get("telefono", ""),
            "url_postulacion": "",
            "instrucciones_postulacion": "",
            "es_demo": True,
        }
        for campo, valor in datos.items():
            setattr(oferta, campo, valor)
        oferta.full_clean()
        oferta.save()

        intereses = []
        for codigo_interes in codigos_intereses:
            if codigo_interes not in nombres_intereses:
                raise ValidationError(f"El interés {codigo_interes!r} no está definido en INTERESES.")
            interes, _ = Interes.objects.get_or_create(
                codigo=codigo_interes, defaults={"nombre": nombres_intereses[codigo_interes]},
            )
            interes.full_clean()
            intereses.append(interes)
        oferta.intereses.set(intereses)

        # Reemplazar únicamente los horarios de esta demo evita acumular alternativas.
        oferta.alternativas.all().delete()
        alternativa = AlternativaHorario(oferta=oferta, orden=1)
        alternativa.full_clean()
        alternativa.save()
        for horario in horarios:
            if not isinstance(horario, dict):
                raise ValidationError("Cada bloque horario de la fuente debe ser un diccionario.")
            bloque = HorarioOferta(
                alternativa=alternativa, dia=horario["dia"],
                inicio=horario["inicio"], fin=horario["fin"],
            )
            bloque.full_clean()
            bloque.save()
        oferta.validar_publicacion()
        return creada
