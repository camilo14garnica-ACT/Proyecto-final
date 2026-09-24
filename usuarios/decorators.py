from functools import wraps
from django.shortcuts import redirect


def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica si el usuario está autenticado y tiene uno de los roles permitidos.
    Si no cumple con los roles requeridos, se le redirige a la página de inicio.
    """
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('inicio')

            if request.user.rol not in roles_permitidos:
                return redirect('inicio')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorador


def solo_admin(view_func):
    """Permite el acceso únicamente a administradores; de lo contrario redirige a inicio."""
    return rol_requerido('ADMIN')(view_func)


def solo_veterinario(view_func):
    """Permite el acceso únicamente a veterinarios; de lo contrario redirige a inicio."""
    return rol_requerido('VETERINARIO')(view_func)


# Alias por compatibilidad con posibles llamadas previas
solo_veterianrio = solo_veterinario


def solo_admin_o_veterinario(view_func):
    """Permite el acceso a administradores o veterinarios; de lo contrario redirige a inicio."""
    return rol_requerido('ADMIN', 'VETERINARIO')(view_func)


def solo_cliente(view_func):
    """Permite el acceso únicamente a clientes; de lo contrario redirige a inicio."""
    return rol_requerido('CLIENTE')(view_func)
