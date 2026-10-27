"""Catálogo ficticio: no son vacantes ni cursos vigentes."""

COMUNAS = [("valparaiso", "Valparaíso"), ("vina", "Viña del Mar"), ("quilpue", "Quilpué")]
INTERESES = [("tecnologia", "Tecnología"), ("administracion", "Administración"), ("ventas", "Ventas")]
HORARIOS = [("manana", "Mañana"), ("tarde", "Tarde"), ("noche", "Noche"), ("fin_semana", "Fines de semana")]
ESTUDIOS = [("media_en_curso", "Enseñanza media en curso"), ("media_completa", "Enseñanza media completa"), ("superior_en_curso", "Educación superior en curso"), ("superior_completa", "Educación superior completa")]

# Cada horario es un turno alternativo: basta con poder asistir a uno.
# Las edades son condiciones inventadas del ejemplo, no asesoría legal.
OPORTUNIDADES = [
    {
        "id": 1, "titulo": "Apoyo de soporte tecnológico", "tipo": "Pasantía",
        "comuna": "valparaiso", "remota": False, "edad_min": 18,
        "experiencia_min": 0, "estudios_min": "media_completa",
        "intereses": ["tecnologia"], "horarios": ["tarde", "fin_semana"],
        "descripcion": "Aprende a orientar a usuarios y preparar equipos junto a un tutor ficticio.",
        "contacto": "soporte@example.com",
    },
    {
        "id": 2, "titulo": "Introducción al desarrollo web", "tipo": "Curso",
        "comuna": "vina", "remota": True, "edad_min": 16,
        "experiencia_min": 0, "estudios_min": "media_en_curso",
        "intereses": ["tecnologia"], "horarios": ["noche", "fin_semana"],
        "descripcion": "Curso ficticio para dar los primeros pasos en HTML y Python.",
        "contacto": "curso-web@example.com",
    },
    {
        "id": 3, "titulo": "Asistente de oficina", "tipo": "Empleo",
        "comuna": "quilpue", "remota": False, "edad_min": 18,
        "experiencia_min": 1, "estudios_min": "media_completa",
        "intereses": ["administracion"], "horarios": ["manana"],
        "descripcion": "Ejemplo de apoyo en organización de documentos y atención de consultas.",
        "contacto": "oficina@example.com",
    },
    {
        "id": 4, "titulo": "Atención en tienda", "tipo": "Empleo",
        "comuna": "vina", "remota": False, "edad_min": 18,
        "experiencia_min": 0, "estudios_min": "media_en_curso",
        "intereses": ["ventas"], "horarios": ["tarde", "fin_semana"],
        "descripcion": "Oferta ficticia de orientación a clientes y organización de productos.",
        "contacto": "tienda@example.com",
    },
    {
        "id": 5, "titulo": "Herramientas digitales para oficinas", "tipo": "Curso",
        "comuna": "valparaiso", "remota": True, "edad_min": 16,
        "experiencia_min": 0, "estudios_min": "media_en_curso",
        "intereses": ["tecnologia", "administracion"], "horarios": ["manana"],
        "descripcion": "Ejemplo de capacitación inicial en planillas y organización digital.",
        "contacto": "herramientas@example.com",
    },
    {
        "id": 6, "titulo": "Apoyo administrativo inicial", "tipo": "Pasantía",
        "comuna": "valparaiso", "remota": False, "edad_min": 18,
        "experiencia_min": 0, "estudios_min": "media_completa",
        "intereses": ["administracion"], "horarios": ["tarde"],
        "descripcion": "Ejemplo de acompañamiento en tareas de una oficina para principiantes.",
        "contacto": "pasantia@example.com",
    },
]
