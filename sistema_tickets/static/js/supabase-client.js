// ============================================================
// static/js/supabase-client.js
// Cliente Supabase: autenticación y operaciones CRUD
// Toda la lógica de datos se ejecuta aquí en el navegador
// Autor: Equipo 1º DAM | Proyecto: Sistema de Tickets 1º DAM
// Fecha: 2026-03-26
// ============================================================

// ============================================================
// Inicialización del cliente Supabase
// Las variables SUPABASE_URL y SUPABASE_ANON_KEY se inyectan
// desde Flask en la plantilla base.html
// ============================================================
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Variable global para el usuario actual
let currentUser = null;
let currentProfile = null;

// ============================================================
// AUTENTICACIÓN
// ============================================================

/**
 * Registra un nuevo usuario en Supabase Auth.
 * Crea automáticamente un perfil en la tabla profiles (trigger SQL).
 *
 * @param {string} name - Nombre del usuario.
 * @param {string} email - Email del usuario.
 * @param {string} password - Contraseña (mínimo 6 caracteres).
 * @returns {Object} Resultado con data o error.
 */
async function registrarUsuario(name, email, password) {
    const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password,
        options: {
            data: { name: name, role: 'reporter' }
        }
    });

    if (error) return { data: null, error: error.message };
    return { data: data, error: null };
}

/**
 * Inicia sesión con email y contraseña.
 *
 * @param {string} email - Email del usuario.
 * @param {string} password - Contraseña.
 * @returns {Object} Resultado con data o error.
 */
async function loginUsuario(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password
    });

    if (error) return { data: null, error: error.message };
    return { data: data, error: null };
}

/**
 * Cierra la sesión del usuario actual.
 */
async function logoutUsuario() {
    await supabase.auth.signOut();
    window.location.href = '/login';
}

/**
 * Obtiene el usuario actual de Supabase Auth.
 *
 * @returns {Object|null} Usuario actual o null si no está logueado.
 */
async function obtenerUsuarioActual() {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
}

/**
 * Obtiene el perfil del usuario actual desde la tabla profiles.
 *
 * @returns {Object|null} Perfil del usuario o null.
 */
async function obtenerPerfilActual() {
    const user = await obtenerUsuarioActual();
    if (!user) return null;

    const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();

    if (error) return null;
    return data;
}

/**
 * Verifica que el usuario está autenticado.
 * Si no lo está, redirige al login.
 * Carga el perfil en las variables globales.
 *
 * @returns {Object} Perfil del usuario autenticado.
 */
async function requiereAuth() {
    currentUser = await obtenerUsuarioActual();
    if (!currentUser) {
        window.location.href = '/login';
        return null;
    }

    currentProfile = await obtenerPerfilActual();
    if (!currentProfile) {
        window.location.href = '/login';
        return null;
    }

    // Actualizar navbar con info del usuario
    actualizarNavbar();
    return currentProfile;
}

/**
 * Verifica que el usuario tiene uno de los roles especificados.
 *
 * @param {...string} roles - Roles permitidos.
 * @returns {boolean} True si tiene el rol, false si redirige.
 */
async function requiereRol(...roles) {
    const profile = await requiereAuth();
    if (!profile) return false;

    if (!roles.includes(profile.role)) {
        window.location.href = '/tickets';
        return false;
    }
    return true;
}

/**
 * Actualiza la barra de navegación con el nombre y rol del usuario.
 */
function actualizarNavbar() {
    const userNameEl = document.getElementById('nav-user-name');
    const userRoleEl = document.getElementById('nav-user-role');
    const navLinks = document.getElementById('nav-links');
    const adminLinks = document.getElementById('admin-links');

    if (currentProfile && userNameEl) {
        userNameEl.textContent = currentProfile.name;
    }
    if (currentProfile && userRoleEl) {
        userRoleEl.textContent = currentProfile.role;
        userRoleEl.className = 'badge badge-role badge-' + currentProfile.role;
    }
    if (navLinks) {
        navLinks.style.display = 'flex';
    }
    // Mostrar links de admin solo si es admin
    if (adminLinks && currentProfile) {
        adminLinks.style.display = currentProfile.role === 'admin' ? 'contents' : 'none';
    }
}

