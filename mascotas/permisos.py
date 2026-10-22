from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.exceptions import PermissionDenied

def es_personal(usuario):
    """Administrador, veterinario o superusuario."""
    return usuario.is_superuser or usuario.es_admin() or usuario.es_veterinario()

def solo_admin(vista):
    @login_required
    @wraps(vista)
    def envoltura(request, *args, **kwrags):
        u = request.user
        if not (u.is_superuser or u.es_admin()):
            raise PermissionDenied
        return vista(request, *args, **kwrags)
    return envoltura
    
    