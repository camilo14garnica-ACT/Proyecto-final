from django.core.management.base import BaseCommand
from django.utils import timezone

from promociones.models import Promocion


class Command(BaseCommand):
    help = "Desactiva las promociones activas cuya fecha de fin ya pasó."

    def handle(self, *args, **options):
        hoy = timezone.localdate()
        cantidad = Promocion.objects.filter(
            estado="ACTIVA", fecha_fin__lt=hoy
        ).update(estado="INACTIVA", inactiva_por_vencimiento=True)
        self.stdout.write(self.style.SUCCESS(f"Promociones desactivadas por vencimiento: {cantidad}"))