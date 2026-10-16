/* ============================================================
   HOTEL AEROLITO — script.js
   jQuery + vanilla JS para todas las páginas
   ============================================================ */

$(document).ready(function () {

  /* ============================================================
     UTILIDADES
  ============================================================ */

  function mostrarAlerta($elem, texto, tipo) {
    $elem
      .text(texto)
      .removeClass('alerta-exito alerta-error alerta-aviso')
      .addClass('alerta alerta-' + tipo)
      .fadeIn(250);
  }

  function ocultarAlerta($elem) {
    $elem.fadeOut(300, function () {
      $(this).text('').removeClass('alerta alerta-exito alerta-error alerta-aviso');
    });
  }

  /* ============================================================
     NAVBAR — marcar enlace activo según página actual
  ============================================================ */
  var pagina = window.location.pathname.split('/').pop();
  $('.navbar-aerolito .nav-link').each(function () {
    var href = $(this).attr('href');
    if (href === pagina || (pagina === '' && href === 'index.html')) {
      $(this).addClass('active').attr('aria-current', 'page');
    }
  });

  /* ============================================================
     PÁGINA DE LOGIN — login.html
  ============================================================ */

  // Mostrar / ocultar mensaje de bienvenida
  $('#btnBienvenida').on('click', function () {
    $('#bienvenida').slideToggle(300);
    var visible = $('#bienvenida').is(':visible');
    $(this).text(visible ? 'Ocultar bienvenida' : 'Mostrar bienvenida');
    $(this).attr('aria-expanded', visible ? 'true' : 'false');
  });

  // Efecto hover en botón ingresar
  $('#btnIngresar').on('mouseenter', function () {
    $(this).css({ transform: 'translateY(-1px)', boxShadow: '0 4px 16px rgba(106,27,31,0.45)' });
  }).on('mouseleave', function () {
    $(this).css({ transform: '', boxShadow: '' });
  });

  // Validación del formulario de login
  $('#formulario').on('submit', function (e) {
    e.preventDefault();

    var nombre = $.trim($('#nombre').val());
    var correo  = $.trim($('#correo').val());

    if (nombre === '' || correo === '') {
      mostrarAlerta($('#mensaje'), '⚠ Todos los campos son obligatorios.', 'error');
      ocultarAlerta($('#resultado'));
      $('#nombre').focus();
      return;
    }

    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(correo)) {
      mostrarAlerta($('#mensaje'), '⚠ Ingresa un correo electrónico válido.', 'error');
      ocultarAlerta($('#resultado'));
      $('#correo').focus();
      return;
    }

    ocultarAlerta($('#mensaje'));
    $('#titulo').text('¡Sesión iniciada!');
    $('#subtitulo').text('Hola, ' + nombre + ' 👋');
    $('#marca').text('Bienvenido, ' + nombre);

    mostrarAlerta($('#resultado'), '✔ Bienvenido al Hotel Aerolito, ' + nombre + '.', 'exito');
    $(this)[0].reset();

    setTimeout(function () { ocultarAlerta($('#resultado')); }, 4500);
  });

  // Limpiar error al escribir
  $('#nombre, #correo').on('input', function () {
    if ($('#mensaje').is(':visible')) ocultarAlerta($('#mensaje'));
  });

  /* ============================================================
     PÁGINA DE INICIO — formulario de contacto (index.html)
  ============================================================ */

  $('#formContacto').on('submit', function (e) {
    e.preventDefault();

    var nombre = $.trim($('#contactoNombre').val());
    var correo  = $.trim($('#contactoCorreo').val());
    var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (nombre === '' || correo === '') {
      mostrarAlerta($('#msgContacto'), '⚠ Por favor completa todos los campos.', 'error');
      return;
    }
    if (!emailRe.test(correo)) {
      mostrarAlerta($('#msgContacto'), '⚠ Correo electrónico no válido.', 'error');
      return;
    }

    mostrarAlerta($('#msgContacto'), '✔ Mensaje enviado. Te contactaremos pronto.', 'exito');
    $(this)[0].reset();
    setTimeout(function () { ocultarAlerta($('#msgContacto')); }, 4000);
  });

  /* ============================================================
     PÁGINA DE PAGOS — pagosreserva.html
     Mostrar / ocultar campos según método de pago seleccionado
  ============================================================ */

  function toggleMetodoPago() {
    var metodo = $('input[name="metodo_pago"]:checked').val();

    if (metodo === 'tarjeta') {
      $('#campos-tarjeta').slideDown(250);
      $('#campos-pse').slideUp(250);
    } else if (metodo === 'pse') {
      $('#campos-pse').slideDown(250);
      $('#campos-tarjeta').slideUp(250);
    }
  }

  // Inicializar estado
  toggleMetodoPago();

  // Cambio de método
  $('input[name="metodo_pago"]').on('change', toggleMetodoPago);

  // Validación de pago
  $('#formPago').on('submit', function (e) {
    e.preventDefault();
    var metodo = $('input[name="metodo_pago"]:checked').val();

    if (metodo === 'tarjeta') {
      var tarjeta = $.trim($('#numTarjeta').val());
      var expira  = $.trim($('#expiracion').val());
      var cvv     = $.trim($('#cvv').val());
      if (tarjeta.length < 16 || expira === '' || cvv.length < 3) {
        mostrarAlerta($('#msgPago'), '⚠ Completa correctamente los datos de la tarjeta.', 'error');
        return;
      }
    } else {
      var banco = $('#banco').val();
      if (!banco) {
        mostrarAlerta($('#msgPago'), '⚠ Selecciona un banco para continuar con PSE.', 'error');
        return;
      }
    }

    ocultarAlerta($('#msgPago'));
    mostrarAlerta($('#msgPago'), '✔ Procesando pago...', 'aviso');
    setTimeout(function () {
      window.location.href = 'confirmacionreserva.html';
    }, 1800);
  });

  // Formateo automático del número de tarjeta
  $('#numTarjeta').on('input', function () {
    var v = $(this).val().replace(/\D/g, '').substring(0, 16);
    var fmt = v.replace(/(.{4})/g, '$1 ').trim();
    $(this).val(fmt);
  });

  // Formateo de fecha de vencimiento
  $('#expiracion').on('input', function () {
    var v = $(this).val().replace(/\D/g, '').substring(0, 4);
    if (v.length >= 3) v = v.substring(0,2) + '/' + v.substring(2);
    $(this).val(v);
  });

  /* ============================================================
     ANIMACIÓN DE ENTRADA SUAVE PARA CARDS
  ============================================================ */
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    $('.card-aerolito, .stat-card').each(function () {
      $(this).css({ opacity: '0', transform: 'translateY(16px)', transition: 'opacity 0.4s ease, transform 0.4s ease' });
      observer.observe(this);
    });
  }

});
