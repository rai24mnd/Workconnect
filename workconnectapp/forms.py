"""Formularios de cuentas, preferencias, búsqueda y publicaciones empresariales."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .datos import COMUNAS, DIAS, ESTUDIOS, INTERESES
from .models import (
    EstadoRemuneracion, EstadoRequisito, ModalidadLaboral, Oferta, PerfilEmpresa,
    TipoCuenta, TipoOferta,
)
from .validaciones import validar_bloque_horario, validar_horarios_oferta


class RegistroForm(UserCreationForm):
    # Django comprueba las contraseñas y guarda su versión protegida, nunca el texto original.
    tipo = forms.ChoiceField(
        label="Tipo de cuenta",
        choices=[(TipoCuenta.JOVEN, "Busco oportunidades"), (TipoCuenta.EMPRESA, "Represento a una empresa")],
        widget=forms.RadioSelect,
    )
    field_order = ["username", "password1", "password2", "tipo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].help_text = "Usa este nombre para iniciar sesión. " + str(self.fields["username"].help_text)
        self.fields["tipo"].help_text = "Elige si buscas oportunidades o si publicarás y administrarás ofertas para una empresa."
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"


class InicioSesionForm(AuthenticationForm):
    # AuthenticationForm comprueba usuario, contraseña y que la cuenta esté activa.
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Nombre de usuario o contraseña incorrectos.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class PerfilForm(forms.Form):
    """Valida las preferencias; cleaned_data contiene los valores listos para guardar."""
    exigir_disponibilidad = True
    # Estos campos reciben las preferencias que completa la persona.
    comuna = forms.ChoiceField(label="Tu comuna", choices=[("", "Selecciona una comuna")] + COMUNAS)
    edad = forms.IntegerField(label="Edad", min_value=1, max_value=120, help_text="Tu edad actual, en años completos.")
    experiencia = forms.IntegerField(
        label="Años completos de experiencia", min_value=0, max_value=100,
        help_text="Escribe 0 si todavía no tienes experiencia laboral.",
    )
    estudios = forms.ChoiceField(label="Nivel de estudios", choices=[("", "Selecciona un nivel")] + ESTUDIOS)
    intereses = forms.MultipleChoiceField(
        label="Tus intereses", choices=INTERESES, widget=forms.CheckboxSelectMultiple,
        help_text="Selecciona al menos uno. Ventas incluye atención al cliente; Administración, oficina; Tecnología, informática y soporte técnico. Se usan para ordenar, no para descartar.",
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
        if not hay_dia_marcado and self.exigir_disponibilidad:
            self.add_error(None, "Selecciona al menos un día disponible y completa sus horas.")
        datos["disponibilidad"] = disponibilidad
        return datos


class BusquedaForm(PerfilForm):
    """Reutiliza los campos de preferencias, pero estos filtros nunca guardan datos."""
    exigir_disponibilidad = False
    q = forms.CharField(label="Buscar oportunidades", max_length=150, required=False,
                        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Cajero, reponedor, vendedor, práctica…"}))
    modalidad = forms.ChoiceField(label="Modalidad", required=False,
                                  choices=[("", "Todas")] + ModalidadLaboral.choices)
    experiencia_estado = forms.ChoiceField(label="Experiencia requerida", required=False,
                                          choices=[("", "Cualquiera")] + EstadoRequisito.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields["edad"]
        for campo in self.fields.values():
            campo.required = False
        self.fields["comuna"].label = "Comuna"
        self.fields["comuna"].choices = [("", "Todas")] + COMUNAS
        self.fields["experiencia"].label = "Experiencia máxima requerida (años)"
        self.fields["experiencia"].help_text = "Incluye requisitos conocidos hasta este máximo, también ofertas sin experiencia."
        self.fields["estudios"].label = "Nivel de estudios disponible"
        self.fields["estudios"].choices = [("", "Cualquiera")] + ESTUDIOS
        self.fields["estudios"].help_text = "Incluye ofertas sin estudios mínimos o con un mínimo hasta este nivel."
        self.fields["intereses"].label = "Intereses laborales"
        self.fields["intereses"].help_text = "Encuentra ofertas con al menos uno de los intereses seleccionados."


# Formularios de la empresa y de sus publicaciones.
class PerfilEmpresaForm(forms.ModelForm):
    # ModelForm crea los campos a partir del modelo y comprueba sus reglas al validar.
    class Meta:
        model = PerfilEmpresa
        fields = ["nombre", "comuna", "descripcion", "email", "telefono"]
        labels = {"nombre": "Nombre de la empresa", "descripcion": "Descripción breve", "email": "Correo público", "telefono": "Teléfono público"}
        help_texts = {
            "nombre": "Nombre con el que quieres presentar la empresa en tus publicaciones.",
            "email": "Indica al menos un correo o teléfono que pueda mostrarse públicamente.",
            "telefono": "Opcional si ya indicaste un correo público. Incluye el código de país cuando corresponda.",
        }
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre"].required = True
        self.fields["comuna"].required = True

    def clean(self):
        datos = super().clean()
        if not datos.get("email") and not datos.get("telefono"):
            raise ValidationError("Indica un correo o teléfono público de la empresa.")
        return datos


class OfertaForm(forms.ModelForm):
    # Solo estos campos pueden venir del formulario; la empresa propietaria la fija la vista.
    class Meta:
        model = Oferta
        fields = [
            "titulo", "descripcion", "tipo", "comuna", "modalidad_laboral", "edad_min",
            "remuneracion_estado", "remuneracion_monto", "remuneracion_periodo",
            "experiencia_estado", "experiencia_min", "estudios_estado", "estudios_min",
            "intereses", "modalidad_horario", "descripcion_horario", "contacto_nombre",
            "contacto_email", "contacto_telefono", "url_postulacion", "instrucciones_postulacion",
        ]
        labels = {
            "descripcion": "Descripción y funciones del cargo",
            "edad_min": "Edad mínima (opcional)", "experiencia_estado": "Experiencia requerida",
            "experiencia_min": "Años mínimos de experiencia", "estudios_estado": "Estudios requeridos",
            "estudios_min": "Nivel mínimo de estudios", "contacto_nombre": "Persona de contacto",
            "contacto_email": "Correo de contacto", "contacto_telefono": "Teléfono de contacto",
            "modalidad_laboral": "Modalidad laboral", "modalidad_horario": "Modalidad de horario",
            "descripcion_horario": "Condiciones del horario (opcional)",
            "url_postulacion": "Enlace para postular", "instrucciones_postulacion": "Instrucciones para postular",
            "intereses": "Intereses o área laboral",
        }
        help_texts = {
            "remuneracion_estado": "Selecciona Monto informado, A convenir o No informado. No se asignará un sueldo automáticamente.",
            "remuneracion_monto": "Solo para Monto informado: pesos enteros, sin puntos, comas ni símbolo $. Debe ser mayor que cero.",
            "remuneracion_periodo": "Solo para Monto informado: mensual, semanal o por hora.",
            "titulo": "Usa un título breve que identifique el trabajo o la práctica.",
            "descripcion": "Explica las tareas y lo que debe conocer quien postula.",
            "comuna": "Ubicación de la oferta. Si no está definida y se necesita presencialidad, quedará por confirmar.",
            "edad_min": "Si la omites, la edad mínima quedará por confirmar; no se inventará un valor.",
            "experiencia_estado": "No requerido: no exige experiencia. Específico: indica años mínimos. Negociable: conversar con la empresa. Por confirmar: el requisito aún no está definido.",
            "experiencia_min": "Completa solo si elegiste Específico. Si cambias a otro estado, deja este mínimo vacío.",
            "estudios_estado": "No requerido: no exige un nivel mínimo. Específico: elige el nivel mínimo. Negociable: conversar con la empresa. Por confirmar: el requisito aún no está definido.",
            "estudios_min": "Completa solo si elegiste Específico. Si cambias a otro estado, deja este mínimo vacío.",
            "intereses": "Puedes elegir varias áreas. Ventas incluye atención al cliente; Administración, oficina; Tecnología, informática y soporte técnico. Se utilizan para calcular afinidad, sin agregar requisitos.",
            "modalidad_horario": "Obligatorio. Fijo: se cumplen todos los bloques. Varias opciones: basta una alternativa completa. Flexible: requiere acuerdo y queda pendiente.",
            "descripcion_horario": "Puedes explicar las condiciones del horario flexible o aclarar los bloques indicados.",
            "contacto_email": "Indica al menos un correo, teléfono, enlace o instrucciones para postular. Estos datos serán públicos.",
            "url_postulacion": "Usa una dirección completa que comience con https:// o http://.",
        }
        widgets = {
            "intereses": forms.CheckboxSelectMultiple,
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "descripcion_horario": forms.Textarea(attrs={"rows": 2}),
            "instrucciones_postulacion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo"].choices = [("", "Selecciona un tipo"),
                                       (TipoOferta.EMPLEO, "Empleo"), (TipoOferta.PRACTICA, "Práctica")]
        self.fields["modalidad_laboral"].required = True
        self.fields["remuneracion_estado"].required = False
        self.fields["url_postulacion"].validators.append(self.validar_enlace)

    @staticmethod
    def validar_enlace(valor):
        if not valor.startswith(("https://", "http://")):
            raise ValidationError("Utiliza un enlace http o https.")

    def clean(self):
        datos = super().clean()
        # Omitir el sueldo mantiene el estado explícito No informado, sin inventar montos.
        datos["remuneracion_estado"] = datos.get("remuneracion_estado") or EstadoRemuneracion.NO_INFORMADO
        # Django llama después a Oferta.clean(), que revisa mínimos, sueldo y contacto.
        return datos


class BloqueHorarioForm(forms.Form):
    dia = forms.ChoiceField(label="Día", choices=[("", "Selecciona un día")] + DIAS)
    inicio = forms.TimeField(label="Hora de inicio", input_formats=["%H:%M"], widget=forms.TimeInput(attrs={"type": "time", "step": "60"}, format="%H:%M"))
    fin = forms.TimeField(label="Hora de término", input_formats=["%H:%M"], widget=forms.TimeInput(attrs={"type": "time", "step": "60"}, format="%H:%M"))

    def clean(self):
        datos = super().clean()
        dia = datos.get("dia")
        inicio = datos.get("inicio")
        fin = datos.get("fin")
        if dia is not None and inicio is not None and fin is not None:
            validar_bloque_horario(dia, inicio, fin)
        return datos


BloquesFormSet = forms.formset_factory(
    BloqueHorarioForm, extra=1, can_delete=True, max_num=50, validate_max=True, absolute_max=100,
)


class CantidadAlternativasForm(forms.Form):
    # Aunque sea un campo oculto, Django limita lo recibido para evitar cantidades excesivas.
    total_alternativas = forms.IntegerField(min_value=0, max_value=20, widget=forms.HiddenInput)


class EditorHorarios:
    """Prepara y valida los formularios de horarios, sin guardar datos.

    Cada alternativa tiene su grupo de formularios (formset) para mantener todos
    sus bloques juntos. La vista guarda las listas validadas en self.bloques.
    """
    def __init__(self, datos=None, oferta=None):
        self.errores = []
        self.alternativas = []
        if datos is None:
            # Al editar, precargamos las alternativas y bloques guardados en SQLite.
            guardadas = list(oferta.alternativas.all()) if oferta and oferta.pk else []
            total = len(guardadas) if oferta and oferta.pk else 1
            self.cantidad = CantidadAlternativasForm(initial={"total_alternativas": total})
        else:
            guardadas = []
            self.cantidad = CantidadAlternativasForm(datos)
            total = 0
            if self.cantidad.is_valid():
                total = self.cantidad.cleaned_data["total_alternativas"]
        for numero in range(total):
            inicial = None
            if guardadas:
                inicial = list(guardadas[numero].bloques.values("dia", "inicio", "fin"))
            self.alternativas.append(BloquesFormSet(datos, initial=inicial, prefix=f"alternativa-{numero}"))
        self.vacia = BloquesFormSet(prefix="alternativa-__grupo__")
        self.bloques = []

    def is_valid(self, modalidad):
        # Recibe la modalidad elegida y deja en bloques solo los horarios completos y válidos.
        self.errores = []
        self.bloques = []
        if not self.cantidad.is_valid():
            self.errores = ["La cantidad de alternativas no es válida (máximo 20)."]
            return False
        validos = True
        for alternativa in self.alternativas:
            if not alternativa.is_valid():
                validos = False
                continue
            bloques = []
            for bloque in alternativa.cleaned_data:
                # Un formulario vacío o marcado para eliminar no se publica.
                if not bloque or bloque.get("DELETE", False):
                    continue
                bloques.append({"dia": bloque["dia"], "inicio": bloque["inicio"], "fin": bloque["fin"]})
            self.bloques.append(bloques)
        if not validos:
            return False
        try:
            # Esta regla compartida comprueba alternativas completas y evita superposiciones.
            validar_horarios_oferta(modalidad, self.bloques)
        except ValidationError as error:
            self.errores = error.messages
            return False
        return True
