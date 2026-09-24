from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def solo_admin(view_func):
    def check(user):
        if user.is_authenticated and user.rol == 'ADMIN':
            return True
        raise PermissionDenied
    return user_passes_test(check)(view_func)


def solo_veterianrio(view_func):
    def check(user):
        if user.is_authenticated and user.rol == 'VETERINARIO':
            return True
        raise PermissionDenied
    return user_passes_test(check)(view_func)

def solo_admin_o_veterinario(view_func):
    def check(user):
        if user.is_authenticated and user.rol in ('ADMIN', 'VETERINARIA'):
            return True
        raise PermissionDenied
    return user_passes_test(check)(view_func)