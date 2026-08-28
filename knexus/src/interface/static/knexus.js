/* KNexus Engine -- mejora progresiva (UX), vendorizado, sin dependencias
   (Regla R5: el sistema corre sin internet). Sin este archivo, cada
   formulario de busqueda sigue funcionando exactamente igual via GET
   normal del navegador -- esto solo anade feedback de carga mientras
   /results, /opportunity o /audit tardan en responder con el modelo real. */
(function () {
  "use strict";

  function loadingMessageFor(form) {
    var existing = form.parentElement.querySelector(".header-loading");
    if (existing) return existing;
    var msg = document.createElement("p");
    msg.className = "muted header-loading";
    msg.textContent = "Conectando fuentes...";
    msg.hidden = true;
    form.insertAdjacentElement("afterend", msg);
    return msg;
  }

  function attachLoadingState(form) {
    if (!form || form.dataset.knexusLoadingBound) return;
    form.dataset.knexusLoadingBound = "1";
    var loading = loadingMessageFor(form);
    form.addEventListener("submit", function () {
      var button = form.querySelector("button[type=submit]");
      if (button && !button.disabled) {
        button.disabled = true;
        button.textContent = "Buscando...";
      }
      loading.hidden = false;
      loading.textContent = "Conectando fuentes...";
    });
  }

  /* Barras de /metrics: crecen de 0 al valor medido en vez de aparecer ya
     llenas — puramente visual (la medición sigue siendo la misma foto fija
     de evaluate.py), ayuda a notar que cada barra es un número distinto.
     Sin JS, o con "reduce motion", la barra simplemente se ve en su ancho
     final -- nunca depende de esto para mostrar el dato correcto. */
  function animateMetricBars() {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var bars = document.querySelectorAll(".metrics-grid .chart-bar");
    bars.forEach(function (bar) {
      var target = bar.style.width;
      bar.style.width = "0%";
      // reflow forzado para que el navegador registre el "0%" antes del
      // cambio siguiente -- si no, ambos cambios se funden y no hay transición.
      void bar.offsetWidth;
      bar.style.width = target;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form.search-form, #header-search-form").forEach(attachLoadingState);
    animateMetricBars();
  });
})();
