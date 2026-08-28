/* KNexus Engine -- mejora progresiva (UX), vendorizado, sin dependencias
   (Regla R5: el sistema corre sin internet). Sin este archivo, cada
   formulario y cada link siguen funcionando exactamente igual via GET
   normal del navegador -- esto solo anade feedback de carga (modal con
   frases rotando) mientras /results, /connection, /opportunity o /audit
   tardan en responder con el modelo real. */
(function () {
  "use strict";

  /* Frases que rotan mientras se espera la respuesta -- describen el
     pipeline real (F1-F4 de ARCHITECTURE.md), no un "cargando..." genérico:
     la idea es que la espera SE SIENTA como lo que realmente está pasando
     (recuperación híbrida + 7 features), no como un spinner vacío. */
  var LOADING_PHRASES = [
    "Analizando el dataset institucional...",
    "Cruzando necesidades, proyectos y capacidades...",
    "Recuperando por semántica, texto y grafo...",
    "Puntuando conexiones con las 7 features...",
    "Verificando evidencia y procedencia..."
  ];

  function buildLoadingModal() {
    var existing = document.getElementById("knexus-loading-modal");
    if (existing) return existing;
    var modal = document.createElement("div");
    modal.id = "knexus-loading-modal";
    modal.className = "knexus-loading-modal";
    modal.setAttribute("role", "status");

    var card = document.createElement("div");
    card.className = "knexus-loading-card";

    var spinner = document.createElement("div");
    spinner.className = "knexus-loading-spinner";
    spinner.setAttribute("aria-hidden", "true");

    var text = document.createElement("p");
    text.className = "knexus-loading-text";
    text.setAttribute("aria-live", "polite");

    card.appendChild(spinner);
    card.appendChild(text);
    modal.appendChild(card);
    document.body.appendChild(modal);
    return modal;
  }

  function showLoadingModal() {
    var modal = buildLoadingModal();
    var text = modal.querySelector(".knexus-loading-text");
    var i = 0;
    text.textContent = LOADING_PHRASES[i];
    modal.classList.add("is-visible");
    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduceMotion) {
      // No hace falta clearInterval: la navegación normal reemplaza toda la
      // página, así que este intervalo nunca sobrevive más que la espera.
      setInterval(function () {
        i = (i + 1) % LOADING_PHRASES.length;
        text.textContent = LOADING_PHRASES[i];
      }, 1100);
    }
  }

  function attachLoadingState(form) {
    if (!form || form.dataset.knexusLoadingBound) return;
    form.dataset.knexusLoadingBound = "1";
    form.addEventListener("submit", function () {
      var button = form.querySelector("button[type=submit]");
      if (button && !button.disabled) {
        button.disabled = true;
        button.textContent = "Buscando...";
      }
      showLoadingModal();
    });
  }

  /* Resultados, "Comparar con...", quick-picks y el menú lateral navegan por
     <a href> normal, no por un form -- sin esto, sólo la búsqueda del header
     mostraba el modal y el resto de los clics (los que de verdad tardan:
     abrir una conexión, generar una oportunidad, armar la auditoría) se
     quedaban sin feedback. Excluye los nodos del mini-grafo: esos ya
     resuelven arrastre-vs-clic con su propio script (presenters.py) y
     mostrar el modal ahí interferiría con ese gesto. */
  function attachLinkLoadingState(link) {
    if (!link || link.dataset.knexusLoadingBound) return;
    link.dataset.knexusLoadingBound = "1";
    link.addEventListener("click", function (e) {
      if (link.classList.contains("graph-node-link")) return;
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      showLoadingModal();
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
    document.querySelectorAll("form").forEach(attachLoadingState);
    document.querySelectorAll('a[href^="/"]').forEach(attachLinkLoadingState);
    animateMetricBars();
  });
})();
