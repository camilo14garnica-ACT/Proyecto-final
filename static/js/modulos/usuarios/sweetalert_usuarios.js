document.addEventListener('DOMContentLoaded', function () {

    // Mostrar mensajes de Django mediante SweetAlert2
    document.querySelectorAll('.mensaje-django').forEach(function (elemento) {
        const tipo = elemento.dataset.tipo;
        const mensaje = elemento.dataset.mensaje;

        let icono = 'info';

        if (tipo === 'success') {
            icono = 'success';
        } else if (tipo === 'error' || tipo === 'danger') {
            icono = 'error';
        } else if (tipo === 'warning') {
            icono = 'warning';
        }

        Swal.fire({
            icon: icono,
            title: mensaje,
            confirmButtonText: 'Aceptar'
        });
    });

    // Confirmar eliminación de usuarios
    document.addEventListener('submit', function (evento) {
        const formulario = evento.target.closest('.form-eliminar-usuario');

        if (!formulario) {
            return;
        }

        evento.preventDefault();

        const nombreUsuario = formulario.dataset.usuario;

        Swal.fire({
            title: '¿Eliminar usuario?',
            text: `¿Estás seguro de que deseas eliminar a ${nombreUsuario}? Esta acción no se puede deshacer.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then(function (resultado) {
            if (resultado.isConfirmed) {
                formulario.submit();
            }
        });
    });

});