/* =====================================================
   INICIO.JS — Animaciones de la página principal
   ===================================================== */

/**
 * Anima un número desde 0 hasta su valor final
 * cuando el elemento entra en el viewport (scroll)
 */
document.addEventListener('DOMContentLoaded', function () {

  // Seleccionamos todos los números animables
  const contadores = document.querySelectorAll('.stat-number');

  // Función que anima un contador de 0 al valor final
  function animarContador(el) {
    const valorFinal = parseFloat(el.dataset.valor);
    const esComa    = el.dataset.coma === 'true'; // para el 4,5
    const duracion  = 1800; // ms
    const inicio    = performance.now();

    function tick(ahora) {
      const transcurrido = ahora - inicio;
      const progreso     = Math.min(transcurrido / duracion, 1);
      // Ease-out cúbico para que desacelere al final
      const ease         = 1 - Math.pow(1 - progreso, 3);
      const valorActual  = valorFinal * ease;

      if (esComa) {
        el.textContent = valorActual.toFixed(1).replace('.', ',');
      } else {
        el.textContent = Math.floor(valorActual).toLocaleString('es-CO');
      }

      if (progreso < 1) {
        requestAnimationFrame(tick);
      } else {
        // Valor final exacto
        el.textContent = esComa
          ? valorFinal.toString().replace('.', ',')
          : valorFinal.toLocaleString('es-CO');
      }
    }

    requestAnimationFrame(tick);
  }

  // IntersectionObserver: dispara la animación al entrar en pantalla
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting && !entry.target.dataset.animado) {
        entry.target.dataset.animado = 'true';
        animarContador(entry.target);
      }
    });
  }, { threshold: 0.3 });

  // Guardamos el valor real en data-valor y ponemos 0 como inicio
  contadores.forEach(function (el) {
    const texto = el.textContent.replace(',', '.');
    const valor = parseFloat(texto);
    if (!isNaN(valor)) {
      el.dataset.valor = valor;
      // Si tiene coma decimal (4,5) lo marcamos
      if (el.textContent.includes(',') || el.textContent.includes('.')) {
        el.dataset.coma = 'true';
      }
      el.textContent = '0';
      observer.observe(el);
    }
  });

});
