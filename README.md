# WorkConnect — Entregable III

Versión mínima de la funcionalidad corazón: recibir un perfil, procesarlo en
Django y mostrar oportunidades compatibles con motivos y puntos de afinidad.
Todo el catálogo es ficticio y está identificado como demostración.

## Ejecutar en Windows y VS Code

Abre la carpeta `C:\Users\rai77\Workconnect` en VS Code y una terminal PowerShell.
Usa el `manage.py` de la raíz, junto a este README, no el que está dentro de
`workconnect`.

La implementación se comprobó con Python 3.14 y Django 6.1.2. La dependencia
de Django declara Python 3.12 o superior. No necesitas instalar una base de
datos adicional.

Primera instalación (crea un entorno separado para las dependencias):

```powershell
cd C:\Users\rai77\Workconnect
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si `py` muestra `No installed Python found!`, en este equipo se encontró Python
en la siguiente ruta. Sustituye **solo el comando de creación del entorno** por:

```powershell
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Después, comprueba y ejecuta la aplicación:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test workconnectapp --verbosity 2
.\.venv\Scripts\python.exe manage.py runserver
```

Abre **http://127.0.0.1:8000/** en tu navegador. Detén el servidor con `Ctrl+C`.
No es necesario activar el entorno virtual ni cambiar la política de PowerShell:
los comandos usan directamente su Python.

Para usar inmediatamente la instalación existente de este equipo, sin crear
otro entorno (ya tenía Django 6.1.2 al realizar esta revisión):

```powershell
cd C:\Users\rai77\Workconnect
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' manage.py check
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' manage.py test workconnectapp --verbosity 2
& 'C:\Users\rai77\AppData\Local\Programs\Python\Python314\python.exe' manage.py runserver
```

El recomendador no necesita `makemigrations`, `migrate` ni superusuario. Si Django
avisa de migraciones pendientes al iniciar, ese aviso corresponde a las funciones
de base de datos del proyecto; el flujo de recomendaciones no las utiliza.
El modelo `Alumno`, su registro administrativo y la base existente se conservan.
El panel `/admin/` no forma parte de esta implementación.

## Entrada, procesamiento y salida

1. La persona elige comuna, edad, años completos de experiencia, estudios,
   intereses y uno o varios horarios.
2. Django valida los datos y una función de Python recorre seis oportunidades.
3. La página muestra los resultados ordenados y explica sus coincidencias.
   Si no hay resultados, invita a modificar las respuestas. El formulario
   conserva las selecciones al mostrar el resultado o los errores.

Se comprueban campos obligatorios, opciones admitidas, edad de 1 a 120,
experiencia de 0 a 100 y que la experiencia no supere la edad. Es una validación
simple para la demostración, no una evaluación laboral o legal.

### Requisitos que descartan una oportunidad

- Presencial en otra comuna. Las remotas pueden estar en cualquier comuna.
- Edad inferior al mínimo del ejemplo.
- Experiencia inferior al mínimo del ejemplo.
- Estudios por debajo del mínimo. Orden simplificado: media en curso,
  media completa, superior en curso, superior completa.
- Ningún horario de la oportunidad coincide con la disponibilidad.

Los horarios `Mañana`, `Tarde`, `Noche` y `Fines de semana` son opciones
independientes. En este catálogo representan **turnos alternativos**: basta con
coincidir en uno, no es necesario poder asistir a todos. Las oportunidades
remotas también deben cumplir el requisito horario.

### Preferencias que solo suman afinidad

- Cada interés compartido suma **2 puntos**.
- La misma comuna suma **1 punto**, también en oportunidades remotas.
- No compartir intereses no descarta una oportunidad que cumple los requisitos.
- Edad, experiencia, estudios y horarios habilitan la participación, sin sumar.

Se ordena de mayor a menor puntuación y los empates por identificador ascendente.
Son puntos, no porcentajes ni probabilidades de contratación. Cada tarjeta
explica ubicación/modalidad, turnos coincidentes, requisitos e intereses.
Los contactos `example.com` son ficticios, se muestran como texto y no se envían
mensajes ni postulaciones.

## Dos casos para probar en el navegador y en el video

| Campo | Caso 1: con coincidencias | Caso 2: sin coincidencias |
|---|---|---|
| Comuna | Valparaíso | Quilpué |
| Edad | 19 | 19 |
| Experiencia | 0 | 1 |
| Estudios | Enseñanza media completa | Enseñanza media completa |
| Intereses | Tecnología | Administración |
| Horarios | Tarde y Fines de semana | Tarde |

**Resultado esperado del caso 1**, en este orden:

1. Apoyo de soporte tecnológico: **3 puntos**.
2. Introducción al desarrollo web: **2 puntos** (remota).
3. Apoyo administrativo inicial: **1 punto** (sin interés compartido).

El curso de herramientas digitales no aparece porque solo ofrece mañana.

**Resultado esperado del caso 2:** “No encontramos oportunidades compatibles”.
La oficina de Quilpué requiere mañana, los cursos remotos tampoco ofrecen tarde,
y las otras oportunidades presenciales pertenecen a otra comuna.

Como comprobación adicional del segundo caso, cambiar solo el horario a
**Mañana** devuelve Asistente de oficina (3 puntos) y Herramientas digitales para
oficinas (2 puntos). Esto permite observar que el horario modifica el resultado.

Las dos pruebas de `tests.py` envían el formulario mediante el cliente de Django
y comprueban resultados HTML, orden, puntos y motivos. La segunda también
comprueba el cambio de horario. Se usa `SimpleTestCase`, sin crear una base de
datos de pruebas. En el entorno revisado ambas pasaron y `manage.py check`
informó que no había problemas. Falta que el equipo ejecute y documente sus
casos en el navegador para el informe y el video.

## Mapa sencillo del código

| Archivo | Responsabilidad |
|---|---|
| `workconnectapp/forms.py` | Preguntas y validación del perfil. |
| `workconnectapp/datos.py` | Opciones y oportunidades de demostración, con listas y diccionarios. |
| `workconnectapp/services.py` | Función `recomendar`: filtra, puntúa y ordena sin cambiar el catálogo. |
| `workconnectapp/views.py` | Conecta el formulario, la función y el HTML. |
| `workconnectapp/templates/workconnectapp/index.html` | Formulario, errores, resultados y reglas explicadas. |
| `workconnectapp/static/workconnectapp/styles.css` | Diseño verde y turquesa, adaptable a pantalla pequeña. |
| `workconnectapp/tests.py` | Los dos casos automatizados. |
| `requirements.txt` | Versión de Django utilizada. |

La dirección `/` ya estaba conectada en ambos archivos `urls.py`; se reutiliza.
Se configuraron idioma español y zona horaria de Santiago. Los estilos se
descubren en la carpeta `static` de la aplicación mediante Django.

Para explicar el código en el video, puede mostrarse el bloque de filtrado
de `recomendar` y cómo `views.py` le pasa `formulario.cleaned_data`: significa
que se usan las respuestas que Django ya comprobó. Una decisión técnica es
separar requisitos obligatorios de preferencias que solo suman puntos.

## Alcance y pendientes de la entrega

Se implementa solo el recomendador. No incorpora registro, almacenamiento de
perfiles, APIs, envío de mensajes, favoritos ni funcionalidades secundarias.
No se ha hecho push al repositorio. El diseño es una interpretación sencilla
en verde y turquesa, no una reproducción exacta del prototipo.

Para completar el Entregable III, el equipo todavía debe completar el documento
oficial con sus resultados observados, estado de las tres funcionalidades,
tareas, responsables, plazos y riesgos reales de su matriz; grabar el video
de máximo cinco minutos y verificar acceso al video y al repositorio. No
inventar resultados observados ni identificadores de riesgos.
