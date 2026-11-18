from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import PQRS, NoConformidad, EncuestaSatisfaccion, Notificacion
from .notificaciones import crear_notificacion, notificar_administradores


@receiver(pre_save, sender=PQRS)
def capturar_estado_anterior_pqrs(sender, instance, **kwargs):
    """Guarda en memoria el estado previo para detectar cambios de estado."""
    if instance.pk:
        try:
            instance._estado_anterior = PQRS.objects.get(pk=instance.pk).estado
        except PQRS.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=PQRS)
def notificar_eventos_pqrs(sender, instance, created, **kwargs):
    """Genera notificaciones automáticas cuando se radica o actualiza una PQRS."""
    if created:
        cliente_nombre = instance.cliente.get_full_name() or instance.cliente.username
        # 1. Notificar a administradores
        notificar_administradores(
            titulo=f"Nueva {instance.get_tipo_display()} #{instance.pk}",
            mensaje=(
                f"El cliente {cliente_nombre} ha radicado una {instance.get_tipo_display().lower()}:\n"
                f"\"{instance.descripcion[:160]}{'...' if len(instance.descripcion) > 160 else ''}\""
            ),
            tipo=Notificacion.Tipo.PQRS,
            enlace=f"/calidad/admin/pqrs/{instance.pk}/",
        )

        # 2. Notificar al cliente confirmación de radicación
        crear_notificacion(
            usuario=instance.cliente,
            titulo=f"Tu {instance.get_tipo_display()} #{instance.pk} fue radicada con éxito",
            mensaje=(
                f"Hemos recibido tu {instance.get_tipo_display().lower()} correctamente. "
                "Nuestro equipo de calidad y atención revisará tu caso a la mayor brevedad."
            ),
            tipo=Notificacion.Tipo.PQRS,
            enlace="/calidad/mis-pqrs/",
        )
    else:
        # Detectar si cambió el estado
        estado_previo = getattr(instance, '_estado_anterior', None)
        if estado_previo and estado_previo != instance.estado:
            crear_notificacion(
                usuario=instance.cliente,
                titulo=f"Actualización en tu {instance.get_tipo_display()} #{instance.pk}",
                mensaje=(
                    f"Tu solicitud #{instance.pk} ha cambiado de estado: "
                    f"ahora se encuentra en '{instance.get_estado_display()}'."
                ),
                tipo=Notificacion.Tipo.PQRS,
                enlace="/calidad/mis-pqrs/",
            )


@receiver(post_save, sender=NoConformidad)
def notificar_no_conformidad(sender, instance, created, **kwargs):
    """Notifica al equipo administrativo cuando se registra una no conformidad."""
    if created:
        notificar_administradores(
            titulo=f"Nueva No Conformidad #{instance.pk} registrada",
            mensaje=(
                f"Se ha registrado una no conformidad en el sistema:\n"
                f"\"{instance.descripcion_problema[:160]}{'...' if len(instance.descripcion_problema) > 160 else ''}\""
            ),
            tipo=Notificacion.Tipo.CALIDAD,
            enlace=f"/calidad/admin/no-conformidades/editar/{instance.pk}/",
        )


@receiver(post_save, sender=EncuestaSatisfaccion)
def notificar_alerta_satisfaccion(sender, instance, created, **kwargs):
    """Alerta a los administradores si un cliente califica un servicio con 1 o 2 estrellas."""
    if created and instance.puntuacion <= 2:
        cliente_nombre = instance.cliente.get_full_name() or instance.cliente.username
        notificar_administradores(
            titulo=f"⚠️ Alerta de Calidad: Calificación baja ({instance.puntuacion}★)",
            mensaje=(
                f"El cliente {cliente_nombre} calificó con {instance.puntuacion} estrella(s) su atención. "
                f"Comentario: \"{instance.comentarios or 'Sin comentario adicional'}\""
            ),
            tipo=Notificacion.Tipo.ENCUESTA,
            enlace="/calidad/admin/encuestas/",
        )

