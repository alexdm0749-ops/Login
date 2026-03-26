from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave-secreta-cambia-esto-en-produccion'

DB_PATH = 'usuarios.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('auth.html', modo='login')

        conn = get_db()
        usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()

        if usuario and check_password_hash(usuario['password'], password):
            session['usuario_id'] = usuario['id']
            session['usuario_nombre'] = usuario['nombre']
            flash(f'¡Bienvenido, {usuario["nombre"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos.', 'error')

    return render_template('auth.html', modo='login')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirmar = request.form.get('confirmar', '')

        if not nombre or not email or not password or not confirmar:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('auth.html', modo='registro')

        if password != confirmar:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('auth.html', modo='registro')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('auth.html', modo='registro')

        password_hash = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)',
                (nombre, email, password_hash)
            )
            conn.commit()
            conn.close()
            flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Ya existe una cuenta con ese email.', 'error')

    return render_template('auth.html', modo='registro')


@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', nombre=session['usuario_nombre'])


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)