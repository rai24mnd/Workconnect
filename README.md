# WorkConnect — Versión Final

Prototipo académico en Django que muestra empleos y prácticas, y recomienda
oportunidades según el perfil y la disponibilidad semanal de la persona.
Los datos de las cuentas, preferencias y ofertas se guardan en SQLite.
Utiliza Python, Django, HTML, CSS y JavaScript, sin servicios de inteligencia artificial.

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
3. Instala las dependencias:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Genera una clave local en `.env`. Este comando no muestra la clave y no
   sobrescribe el archivo si ya existe:

   ```powershell
   .\.venv\Scripts\python.exe -c "from pathlib import Path; import secrets; Path('.env').open('x', encoding='utf-8').write('SECRET_KEY=' + secrets.token_urlsafe(64) + '\n')"
   ```

   Django lee `SECRET_KEY` desde el entorno o desde `.env`. Si falta, muestra un
   error de configuración. No compartas ni subas `.env` al repositorio.
5. Aplica las migraciones, comprueba la configuración e inicia Django:

   ```powershell
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py check
   .\.venv\Scripts\python.exe manage.py runserver
   ```

6. Abre **http://127.0.0.1:8000/**. Detén el servidor con **Ctrl+C**.

No es necesario activar el entorno virtual. Para crear o restaurar las cuatro
ofertas ficticias de demostración, puedes ejecutar antes de iniciar el servidor:

```powershell
.\.venv\Scripts\python.exe manage.py cargar_demo
```

Este comando conserva las publicaciones de las empresas. Las demostraciones
no tienen sueldos asignados: muestran **No informado**.

## Uso básico

1. Al entrar debes iniciar sesión o crear una cuenta. Elige **Busco oportunidades**
   o **Represento a una empresa**, según corresponda.
2. Para buscar oportunidades, el registro pide comuna, edad, experiencia,
   estudios, intereses y disponibilidad semanal. Marca tus días y sus horas de
   inicio y término. Después puedes revisar **Mi perfil** y **Editar mis preferencias**
   desde el icono de usuario.
3. Las empresas tienen su propio perfil y panel para publicar, editar y eliminar
   sus ofertas. Cada empresa administra solamente sus publicaciones.
4. En el **Catálogo general** puedes buscar por título o descripción y abrir
   **Filtros** para acotar por comuna, modalidad, experiencia, estudios, intereses
   o disponibilidad. **Borrar búsqueda** y **Limpiar filtros** permiten empezar de
   nuevo. Estas consultas no cambian las preferencias guardadas.
5. En **Mis recomendaciones** se usan tus preferencias guardadas. Se revisan
   ubicación, edad, experiencia, estudios y horarios. Un horario fijo exige todos
   sus bloques; con varias opciones basta una alternativa completa, sin mezclar
   días de alternativas distintas. Lo negociable o desconocido queda pendiente
   de confirmar, salvo que exista otro requisito incumplido.
   Las compatibles se ordenan por afinidad: cada interés compartido suma 2 puntos
   y la misma comuna suma 1. No compartir intereses no descarta una oferta. En
   empate aparece primero la de menor identificador. Compatibles, pendientes e
   incompatibles se distinguen por separado; las recomendaciones muestran las
   compatibles y las pendientes.
6. Las tarjetas muestran empresa, descripción y funciones, ubicación, modalidad,
   horarios y requisitos. También muestran el sueldo en CLP y su período mensual,
   semanal o por hora, o los estados **A convenir** y **No informado**. La empresa
   puede editar esta información.
7. Usa **Contactar** para abrir el contacto o método de postulación. La ventana se
   cierra con **Cerrar**, **Escape** o al pulsar fuera. El enlace de correo abre tu
   aplicación de correo; WorkConnect no envía mensajes.

El enlace a **SENCE** abre un buscador externo de capacitaciones. Sus cursos no
están integrados al catálogo ni al recomendador de WorkConnect.

