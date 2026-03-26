# ============================================================
# tests/conftest.py
# Configuración compartida de pytest (fixtures)
# Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
# Fecha: 2026-03-26
# ============================================================

import os
import sys
import tempfile
import pytest

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from database.db import get_db, init_db


@pytest.fixture
def app():
    """
    Fixture que crea una instancia de la aplicación con base de datos temporal.

    Crea un archivo temporal para SQLite, inicializa el esquema
    y lo elimina al finalizar el test.

    Yields:
        Flask: Instancia de la aplicación configurada para testing.
    """
    # Crear archivo temporal para la base de datos de test
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key'
    })

    yield app

    # Limpiar: cerrar y eliminar base de datos temporal
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """
    Fixture que proporciona un cliente HTTP de test.

    Args:
        app (Flask): Instancia de la aplicación (fixture).

    Returns:
        FlaskClient: Cliente para hacer peticiones HTTP de test.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture que proporciona un CLI runner de test.

    Args:
        app (Flask): Instancia de la aplicación (fixture).

    Returns:
        FlaskCliRunner: Runner para comandos CLI de test.
    """
    return app.test_cli_runner()


def registrar_usuario(client, name='Test User', email='test@test.com',
                       password='123456', role=None):
    """
    Helper: registra un usuario via API para uso en tests.

    Args:
        client (FlaskClient): Cliente HTTP de test.
        name (str): Nombre del usuario.
        email (str): Email del usuario.
        password (str): Contraseña del usuario.
        role (str|None): Rol (se ignora en registro normal, se usa post-registro).

    Returns:
        Response: Respuesta HTTP del registro.
    """
    return client.post('/api/auth/registro', json={
        'name': name,
        'email': email,
        'password': password
    })


def login_usuario(client, email='test@test.com', password='123456'):
    """
    Helper: inicia sesión de un usuario via API.

    Args:
        client (FlaskClient): Cliente HTTP de test.
        email (str): Email del usuario.
        password (str): Contraseña del usuario.

    Returns:
        Response: Respuesta HTTP del login.
    """
    return client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })


def crear_usuario_con_rol(app, name, email, password, role):
    """
    Helper: crea un usuario con un rol específico directamente en la BD.

    Útil para crear agentes y admins en tests.

    Args:
        app (Flask): Instancia de la aplicación.
        name (str): Nombre del usuario.
        email (str): Email del usuario.
        password (str): Contraseña del usuario.
        role (str): Rol del usuario ('reporter', 'agente', 'admin').
    """
    from werkzeug.security import generate_password_hash
    with app.app_context():
        db = get_db()
        db.execute(
            'INSERT INTO users (name, email, pass_hash, role) VALUES (?, ?, ?, ?)',
            (name, email, generate_password_hash(password), role)
        )
        db.commit()
