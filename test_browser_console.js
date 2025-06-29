// SCRIPT DE PRUEBA PARA EJECUTAR EN LA CONSOLA DEL NAVEGADOR
// Copia y pega este código en la consola del navegador cuando estés en el calendario

console.log("🔧 SCRIPT DE PRUEBA DEL CALENDARIO - INICIANDO");

// Función para probar todos los elementos del modal
function probarCalendario() {
    console.log("📋 === INICIANDO PRUEBAS DEL CALENDARIO ===");
    
    // 1. Verificar que el modal existe
    const modal = document.getElementById('modalCrearEvento');
    console.log("🎯 Modal encontrado:", !!modal);
    
    // 2. Verificar formulario
    const form = document.getElementById('formCrearEvento');
    console.log("📝 Formulario encontrado:", !!form);
    
    // 3. Verificar elementos de selección de cursos
    const dirigidoTodos = document.getElementById('dirigido_todos');
    const dirigidoEspecificos = document.getElementById('dirigido_especificos');
    const cursosDiv = document.getElementById('cursosEspecificos');
    
    console.log("📋 Elementos de selección:");
    console.log("   - dirigido_todos:", !!dirigidoTodos);
    console.log("   - dirigido_especificos:", !!dirigidoEspecificos);
    console.log("   - cursosEspecificos div:", !!cursosDiv);
    
    if (cursosDiv) {
        const checkboxes = cursosDiv.querySelectorAll('input[name="cursos_especificos"]');
        console.log("   - checkboxes de cursos:", checkboxes.length);
        
        checkboxes.forEach((cb, index) => {
            console.log(`     ${index + 1}. ${cb.value} - ${cb.nextElementSibling?.textContent?.trim() || 'Sin texto'}`);
        });
    }
    
    // 4. Verificar elementos de validación de horas
    const horaInicio = document.getElementById('hora_inicio');
    const horaFin = document.getElementById('hora_fin');
    const errorInicio = document.getElementById('error_hora_inicio');
    const errorFin = document.getElementById('error_hora_fin');
    
    console.log("🕐 Elementos de validación de horas:");
    console.log("   - hora_inicio:", !!horaInicio);
    console.log("   - hora_fin:", !!horaFin);
    console.log("   - error_hora_inicio:", !!errorInicio);
    console.log("   - error_hora_fin:", !!errorFin);
    
    console.log("✅ === PRUEBAS COMPLETADAS ===");
    
    return {
        modal: !!modal,
        form: !!form,
        dirigidoTodos: !!dirigidoTodos,
        dirigidoEspecificos: !!dirigidoEspecificos,
        cursosDiv: !!cursosDiv,
        checkboxes: cursosDiv ? cursosDiv.querySelectorAll('input[name="cursos_especificos"]').length : 0,
        horaInicio: !!horaInicio,
        horaFin: !!horaFin,
        errorInicio: !!errorInicio,
        errorFin: !!errorFin
    };
}

// Función para simular selección de cursos específicos
function simularSeleccionCursos() {
    console.log("🎯 SIMULANDO SELECCIÓN DE CURSOS ESPECÍFICOS");
    
    const dirigidoEspecificos = document.getElementById('dirigido_especificos');
    const cursosDiv = document.getElementById('cursosEspecificos');
    
    if (dirigidoEspecificos && cursosDiv) {
        // Simular clic en "cursos específicos"
        dirigidoEspecificos.click();
        
        setTimeout(() => {
            console.log("📋 Estado después de seleccionar 'cursos específicos':");
            console.log("   - Radio seleccionado:", dirigidoEspecificos.checked);
            console.log("   - Div visible:", cursosDiv.style.display !== 'none');
            console.log("   - Opacidad:", cursosDiv.style.opacity);
            
            // Verificar checkboxes
            const checkboxes = cursosDiv.querySelectorAll('input[name="cursos_especificos"]');
            console.log("   - Checkboxes visibles:", checkboxes.length);
            
            // Seleccionar el primer checkbox si existe
            if (checkboxes.length > 0) {
                checkboxes[0].checked = true;
                console.log("   - Primer checkbox seleccionado:", checkboxes[0].value);
            }
        }, 100);
    } else {
        console.log("❌ No se encontraron los elementos necesarios");
    }
}

// Función para probar validación de horas
function probarValidacionHoras() {
    console.log("🕐 PROBANDO VALIDACIÓN DE HORAS");
    
    const horaInicio = document.getElementById('hora_inicio');
    const horaFin = document.getElementById('hora_fin');
    
    if (horaInicio && horaFin) {
        // Configurar horas inválidas
        horaInicio.value = "10:00";
        horaFin.value = "09:00";
        
        // Disparar evento de cambio
        horaInicio.dispatchEvent(new Event('change'));
        horaFin.dispatchEvent(new Event('change'));
        
        setTimeout(() => {
            console.log("📊 Estado después de configurar horas inválidas:");
            console.log("   - Hora inicio:", horaInicio.value);
            console.log("   - Hora fin:", horaFin.value);
            console.log("   - Inicio tiene error:", horaInicio.classList.contains('is-invalid'));
            console.log("   - Fin tiene error:", horaFin.classList.contains('is-invalid'));
            
            const errorInicio = document.getElementById('error_hora_inicio');
            const errorFin = document.getElementById('error_hora_fin');
            console.log("   - Mensaje error inicio:", errorInicio?.textContent || 'Sin mensaje');
            console.log("   - Mensaje error fin:", errorFin?.textContent || 'Sin mensaje');
        }, 100);
    } else {
        console.log("❌ No se encontraron los campos de hora");
    }
}

// Función para abrir el modal automáticamente
function abrirModal() {
    console.log("🎯 ABRIENDO MODAL");
    const btnNuevoEvento = document.querySelector('[data-bs-target="#modalCrearEvento"]');
    if (btnNuevoEvento) {
        btnNuevoEvento.click();
        console.log("✅ Modal abierto");
        
        // Ejecutar pruebas después de que el modal se abra
        setTimeout(() => {
            probarCalendario();
        }, 500);
    } else {
        console.log("❌ No se encontró el botón para abrir el modal");
    }
}

// Instrucciones
console.log("📝 INSTRUCCIONES:");
console.log("1. Ejecuta: probarCalendario() - para verificar elementos");
console.log("2. Ejecuta: abrirModal() - para abrir el modal automáticamente");
console.log("3. Ejecuta: simularSeleccionCursos() - para simular selección de cursos");
console.log("4. Ejecuta: probarValidacionHoras() - para probar validación de horas");
console.log("5. O ejecuta todo junto con: abrirModal()");

// Ejecutar prueba inicial
probarCalendario();
