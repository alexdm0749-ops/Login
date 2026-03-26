# ============================================================
# tests/test_auth.py
# Tests de autenticación (registro y login)
# Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
# Fecha: 2026-03-26
# ============================================================

import pytest
from tests.conftest import registrar_usuario, login_usuario


class TestRegistro:
    """Tests para el endpoint de registro de usuarios."""

    def test_registro_valido(self, client):
        """
        Test: registro exitoso con datos válidos.

        Verifica que un usuario se crea correctamente con nombre,
        email y contraseña válidos.
        """
        response = registrar_usuario(client)
        data = response.get_json()

        assert response.status_code == 201
        assert data['error'] is None
        assert data['data']['name'] == 'Test User'
        assert data['data']['email'] == 'test@test.com'

    def test_registro_email_duplicado(self, client):
        """
        Test: registro falla con email ya existente.

        Verifica que no se permiten emails duplicados.
        """
        registrar_usuario(client)
        response = registrar_usuario(client)
        data = response.get_json()

        assert response.status_code == 400
        assert data['error'] is not None

    def test_registro_nombre_corto(self, client):
        """
        Test: registro falla con nombre menor a 3 caracteres.
        """
        response = registrar_usuario(client, name='AB')
        data = response.get_json()

        assert response.status_code == 400
        assert 'nombre' in data['error'].lower()

    def test_registro_password_corta(self, client):
        """
        Test: registro falla con contraseña menor a 6 caracteres.
        """
        response = registrar_usuario(client, password='12345')
        data = response.get_json()

        assert response.status_code == 400
        assert 'contraseña' in data['error'].lower()

    def test_registro_email_invalido(self, client):
        """
        Test: registro falla con formato de email inválido.
        """
        response = registrar_usuario(client, email='noesunmail')
        data = response.get_json()

        assert response.status_code == 400
        assert 'email' in data['error'].lower()


class TestLogin:
    """Tests para el endpoint de login."""

    def test_login_correcto(self, client):
        """
        Test: login exitoso con credenciales válidas.

        Verifica que se devuelven datos del usuario sin contraseña.
        """
        registrar_usuario(client)
        response = login_usuario(client)
        data = response.get_json()

        assert response.status_code == 200
        assert data['error'] is None
        assert data['data']['email'] == 'test@test.com'
        assert 'pass_hash' not in data['data']

    def test_login_incorrecto(self, client):
        """
        Test: login falla con contraseña incorrecta.

        Verifica mensaje genérico (OWASP: no revelar información).
        """
        registrar_usuario(client)
        response = login_usuario(client, password='wrongpass')
        data = response.get_json()

        assert response.status_code == 401
        assert data['error'] is not None
        # No debe revelar si el email existe o no
        assert 'incorrectas' in data['error'].lower()

    def test_login_email_no_existente(self, client):
        """
        Test: login falla con email no registrado.

        El mensaje debe ser idéntico al de contraseña incorrecta (OWASP).
        """
        response = login_usuario(client, email='noexiste@test.com')
        data = response.get_json()

        assert response.status_code == 401
        assert 'incorrectas' in data['error'].lower()
