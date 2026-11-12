from django.db import migrations


NUEVOS_INTERESES = [
    ('retail', 'Comercio y retail'),
    ('reposicion_caja', 'Reposición y caja'),
    ('gastronomia', 'Gastronomía, cocina y garzonería'),
    ('turismo_hoteleria', 'Turismo y hotelería'),
    ('logistica', 'Bodega y logística'),
    ('reparto', 'Reparto'),
    ('diseno_marketing', 'Diseño y marketing'),
    ('educacion', 'Educación'),
    ('cuidados', 'Cuidado de personas'),
    ('limpieza_mantencion', 'Limpieza y mantención'),
    ('construccion_produccion', 'Construcción y producción'),
    ('eventos', 'Eventos'),
    ('practicas', 'Prácticas profesionales'),
]


def agregar_intereses(apps, schema_editor):
    Interes = apps.get_model("workconnectapp", "Interes")
    for codigo, nombre in NUEVOS_INTERESES:
        Interes.objects.using(schema_editor.connection.alias).get_or_create(
            codigo=codigo, defaults={"nombre": nombre},
        )


class Migration(migrations.Migration):
    dependencies = [("workconnectapp", "0002_alter_perfilempresa_nombre")]
    operations = [migrations.RunPython(agregar_intereses, migrations.RunPython.noop)]
