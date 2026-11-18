from .models import Notificacion


def notificaciones_context(request):
    """Inyecta el conteo de notificaciones no leídas y las últimas 5 notificaciones en el contexto global de plantillas."""
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'is_authenticated', False) or not getattr(user, 'pk', None):
        return {
            'notificaciones_no_leidas_count': 0,
            'ultimas_notificaciones': [],
        }

    try:
        no_leidas = Notificacion.objects.filter(usuario=user, leida=False).count()
        ultimas = Notificacion.objects.filter(usuario=user).order_by('-fecha')[:5]
        return {
            'notificaciones_no_leidas_count': no_leidas,
            'ultimas_notificaciones': ultimas,
        }
    except Exception:
        return {
            'notificaciones_no_leidas_count': 0,
            'ultimas_notificaciones': [],
        }
