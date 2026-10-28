# WorkConnect — Entregable III

Plataforma de demostración en Django: catálogo de empleos, pasantías y cursos,
con recomendaciones personalizadas según perfil y disponibilidad semanal.
Las seis oportunidades, organizaciones y contactos son ficticios.

## Ejecutar desde VS Code en Windows

Abre la carpeta C:\Users\rai77\Workconnect y una terminal PowerShell.
Utiliza el manage.py de la raíz, junto a este README.

Si quieres usar la instalación existente de este equipo:

~~~powershell
cd C:\Users\rai77\Workconnect
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' manage.py check
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' manage.py test workconnectapp --verbosity 2
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' manage.py runserver
~~~

Abre **http://127.0.0.1:8000/**. Para detener el servidor pulsa Ctrl+C.
Se comprobó con Python 3.14 y Django 6.1.2.

Para una instalación nueva, usa Python 3.12 o superior (se recomienda la versión
3.14 utilizada para probar este proyecto) y un entorno virtual:

~~~powershell
cd C:\Users\rai77\Workconnect
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test workconnectapp --verbosity 2
.\.venv\Scripts\python.exe manage.py runserver
~~~

Si el lanzador py muestra “No installed Python found!”, reemplaza el comando
de creación del entorno por esta ruta existente en este equipo:

~~~powershell
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' -m venv .venv
~~~

No necesitas activar el entorno ni cambiar la política de PowerShell.
El recomendador no requiere migraciones ni superusuario: no consulta ni guarda
datos en una base de datos. Se conserva Alumno y la configuración administrativa
existente; /admin/ no forma parte de esta entrega. No ejecutes migraciones para
intentar corregir el recomendador.

## Cómo usar la página

1. Al entrar se ve el **Catálogo general**, con todas las oportunidades.
   Las tarjetas muestran tipo, comuna, modalidad, bloques horarios, requisito de
   experiencia y descripción. Aquí todavía no hay recomendaciones ni puntos.
2. Pulsa **Tus preferencias** en el encabezado. En computador el formulario queda
   a la izquierda y las oportunidades a la derecha; en celular se apilan.
3. Completa comuna, edad, años de experiencia, estudios e intereses.
   La casilla “Mostrar solo oportunidades sin experiencia requerida” es opcional.
4. Marca cada día disponible y escribe Desde/Hasta en formato de 24 horas.
   Un día sin marcar es no disponible, incluso si conserva horas escritas.
5. Pulsa **Encontrar oportunidades**. Django valida, filtra y ordena; se muestran
   **Tus recomendaciones**, sus puntos y las razones de compatibilidad.
   El panel permanece abierto y conserva las respuestas.
6. **Cerrar panel** o volver a pulsar **Tus preferencias** centra las tarjetas
   sin borrar el formulario. **Volver al catálogo** o **Ver catálogo general**
   restaura todas las tarjetas y conserva las preferencias en esa respuesta.
7. **Contactar** (empleos/pasantías) o **Más información** (cursos) abre una ventana
   con la organización y el departamento ficticios. Se cierra con Cerrar,
   Escape o al pulsar fuera. Los enlaces mailto abren la aplicación de correo;
   WorkConnect no envía nada. La plantilla admite tel si se añade un teléfono,
   pero el catálogo no inventa números que puedan corresponder a personas reales.

No hay cuentas, base de datos de perfiles, almacenamiento del navegador ni APIs.
Las respuestas se conservan en el formulario durante esta navegación; entrar
nuevamente con el enlace del logo o recargar mediante una nueva visita puede
restablecerlas. Volver al catálogo funciona mediante POST, sin exigir completar
ni validar las preferencias para mostrar todas las oportunidades.

## Reglas sencillas del recomendador

**Requisitos obligatorios que descartan:**

- Oportunidad presencial en otra comuna (una remota sí puede ser de otra).
- Edad o experiencia inferiores al mínimo del ejemplo.
- Estudios inferiores al mínimo: media en curso, media completa, superior en
  curso, superior completa.
- Con la casilla sin experiencia activada, cualquier requisito mayor que cero.
- Algún bloque horario de la oportunidad no cabe completo en la disponibilidad.
- Oportunidad sin agenda conocida, con datos horarios inválidos o con un turno
  que cruza medianoche. Puede verse en el catálogo, pero no recomendarse.

**Disponibilidad:**

Todos los bloques de una oportunidad son **obligatorios**, no turnos alternativos.
Por ejemplo, soporte exige lunes 17:00–19:00 **y** sábado 10:00–12:00.
Debes poder asistir a los dos. Cada bloque debe caber en un intervalo del mismo
día; no basta un solapamiento parcial. Se aceptan límites iguales: disponibilidad
17:00–19:00 cubre una oportunidad 17:00–19:00, pero 17:01–19:00 no la cubre.

El formulario ofrece **un intervalo por día**. La función puede evaluar varios
intervalos por día si en el futuro se amplía el formulario, pero no une dos
intervalos parciales para cubrir un bloque. No se admiten turnos nocturnos que
crucen medianoche ni agendas por fechas; es una semana genérica en hora local.
Un día marcado exige ambas horas válidas, con inicio estrictamente anterior
al término. Se debe marcar al menos un día.

**Afinidad:**

- 2 puntos por cada interés coincidente.
- 1 punto por misma comuna, también en oportunidades remotas.
- La experiencia nunca suma puntos ni da prioridad a una persona más experimentada.
- No tener intereses en común no descarta una oportunidad que cumple requisitos.
- Los empates se ordenan por identificador del catálogo.

Los puntos no son porcentajes ni probabilidades de contratación.
El servicio crea diccionarios de resultados sin modificar el catálogo original.

## Dos perfiles exactos para el video

