# Sistema de Tickets — 1º DAM

Sistema de gestión de tickets de incidencias y sugerencias desarrollado con
Python 3 + Flask + SQLite. Proyecto evaluable para 1º DAM — Solutia Innovación
y Tecnología.

---

## Descripción del proyecto

Módulo de Feedback de Usuarios con Sistema de Tickets que permite:
- **Reporters**: crear tickets, ver sus propios tickets, añadir comentarios.
- **Agentes**: ver todos los tickets, asignarse tickets, cambiar estado, comentar.
- **Admins**: todo lo anterior + gestionar categorías, usuarios y ver estadísticas.

El sistema incluye interfaz web con Jinja2 y API REST JSON completa.

---

## Stack tecnológico

| Componente      | Tecnología                     |
|-----------------|--------------------------------|
| Backend         | Python 3.10+ con Flask         |
| Base de datos   | SQLite (archivo local)         |
| Autenticación   | Sesiones Flask                 |
| Seguridad       | Werkzeug (hashing), OWASP      |
| Testing         | pytest                         |
| CI/CD           | GitHub Actions                 |
| Frontend        | Jinja2 + CSS propio            |

---

## Estructura del proyecto

```
sistema_tickets/
│
├── app.py                  # Punto de entrada principal de Flask
├── config.py               # Configuración general (BD, secret key, etc.)
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Este archivo
│
├── database/
│   ├── __init__.py
│   ├── db.py               # Conexión y utilidades de base de datos
│   └── schema.sql          # Script SQL de creación de tablas
│
├── models/
│   ├── __init__.py
│   ├── user.py             # Modelo de usuario
│   ├── ticket.py           # Modelo de ticket
│   ├── comment.py          # Modelo de comentario
│   └── category.py         # Modelo de categoría
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Rutas de autenticación (login, registro)
│   ├── tickets.py          # Rutas CRUD de tickets
│   ├── comments.py         # Rutas de comentarios
│   └── admin.py            # Rutas de administración
│
├── middleware/
│   ├── __init__.py
│   └── auth_middleware.py  # Decoradores de autenticación y roles
│
├── templates/
│   ├── base.html           # Plantilla base con navegación
│   ├── auth/
│   │   ├── login.html
│   │   └── registro.html
│   ├── tickets/
│   │   ├── lista.html      # Listado de tickets con filtros
│   │   ├── detalle.html    # Detalle + comentarios
│   │   └── nuevo.html      # Formulario crear ticket
│   └── admin/
│       ├── dashboard.html  # Panel de administración
│       └── usuarios.html   # Gestión de usuarios
│
├── static/
│   └── css/
│       └── estilo.css      # CSS limpio y profesional
│
└── tests/
    ├── __init__.py
    ├── conftest.py         # Fixtures de pytest
    ├── test_auth.py        # Tests de autenticación
    ├── test_tickets.py     # Tests de tickets
    └── test_comments.py    # Tests de comentarios
```

---

## Instalación y configuración

### Requisitos previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd sistema_tickets

# 2. Crear un entorno virtual
python -m venv venv

# 3. Activar el entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

### Variables de entorno

| Variable     | Descripción                        | Valor por defecto               |
|--------------|------------------------------------|---------------------------------|
| `SECRET_KEY` | Clave secreta para sesiones Flask  | `dev-secret-key-cambiar-en-produccion` |

**Importante:** En producción, configura `SECRET_KEY` como variable de entorno:

```bash
# Windows
set SECRET_KEY=tu-clave-secreta-segura

# Linux/Mac
export SECRET_KEY=tu-clave-secreta-segura
```

---

## Cómo ejecutar el proyecto

