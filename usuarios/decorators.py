from functools import wraps
# pyrefly: ignore [missing-import]
from django.shortcuts import redirect


def rol_requerido(*roles_permitidos):
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return redirect('login')  # Nombre de tu url de login o vista

            # 2. Verificar el rol del usuario (ajusta según cómo manejes los roles en tu modelo)
            # Por ejemplo, si tienes un atributo 'rol' o grupos:
            # if request.user.rol not in roles_permitidos:
            #     return redirect('nombre_vista_acceso_denegado')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorador
