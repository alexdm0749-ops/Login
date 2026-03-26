# ============================================================
# tests/test_comments.py
# Tests de gestión de comentarios
# Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
# Fecha: 2026-03-26
# ============================================================

import pytest
from tests.conftest import registrar_usuario, login_usuario, crear_usuario_con_rol


class TestComentarios:
    """Tests para la gestión de comentarios en tickets."""

    def _setup_ticket(self, client):
        """
        Helper interno: crea un usuario y un ticket para los tests.

        Args:
            client (FlaskClient): Cliente HTTP de test.
        """
        registrar_usuario(client)
        login_usuario(client)
        client.post('/api/tickets', json={
            'title': 'Ticket para comentarios',
            'body': 'Descripción del ticket',
            'category_id': 1,
            'priority': 'media'
        })

    def test_crear_comentario_valido(self, client):
        """
        Test: añadir comentario con texto válido devuelve 201.
        """
        self._setup_ticket(client)

        response = client.post('/api/tickets/1/comments', json={
            'body': 'Este es un comentario de prueba'
        })
        data = response.get_json()

        assert response.status_code == 201
        assert data['error'] is None
        assert data['data']['body'] == 'Este es un comentario de prueba'
        assert data['data']['author_name'] == 'Test User'

    def test_crear_comentario_vacio(self, client):
        """
        Test: comentario vacío devuelve 400.
        """
        self._setup_ticket(client)

        response = client.post('/api/tickets/1/comments', json={
            'body': ''
        })
        data = response.get_json()

        assert response.status_code == 400
        assert 'vacío' in data['error'].lower()

    def test_listar_comentarios(self, client):
        """
        Test: listar comentarios de un ticket devuelve lista correcta.
        """
        self._setup_ticket(client)

        # Crear 2 comentarios
        client.post('/api/tickets/1/comments', json={'body': 'Comentario 1'})
        client.post('/api/tickets/1/comments', json={'body': 'Comentario 2'})

        response = client.get('/api/tickets/1/comments')
        data = response.get_json()

        assert response.status_code == 200
        assert len(data['data']) == 2

    def test_comentario_ticket_inexistente(self, client):
        """
        Test: comentar en ticket inexistente devuelve 404.
        """
        registrar_usuario(client)
        login_usuario(client)

        response = client.post('/api/tickets/999/comments', json={
            'body': 'Comentario en ticket que no existe'
        })
        data = response.get_json()

        assert response.status_code == 404


class TestAdminStats:
    """Tests para las estadísticas de administración."""

    def test_stats_como_admin(self, app, client):
        """
        Test: admin puede ver las estadísticas del sistema.
        """
        crear_usuario_con_rol(app, 'Admin', 'admin@test.com', '123456', 'admin')
        login_usuario(client, email='admin@test.com')

        response = client.get('/api/admin/stats')
        data = response.get_json()

        assert response.status_code == 200
        assert 'total_tickets' in data['data']
        assert 'tickets_por_estado' in data['data']
        assert 'total_usuarios' in data['data']
