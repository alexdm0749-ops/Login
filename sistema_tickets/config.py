# ============================================================
# config.py
# Configuración de Supabase y Flask
# Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
# Fecha: 2026-03-26
# ============================================================

import os


class Config:
    """
    Configuración centralizada de la aplicación.

    Attributes:
        SECRET_KEY (str): Clave secreta para sesiones Flask.
        SUPABASE_URL (str): URL del proyecto Supabase.
        SUPABASE_ANON_KEY (str): Clave pública/anon de Supabase.
    """

    # Clave secreta para sesiones Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')

    # Credenciales de Supabase
    SUPABASE_URL = 'https://vyjuhmqmuazbmoatirid.supabase.co'
    SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ5anVobXFtdWF6Ym1vYXRpcmlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0MjUzNDIsImV4cCI6MjA5MDAwMTM0Mn0.7iKqtf39MhAic4Hb6vPdG9l7RAFJMe3g8in7k4aX0aE'
