"""Catálogo ficticio: no son vacantes ni cursos vigentes."""

# Cada opción relaciona la clave que usa Python con el nombre que muestra Django.
COMUNAS = [
    ("valparaiso", "Valparaíso"),
    ("vina", "Viña del Mar"),
    ("quilpue", "Quilpué"),
]
INTERESES = [
    ("tecnologia", "Tecnología"),
    ("administracion", "Administración"),
    ("ventas", "Ventas"),
]
DIAS = [
    ("lunes", "Lunes"),
    ("martes", "Martes"),
    ("miercoles", "Miércoles"),
    ("jueves", "Jueves"),
    ("viernes", "Viernes"),
    ("sabado", "Sábado"),
    ("domingo", "Domingo"),
]
# Este orden permite comparar los estudios del perfil con el mínimo solicitado.
ESTUDIOS = [
    ("media_en_curso", "Enseñanza media en curso"),
    ("media_completa", "Enseñanza media completa"),
    ("superior_en_curso", "Educación superior en curso"),
    ("superior_completa", "Educación superior completa"),
]

# Cada diccionario contiene los requisitos, horarios y contacto de una oportunidad.
# Todos los bloques de cada oportunidad son obligatorios, dentro del mismo día.
# Las edades son condiciones inventadas del ejemplo, no asesoría legal.
OPORTUNIDADES = [
    {
        "id": 1,
        "titulo": "Apoyo de soporte tecnológico",
        "tipo": "Pasantía",
        "comuna": "valparaiso",
        "remota": False,
        "edad_min": 18,
        "experiencia_min": 0,
        "estudios_min": "media_completa",
        "intereses": ["tecnologia"],
        "horarios": [
            {"dia": "lunes", "inicio": "17:00", "fin": "19:00"},
            {"dia": "sabado", "inicio": "10:00", "fin": "12:00"},
        ],
        "descripcion": "Aprende a orientar a usuarios y preparar equipos junto a un tutor ficticio.",
        "contacto": {
            "empresa": "Laboratorio Horizonte (ficticio)",
            "persona": "Departamento de prácticas",
            "email": "soporte@example.com",
        },
    },
    {
        "id": 2,
        "titulo": "Introducción al desarrollo web",
        "tipo": "Curso",
        "comuna": "vina",
        "remota": True,
        "edad_min": 16,
        "experiencia_min": 0,
        "estudios_min": "media_en_curso",
        "intereses": ["tecnologia"],
        "horarios": [
            {"dia": "lunes", "inicio": "20:00", "fin": "22:00"},
        ],
        "descripcion": "Curso ficticio para dar los primeros pasos en HTML y Python.",
        "contacto": {
            "empresa": "Aula Semilla (ficticia)",
            "persona": "Inscripciones al curso web",
            "email": "curso-web@example.com",
        },
    },
    {
        "id": 3,
        "titulo": "Asistente de oficina",
        "tipo": "Empleo",
        "comuna": "quilpue",
        "remota": False,
        "edad_min": 18,
        "experiencia_min": 1,
        "estudios_min": "media_completa",
        "intereses": ["administracion"],
        "horarios": [
            {"dia": "lunes", "inicio": "09:00", "fin": "13:00"},
        ],
        "descripcion": "Ejemplo de apoyo en organización de documentos y atención de consultas.",
        "contacto": {
            "empresa": "Oficina Brote (ficticia)",
            "persona": "Departamento de selección",
            "email": "oficina@example.com",
        },
    },
    {
        "id": 4,
        "titulo": "Atención en tienda",
        "tipo": "Empleo",
        "comuna": "vina",
        "remota": False,
        "edad_min": 18,
        "experiencia_min": 0,
        "estudios_min": "media_en_curso",
        "intereses": ["ventas"],
        "horarios": [
            {"dia": "sabado", "inicio": "14:00", "fin": "18:00"},
        ],
        "descripcion": "Oferta ficticia de orientación a clientes y organización de productos.",
        "contacto": {
            "empresa": "Tienda Turquesa (ficticia)",
            "persona": "Equipo de postulaciones",
            "email": "tienda@example.com",
        },
    },
    {
        "id": 5,
        "titulo": "Herramientas digitales para oficinas",
        "tipo": "Curso",
        "comuna": "valparaiso",
        "remota": True,
        "edad_min": 16,
        "experiencia_min": 0,
        "estudios_min": "media_en_curso",
        "intereses": ["tecnologia", "administracion"],
        "horarios": [
            {"dia": "lunes", "inicio": "09:00", "fin": "11:00"},
        ],
        "descripcion": "Ejemplo de capacitación inicial en planillas y organización digital.",
        "contacto": {
            "empresa": "Escuela Raíz (ficticia)",
            "persona": "Inscripciones a herramientas digitales",
            "email": "herramientas@example.com",
        },
    },
    {
        "id": 6,
        "titulo": "Apoyo administrativo inicial",
        "tipo": "Pasantía",
        "comuna": "valparaiso",
        "remota": False,
        "edad_min": 18,
        "experiencia_min": 0,
        "estudios_min": "media_completa",
        "intereses": ["administracion"],
        "horarios": [
            {"dia": "lunes", "inicio": "18:00", "fin": "20:00"},
        ],
        "descripcion": "Ejemplo de acompañamiento en tareas de una oficina para principiantes.",
        "contacto": {
            "empresa": "Proyecto Marea (ficticio)",
            "persona": "Coordinación de pasantías",
            "email": "pasantia@example.com",
        },
    },
]