## Comprobaciones manuales

Usa una instalación de prueba con una base SQLite separada de tus datos habituales.
Comprueba estos recorridos en escritorio y en una ventana de 375 píxeles de ancho:

1. Registra un joven, inicia sesión, cambia intereses y disponibilidad, y vuelve
   a entrar para comprobar que las preferencias se conservaron.
2. Registra una empresa, completa su perfil y publica una oferta. Edita el sueldo
   mensual, semanal o por hora y prueba también **A convenir** y **No informado**.
3. Entra con otra empresa: no debe poder editar ni eliminar esa publicación.
   Un joven tampoco debe poder acceder al panel empresarial.
4. Busca texto y combina filtros del catálogo. Vuelve a tus preferencias:
   la consulta no debe haberlas cambiado. Revisa los detalles y **Contactar**.
5. Prueba horarios fijos, alternativas completas y horarios flexibles. Comprueba
   que una oferta sin intereses compartidos pueda ser compatible, que los
   requisitos incumplidos la descarten y que los datos desconocidos queden pendientes.
6. Cierra el servidor y vuelve a abrirlo: cuentas, preferencias y ofertas deben
   conservarse. Comprueba también el menú de usuario y el cierre de sesión.

Los dos casos siguientes permiten revisar el orden y los puntos del recomendador.

Para estos casos usa las cuatro ofertas de demostración, sin otras publicaciones.
Registra una cuenta para buscar oportunidades o edita sus preferencias con estos
datos y abre **Mis recomendaciones**.

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
2. Apoyo administrativo inicial: **1 punto**.

**Resultado esperado del caso 2:** ninguna recomendación y el mensaje
**«No encontramos oportunidades compatibles»**.

Esta versión simplificada no incluye archivos de pruebas automatizadas.
Las 252 pruebas originales se ejecutaron antes y después de los cambios; para
volver a usarlas hay que recuperarlas de la versión anterior, conservada en el
historial de Git. El informe técnico y las evidencias se conservan localmente.

## Archivos principales

| Archivo | Función |
|---|---|
| `manage.py` | Ejecuta los comandos de Django desde la raíz del proyecto. |
| `requirements.txt` | Indica las dependencias que se deben instalar. |
| `workconnect/settings.py` | Configura el proyecto Django. |
| `workconnectapp/urls.py` | Conecta la dirección de la página con su vista. |
| `workconnectapp/datos.py` | Contiene las opciones y las cuatro ofertas de demostración. |
| `workconnectapp/forms.py` | Valida registro, acceso, preferencias, filtros y formularios de empresa. |
| `workconnectapp/services.py` | Comprueba compatibilidad, calcula puntos y ordena las recomendaciones. |
| `workconnectapp/views.py` | Gestiona las cuentas jóvenes, guarda preferencias y aplica filtros al catálogo. |
| `workconnectapp/models.py` | Define las cuentas, perfiles, ofertas y horarios que se guardan. |
| `workconnectapp/vistas_empresa.py` | Muestra el panel y permite guardar el perfil y las ofertas propias. |
| `workconnectapp/adaptadores.py` | Consulta las ofertas y prepara sus relaciones para las tarjetas y el recomendador. |
| `workconnectapp/permisos.py` | Comprueba la sesión y el tipo de cuenta antes de entrar en páginas privadas. |
| `workconnectapp/validaciones.py` | Comparte las reglas de horarios entre modelos y formularios. |
| `workconnectapp/migrations/` | Contiene los cambios de la base de datos. |
| `workconnectapp/templates/workconnectapp/` | Contiene la página y las tarjetas en HTML. |
| `workconnectapp/static/workconnectapp/` | Contiene los estilos y los controles de paneles, horarios y contactos. |

Las cuatro ofertas de demostración, sus organizaciones y sus contactos son **ficticios** y se
usan únicamente para esta demostración universitaria.
