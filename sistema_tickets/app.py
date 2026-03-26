# ============================================================
# app.py
# Punto de entrada principal — Flask sirve páginas, Supabase
# maneja toda la lógica de datos y autenticación
# Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
# Fecha: 2026-03-26
# ============================================================

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template, redirect, url_for
from config import Config


def create_app(test_config=None):
    """
    Factory de la aplicación Flask.

    Flask solo sirve las páginas HTML. Toda la lógica de
    autenticación y datos se ejecuta en el navegador
    mediante el cliente JavaScript de Supabase.

    Args:
        test_config (dict|None): Configuración para tests.

    Returns:
        Flask: Instancia de la aplicación.
    """
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Inyectar credenciales de Supabase en todas las plantillas
    @app.context_processor
    def inject_supabase():
        """
        Inyecta las credenciales de Supabase en el contexto
        de todas las plantillas Jinja2.

        Returns:
            dict: URL y clave anon de Supabase.
        """
        return {
            'SUPABASE_URL': app.config['SUPABASE_URL'],
            'SUPABASE_ANON_KEY': app.config['SUPABASE_ANON_KEY']
        }

    # ============================================================
    # Rutas de páginas (Flask solo renderiza, no procesa datos)
    # ============================================================

    @app.route('/')
    def index():
        """Redirige a la lista de tickets."""
        return redirect(url_for('tickets_page'))

    @app.route('/login')
    def login_page():
        """Muestra la página de inicio de sesión."""
        return render_template('auth/login.html')

    @app.route('/registro')
    def registro_page():
        """Muestra la página de registro."""
        return render_template('auth/registro.html')

    @app.route('/tickets')
    def tickets_page():
        """Muestra el listado de tickets."""
        return render_template('tickets/lista.html')

    @app.route('/tickets/nuevo')
    def nuevo_ticket_page():
        """Muestra el formulario de nuevo ticket."""
        return render_template('tickets/nuevo.html')

    @app.route('/tickets/<int:ticket_id>')
    def detalle_ticket_page(ticket_id):
        """
        Muestra el detalle de un ticket.

        Args:
            ticket_id (int): ID del ticket.
        """
        return render_template('tickets/detalle.html', ticket_id=ticket_id)

    @app.route('/admin/dashboard')
    def admin_dashboard_page():
        """Muestra el panel de administración."""
        return render_template('admin/dashboard.html')

    @app.route('/admin/usuarios')
    def admin_usuarios_page():
        """Muestra la gestión de usuarios."""
        return render_template('admin/usuarios.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
