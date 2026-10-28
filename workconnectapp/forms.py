from django import forms

from .datos import COMUNAS, DIAS, ESTUDIOS, INTERESES


class PerfilForm(forms.Form):
    comuna = forms.ChoiceField(label="Tu comuna", choices=[("", "Selecciona una comuna")] + COMUNAS)
    edad = forms.IntegerField(label="Edad", min_value=1, max_value=120)
    experiencia = forms.IntegerField(label="Años completos de experiencia", min_value=0, max_value=100)
    estudios = forms.ChoiceField(label="Nivel de estudios", choices=[("", "Selecciona un nivel")] + ESTUDIOS)
    intereses = forms.MultipleChoiceField(
        label="Tus intereses", choices=INTERESES, widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona al menos uno. Se usan para ordenar, no para descartar.",
    )
    sin_experiencia = forms.BooleanField(
        label="Mostrar solo oportunidades sin experiencia requerida", required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Un intervalo por día. Las horas de un día no disponible se ignoran.
        for dia, nombre in DIAS:
            self.fields[f"{dia}_disponible"] = forms.BooleanField(
                label=f"Disponible el {nombre.lower()}", required=False,
            )
            for extremo, etiqueta in [("inicio", "Desde"), ("fin", "Hasta")]:
                self.fields[f"{dia}_{extremo}"] = forms.TimeField(
                    label=f"{nombre}: {etiqueta.lower()}", required=False,
                    input_formats=["%H:%M"],
                    widget=forms.TimeInput(format="%H:%M", attrs={"type": "time", "step": "60"}),
                )

    def filas_horario(self):
        return [{"nombre": nombre, "disponible": self[f"{dia}_disponible"],
                 "inicio": self[f"{dia}_inicio"], "fin": self[f"{dia}_fin"]}
                for dia, nombre in DIAS]

    def clean(self):
        datos = super().clean()
        edad = datos.get("edad")
        experiencia = datos.get("experiencia")
        if edad is not None and experiencia is not None and experiencia > edad:
            self.add_error("experiencia", "La experiencia no puede superar tu edad.")
        disponibilidad = {}
        for dia, nombre in DIAS:
            if not datos.get(f"{dia}_disponible"):
                continue
            inicio = datos.get(f"{dia}_inicio")
            fin = datos.get(f"{dia}_fin")
            if inicio is None and f"{dia}_inicio" not in self.errors:
                self.add_error(f"{dia}_inicio", "Indica la hora de inicio.")
            if fin is None and f"{dia}_fin" not in self.errors:
                self.add_error(f"{dia}_fin", "Indica la hora de término.")
            if inicio is not None and fin is not None:
                if inicio >= fin:
                    self.add_error(f"{dia}_fin", "El inicio debe ser anterior al término, dentro del mismo día.")
                else:
                    disponibilidad[dia] = [(inicio, fin)]
        if not any(datos.get(f"{dia}_disponible") for dia, nombre in DIAS):
            self.add_error(None, "Selecciona al menos un día disponible y completa sus horas.")
        datos["disponibilidad"] = disponibilidad
        return datos
