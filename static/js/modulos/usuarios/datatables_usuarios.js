$(document).ready(function () {
    $('#tablaUsuarios').DataTable({
        language: {
            url: 'https://cdn.datatables.net/plug-ins/2.1.8/i18n/es-ES.json'
        },
        pageLength: 10,
        lengthMenu: [5, 10, 25, 50],
        order: [],
        columnDefs: [
            {
                orderable: false,
                targets: 7
            }
        ]
    });
});