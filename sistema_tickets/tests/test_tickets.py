# ============================================================
# tests/test_tickets.py
# Tests de gestión de tickets
# Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
# Fecha: 2026-03-26
# ============================================================

import pytest
from tests.conftest import registrar_usuario, login_usuario, crear_usuario_con_rol


def crear_ticket_helper(client, title='Error en el login', body='No puedo acceder',
                         category_id=1, priority='media'):
    """
    Helper: crea un ticket via API (requiere sesión activa).

    Args:
        client (FlaskClient): Cliente HTTP autenticado.
        title (str): Título del ticket.
        body (str): Descripción del ticket.
        category_id (int): ID de categoría.
        priority (str): Prioridad del ticket.

    Returns:
        Response: Respuesta HTTP de la creación.
    """
    return client.post('/api/tickets', json={
        'title': title,
        'body': body,
        'category_id': category_id,
        'priority': priority
    })


class TestCrearTicket:
    """Tests para la creación de tickets."""

    def test_crear_ticket_valido(self, client):
        """
        Test: crear ticket con datos válidos devuelve 201.
        """
        registrar_usuario(client)
        login_usuario(client)

        response = crear_ticket_helper(client)
        data = response.get_json()

        assert response.status_code == 201
        assert data['error'] is None
        assert data['data']['title'] == 'Error en el login'
        assert data['data']['status'] == 'open'
        assert data['data']['priority'] == 'media'

    def test_crear_ticket_sin_autenticacion(self, client):
        """
        Test: crear ticket sin sesión devuelve 401.
        """
        response = crear_ticket_helper(client)

        assert response.status_code == 401

    def test_crear_ticket_titulo_corto(self, client):
        """
        Test: crear ticket con título menor a 5 caracteres devuelve 400.
        """
        registrar_usuario(client)
        login_usuario(client)

        response = crear_ticket_helper(client, title='AB')
        data = response.get_json()

        assert response.status_code == 400
        assert 'título' in data['error'].lower()


class TestListarTickets:
    """Tests para el listado de tickets con paginación."""

    def test_listar_tickets_con_paginacion(self, client):
        """
        Test: listar tickets devuelve datos de paginación correctos.
        """
        registrar_usuario(client)
        login_usuario(client)

        # Crear algunos tickets
        for i in range(3):
            crear_ticket_helper(client, title=f'Ticket de prueba {i+1}')

        response = client.get('/api/tickets?page=1&pageSize=2')
        data = response.get_json()

        assert response.status_code == 200
        assert data['error'] is None
        assert len(data['data']['tickets']) == 2
        assert data['data']['total'] == 3
        assert data['data']['pages'] == 2


class TestActualizarTicket:
    """Tests para la actualización de estado de tickets."""

    def test_cambiar_estado_como_agente(self, app, client):
        """
        Test: un agente puede cambiar el estado de un ticket.
        """
        # Crear un reporter y crear un ticket
        registrar_usuario(client, name='Reporter', email='rep@test.com')
        login_usuario(client, email='rep@test.com')
        crear_ticket_helper(client)
        client.get('/logout')

        # Crear un agente y cambiar el estado
        crear_usuario_con_rol(app, 'Agente Test', 'agente@test.com', '123456', 'agente')
        login_usuario(client, email='agente@test.com')

        response = client.patch('/api/tickets/1', json={'status': 'in_progress'})
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['status'] == 'in_progress'

    def test_cambiar_estado_como_reporter_falla(self, client):
        """
        Test: un reporter NO puede cambiar el estado de un ticket (403).
        """
        registrar_usuario(client)
        login_usuario(client)
        crear_ticket_helper(client)

        response = client.patch('/api/tickets/1', json={'status': 'in_progress'})

        assert response.status_code == 403


class TestEliminarTicket:
    """Tests para la eliminación de tickets."""

    def test_eliminar_ticket_como_admin(self, app, client):
        """
        Test: un admin puede eliminar un ticket.
        """
        registrar_usuario(client, name='Reporter', email='rep@test.com')
        login_usuario(client, email='rep@test.com')
        crear_ticket_helper(client)
        client.get('/logout')

        crear_usuario_con_rol(app, 'Admin Test', 'admin@test.com', '123456', 'admin')
        login_usuario(client, email='admin@test.com')

        response = client.delete('/api/tickets/1')
        data = response.get_json()

        assert response.status_code == 200
        assert 'eliminado' in data['data']['message'].lower()
