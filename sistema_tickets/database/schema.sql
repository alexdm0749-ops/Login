-- ============================================================
-- schema.sql
-- Script SQL para ejecutar en Supabase SQL Editor
-- Crea las tablas, políticas RLS y datos iniciales
-- Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
-- ============================================================

-- ============================================================
-- Tabla: profiles
-- Perfil de usuario vinculado a auth.users de Supabase
-- Se crea automáticamente al registrarse un usuario
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id         UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name       TEXT NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    role       TEXT NOT NULL DEFAULT 'reporter'
               CHECK(role IN ('reporter', 'agente', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Tabla: categories
-- Categorías de los tickets (bug, sugerencia, consulta, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id    SERIAL PRIMARY KEY,
    name  TEXT UNIQUE NOT NULL
);

-- ============================================================
-- Tabla: tickets
-- Tickets de incidencias o sugerencias creados por los usuarios
-- Prioridades: baja, media, alta, critica
-- Estados: open, in_progress, resolved, closed
-- ============================================================
CREATE TABLE IF NOT EXISTS tickets (
    id          SERIAL PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES profiles(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    priority    TEXT NOT NULL DEFAULT 'media'
                CHECK(priority IN ('baja', 'media', 'alta', 'critica')),
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK(status IN ('open', 'in_progress', 'resolved', 'closed')),
    assignee_id UUID REFERENCES profiles(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Tabla: ticket_comments
-- Comentarios asociados a un ticket
-- ============================================================
CREATE TABLE IF NOT EXISTS ticket_comments (
    id         SERIAL PRIMARY KEY,
    ticket_id  INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id    UUID NOT NULL REFERENCES profiles(id),
    body       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Row Level Security (RLS) — Supabase
-- ============================================================

-- Activar RLS en todas las tablas
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_comments ENABLE ROW LEVEL SECURITY;

-- ---- PROFILES ----
-- Todos los usuarios logueados pueden ver perfiles
CREATE POLICY "Profiles: lectura pública" ON profiles
    FOR SELECT USING (auth.role() = 'authenticated');

-- Cada usuario puede insertar su propio perfil
CREATE POLICY "Profiles: insertar propio" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Cada usuario puede actualizar su propio perfil
CREATE POLICY "Profiles: actualizar propio" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- ---- CATEGORIES ----
-- Todos los usuarios autenticados pueden ver categorías
CREATE POLICY "Categories: lectura pública" ON categories
    FOR SELECT USING (auth.role() = 'authenticated');

-- Solo admins pueden crear categorías
CREATE POLICY "Categories: insertar admin" ON categories
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- ---- TICKETS ----
-- Reporters ven solo sus tickets, agentes y admins ven todos
CREATE POLICY "Tickets: lectura según rol" ON tickets
    FOR SELECT USING (
        user_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role IN ('agente', 'admin')
        )
    );

-- Cualquier usuario autenticado puede crear tickets
CREATE POLICY "Tickets: insertar autenticado" ON tickets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Agentes y admins pueden actualizar tickets
CREATE POLICY "Tickets: update agente/admin" ON tickets
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role IN ('agente', 'admin')
        )
    );

-- Solo admins pueden eliminar tickets
CREATE POLICY "Tickets: delete admin" ON tickets
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ---- TICKET_COMMENTS ----
-- Cualquier autenticado puede ver comentarios de tickets que puede ver
CREATE POLICY "Comments: lectura autenticado" ON ticket_comments
    FOR SELECT USING (auth.role() = 'authenticated');

-- Cualquier autenticado puede crear comentarios
CREATE POLICY "Comments: insertar autenticado" ON ticket_comments
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- Función: crear perfil automáticamente al registrarse
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, name, email, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'name', 'Usuario'),
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'role', 'reporter')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: ejecutar al crear un nuevo usuario en auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- Función RPC: obtener estadísticas (solo admin)
-- ============================================================
CREATE OR REPLACE FUNCTION public.get_admin_stats()
RETURNS json AS $$
DECLARE
    result json;
BEGIN
    -- Verificar que el usuario es admin
    IF NOT EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin') THEN
        RAISE EXCEPTION 'No tienes permisos de administrador';
    END IF;

    SELECT json_build_object(
        'total_tickets', (SELECT COUNT(*) FROM tickets),
        'tickets_por_estado', (
            SELECT json_object_agg(status, cnt)
            FROM (SELECT status, COUNT(*) as cnt FROM tickets GROUP BY status) s
        ),
        'tickets_por_categoria', (
            SELECT json_object_agg(name, cnt)
            FROM (
                SELECT c.name, COUNT(t.id) as cnt
                FROM categories c
                LEFT JOIN tickets t ON c.id = t.category_id
                GROUP BY c.name
            ) s
        ),
        'total_usuarios', (SELECT COUNT(*) FROM profiles),
        'total_comentarios', (SELECT COUNT(*) FROM ticket_comments)
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================
-- Datos iniciales: categorías por defecto
-- ============================================================
INSERT INTO categories (name) VALUES ('bug') ON CONFLICT DO NOTHING;
INSERT INTO categories (name) VALUES ('sugerencia') ON CONFLICT DO NOTHING;
INSERT INTO categories (name) VALUES ('consulta') ON CONFLICT DO NOTHING;
INSERT INTO categories (name) VALUES ('mejora') ON CONFLICT DO NOTHING;