// ============================================================
// TICKETS — CRUD
// ============================================================

/**
 * Crea un nuevo ticket en Supabase.
 *
 * @param {string} title - Título del ticket (mín 5 chars).
 * @param {string} body - Descripción detallada.
 * @param {number} categoryId - ID de la categoría.
 * @param {string} priority - Prioridad (baja|media|alta|critica).
 * @returns {Object} Resultado con data o error.
 */
async function crearTicket(title, categoryId, body, priority) {
    const { data, error } = await supabase
        .from('tickets')
        .insert({
            user_id: currentUser.id,
            category_id: categoryId,
            title: title,
            body: body,
            priority: priority
        })
        .select()
        .single();

    if (error) return { data: null, error: error.message };
    return { data: data, error: null };
}

/**
 * Lista tickets con filtros opcionales y paginación.
 *
 * @param {Object} opciones - Filtros y paginación.
 * @param {string} [opciones.status] - Filtrar por estado.
 * @param {number} [opciones.categoryId] - Filtrar por categoría.
 * @param {number} [opciones.page=1] - Página actual.
 * @param {number} [opciones.pageSize=10] - Elementos por página.
 * @returns {Object} { tickets, total, page, pages }.
 */
async function listarTickets({ status, categoryId, page = 1, pageSize = 10 } = {}) {
    const from = (page - 1) * pageSize;
    const to = from + pageSize - 1;

    let query = supabase
        .from('tickets')
        .select(`
            *,
            author:profiles!tickets_user_id_fkey(name),
            category:categories!tickets_category_id_fkey(name),
            assignee:profiles!tickets_assignee_id_fkey(name)
        `, { count: 'exact' });

    // Aplicar filtros
    if (status) query = query.eq('status', status);
    if (categoryId) query = query.eq('category_id', categoryId);

    // Ordenar y paginar
    query = query.order('created_at', { ascending: false })
                 .range(from, to);

    const { data, error, count } = await query;

    if (error) return { tickets: [], total: 0, page: 1, pages: 1, error: error.message };

    const total = count || 0;
    const pages = Math.max(1, Math.ceil(total / pageSize));

    return { tickets: data, total, page, pages, error: null };
}

/**
 * Obtiene el detalle de un ticket por su ID.
 *
 * @param {number} ticketId - ID del ticket.
 * @returns {Object|null} Ticket con datos del autor y categoría.
 */
async function obtenerTicket(ticketId) {
    const { data, error } = await supabase
        .from('tickets')
        .select(`
            *,
            author:profiles!tickets_user_id_fkey(name),
            category:categories!tickets_category_id_fkey(name),
            assignee:profiles!tickets_assignee_id_fkey(name)
        `)
        .eq('id', ticketId)
        .single();

    if (error) return null;
    return data;
}

/**
 * Actualiza el estado y/o asignado de un ticket.
 *
 * @param {number} ticketId - ID del ticket.
 * @param {Object} campos - Campos a actualizar.
 * @param {string} [campos.status] - Nuevo estado.
 * @param {string} [campos.assignee_id] - ID del agente asignado.
 * @returns {Object} Resultado con data o error.
 */
async function actualizarTicket(ticketId, campos) {
    campos.updated_at = new Date().toISOString();

    const { data, error } = await supabase
        .from('tickets')
        .update(campos)
        .eq('id', ticketId)
        .select()
        .single();

    if (error) return { data: null, error: error.message };
    return { data: data, error: null };
}

/**
 * Elimina un ticket (solo admin, controlado por RLS).
 *
 * @param {number} ticketId - ID del ticket a eliminar.
 * @returns {Object} Resultado con éxito o error.
 */
async function eliminarTicket(ticketId) {
    const { error } = await supabase
        .from('tickets')
        .delete()
        .eq('id', ticketId);

    if (error) return { error: error.message };
    return { error: null };
}

// ============================================================
// COMENTARIOS
// ============================================================

/**
 * Añade un comentario a un ticket.
 *
 * @param {number} ticketId - ID del ticket.
 * @param {string} body - Contenido del comentario.
 * @returns {Object} Resultado con data o error.
 */
