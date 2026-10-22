document.addEventListener('DOMContentLoaded', function () {
    const especie = document.getElementById('id_especie');
    const raza = document.getElementById('id_raza');
    const plantillaUrl = document.body.dataset.razasUrl;

    // Inicializar Select2
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

    // Cargar las razas según la especie seleccionada
    if (!especie || !raza || !plantillaUrl) return;

    especie.addEventListener('change', async function () {
        raza.innerHTML = '<option value="">Selecciona una raza</option>';

        if (window.jQuery && jQuery.fn.select2) {
            jQuery(raza).trigger('change');
        }

        if (!especie.value) return;

        try {
            const url = plantillaUrl.replace('/0/', `/${especie.value}/`);
            const respuesta = await fetch(url);

            if (!respuesta.ok) {
                throw new Error('No se pudieron cargar las razas.');
            }

            const datos = await respuesta.json();

            datos.razas.forEach(function (r) {
                raza.add(new Option(r.nombre, r.id));
            });

            if (window.jQuery && jQuery.fn.select2) {
                jQuery(raza).trigger('change');
            }
        } catch (error) {
            console.error('Error al cargar las razas:', error);
        }
    });
});