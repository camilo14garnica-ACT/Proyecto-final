from django.contrib.auth import get_user_model
from .models import Notificacion
from .emails import enviar_correo_notificacion

Usuario = get_user_model()


def crear_notificacion(usuario, titulo, mensaje, tipo=Notificacion.Tipo.INFO, enlace='', enviar_email=True):
    """Crea una notificación en el sistema y opcionalmente envía un correo al usuario."""
    notif = Notificacion.objects.create(
        usuario=usuario,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo,
        enlace=enlace,
    )

    if enviar_email and usuario.email:
        asunto = f"[Mascott Calidad] {titulo}"
        cuerpo = f"Hola {usuario.first_name or usuario.username},\n\n{mensaje}\n\nPara más detalles visita la plataforma Mascott:\n{enlace if enlace else 'https://mascott.com'}\n\nAtentamente,\nEquipo de Gestión de Calidad Veterinaria Mascott"
        enviar_correo_notificacion(usuario.email, asunto, cuerpo)

    return notif


def notificar_administradores(titulo, mensaje, tipo=Notificacion.Tipo.INFO, enlace='', enviar_email=True):
    """Envía una notificación a todos los usuarios administradores."""
    admins = Usuario.objects.filter(rol='ADMIN')
    creadas = []
    for admin_user in admins:
        n = crear_notificacion(
            usuario=admin_user,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            enlace=enlace,
            enviar_email=enviar_email,
        )
        creadas.append(n)
    return creadas

