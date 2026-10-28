from .permisos import es_personal


def plantilla_base(request):
    if request.user.is_authenticated and es_personal(request.user):
        return {'base_template': 'usuarios/base_panel.html', 'es_personal': True}
    return {'base_template': 'mascotas/base_cliente.html', 'es_personal': False}
