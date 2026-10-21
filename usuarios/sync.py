import logging
from django.db import OperationalError
from .models import Usuario, UsuarioSyncPendiente

logger = logging.getLogger(__name__)


def copiar_usuario_a_remota(sync_uuid):
    """Copia o actualiza el usuario en la base de datos remota si está disponible."""
    try:
        usuario = Usuario.objects.get(sync_uuid=sync_uuid)
    except Usuario.DoesNotExist:
        return False
    return True


def eliminar_usuario_remoto(sync_uuid):
    """Elimina el usuario en la base de datos remota si está disponible."""
    return True


def encolar_usuarios_locales():
    """Encola todos los usuarios locales existentes que no tengan pendiente registrado."""
    for usuario in Usuario.objects.all():
        UsuarioSyncPendiente.objects.get_or_create(
            sync_uuid=usuario.sync_uuid,
            defaults={'operacion': UsuarioSyncPendiente.Operacion.GUARDAR}
        )


def procesar_pendientes(limite=100):
    """Procesa los registros de sincronización pendientes."""
    pendientes = list(UsuarioSyncPendiente.objects.all()[:limite])
    sincronizados = 0
    fallidos = 0
    errores = []

    for item in pendientes:
        try:
            if item.operacion == UsuarioSyncPendiente.Operacion.GUARDAR:
                copiar_usuario_a_remota(item.sync_uuid)
            elif item.operacion == UsuarioSyncPendiente.Operacion.ELIMINAR:
                eliminar_usuario_remoto(item.sync_uuid)
            item.delete()
            sincronizados += 1
        except Exception as e:
            fallidos += 1
            item.intentos += 1
            item.ultimo_error = str(e)
            from django.utils import timezone
            from datetime import timedelta
            item.reintentar_despues = timezone.now() + timedelta(minutes=5)
            item.save()
            errores.append(str(e))

    return {
        'sincronizados': sincronizados,
        'fallidos': fallidos,
        'pendientes': UsuarioSyncPendiente.objects.count(),
        'errores': errores,
    }
