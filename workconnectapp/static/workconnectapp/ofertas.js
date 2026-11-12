// Django valida y guarda los datos. Este archivo solo organiza el formulario.
const contenedor = document.getElementById("alternativas-horario");
const total = document.getElementById("id_total_alternativas");
const modalidad = document.getElementById("id_modalidad_horario");
const agregar = document.getElementById("agregar-alternativa");
const plantilla = document.getElementById("alternativa-vacia");
const estadoEditor = document.getElementById("estado-editor-horarios");

function gruposHorario() {
    return Array.from(contenedor.querySelectorAll(".alternativa-horario"));
}

function enfocarGrupo(grupo) {
    if (grupo) grupo.querySelector('select:not(:disabled), input:not([type="hidden"]):not(:disabled)')?.focus();
}

function numerarAlternativas() {
    const grupos = gruposHorario();
    grupos.forEach((grupo, indice) => {
        const gestion = grupo.querySelector('input[name$="-TOTAL_FORMS"]');
        const anterior = gestion.name.replace(/-TOTAL_FORMS$/, "") + "-";
        const nuevo = `alternativa-${indice}-`;
        // Cambiar atributos, sin recrear los controles ni perder valores escritos.
        grupo.querySelectorAll("[name], [id], label[for], [aria-describedby]").forEach((elemento) => {
            ["name", "id", "for", "aria-describedby"].forEach((atributo) => {
                const valor = elemento.getAttribute(atributo);
                if (valor) elemento.setAttribute(atributo, valor.replaceAll(anterior, nuevo));
            });
        });
        grupo.querySelector("template").innerHTML = grupo.querySelector("template").innerHTML.replaceAll(anterior, nuevo);
        grupo.querySelector("[data-numero-alternativa]").textContent = indice + 1;
        grupo.querySelector("[data-eliminar-alternativa]").setAttribute("aria-label", `Eliminar alternativa ${indice + 1}`);
    });
    // Django solo debe recibir las alternativas visibles de la modalidad elegida.
    total.value = grupos.filter((grupo) => !grupo.hidden).length;
    agregar.disabled = grupos.length >= 20;
}

function actualizarBloque(bloque, activo) {
    const eliminar = bloque.querySelector('input[name$="-DELETE"]');
    const quitado = eliminar.checked;
    bloque.classList.toggle("bloque-eliminado", quitado);
    bloque.querySelectorAll("input, select").forEach((campo) => {
        campo.disabled = !activo || (quitado && campo !== eliminar);
    });
    bloque.querySelector("[data-estado-bloque]").textContent = quitado ? "Este bloque se eliminará al guardar. Desmarca para conservarlo." : "";
}

function prepararBloque(bloque, grupo) {
    bloque.querySelector('input[name$="-DELETE"]').addEventListener("change", () => {
        actualizarBloque(bloque, !grupo.hidden);
    });
    actualizarBloque(bloque, !grupo.hidden);
}

function prepararGrupo(grupo) {
    const botonBloque = grupo.querySelector("[data-agregar-bloque]");
    const botonEliminar = grupo.querySelector("[data-eliminar-alternativa]");
    botonBloque.hidden = false;
    botonEliminar.hidden = false;
    grupo.querySelectorAll(".bloque-oferta").forEach((bloque) => prepararBloque(bloque, grupo));
    botonBloque.addEventListener("click", () => {
        const gestion = grupo.querySelector('input[name$="-TOTAL_FORMS"]');
        const indice = Number(gestion.value);
        if (indice >= 50 || grupo.hidden) return;
        const html = grupo.querySelector("[data-bloque-vacio]").innerHTML.replaceAll("__prefix__", indice);
        grupo.querySelector("[data-bloques]").insertAdjacentHTML("beforeend", html);
        gestion.value = indice + 1;
        prepararBloque(grupo.querySelector("[data-bloques]").lastElementChild, grupo);
        botonBloque.disabled = indice + 1 >= 50;
        grupo.querySelector("[data-bloques]").lastElementChild.querySelector("select").focus();
    });
    botonEliminar.addEventListener("click", () => {
        if (botonEliminar.disabled) return;
        const indice = gruposHorario().indexOf(grupo);
        grupo.remove();
        actualizarModalidad();
        const restantes = gruposHorario();
        enfocarGrupo(restantes[Math.min(indice, restantes.length - 1)]);
    });
    botonBloque.disabled = Number(grupo.querySelector('input[name$="-TOTAL_FORMS"]').value) >= 50;
}

function agregarAlternativa() {
    const indice = gruposHorario().length;
    if (indice >= 20) return;
    contenedor.insertAdjacentHTML("beforeend", plantilla.innerHTML.replaceAll("__grupo__", indice));
    prepararGrupo(contenedor.lastElementChild);
    numerarAlternativas();
}

function actualizarModalidad() {
    const varias = modalidad.value === "varias_opciones";
    const fijo = modalidad.value === "fijo";
    const minimo = varias ? 2 : fijo ? 1 : 0;
    while (gruposHorario().length < minimo) agregarAlternativa();
    const grupos = gruposHorario();
    grupos.forEach((grupo, indice) => {
        const activo = varias || (fijo && indice === 0);
        // Ocultar y deshabilitar conserva el borrador si se vuelve de modalidad.
        grupo.hidden = !activo;
        grupo.querySelectorAll("input, select, button").forEach((campo) => { campo.disabled = !activo; });
        grupo.querySelectorAll(".bloque-oferta").forEach((bloque) => actualizarBloque(bloque, activo));
        grupo.querySelector("[data-eliminar-alternativa]").disabled = !varias || grupos.length <= 2;
        const gestion = grupo.querySelector('input[name$="-TOTAL_FORMS"]');
        grupo.querySelector("[data-agregar-bloque]").disabled = !activo || Number(gestion.value) >= 50;
    });
    agregar.hidden = modalidad.value !== "varias_opciones";
    numerarAlternativas();
    const borradores = grupos.filter((grupo) => grupo.hidden).length;
    estadoEditor.textContent = borradores
        ? `${borradores} alternativa(s) conservada(s) como borrador en esta página. No se enviarán con esta modalidad; puedes recuperarlas cambiando de modalidad antes de guardar.`
        : varias ? "Cada alternativa debe estar completa. El joven solo necesita cumplir una."
        : fijo ? "Todos los bloques de esta alternativa son obligatorios."
        : modalidad.value === "flexible" ? "No se enviarán bloques. El horario requerirá acuerdo con la empresa."
        : "Selecciona una modalidad de horario para completar sus condiciones.";
}

contenedor.querySelectorAll(".alternativa-horario").forEach(prepararGrupo);
agregar.addEventListener("click", () => {
    agregarAlternativa();
    actualizarModalidad();
    enfocarGrupo(contenedor.lastElementChild);
});
modalidad.addEventListener("change", actualizarModalidad);
actualizarModalidad();

["experiencia", "estudios"].forEach((requisito) => {
    const estado = document.getElementById(`id_${requisito}_estado`);
    const minimo = document.getElementById(`id_${requisito}_min`);
    function actualizarRequisito() {
        const especifico = estado.value === "especifico";
        const campo = minimo.closest(".campo");
        // Un error devuelto por Django debe seguir visible y poder corregirse.
        const tieneError = campo.querySelector(".errorlist") !== null;
        campo.hidden = !especifico && !tieneError;
        minimo.disabled = !especifico && !tieneError;
        minimo.required = especifico;
    }
    estado.addEventListener("change", actualizarRequisito);
    actualizarRequisito();
});
