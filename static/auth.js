/* ============================================================
   HOTEL AEROLITO — auth.js
   Helpers de sesión compartidos entre todas las páginas.
   Incluir con <script src="auth.js"></script> ANTES del script
   propio de cada página.

   OJO!!! AJUSTAR SI ES NECESARIO: API_BASE_URL y los nombres de campo
   marcados abajo, según tu auth.py real.
   ============================================================ */

const API_BASE_URL = 'http://localhost:5000/api';

function guardarSesion(token, usuario) {
  localStorage.setItem('aerolito_token', token);
  localStorage.setItem('aerolito_usuario', JSON.stringify(usuario));
}

function obtenerToken() {
  return localStorage.getItem('aerolito_token');
}

function obtenerUsuario() {
  var raw = localStorage.getItem('aerolito_usuario');
  return raw ? JSON.parse(raw) : null;
}

function haySesion() {
  return !!obtenerToken();
}

function cerrarSesion() {
  localStorage.removeItem('aerolito_token');
  localStorage.removeItem('aerolito_usuario');
  window.location.href = 'Index.html';
}

/* Cabecera lista para usar en fetch() a rutas protegidas */
function cabecerasAuth() {
  var token = obtenerToken();
  return token
    ? { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token }
    : { 'Content-Type': 'application/json' };
}

/* Pinta el estado de sesión dentro de cualquier elemento con id="nav-auth" */
function pintarNavAuth() {
  var $contenedor = document.getElementById('nav-auth');
  if (!$contenedor) return;

  var usuario = obtenerUsuario();

  if (usuario) {
    $contenedor.innerHTML =
      'Hola, ' + (usuario.nombre || 'Usuario') + ' — ' +
      '<a href="#" id="btnCerrarSesion">Cerrar sesión</a>';

    var btn = document.getElementById('btnCerrarSesion');
    if (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        cerrarSesion();
      });
    }
  } else {
    $contenedor.innerHTML = '<a href="login.html">Ingresar</a>';
  }
}

document.addEventListener('DOMContentLoaded', pintarNavAuth);