# WorkConnect — Entregable III

Prototipo académico en Django que muestra empleos, pasantías y cursos, y recomienda
oportunidades según el perfil y la disponibilidad semanal de la persona.

## Requisitos

- Python 3.12 o superior y VS Code.
- Un navegador con JavaScript habilitado.
- Conexión a internet para instalar las dependencias de `requirements.txt`.

## Instalación y ejecución local

1. Abre en VS Code la carpeta del proyecto que contiene este README y `manage.py`.
2. Abre una terminal PowerShell y crea el entorno virtual:

   ```powershell
   py -m venv .venv
   ```

   Si tu equipo usa el comando `python` en lugar de `py`, ejecuta
   `python -m venv .venv`.
3. Instala las dependencias, comprueba la configuración e inicia Django:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe manage.py check
   .\.venv\Scripts\python.exe manage.py runserver
   ```

4. Abre **http://127.0.0.1:8000/**. Detén el servidor con **Ctrl+C**.

No es necesario activar el entorno virtual. El catálogo y el recomendador no
requieren migraciones ni crear usuarios.

## Uso básico

1. Al entrar aparece el **Catálogo general** con seis oportunidades.
2. Abre **Tus preferencias** y completa comuna, edad, experiencia, estudios e
   intereses. Puedes activar el filtro de oportunidades sin experiencia requerida.
3. Marca los días disponibles y escribe sus horas de inicio y término. Los días
   desmarcados no se consideran; debes cubrir todos los bloques de cada oportunidad.
4. Pulsa **Encontrar oportunidades** para ver las recomendaciones, sus puntos y
   motivos. **Cerrar panel** conserva los valores; **Volver al catálogo** o
   **Ver catálogo general** muestra nuevamente las seis oportunidades.
5. Usa **Contactar** o **Más información** para abrir el contacto. La ventana se
   cierra con **Cerrar**, **Escape** o al pulsar fuera. El enlace de correo abre tu
   aplicación de correo; WorkConnect no envía mensajes.

## Dos casos de prueba manuales

En ambos casos deja desactivado **Mostrar solo oportunidades sin experiencia
requerida** y desmarca todos los días que no se indican.

| Entrada | Caso 1 | Caso 2 |
|---|---|---|
| Comuna | Valparaíso | Quilpué |
| Edad | 19 años | 19 años |
| Experiencia | 0 años | 1 año |
| Estudios | Enseñanza media completa | Enseñanza media completa |
| Intereses | Solo Tecnología | Solo Administración |
| Lunes | 17:00–22:00 | 17:00–19:00 |
| Sábado | 10:00–12:00 | Desmarcado |

**Resultado esperado del caso 1**, en este orden:

1. Apoyo de soporte tecnológico: **3 puntos**.
2. Introducción al desarrollo web: **2 puntos**.
3. Apoyo administrativo inicial: **1 punto**.

**Resultado esperado del caso 2:** ninguna recomendación y el mensaje
**«No encontramos oportunidades compatibles»**.

## Archivos principales

| Archivo | Función |
|---|---|
| `manage.py` | Ejecuta los comandos de Django desde la raíz del proyecto. |
| `requirements.txt` | Indica las dependencias que se deben instalar. |
| `workconnect/settings.py` | Configura el proyecto Django. |
| `workconnectapp/urls.py` | Conecta la dirección de la página con su vista. |
| `workconnectapp/datos.py` | Contiene las opciones y las seis oportunidades. |
| `workconnectapp/forms.py` | Define el formulario y valida el perfil y los horarios. |
| `workconnectapp/services.py` | Filtra oportunidades, calcula puntos y ordena resultados. |
| `workconnectapp/views.py` | Prepara el catálogo o las recomendaciones para la página. |
| `workconnectapp/templates/workconnectapp/` | Contiene la página y las tarjetas en HTML. |
| `workconnectapp/static/workconnectapp/` | Contiene los estilos y los controles de paneles, horarios y contactos. |

Las seis oportunidades, sus organizaciones y sus contactos son **ficticios** y se
usan únicamente para esta demostración universitaria.
