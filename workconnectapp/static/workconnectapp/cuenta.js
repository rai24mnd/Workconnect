// El desplegable nativo también funciona sin JavaScript y en pantallas táctiles.
document.querySelectorAll("[data-menu-usuario]").forEach((menu) => {
    const activador = menu.querySelector("summary");

    menu.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape" && menu.open) {
            menu.open = false;
            activador.focus();
            evento.preventDefault();
        }
    });

    document.addEventListener("click", (evento) => {
        if (menu.open && !menu.contains(evento.target)) menu.open = false;
    });

    menu.addEventListener("focusout", (evento) => {
        if (evento.relatedTarget && !menu.contains(evento.relatedTarget)) menu.open = false;
    });
});
