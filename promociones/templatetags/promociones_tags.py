from django import template
from django.utils import timezone

from promociones.models import Promocion

register = template.Library()


def promociones_vigentes():
    """Activas y dentro de sus fechas de inicio y fin."""
    hoy = timezone.localdate()
    return Promocion.objects.filter(
        estado="ACTIVA", fecha_inicio__lte=hoy, fecha_fin__gte=hoy
    ).order_by("fecha_fin")


@register.inclusion_tag("promociones/_carrusel.html")
def carrusel_promociones():
    return {"promociones": promociones_vigentes()}