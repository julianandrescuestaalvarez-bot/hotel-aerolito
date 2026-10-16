/* ============================================================
   HOTEL AEROLITO — gestionServicios.js
   CRUD de servicios para el panel de administración.
   Requiere auth.js cargado antes que este archivo.
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Protección de la página: solo admins logueados ──────────────
  var usuario = obtenerUsuario();

  if (!haySesion() || !usuario || usuario.rol !== 'admin') {
    // OJO: si tu Usuario.to_dict() usa otro nombre de campo distinto
    // a "rol" (ej. "tipo_usuario"), ajusta la condición de arriba.
    window.location.href = 'login.html';
    return;
  }

  var tabla        = document.getElementById('tablaServicios');
  var form         = document.getElementById('formServicio');
  var inputId      = document.getElementById('servicioId');
  var inputNombre  = document.getElementById('nombre');
  var inputDesc    = document.getElementById('descripcion');
  var inputPrecio  = document.getElementById('precio');
  var btnGuardar   = document.getElementById('btnGuardar');
  var btnCancelar  = document.getElementById('btnCancelar');
  var tituloForm   = document.getElementById('tituloFormulario');
  var mensajeBox   = document.getElementById('mensaje');

  cargarServicios();

  // ── Cargar y pintar la tabla ─────────────────────────────────────
  function cargarServicios() {
    fetch(API_BASE_URL + '/servicios/')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        tabla.innerHTML = '';

        if (!data.servicios || data.servicios.length === 0) {
          tabla.innerHTML = '<tr><td colspan="4">Aún no hay servicios registrados.</td></tr>';
          return;
        }

        data.servicios.forEach(function (servicio) {
          var fila = document.createElement('tr');
          fila.innerHTML =
            '<td>' + escapeHtml(servicio.nombre) + '</td>' +
            '<td>' + escapeHtml(servicio.descripcion || '') + '</td>' +
            '<td>$' + Number(servicio.precio).toLocaleString('es-CO') + '</td>' +
            '<td>' +
              '<button type="button" class="btn-editar" data-id="' + servicio.id + '">Editar</button> ' +
              '<button type="button" class="btn-eliminar" data-id="' + servicio.id + '" style="background-color: var(--error);">Eliminar</button>' +
            '</td>';
          tabla.appendChild(fila);
        });

        // Enganchar botones de cada fila
        document.querySelectorAll('.btn-editar').forEach(function (btn) {
          btn.addEventListener('click', function () {
            cargarServicioEnFormulario(btn.dataset.id, data.servicios);
          });
        });
        document.querySelectorAll('.btn-eliminar').forEach(function (btn) {
          btn.addEventListener('click', function () {
            eliminarServicio(btn.dataset.id);
          });
        });
      })
      .catch(function () {
        mostrarMensaje('No se pudieron cargar los servicios. Revisa que el backend esté corriendo.', 'error');
      });
  }

  // ── Poner un servicio existente en el formulario (modo edición) ──
  function cargarServicioEnFormulario(id, listaServicios) {
    var servicio = listaServicios.find(function (s) { return String(s.id) === String(id); });
    if (!servicio) return;

    inputId.value = servicio.id;
    inputNombre.value = servicio.nombre;
    inputDesc.value = servicio.descripcion || '';
    inputPrecio.value = servicio.precio;

    tituloForm.textContent = 'Editar servicio: ' + servicio.nombre;
    btnGuardar.textContent = 'Guardar cambios';
    btnCancelar.style.display = 'inline-block';

    form.scrollIntoView({ behavior: 'smooth' });
  }

  // ── Cancelar edición → volver a modo "crear" ─────────────────────
  btnCancelar.addEventListener('click', function () {
    resetFormulario();
  });

  function resetFormulario() {
    form.reset();
    inputId.value = '';
    tituloForm.textContent = 'Crear nuevo servicio';
    btnGuardar.textContent = 'Crear servicio';
    btnCancelar.style.display = 'none';
  }

  // ── Envío del formulario (crear o actualizar según haya id) ──────
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var precioNumerico = parseFloat(inputPrecio.value);
    if (isNaN(precioNumerico) || precioNumerico <= 0) {
      mostrarMensaje('El precio debe ser un número válido mayor a 0.', 'error');
      return;
    }

    var payload = {
      nombre: inputNombre.value.trim(),
      descripcion: inputDesc.value.trim(),
      precio: precioNumerico
    };

    var esEdicion = !!inputId.value;
    var url = esEdicion
      ? API_BASE_URL + '/servicios/' + inputId.value
      : API_BASE_URL + '/servicios/';
    var metodo = esEdicion ? 'PUT' : 'POST';

    btnGuardar.disabled = true;

    fetch(url, {
      method: metodo,
      headers: cabecerasAuth(),
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error(data.error || 'Error al guardar el servicio.');
          return data;
        });
      })
      .then(function (data) {
        mostrarMensaje(data.mensaje || 'Servicio guardado correctamente.', 'exito');
        resetFormulario();
        cargarServicios();
      })
      .catch(function (err) {
        mostrarMensaje(err.message, 'error');
      })
      .finally(function () {
        btnGuardar.disabled = false;
      });
  });

  // ── Eliminar servicio ─────────────────────────────────────────────
  function eliminarServicio(id) {
    if (!confirm('¿Seguro que quieres eliminar este servicio? Esta acción no se puede deshacer.')) {
      return;
    }

    fetch(API_BASE_URL + '/servicios/' + id, {
      method: 'DELETE',
      headers: cabecerasAuth()
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) throw new Error(data.error || 'Error al eliminar el servicio.');
          return data;
        });
      })
      .then(function (data) {
        mostrarMensaje(data.mensaje || 'Servicio eliminado.', 'exito');
        cargarServicios();
      })
      .catch(function (err) {
        mostrarMensaje(err.message, 'error');
      });
  }

  // ── Helpers ────────────────────────────────────────────────────────
  function mostrarMensaje(texto, tipo) {
    mensajeBox.textContent = texto;
    mensajeBox.className = 'alerta ' + (tipo === 'error' ? 'alerta-error' : 'alerta-exito');
    mensajeBox.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });

    setTimeout(function () {
      mensajeBox.style.display = 'none';
    }, 4000);
  }

  function escapeHtml(texto) {
    var div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
  }

});