document.addEventListener('DOMContentLoaded', function () {
    const especie = document.getElementById('id_especie');
    const raza = document.getElementById('id_raza');
    const formulario = especie ? especie.form : null;
    const urlRazas = formulario ? formulario.dataset.razasUrl : null;

    // Activar los desplegables con buscador
    if (window.jQuery && jQuery.fn.select2) {
        jQuery('#id_Cliente, #id_especie, #id_raza').each(function () {
            if (this.tagName === 'SELECT' && !jQuery(this).hasClass('select2-hidden-accessible')) {
                jQuery(this).select2({
                    width: '100%',
                    placeholder: 'Selecciona una opción',
                    allowClear: true
                });
            }
        });
    }

    if (!especie || !raza) return;

    if (!urlRazas) {
        console.error('Falta data-razas-url en el <form> de mascota_form.html');
        return;
    }

    async function cargarRazas() {
        raza.innerHTML = '<option value="">Selecciona una raza</option>';

        if (especie.value) {
            try {
                const url = urlRazas.replace('/0/', '/' + especie.value + '/');
                const respuesta = await fetch(url);
                if (!respuesta.ok) throw new Error('No se pudieron cargar las razas.');

                const datos = await respuesta.json();
                datos.razas.forEach(function (r) {
                    raza.add(new Option(r.nombre, r.id));
                });
            } catch (error) {
                console.error('Error al cargar las razas:', error);
            }
        }

        // Avisar al desplegable con buscador que la lista cambió
        if (window.jQuery) jQuery(raza).trigger('change');
    }

    // Select2 avisa los cambios por jQuery, por eso se escucha así
    if (window.jQuery) {
        jQuery(especie).on('change', cargarRazas);
    } else {
        especie.addEventListener('change', cargarRazas);
    }
});
