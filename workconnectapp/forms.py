from django import forms

from .datos import COMUNAS, ESTUDIOS, HORARIOS, INTERESES


class PerfilForm(forms.Form):
    comuna = forms.ChoiceField(label="Tu comuna", choices=[("", "Selecciona una comuna")] + COMUNAS)
    edad = forms.IntegerField(label="Edad", min_value=1, max_value=120)
    experiencia = forms.IntegerField(label="Años completos de experiencia", min_value=0, max_value=100)
    estudios = forms.ChoiceField(label="Nivel de estudios", choices=[("", "Selecciona un nivel")] + ESTUDIOS)
    intereses = forms.MultipleChoiceField(
        label="Tus intereses", choices=INTERESES, widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona al menos uno. Se usan para ordenar, no para descartar.",
    )
    horarios = forms.MultipleChoiceField(
        label="Disponibilidad horaria", choices=HORARIOS, widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona al menos una opción. Debe coincidir con algún turno de la oportunidad.",
    )

    def clean(self):
        datos = super().clean()
        edad = datos.get("edad")
        experiencia = datos.get("experiencia")
        if edad is not None and experiencia is not None and experiencia > edad:
            self.add_error("experiencia", "La experiencia no puede superar tu edad.")
        return datos
