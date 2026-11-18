import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def enviar_correo_notificacion(destinatario_email, asunto, mensaje_texto, html_message=None):
    """Envía un correo electrónico de forma segura sin interrumpir la ejecución si falla el SMTP."""
    if not destinatario_email:
        return False

    remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@mascott.com'

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=remitente,
            recipient_list=[destinatario_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Correo enviado exitosamente a {destinatario_email}: {asunto}")
        return True
    except Exception as e:
        logger.warning(f"No se pudo enviar correo a {destinatario_email} ({asunto}): {e}")
        return False

