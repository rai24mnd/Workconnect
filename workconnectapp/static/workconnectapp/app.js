// Solo controla la presentación. Django calcula todas las recomendaciones.
const panel = document.getElementById("preferencias");
const contenido = document.getElementById("contenido");
const abrir = document.getElementById("abrir-preferencias");
const cerrar = document.getElementById("cerrar-preferencias");
abrir.hidden = false;
cerrar.hidden = false;

function mostrarPreferencias(mostrar) {
    panel.hidden = !mostrar;
    contenido.classList.toggle("panel-abierto", mostrar);
    abrir.setAttribute("aria-expanded", String(mostrar));
    if (mostrar) {
        panel.querySelector("select").focus({ preventScroll: true });
        panel.scrollIntoView({ block: "start" });
    } else {
        abrir.focus({ preventScroll: true });
    }
}
abrir.addEventListener("click", () => mostrarPreferencias(panel.hidden));
cerrar.addEventListener("click", () => mostrarPreferencias(false));
panel.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape") mostrarPreferencias(false);
});

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
