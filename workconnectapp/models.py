"""Tablas de SQLite y sus relaciones; las migraciones conservan este esquema."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q

from .datos import COMUNAS, DIAS, ESTUDIOS
from .validaciones import validar_bloque_horario, validar_horarios_oferta

# Modelo heredado usado en el administrador. Se conserva para respetar el esquema.
class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=11)
    fecha_ingreso = models.DateField()

    def __str__(self):
        return self.nombre


class TipoCuenta(models.TextChoices):
    JOVEN = "joven", "Joven"
    EMPRESA = "empresa", "Empresa"


class EstadoRequisito(models.TextChoices):
    NO_REQUERIDO = "no_requerido", "No requerido"
    ESPECIFICO = "especifico", "Específico"
    NEGOCIABLE = "negociable", "Negociable"
    POR_CONFIRMAR = "por_confirmar", "Por confirmar"


class TipoOferta(models.TextChoices):
    EMPLEO = "empleo", "Empleo"
    PRACTICA = "practica", "Práctica"
    CURSO = "curso", "Curso de demostración"


class ModalidadLaboral(models.TextChoices):
    PRESENCIAL = "presencial", "Presencial"
    REMOTA = "remota", "Remota"


class ModalidadHorario(models.TextChoices):
    FIJO = "fijo", "Horario fijo"
    VARIAS_OPCIONES = "varias_opciones", "Varias opciones de horario"
    FLEXIBLE = "flexible", "Horario flexible o negociable"


class EstadoRemuneracion(models.TextChoices):
    NO_INFORMADO = "no_informado", "No informado"
    A_CONVENIR = "a_convenir", "A convenir"
    INFORMADO = "informado", "Monto informado"


class PeriodoRemuneracion(models.TextChoices):
    MENSUAL = "mensual", "Mensual"
    SEMANAL = "semanal", "Semanal"
    HORA = "hora", "Por hora"


class Cuenta(models.Model):
    # OneToOneField relaciona cada usuario de Django con un único tipo de cuenta.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cuenta",
    )
    tipo = models.CharField(max_length=10, choices=TipoCuenta.choices)

    class Meta:
        # Las restricciones también protegen la base ante escrituras sin formulario.
        constraints = [
            models.CheckConstraint(condition=Q(tipo__in=TipoCuenta.values), name="cuenta_tipo_valido"),
        ]

    def clean(self):
        super().clean()
        if self.pk:
            if self.tipo == TipoCuenta.JOVEN and PerfilEmpresa.objects.filter(cuenta_id=self.pk).exists():
                raise ValidationError({"tipo": "Esta cuenta ya tiene un perfil de empresa."})
            if self.tipo == TipoCuenta.EMPRESA and PerfilJoven.objects.filter(cuenta_id=self.pk).exists():
                raise ValidationError({"tipo": "Esta cuenta ya tiene un perfil de joven."})

    def __str__(self):
        return f"{self.usuario} ({self.get_tipo_display()})"


class Interes(models.Model):
    codigo = models.SlugField(max_length=30, unique=True)
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre


class PerfilJoven(models.Model):
    # El perfil agrega preferencias al usuario; ManyToMany permite varios intereses.
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name="perfil_joven")
    comuna = models.CharField(max_length=20, choices=COMUNAS, blank=True)
    edad = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(120)],
    )
    experiencia = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(100)],
    )
    estudios = models.CharField(max_length=30, choices=ESTUDIOS, blank=True)
    intereses = models.ManyToManyField(Interes, blank=True, related_name="jovenes")
    sin_experiencia = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(edad__isnull=True) | Q(edad__gte=1, edad__lte=120),
                name="joven_edad_valida",
            ),
            models.CheckConstraint(
                condition=Q(experiencia__isnull=True) | Q(experiencia__lte=100),
                name="joven_experiencia_valida",
            ),
            models.CheckConstraint(
                condition=Q(edad__isnull=True) | Q(experiencia__isnull=True) | Q(experiencia__lte=F("edad")),
                name="joven_experiencia_no_supera_edad",
            ),
        ]

    def clean(self):
        super().clean()
        errores = {}
        if self.cuenta_id:
            tipo = Cuenta.objects.filter(pk=self.cuenta_id).values_list("tipo", flat=True).first()
            if tipo is not None and tipo != TipoCuenta.JOVEN:
                errores["cuenta"] = "El perfil joven requiere una cuenta de tipo joven."
        if isinstance(self.edad, int) and isinstance(self.experiencia, int) and self.experiencia > self.edad:
            errores["experiencia"] = "La experiencia no puede superar la edad."
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f"Perfil joven: {self.cuenta.usuario}"


class DisponibilidadJoven(models.Model):
    # ForeignKey permite varios días de disponibilidad para un mismo perfil.
    perfil = models.ForeignKey(PerfilJoven, on_delete=models.CASCADE, related_name="disponibilidad")
    dia = models.CharField(max_length=10, choices=DIAS)
    inicio = models.TimeField()
    fin = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["perfil", "dia"], name="disponibilidad_unica_por_dia"),
            models.CheckConstraint(condition=Q(inicio__lt=F("fin")), name="disponibilidad_inicio_antes_fin"),
            models.CheckConstraint(condition=Q(dia__in=[dia for dia, _ in DIAS]), name="disponibilidad_dia_valido"),
        ]

    def clean(self):
        super().clean()
        validar_bloque_horario(self.dia, self.inicio, self.fin)

    def __str__(self):
        return f"{self.get_dia_display()}: {self.inicio}–{self.fin}"


class PerfilEmpresa(models.Model):
    # Datos públicos de la empresa; las credenciales siguen en el usuario de Django.
    cuenta = models.OneToOneField(Cuenta, on_delete=models.CASCADE, related_name="perfil_empresa")
    nombre = models.CharField(max_length=150, blank=True)
    comuna = models.CharField(max_length=20, choices=COMUNAS, blank=True)
    descripcion = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def clean(self):
        super().clean()
        if self.cuenta_id:
            tipo = Cuenta.objects.filter(pk=self.cuenta_id).values_list("tipo", flat=True).first()
            if tipo is not None and tipo != TipoCuenta.EMPRESA:
                raise ValidationError({"cuenta": "El perfil empresarial requiere una cuenta de tipo empresa."})

    def __str__(self):
        return self.nombre


class Oferta(models.Model):
    # PROTECT impide borrar una empresa que todavía tiene publicaciones asociadas.
    empresa = models.ForeignKey(
        PerfilEmpresa, on_delete=models.PROTECT, related_name="ofertas", null=True, blank=True,
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    remuneracion_estado = models.CharField(
        "Estado del sueldo", max_length=12, choices=EstadoRemuneracion.choices,
        default=EstadoRemuneracion.NO_INFORMADO,
    )
    remuneracion_monto = models.DecimalField(
        "Sueldo en pesos chilenos (CLP)", max_digits=12, decimal_places=0, null=True, blank=True,
        validators=[MinValueValidator(1)],
    )
    remuneracion_periodo = models.CharField(
        "Período de pago", max_length=7, choices=PeriodoRemuneracion.choices, blank=True,
    )
    tipo = models.CharField(max_length=10, choices=TipoOferta.choices)
    comuna = models.CharField(max_length=20, choices=COMUNAS, blank=True)
    modalidad_laboral = models.CharField(max_length=12, choices=ModalidadLaboral.choices, blank=True)
    edad_min = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(120)],
    )
    experiencia_estado = models.CharField(max_length=15, choices=EstadoRequisito.choices)
    experiencia_min = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    estudios_estado = models.CharField(max_length=15, choices=EstadoRequisito.choices)
    estudios_min = models.CharField(max_length=30, choices=ESTUDIOS, blank=True)
    intereses = models.ManyToManyField(Interes, blank=True, related_name="ofertas")
    modalidad_horario = models.CharField(max_length=20, choices=ModalidadHorario.choices)
    descripcion_horario = models.TextField(blank=True)
    contacto_nombre = models.CharField(max_length=100, blank=True)
    empresa_demo = models.CharField(max_length=150, blank=True)
    contacto_email = models.EmailField(blank=True)
    contacto_telefono = models.CharField(max_length=30, blank=True)
    url_postulacion = models.URLField(blank=True)
    instrucciones_postulacion = models.TextField(blank=True)
    es_demo = models.BooleanField(default=False)
    codigo_demo = models.SlugField(max_length=40, unique=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(remuneracion_estado=EstadoRemuneracion.INFORMADO,
                             remuneracion_monto__isnull=False, remuneracion_monto__gte=1,
                             remuneracion_monto__lte=999999999999,
                             remuneracion_periodo__in=PeriodoRemuneracion.values)
                           | Q(remuneracion_estado__in=[EstadoRemuneracion.NO_INFORMADO,
                                                      EstadoRemuneracion.A_CONVENIR],
                               remuneracion_monto__isnull=True, remuneracion_periodo="")),
                name="oferta_remuneracion_coherente",
            ),
            models.CheckConstraint(condition=Q(tipo__in=TipoOferta.values), name="oferta_tipo_valido"),
            models.CheckConstraint(
                condition=Q(modalidad_laboral="") | Q(modalidad_laboral__in=ModalidadLaboral.values),
                name="oferta_modalidad_laboral_valida",
            ),
            models.CheckConstraint(
                condition=Q(modalidad_horario__in=ModalidadHorario.values),
                name="oferta_modalidad_horario_valida",
            ),
            models.CheckConstraint(
                condition=Q(experiencia_estado__in=EstadoRequisito.values),
                name="oferta_estado_experiencia_valido",
            ),
            models.CheckConstraint(
                condition=Q(estudios_estado__in=EstadoRequisito.values),
                name="oferta_estado_estudios_valido",
            ),
            models.CheckConstraint(
                condition=(Q(experiencia_estado=EstadoRequisito.ESPECIFICO, experiencia_min__isnull=False,
                             experiencia_min__gte=1, experiencia_min__lte=100)
                           | (~Q(experiencia_estado=EstadoRequisito.ESPECIFICO) & Q(experiencia_min__isnull=True))),
                name="oferta_minimo_experiencia_coherente",
            ),
            models.CheckConstraint(
                condition=(Q(estudios_estado=EstadoRequisito.ESPECIFICO, estudios_min__in=[nivel for nivel, _ in ESTUDIOS])
                           | (~Q(estudios_estado=EstadoRequisito.ESPECIFICO) & Q(estudios_min=""))),
                name="oferta_minimo_estudios_coherente",
            ),
            models.CheckConstraint(
                condition=Q(edad_min__isnull=True) | Q(edad_min__gte=1, edad_min__lte=120),
                name="oferta_edad_minima_valida",
            ),
            models.CheckConstraint(
                condition=Q(es_demo=True) | Q(empresa__isnull=False), name="oferta_empresa_o_demo",
            ),
            models.CheckConstraint(
                condition=((Q(es_demo=True, codigo_demo__isnull=False) & ~Q(codigo_demo=""))
                           | Q(es_demo=False, codigo_demo__isnull=True)),
                name="oferta_codigo_demo_coherente",
            ),
            models.CheckConstraint(
                condition=~Q(tipo=TipoOferta.CURSO) | Q(es_demo=True), name="oferta_curso_solo_demo",
            ),
        ]

    def clean(self):
        super().clean()
        errores = {}
        if self.empresa_id:
            tipo_cuenta = PerfilEmpresa.objects.filter(pk=self.empresa_id).values_list("cuenta__tipo", flat=True).first()
            if tipo_cuenta is not None and tipo_cuenta != TipoCuenta.EMPRESA:
                errores["empresa"] = "La empresa propietaria debe tener una cuenta de tipo empresa."
        if self.remuneracion_estado == EstadoRemuneracion.INFORMADO:
            if self.remuneracion_monto is None:
                errores["remuneracion_monto"] = "Indica el sueldo en pesos chilenos."
            if not self.remuneracion_periodo:
                errores["remuneracion_periodo"] = "Selecciona el período de pago."
        else:
            if self.remuneracion_monto is not None:
                errores["remuneracion_monto"] = "El monto solo corresponde a un sueldo informado."
            if self.remuneracion_periodo:
                errores["remuneracion_periodo"] = "El período solo corresponde a un sueldo informado."
        for requisito in ("experiencia", "estudios"):
            estado = getattr(self, f"{requisito}_estado")
            minimo = getattr(self, f"{requisito}_min")
            if estado == EstadoRequisito.ESPECIFICO and minimo in (None, ""):
                errores[f"{requisito}_min"] = "Indica el mínimo del requisito específico."
            elif estado != EstadoRequisito.ESPECIFICO and minimo not in (None, ""):
                errores[f"{requisito}_min"] = "Solo un requisito específico puede tener un valor mínimo."
        if not any((self.contacto_email, self.contacto_telefono, self.url_postulacion, self.instrucciones_postulacion)):
            errores["contacto_email"] = "Indica un contacto o un método de postulación."
        if not self.es_demo and self.empresa_demo:
            errores["empresa_demo"] = "El nombre ficticio corresponde únicamente a demostraciones."
        if errores:
            raise ValidationError(errores)

    @property
    def remuneracion_texto(self):
        """Mostrar CLP y período solo cuando la empresa informó un monto."""
        if self.remuneracion_estado == EstadoRemuneracion.INFORMADO:
            monto = format(self.remuneracion_monto, ",.0f").replace(",", ".")
            return f"${monto} CLP · {self.get_remuneracion_periodo_display()}"
        return self.get_remuneracion_estado_display()

    def validar_publicacion(self, alternativas=None):
        """Validar fila y horario completo; guardar no llama a este método."""
        # full_clean revisa campos y reglas del modelo. save solo escribe los datos.
        self.full_clean()
        if alternativas is None:
            alternativas = []
            if self.pk:
                alternativas = [
                    list(alternativa.bloques.values("dia", "inicio", "fin"))
                    for alternativa in self.alternativas.all()
                ]
        validar_horarios_oferta(self.modalidad_horario, alternativas)

    def __str__(self):
        return self.titulo


class AlternativaHorario(models.Model):
    # Cada alternativa agrupa todos los bloques que deben cumplirse juntos.
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name="alternativas")
    orden = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["orden", "pk"]
        constraints = [
            models.UniqueConstraint(fields=["oferta", "orden"], name="alternativa_orden_unico"),
            models.CheckConstraint(condition=Q(orden__gte=1), name="alternativa_orden_positivo"),
        ]

    def __str__(self):
        return f"Alternativa {self.orden}: {self.oferta.titulo}"


class HorarioOferta(models.Model):
    # CASCADE borra estos bloques cuando se elimina su alternativa o su oferta.
    alternativa = models.ForeignKey(AlternativaHorario, on_delete=models.CASCADE, related_name="bloques")
    dia = models.CharField(max_length=10, choices=DIAS)
    inicio = models.TimeField()
    fin = models.TimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(inicio__lt=F("fin")), name="horario_inicio_antes_fin"),
            models.CheckConstraint(condition=Q(dia__in=[dia for dia, _ in DIAS]), name="horario_dia_valido"),
            models.UniqueConstraint(fields=["alternativa", "dia", "inicio", "fin"], name="horario_bloque_unico"),
        ]

    def clean(self):
        super().clean()
        validar_bloque_horario(self.dia, self.inicio, self.fin)

    def __str__(self):
        return f"{self.get_dia_display()}: {self.inicio}–{self.fin}"
