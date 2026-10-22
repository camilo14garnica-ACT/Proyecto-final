import logging
from datetime import timedelta

from django.db import OperationalError
from django.utils import timezone

from .models import Usuario, UsuarioSyncPendiente

logger = logging.getLogger(__name__)


def copiar_usuario_a_remota(sync_uuid):
    """Copia o actualiza el usuario en la base de datos remota si está disponible."""
    try:
        usuario = Usuario.objects.get(sync_uuid=sync_uuid)
    except Usuario.DoesNotExist:
        logger.warning("copiar_usuario_a_remota: UUID %s no encontrado.", sync_uuid)
        return False

    try:
        Usuario.objects.using('remota').update_or_create(
            sync_uuid=sync_uuid,
            defaults={
                'username': usuario.username,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'email': usuario.email,
                'password': usuario.password,
                'rol': usuario.rol,
                'is_active': usuario.is_active,
                'Document_Type': usuario.Document_Type,
                'Number_Document': usuario.Number_Document,
                'Date_of_birth': usuario.Date_of_birth,
            }
        )
        return True
    except OperationalError as exc:
        logger.error("Base remota no disponible al copiar %s: %s", sync_uuid, exc)
        raise


def eliminar_usuario_remoto(sync_uuid):
    """Elimina el usuario en la base de datos remota si está disponible."""
    try:
        Usuario.objects.using('remota').filter(sync_uuid=sync_uuid).delete()
        return True
    except OperationalError as exc:
        logger.error("Base remota no disponible al eliminar %s: %s", sync_uuid, exc)
        raise


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
        except Exception as exc:
            fallidos += 1
            item.intentos += 1
            item.ultimo_error = str(exc)
            item.reintentar_despues = timezone.now() + timedelta(minutes=5)
            item.save()
            errores.append(str(exc))

    return {
        'sincronizados': sincronizados,
        'fallidos': fallidos,
        'pendientes': UsuarioSyncPendiente.objects.count(),
        'errores': errores,
    }