async function crearComentario(ticketId, body) {
    const { data, error } = await supabase
        .from('ticket_comments')
        .insert({
            ticket_id: ticketId,
            user_id: currentUser.id,
            body: body
        })
        .select(`
            *,
            author:profiles!ticket_comments_user_id_fkey(name)
        `)
        .single();

    if (error) return { data: null, error: error.message };
    return { data: data, error: null };
}

/**
 * Lista los comentarios de un ticket.
 *
 * @param {number} ticketId - ID del ticket.
 * @returns {Array} Lista de comentarios con datos del autor.
 */
async function listarComentarios(ticketId) {
    const { data, error } = await supabase
        .from('ticket_comments')
        .select(`
            *,
            author:profiles!ticket_comments_user_id_fkey(name)
        `)
        .eq('ticket_id', ticketId)
        .order('created_at', { ascending: true });

    if (error) return [];
    return data;
}

// ============================================================
// CATEGORÍAS
// ============================================================

/**
 * Lista todas las categorías disponibles.
 *
 * @returns {Array} Lista de categorías.
 */
async function listarCategorias() {
    const { data, error } = await supabase
        .from('categories')
        .select('*')
        .order('name');

    if (error) {
        mostrarFlash('Error cargando categorías: ' + error.message, 'error');
        console.error('Categories error:', error);
        return [];
    }
    return data;
}

/**
 * Crea una nueva categoría (solo admin, controlado por RLS).
 *
 * @param {string} name - Nombre de la categoría.
 * @returns {Object} Resultado con data o error.
 */
async function crearCategoria(name) {
    const { data, error } = await supabase
        .from('categories')
        .insert({ name: name })
        .select()
        .single();

    if (error) return { data: null, error: error.message };
    return { data: data, error: null };
}

// ============================================================
// ADMIN — USUARIOS Y ESTADÍSTICAS
// ============================================================

/**
 * Lista todos los usuarios (perfiles).
 *
 * @returns {Array} Lista de perfiles de usuario.
 */
async function listarUsuarios() {
    const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .order('created_at', { ascending: false });

    if (error) return [];
    return data;
}

/**
 * Obtiene estadísticas del sistema llamando a la función RPC.
 *
 * @returns {Object|null} Estadísticas o null si hay error.
 */
async function obtenerEstadisticas() {
    const { data, error } = await supabase.rpc('get_admin_stats');

    if (error) return null;
    return data;
}

// ============================================================
// UTILIDADES
// ============================================================

/**
 * Escapa HTML para prevenir XSS al insertar texto en el DOM.
 *
 * @param {string} text - Texto a escapar.
 * @returns {string} Texto seguro para HTML.
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Formatea una fecha ISO a formato legible.
 *
 * @param {string} isoDate - Fecha en formato ISO.
 * @returns {string} Fecha formateada (dd/mm/yyyy HH:MM).
 */
function formatearFecha(isoDate) {
    if (!isoDate) return '-';
    const d = new Date(isoDate);
    return d.toLocaleDateString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

/**
 * Muestra un mensaje flash temporal en la página.
 *
 * @param {string} message - Texto del mensaje.
 * @param {string} type - Tipo: 'success' o 'error'.
 */
function mostrarFlash(message, type) {
    const container = document.getElementById('flash-container');
    if (!container) return;

    const flash = document.createElement('div');
    flash.className = 'flash flash-' + type;
    flash.innerHTML = escapeHtml(message) +
        '<button class="flash-close" onclick="this.parentElement.remove()">✕</button>';
    container.appendChild(flash);

    // Auto-eliminar después de 5 segundos
    setTimeout(function() { flash.remove(); }, 5000);
}

/**
 * Traduce el estado del ticket a texto en español.
 *
 * @param {string} status - Estado en inglés.
 * @returns {string} Estado en español.
 */
function traducirEstado(status) {
    const estados = {
        'open': 'Abierto',
        'in_progress': 'En progreso',
        'resolved': 'Resuelto',
        'closed': 'Cerrado'
    };
    return estados[status] || status;
}
