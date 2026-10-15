from .permisos import es_personal


def plantilla_base(request):
    if request.user.is_authenticated and es_personal(request.user):
        return {'base_template': 'base_panel.html', 'es_personal': True}
    return {'base_templare': 'base.html', 'es_personal': False}