```bash
# Desde el directorio sistema_tickets/
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

La base de datos se crea automáticamente al iniciar la aplicación.

---

## Endpoints de la API

Todas las respuestas siguen el formato: `{ "data": ..., "error": null }` o
`{ "data": null, "error": "mensaje" }`.

### Autenticación

| Método | Endpoint              | Descripción              | Acceso    |
|--------|-----------------------|--------------------------|-----------|
| POST   | `/api/auth/registro`  | Registro de usuario      | Público   |
| POST   | `/api/auth/login`     | Inicio de sesión         | Público   |

### Tickets

| Método | Endpoint              | Descripción                    | Acceso     |
|--------|-----------------------|--------------------------------|------------|
| POST   | `/api/tickets`        | Crear ticket                   | reporter+  |
| GET    | `/api/tickets`        | Listar tickets (filtros/pag.)  | reporter+  |
| GET    | `/api/tickets/<id>`   | Ver detalle de un ticket       | reporter+  |
| PATCH  | `/api/tickets/<id>`   | Actualizar estado/asignar      | agente+    |
| DELETE | `/api/tickets/<id>`   | Eliminar ticket                | admin      |

### Comentarios

| Método | Endpoint                         | Descripción               | Acceso     |
|--------|----------------------------------|---------------------------|------------|
| POST   | `/api/tickets/<id>/comments`     | Añadir comentario         | reporter+  |
| GET    | `/api/tickets/<id>/comments`     | Listar comentarios        | reporter+  |

### Administración

| Método | Endpoint                  | Descripción             | Acceso    |
|--------|---------------------------|-------------------------|-----------|
| GET    | `/api/admin/categorias`   | Listar categorías       | reporter+ |
| POST   | `/api/admin/categorias`   | Crear categoría         | admin     |
| GET    | `/api/admin/usuarios`     | Listar usuarios         | admin     |
| GET    | `/api/admin/stats`        | Estadísticas generales  | admin     |

---

## Roles y permisos

| Rol       | Permisos                                                              |
|-----------|-----------------------------------------------------------------------|
| reporter  | Crear tickets, ver propios tickets, añadir comentarios                |
| agente    | Ver todos los tickets, asignarse tickets, cambiar estado, comentar    |
| admin     | Todo lo anterior + gestionar categorías, usuarios y estadísticas      |

---

## Diseño de base de datos

```
┌─────────────────┐       ┌─────────────────┐
│     users        │       │   categories     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ name (UNIQUE)   │
│ email (UNIQUE)  │       └────────┬────────┘
│ pass_hash       │                │
│ role            │       ┌────────┴────────┐
│ created_at      │       │    tickets       │
└──┬──────────┬───┘       ├─────────────────┤
   │          │           │ id (PK)         │
   │ user_id  │           │ user_id (FK)    │──→ users
   │          │           │ category_id(FK) │──→ categories
   │          │           │ title           │
   │          │           │ body            │
   │          │           │ priority        │
   │          │           │ status          │
   │          │assignee_id│ assignee_id(FK) │──→ users
   │          └───────────│ created_at      │
   │                      │ updated_at      │
   │                      └────────┬────────┘
   │                               │
   │  ┌────────────────────────────┘
   │  │  ┌──────────────────────┐
   │  │  │  ticket_comments     │
   │  │  ├──────────────────────┤
   │  │  │ id (PK)             │
   │  └──│ ticket_id (FK)      │──→ tickets (CASCADE)
   └─────│ user_id (FK)        │──→ users
          │ body               │
          │ created_at         │
          └────────────────────┘
```

---

## Ejecución de tests

```bash
# Desde el directorio sistema_tickets/
python -m pytest tests/ -v
```

Los tests cubren:
- Registro válido e inválido
- Login correcto e incorrecto
- Creación de tickets (válido, sin auth, título corto)
- Listado con paginación
- Comentarios (crear, listar, ticket inexistente)
- Cambio de estado por roles (agente vs reporter)
- Eliminación por admin
- Estadísticas de admin

---

## CI/CD con GitHub Actions

El proyecto incluye un workflow en `.github/workflows/tests.yml` que ejecuta
automáticamente los tests en Python 3.10, 3.11 y 3.12 cuando se hace push
a `main` o `develop`, o al abrir un Pull Request.

---

## Autor y licencia

- **Proyecto:** Sistema de Tickets — Módulo de Feedback de Usuarios
- **Curso:** 1º DAM — Solutia Innovación y Tecnología
- **Licencia:** Uso educativo
