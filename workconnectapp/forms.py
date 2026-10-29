from django import forms

from .datos import COMUNAS, DIAS, ESTUDIOS, INTERESES


class PerfilForm(forms.Form):
    # Estos campos reciben las preferencias que completa la persona.
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
        # Recibe los datos del formulario y agrega los campos por día; no devuelve un valor.
        super().__init__(*args, **kwargs)
        # Un intervalo por día. Las horas de un día no disponible se ignoran.
        for dia, nombre_dia in DIAS:
            self.fields[f"{dia}_disponible"] = forms.BooleanField(
                label=f"Disponible el {nombre_dia.lower()}", required=False,
            )
            self.fields[f"{dia}_inicio"] = forms.TimeField(
                label=f"{nombre_dia}: desde", required=False,
                input_formats=["%H:%M"],
                widget=forms.TimeInput(format="%H:%M", attrs={"type": "time", "step": "60"}),
            )
            self.fields[f"{dia}_fin"] = forms.TimeField(
                label=f"{nombre_dia}: hasta", required=False,
                input_formats=["%H:%M"],
                widget=forms.TimeInput(format="%H:%M", attrs={"type": "time", "step": "60"}),
            )

    def filas_horario(self):
        # Usa este formulario y devuelve las filas de días y campos para la página.
        filas = []  # Cada fila contiene los campos que se muestran juntos para un día.
        for dia, nombre_dia in DIAS:
            fila = {
                "nombre": nombre_dia,
                "disponible": self[f"{dia}_disponible"],
                "inicio": self[f"{dia}_inicio"],
                "fin": self[f"{dia}_fin"],
            }
            filas.append(fila)
        return filas

    def clean(self):
        # Usa los datos recibidos, valida el perfil y devuelve los datos con su disponibilidad.
        datos = super().clean()  # Valores que Django ya convirtió a sus tipos de Python.
        edad = datos.get("edad")
        experiencia = datos.get("experiencia")
        if edad is not None and experiencia is not None and experiencia > edad:
            self.add_error("experiencia", "La experiencia no puede superar tu edad.")

        disponibilidad = {}  # Guarda los intervalos válidos de cada día marcado.
        hay_dia_marcado = False
        for dia, nombre_dia in DIAS:
            if not datos.get(f"{dia}_disponible"):
                continue
            hay_dia_marcado = True
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
        if not hay_dia_marcado:
            self.add_error(None, "Selecciona al menos un día disponible y completa sus horas.")
        datos["disponibilidad"] = disponibilidad
        return datos
