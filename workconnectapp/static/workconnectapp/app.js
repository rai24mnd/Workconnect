// Solo controla la presentación. Django calcula todas las recomendaciones.
document.querySelectorAll(".dia-horario").forEach((fila) => {
    const disponible = fila.querySelector('input[type="checkbox"]');
    const horas = fila.querySelectorAll('input[type="time"]');
    function actualizarDia() {
        fila.querySelector(".estado-dia").textContent = disponible.checked ? "Disponible" : "No disponible";
        horas.forEach((hora) => {
            // Conservamos las horas aunque se desmarque el día. Django las ignora.
            hora.readOnly = !disponible.checked;
            hora.required = disponible.checked;
            hora.setAttribute("aria-disabled", String(!disponible.checked));
        });
    }
    disponible.addEventListener("change", actualizarDia);
    actualizarDia();
});

document.querySelectorAll("[data-contacto]").forEach((boton) => {
    boton.hidden = false;
    const dialogo = document.getElementById(boton.dataset.contacto);
    boton.addEventListener("click", () => dialogo.showModal());
    dialogo.querySelector("[data-cerrar-dialogo]").addEventListener("click", () => dialogo.close());
    // Escape y el retorno del foco al botón los gestiona el dialog nativo.
    dialogo.addEventListener("click", (evento) => {
        if (evento.target !== dialogo) return;
        const limites = dialogo.getBoundingClientRect();
        if (evento.clientX < limites.left || evento.clientX > limites.right ||
            evento.clientY < limites.top || evento.clientY > limites.bottom) dialogo.close();
    });
});

// Sin JavaScript los filtros quedan visibles y el formulario GET sigue funcionando.
const botonFiltros = document.querySelector("[data-alternar-filtros]");
const panelFiltros = document.getElementById("panel-filtros");
if (botonFiltros && panelFiltros) {
    function mostrarFiltros(abierto) {
        panelFiltros.hidden = !abierto;
        botonFiltros.setAttribute("aria-expanded", String(abierto));
    }
    mostrarFiltros(panelFiltros.dataset.abierto === "true");
    botonFiltros.hidden = false;
    botonFiltros.addEventListener("click", () => mostrarFiltros(panelFiltros.hidden));
    panelFiltros.addEventListener("invalid", () => mostrarFiltros(true), true);
    panelFiltros.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape") {
            mostrarFiltros(false);
            botonFiltros.focus();
            evento.preventDefault();
        }
    });
}