En ambos casos deja la casilla **sin experiencia desmarcada** y todos los días
no indicados **sin marcar**.

| Campo | Caso 1: con recomendaciones | Caso 2: sin coincidencias |
|---|---|---|
| Comuna | Valparaíso | Quilpué |
| Edad | 19 | 19 |
| Años de experiencia | 0 | 1 |
| Estudios | Enseñanza media completa | Enseñanza media completa |
| Intereses | Solo Tecnología | Solo Administración |
| Lunes disponible | Sí, 17:00 a 22:00 | Sí, 17:00 a 19:00 |
| Sábado disponible | Sí, 10:00 a 12:00 | No |
| Otros días | No disponibles | No disponibles |

**Caso 1:** aparecen, en este orden:

1. Apoyo de soporte tecnológico: **3 puntos**.
2. Introducción al desarrollo web: **2 puntos**.
3. Apoyo administrativo inicial: **1 punto**.

El primer ejemplo cumple los dos bloques obligatorios. El curso es remoto.
La tercera recomendación no comparte intereses, pero cumple requisitos y horario.

**Caso 2:** aparece “No encontramos oportunidades compatibles”.
La oficina de Quilpué exige lunes 09:00–13:00; los cursos remotos tampoco caben.

Para demostrar el efecto del horario, en el caso 2 cambia **solo el lunes** a
09:00–13:00: aparecen Asistente de oficina (3 puntos) y Herramientas digitales
para oficinas (2 puntos). Luego marca **sin experiencia**: queda únicamente
Herramientas digitales para oficinas, porque la oficina exige un año.

## Pruebas y arquitectura

Las dos pruebas originales se adaptaron a intervalos reales. La suite tiene
**14 pruebas**: perfiles con/sin resultados, catálogo inicial, rutas y plantillas,
descubrimiento de CSS/JS, contactos, retorno al catálogo conservando valores,
casilla sin experiencia, experiencia sin puntos extra, límites horarios,
solapamientos parciales, todos los bloques obligatorios, ausencia de horarios,
validaciones y CSRF. Todas usan SimpleTestCase y no crean base de datos.

Resultado de la verificación: **14 pruebas aprobadas** y **manage.py check sin
problemas**. También se comprobó con Edge sin ventana, en tamaños de ventana
1280×1000 y 390×844: catálogo, apertura/cierre de preferencias conservando horas,
habilitación de controles, apertura/cierre de contactos, envío real a Django,
tres recomendaciones y retorno al catálogo con preferencias conservadas.
No se detectó desbordamiento horizontal en esas comprobaciones. La revisión
en un teléfono físico y la grabación del video siguen a cargo del equipo.

Se añadió una prueba del perfil reportado: Valparaíso, 19 años, cero experiencia,
Educación superior en curso, los tres intereses y los siete días de 11:00 a
22:00, sin activar el filtro sin experiencia. El resultado comprobado es Apoyo
administrativo inicial (3 puntos), seguido de Introducción al desarrollo web
(2 puntos). El servicio, la respuesta HTML y el envío desde Edge coinciden.

En el diagnóstico sí se reprodujo cero en el servidor que ya estaba abierto
en el puerto 8000: conservaba una vista anterior que pasaba recomendaciones,
pero no oportunidades, el nombre que ahora utiliza la plantilla. El catálogo
inicial también aparecía vacío. Al activar la recarga de Django actualizando
solo la fecha de views.py (sin cambiar su contenido), ese mismo servidor mostró
las seis tarjetas del catálogo y las dos recomendaciones correctas. No fue
necesario modificar las reglas, los estudios ni las agendas. Si después de
actualizar el proyecto aparece un comportamiento antiguo, detén runserver con
Ctrl+C, ejecútalo nuevamente desde esta carpeta y recarga el navegador.

| Archivo | Para qué sirve |
|---|---|
| workconnectapp/datos.py | Opciones, días y seis oportunidades con agendas y contactos ficticios. |
| workconnectapp/forms.py | Recibe el perfil, valida horas y construye la disponibilidad. |
| workconnectapp/services.py | Comprueba requisitos y horarios, calcula puntos y prepara resultados. |
| workconnectapp/views.py | Decide si mostrar catálogo o recomendaciones y pasa datos al HTML. |
| templates/workconnectapp/index.html | Página, formulario y panel de preferencias. |
| templates/workconnectapp/tarjeta.html | Tarjeta reutilizada en catálogo y recomendaciones, con contacto. |
| static/workconnectapp/styles.css | Colores, tamaños y distribución adaptable. |
| static/workconnectapp/app.js | Abre/cierra preferencias y contactos; activa las horas de cada día. |
| workconnectapp/tests.py | Comprueba el comportamiento del servidor y las reglas. |

Se mantienen las rutas existentes. JavaScript solo controla la presentación:
**el filtrado se ejecuta en Python dentro de Django**, no en el navegador.
Si JavaScript está desactivado, el formulario sigue visible y los contactos
pueden abrirse como detalles de texto.

## Pendientes y alcance

La versión final todavía necesita definir la segunda funcionalidad priorizada y
la persistencia, API pública u otra característica aprobada por el equipo docente.
No se añadieron autenticación, persistencia, APIs, imágenes externas, frameworks
de interfaz, despliegue ni push a GitHub.

Para el Entregable III faltan las tareas del equipo: documentar lo observado en
sus pruebas de navegador, completar estado, planificación y riesgos de la matriz
real, grabar un video de máximo cinco minutos y verificar permisos de los enlaces.
No inventar resultados observados ni identificadores de riesgos.

Antes de esta ampliación se creó el commit local **d72e247** como respaldo del
código previo. No incluye la base de datos ni archivos automáticos de Python.
