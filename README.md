# Proyecto Taller ISI

## Descripción

Proyecto desarrollado en Python como parte de la asignatura Taller de Proyecto ISI.

La aplicación consiste en una plataforma web de preguntas y respuestas, donde los usuarios pueden registrarse, iniciar sesión, publicar preguntas y responder a las consultas de otros usuarios.

Además, incorpora un agente de inteligencia artificial que puede generar respuestas automáticamente utilizando distintos proveedores de IA.

## Funcionalidades principales

### Usuarios
- Registro de nuevos usuarios.
- Inicio y cierre de sesión.
- Visualización de usuarios.
- Consulta del perfil de cada usuario.

### Preguntas y respuestas
- Publicación de preguntas.
- Visualización del listado de preguntas.
- Consulta del detalle de cada pregunta.
- Publicación de respuestas.
- Asociación de preguntas con categorías y etiquetas.
- Gestión de respuestas aceptadas.

### Agente de inteligencia artificial

El sistema incorpora un agente de IA que permite generar respuestas automáticas a las preguntas mediante diferentes proveedores:

- Google Gemini.
- OpenAI.
- Anthropic Claude.

El agente utiliza el patrón de diseño **Strategy**, permitiendo seleccionar e intercambiar el proveedor de inteligencia artificial.

También contempla:
- Respuestas automáticas a preguntas identificadas con la etiqueta `#ia-help`.
- Tiempo de espera configurable antes de responder preguntas sin respuestas.
- Prevención de respuestas duplicadas del agente.

## Tecnologías utilizadas

| Tecnología | Utilización |
|---|---|
| Python 3.14+ | Lenguaje principal |
| Flask | Framework web |
| Flask-SQLAlchemy | ORM y persistencia |
| SQLite | Base de datos |
| Alembic | Migraciones de base de datos |
| Google Gemini | Inteligencia artificial |
| OpenAI | Inteligencia artificial |
| Anthropic Claude | Inteligencia artificial |
| HTML / CSS | Interfaz web |
| pytest | Pruebas automatizadas |
| Ruff | Análisis y calidad del código |
| uv | Gestión de dependencias y entorno |

## Estructura del proyecto

```text
ProyectoTaller.ISI/
│
├── migrations/
│   └── versions/
│
├── src/
│   └── myapp/
│       ├── api/
│       ├── models/
│       ├── services/
│       │   └── ai_agent.py
│       ├── web/
│       ├── templates/
│       ├── static/
│       ├── config.py
│       ├── extensions.py
│       └── __init__.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md
```

### Organización del código

- **api:** endpoints de la API.
- **models:** modelos y entidades del sistema.
- **services:** lógica de negocio y servicios, incluido el agente de inteligencia artificial.
- **web:** rutas y funcionalidades de la aplicación web.
- **templates:** plantillas HTML.
- **static:** archivos estáticos, como CSS.
- **migrations:** migraciones para mantener actualizada la estructura de la base de datos.
- **tests:** pruebas automatizadas del proyecto.

## Instalación y configuración

### 1. Requisitos previos

Para ejecutar el proyecto se necesita:

- Python 3.14 o superior.
- uv.
- Git.

### 2. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

Ingresar a la carpeta:

```bash
cd ProyectoTaller.ISI
```

### 3. Instalar las dependencias

```bash
uv sync --all-groups
```

Este comando instala las dependencias necesarias para ejecutar el proyecto y realizar las pruebas.

### 4. Configurar las variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Se puede utilizar `.env.example` como referencia.

El archivo debe contener:

```env
SECRET_KEY=development-only-key
DATABASE_URL=sqlite:///app.db

GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

AI_AGENT_WAIT_MINUTES=5
```

Las claves de las distintas plataformas de inteligencia artificial son independientes.

Para utilizarlas, es necesario obtenerlas desde sus respectivas plataformas:

- Gemini: https://aistudio.google.com/api-keys
- OpenAI: https://platform.openai.com/api-keys
- Claude: https://console.anthropic.com/settings/keys

Se debe completar únicamente la clave del proveedor que se desea utilizar.

**Importante:** el archivo `.env` contiene información privada y no debe subirse al repositorio. Debe estar incluido en `.gitignore`.

### 5. Ejecutar las migraciones

En PowerShell:

```powershell
$env:PYTHONPATH = "src"
uv run alembic upgrade head
```

Esto crea y actualiza las tablas necesarias en la base de datos SQLite.

### 6. Ejecutar la aplicación

Desde la raíz del proyecto:

```powershell
$env:PYTHONPATH = "src"
uv run flask --app "myapp:create_app" run --debug
```

Una vez iniciada la aplicación, ingresar desde el navegador a:

http://127.0.0.1:5000

## Pruebas automatizadas

Para ejecutar los tests del proyecto:

```powershell
$env:PYTHONPATH = "src"
uv run pytest
```

Para ejecutar las pruebas mostrando información detallada:

```powershell
uv run pytest -v
```

## Base de datos

El proyecto utiliza SQLite como sistema de gestión de base de datos predeterminado.

La estructura se administra mediante Alembic, que permite aplicar migraciones y mantener sincronizado el esquema de la base de datos con los modelos de la aplicación.

Entre las entidades principales se encuentran:

- Users
- Categories
- Tags
- Questions
- Answers
- QuestionTags

## Inteligencia artificial

La integración de los proveedores de IA se implementa mediante estrategias independientes.

Esto permite que el sistema pueda cambiar de proveedor sin modificar la lógica general del agente.

Los proveedores disponibles son:

- GeminiStrategy
- OpenAIStrategy
- ClaudeStrategy

La selección del modelo se realiza mediante el servicio de IA, utilizando las claves de acceso configuradas en las variables de entorno.

